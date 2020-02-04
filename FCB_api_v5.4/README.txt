This software is a serial connected API use for controlling the fluid control board project. Listed below are the avaliable function of the program. 


def startLink(SerAdr):
	begin serial link connection to the arduino with the given serial port address. SerAdr take in String as a variable
	The funtion utilize the SerialInterface module and call the constructor and connectDevice function
	More function can be access from the SerialDev object within this module

def listAllSerialPort():
	This function call the listAllPort function from the SerialDev object.
	print all existing serial port on the computer.

def addChannel(indexIn, SRangeIn, channelIDIn):
	This function add a channel into the stored list of channels. 
	return true if the channel item is added

	indexIn: the index that will be use for future call within this API. Use -1 for appending to the end, and other for insert. The index check is 		included for checking the validity of the input
	SRangIn: The range of seneor used, this is given in PSI value, For example, the current existing sensor in the lab are 30, and 100 PSI range, Put 	in 30 or 100 accordindly.
	channelIDIn: this value need to corrspond to the ID number stored in the arduino, cor the current setup, the Channel ID is from 0 to 12. this can 	be double checke with the pin maping from the arduino code

def removeChannnel(indexIn):
	Remove channel at the specified index
	return true if successfully removed. 

def getNChannel():
	Get number of channels

def checkIndexBound(ind):
	check if Index is in bound, return index if yes, -1 if false

def printAllChannel():
	Print all channels information, (ID, index, status and range)

def requestStatus():	
	This should be call before function getStatus. This sent request to the control board and retrive channel status information. 

def getStatus(index):
	Get status of the channel, information is not updated until the requestStatus is called.
	return False if the specified channel is in the process of setting. True if the actual value is 1% within the set value.

def setChannelVal(index, valIn):
	set specified index channel to the value specified by valIn, that is from 0 to maximum of VAL_MAX in the program parameter.
	the function return true if channel is successfully set 
	False if the value or index is invalid or the set value is the current value.

def setChannelBinary(index, state):
	input boolean "state" to control channel always on/off, 
	the function return true if channel is successfully set 
	False if the value or index is invalid or the set value is the current value.

def setChannelKPa(index, valIn):
	Same as setChannelVal, instead takes in kPa floating point as parameter
	
def zeroAll():
	Zero all channels
	
def getIndexFromID(IDin):
	get index from channel ID, return -1 if ID is not found
	
def getValFromIndex(ind):
	get current channel value from index
	
def getKPaFromIndex(ind):
	get current channel value in kPa from ID
	
def getValFromID(IDin):
	get current channel value from index

def getKPaFromID(IDin):
	get current channel value in kPa from ID

def convertKPaToVal(index, kpaIn):
	input channel index and kpa value, convert to sensor value

def convertValToKPa(index, valIn):
	input channel index and sensor value, convert to kPa value


def resetAll():
	Reset Object, Serial link, clear channels, do not update value to arduino