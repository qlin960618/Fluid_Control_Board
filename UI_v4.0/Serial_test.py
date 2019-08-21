import serial
import time








tstart=time.time()
time.sleep(0.0000001)


for i in range(1):
	pass

print("Time passed: %.6f"%((time.time())*1000))



pwd="/dev/cu.wchusbserial14140"


#serLink = serial.Serial(pwd, 9600, timeout=0.1, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)

#time.sleep(2)


#while 1:
#	time.sleep(0.1)
#	print("%s"%(serLink.read(1)))
