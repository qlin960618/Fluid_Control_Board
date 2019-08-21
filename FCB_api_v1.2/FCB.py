from sys import version_info


import time
import serial.tools.list_ports as serialList
import serial
from SerialInterface import SerialInterface
import struct





VERBOSE=1 #debugger
DEFULT_SENSOR_RANGE=30  #psi

VAL_MAX=890
VAL_MIN=0



class FCB:

	"""
	n_channel=0
	channelVal=[]
	SensorRange=[]
	SerialDev=None
	"""


	def __init__(self, SerAdr=None):

		self.n_channel=0
		self.channelVal=[]
		self.sensorRange=[]
		self.channelStatus=[]
		self.channelID=[]

		self.SerialDev=SerialInterface()

		if SerAdr!=None:
			if self.SerialDev.connectDevice(SerAdr)==True:
				print("Successful")
			else:
				self.SerialDev.reset()
				print("Unsuccessful")


	"""
	function: reset all
	"""
	def resetAll(self):
		self.n_channel=0
		self.channelVal=[]
		self.sensorRange=[]
		self.channelStatus=[]
		self.channelID=[]

		self.SerialDev.resetAll()


	"""
	Function: Begin Serial Connection
	SerAdr: Serial address of the 
	"""
	def startLink(self, SerAdr):
		ret=self.SerialDev.connectDevice(SerAdr)
		if ret==True:
			if VERBOSE>0:
				print("Successful")
			return True
		else:
			self.SerialDev.reset()
			if VERBOSE>0:
				print("Unsuccessful")
			return False

	"""
	function: add actuator channel
	index: index of inserted location, -1: end
	SRange: Sensor range, 0 for default
	channelID: identifer for Arduino [following order of array in arduino code]
	return: False failed, True successful
	"""
	def addChannel(self, indexIn, SRangeIn, channelIDIn):

		#index processing
		if indexIn<-1:
			return False
		elif indexIn==-1:
			index=self.n_channel
		elif indexIn>self.n_channel:
			return False
		else:
			index=indexIn
		#Sensor range processing
		if SRangeIn<0:
			return False
		elif SRangeIn==0:
			SRange=DEFULT_SENSOR_RANGE
		else:
			SRange=SRangeIn

		#channelID processing
		try:
			self.channelID.index(channelIDIn)
			if VERBOSE>0:
				print("ChannnelID duplication")
			return False
		except ValueError:
			pass


		self.n_channel+=1
		self.channelVal.insert(index, VAL_MIN)
		self.sensorRange.insert(index, SRange)
		self.channelID.insert(index, channelIDIn)
		self.channelStatus.insert(index, False)
		if VERBOSE>0:
			print("Channel Added")
		return True

	"""
	function, remove channel from list
	indexIn: -1 for last, must be <n_channel
	"""
	def removeChannnel(self, indexIn):
		if indexIn<-1:
			if VERBOSE>0:
				print("index out of bound")
			return False
		elif indexIn==-1:
			index=self.n_channel-1
		elif indexIn>=self.n_channel:
			if VERBOSE>0:
				print("index out of bound")
			return False
		else:
			index=indexIn

		self.n_channel-=1
		self.channelVal.pop(index)
		self.sensorRange.pop(index)
		self.channelID.pop(index)
		self.channelStatus.pop(index)
		if VERBOSE>0:
			print("Channel Removed")
		return True

	"""
	Set channel value using sensor value
	index: index of channel
	valIn: value in term of sensor
	"""
	def setChannelVal(self, index, valIn):
		valIn=int(valIn)
		self.SerialDev.testConnection()
		#index validation
		if self.checkIndexBound(index)==-1:
			return False
		#Serial Status check
		if self.SerialDev.getStatus()==False:
			print("Serial not connected")
			return False
		#value repeat check
		if self.channelVal[index]==valIn:
			if VERBOSE>1:
				print("set value is same")
			return False
		#value min max bound check
		if valIn<VAL_MIN or valIn> VAL_MAX:
			if VERBOSE>0:
				print("Value out of bound")
			raise ValueError("set value out of bound")
			return False
		#grab channel ID
		x=self.channelID[index]
		#pre-processing for parity
		par=x<<10|valIn
		par ^= par >> 8
		par ^= par >> 4
		par ^= par >> 2
		par ^= par >> 1
		parity=(~par)
		#processing fo transmission
		c=[0,0]
		#two byte of data: channel 5bits, value 10bits, parity 1bit (set on even)
		c[0]= struct.pack("B",(((x&0x1F)<<3)|((valIn>>7)&0x7))&0xff)
		c[1]= struct.pack("B",(valIn<<1|(parity&0x1))&0xff)

		#initiate communication
		self.SerialDev.resetBuffer()
		nAttemp=0
		#account for frequency limit, repeat untill sent
		while self.SerialDev.sentBytes(c, 2)==-1 and nAttemp<10:
			nAttemp+=1
			if VERBOSE>1:
				print("attempt #%d"%(nAttemp))
			time.sleep(0.02)

		#read return confirmation byte
		b=0
		b=self.SerialDev.readByte()


		if b==b'k':	#return String match
			if VERBOSE>0:
				print("Channel %d is set to %d"%(x+1, valIn))
			self.channelVal[index]=valIn
			self.channelStatus[index]=True
			return True
		else:
			if VERBOSE>1:
				print("Set Failed: return string mismatch")
			return False

	"""
	Set channel value using sensor value
	index: index of channel
	valIn: value in term of kpa
	"""				
	def setChannelKPa(self, index, valIn):
		#index validation
		self.checkIndexBound(index)
		return self.setChannelVal( index, self.convertKPaToVal(self.sensorRange[index], valIn))

	"""
	Function: Set all channel to zero
	"""
	def zeroAll(self):
		succ=True
		for i in range(self.n_channel):
			if VERBOSE>0:
				print("\tSeting index %d to 0"%(i))
			if self.setChannelVal(i,0)==False:
				succ=False
		if succ==False:
			print("Fail to set all channel")
		return succ




	#information function	

	##return number of channel
	def getNChannel(self):
		return self.n_channel
	##call print all port function in SerialInterface
	def listAllSerialPort(self):
		self.SerialDev.listAllPort()
	##list all existing channel
	def printAllChannel(self):
		print("Listing all channel")
		print("\tIndex\tID\tValue\tStatus\tSensor Range")
		for i in range(self.n_channel):
			print("\t%d\t%d\t%d\t%d\t%d"%(i, self.channelID[i], self.channelVal[i], 
					self.channelStatus[i], self.sensorRange[i]))
	##get Index via channel ID
	def getIndexFromID(self, IDin):
		try:
			ind=self.channelID.index(IDin)
		except ValueError:
			raise ValueError("channel ID not found")
			return -1
		return ind
	##get Value by Channel index
	def getValFromIndex(self, ind):
		if ind<0 or ind>=self.n_channel:
			raise IndexError("channel index out of bound")
			return -1
		else:
			return self.channelVal[ind]
	##check index bound
	def checkIndexBound(self, ind):
		if ind<0 or ind>=self.n_channel:
			raise IndexError("channel index out of bound")
			return -1
		else:
			return ind
	##get value in kpa unit 
	def getKPaFromIndex(self,ind):
		self.checkIndexBound(ind)
		return self.getValFromIndex(ind)*self.sensorRange[ind]*0.007013712565

	##get Value by channel ID
	def getValFromID(self, IDin):
		return self.channelVal[self.getIndexFromID(IDin)]
	##get value in kpa unit 
	def getKPaFromID(self,IDin):
		ind = self.getIndexFromID(IDin)
		return self.channelVal[ind]*self.sensorRange[ind]*0.007013712565
	##get channel status
	def getStatus(self, ind):
		self.checkIndexBound(ind)
		return self.channelStatus[ind]
	##convert pressure from kpa to sensor value
	def convertKPaToVal(self, SRange, kpaIn):
		return int(round(kpaIn*142.5778417/SRange))




def main():

	board=FCB()
	board.listAllSerialPort()
	if board.startLink("/dev/cu.wchusbserial14120")==True:
		print("Serial Connected")
	board.addChannel(-1, 0, 0)
	board.removeChannnel(0)
	board.addChannel(-1, 0, 0)
	board.addChannel(-1, 100, 1)
	board.addChannel(-1, 100, 7)
	board.printAllChannel()
	print("val %d"%(board.getValFromID(1)))
	board.setChannelVal(2,80)
	board.setChannelVal(2,30)
	board.setChannelVal(2,40)
	print("kpa %.3f"%(board.getKPaFromID(0)))
	board.setChannelKPa(2,1.03)
	board.getStatus(1)
	board.zeroAll()


if __name__=='__main__':
	main()







