import struct
import pigpio
import subprocess
import time

pi = pigpio.pi()

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
		if(code == 2 and index ==4):
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
	exit()


	
