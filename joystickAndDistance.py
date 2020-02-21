import struct
import pigpio
import subprocess
import time
from threading import Thread
import RPi.GPIO as GPIO

pi = pigpio.pi()

#set GPIO's for the Distance Sensor
GPIO.setmode(GPIO.BCM)
GPIO_TRIGGER = 18
GPIO_ECHO = 24

#pi.set_mode(GPIO_TRIGGER, pigpio.OUTPUT)
#pi.set_mode(GPIO_ECHO, pigpio.INPUT)

GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

def getDistance():
	global distance
	while True:
		time.sleep(0.5)
		#set Trigger to HIGH
		#pi.write(GPIO_TRIGGER, pigpio.HIGH)

		GPIO.output(GPIO_TRIGGER, True)
	
		#set Trigger to LOW again after 0.01 ms
		time.sleep(0.00001)
		#pi.write(GPIO_TRIGGER, pigpio.LOW)
		GPIO.output(GPIO_TRIGGER, False)
			
		startTime = time.time()
		releaseTime = time.time()

		#set startTime
		while GPIO.input(GPIO_ECHO) == 0:
			StartZeit = time.time()
		#set releaseTime
		while GPIO.input(GPIO_ECHO) == 1:
			releaseTime = time.time()

		#get elapsed time
		elapsedTime = releaseTime - startTime

		#multiply by speed of sound and divide by two, because the sound goes there and back
		distance = (elapsedTime*34300)/2
	


def controll():
	with open("/dev/input/js0", "rb") as f:
		while True:
			a = f.read(8)
			t, value, code, index = struct.unpack("<Ihbb", a) # 4 bytes, 2 bytes, 1 byte, 1 byte
			# t: time in ms
			# index: button/axis number (0 for x-axis)
			# code: 1 for buttons, 2 for axis
			# value: axis position, 0 for center, 1 for buttonpress, 0 for button release	
			print("t: {:10d} ms, value: {:6d}, code: {:1d}, index: {:1d}".format(t, value, code, index))
			#if RT pressed move forward
			if(code == 2 and index ==4 and distance > 30):
				dutycycle =int(1500+(value+32767)*100/65534)
				print("RT Pressed by:", dutycycle)
				pi.set_servo_pulsewidth(17,dutycycle)
			if(code == 2 and index ==5):
				dutycycle = int(1500-(value+32767)*100/65534)
				print("LT Pressed by:", dutycycle)
				pi.set_servo_pulsewidth(17,dutycycle)

			#if left stick is pushed to left side => move left
			if(code == 2 and index == 0 and value<0):
				dutycycle =int(value*400/32767+1500)
				print("Turn Left by: ",dutycycle)
				pi.set_servo_pulsewidth(4, dutycycle)
			#if left stick is pushed to right side => move right
			elif(code == 2 and index == 0 and value>0):
				dutycycle = int(value*400/32767+1500)
				print("Turn right by: ",dutycycle)
				pi.set_servo_pulsewidth(4,dutycycle)
			#if left stick is in middle position => center the servo
			elif(code == 2 and index == 0 and value==0):
				print("Center Servo")
				pi.set_servo_pulsewidth(4,1500)
			#set all signals to null
			if(code == 1 and index ==7 and value == 1):
				break
		pi.set_servo_pulsewidth(17,0)
		pi.set_servo_pulsewidth(4,0)
		pi.stop()
		GPIO.cleanup()
		exit()	

thread1 = Thread(target = controll)
thread2 = Thread(target = getDistance)

thread1.start()
thread2.start()

thread1.join()
thread2.join()

	
