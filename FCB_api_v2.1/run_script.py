from sys import version_info
import time
from FCB import FCB



SERIAL_PORT="/dev/cu.wchusbserial14120"


board=FCB()
#board.listAllSerialPort()
if board.startLink("/dev/cu.usbmodem14101")==True:
	print("Serial Connected")

#for i in range(10):
#	b=board.SerialDev.readByte()
#	print(b)


CH0_H =170
CH1_H =320
CH2_H =124
CH3_H =180
CH4_H =157
CH5_H =116



board.addChannel(-1, 30, 0)
board.addChannel(-1, 30, 1)
board.addChannel(-1, 30, 2)
board.addChannel(-1, 30, 3)
board.addChannel(-1, 30, 4)
board.addChannel(-1, 30, 5)

print("starting Sequence")
board.setChannelVal(0,CH0_H)
board.setChannelVal(2,CH2_H)
board.setChannelVal(3,CH3_H)
board.setChannelVal(5,CH5_H)

time.sleep(2)
print("bp1")
board.setChannelVal(2,0)

time.sleep(.5)
board.setChannelVal(1,CH1_H)

time.sleep(.5)
board.setChannelVal(2,CH2_H)

time.sleep(.5)
for i in range(10):
	print("bp2")
	board.setChannelVal(3,0)
	time.sleep(.5)
	board.setChannelVal(4,CH4_H)
	time.sleep(.5)
	board.setChannelVal(3,CH3_H)
	time.sleep(.5)
	print("bp3")
	board.setChannelVal(0,0)
	time.sleep(.5)
	board.setChannelVal(1,0)
	time.sleep(.5)
	board.setChannelVal(0,CH0_H)
	time.sleep(.5)
	print("bp4")
	board.setChannelVal(5,0)
	time.sleep(.5)
	board.setChannelVal(4,0)
	time.sleep(.5)
	board.setChannelVal(5,CH5_H)
	time.sleep(.5)
	print("bp5")

board.zeroAll()