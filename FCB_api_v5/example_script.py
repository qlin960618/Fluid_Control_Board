#import Module
from FCB import FCB
import time


board=FCB()
board.listAllSerialPort()
if board.startLink("/dev/cu.usbmodem14101")==True:
	print("Serial Connected")



#add and initialize channel to list
board.addChannel(-1, 30, 0)
board.addChannel(-1, 30, 1)
board.addChannel(-1, 30, 7)
board.addChannel(-1, 30, 5)

#remove channel from list
board.removeChannnel(0)

#print the list of channel 
board.printAllChannel()

#print current channel value
print("val %d"%(board.getValFromID(1)))
board.setChannelVal(0,600)
print("ch1 set")
time.sleep(2)

#Set Channel using kPa Value
board.setChannelKPa(2,6.03)

#print current channel value in kPa
print("kpa %.3f"%(board.getKPaFromID(0)))

#Set Channel using sensor Value
board.setChannelVal(2,889)

#request Channel Status (This need to be called before getStatus)
board.requestStatus()	#refresh all channels status
print(board.getStatus(2))

#delay
time.sleep(2)


board.requestStatus()
print(board.getStatus(2))

#zero all  channels in the list
board.zeroAll()




