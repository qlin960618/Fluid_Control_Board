import serial.tools.list_ports as serialPortList
from functools import partial
import time
import serial


MIN_INTERVAL=50
VERBOSE_LEVEL=0 #debugger
INITIAL_SLEEP=2	#time fro connection to arduino ready



class SerialInterface():


	portConnected = False
	serialLink = None
	
	#stored list of existing ports
	portsList=None
	n_portsList=0
	#lastTimeCalled=0


	"""
	function: Constructor
	"""
	def __init__(self):

		self.portConnected=False
		self.serialLink=None
		
		self.portsList=None
		self.n_portsList=0
		#self.lastTimeCalled=time.time()
		self.updatePortList()


	"""
	function: Update List of ports
	return: list of port objects
	"""
	def updatePortList(self):

		self.portsList = list(serialPortList.comports())
		self.n_portsList=len(self.portsList)

		return self.portsList

	"""
	function: return device by HWID search
	return: None or device path
	"""
	def getPathFromPID(self, PIDin):
		if self.portsList==None:
			print("Serial: Port list not yet updated.")
			self.updatePortList()

		i_stored=-1
		for i in range(self.n_portsList):
			if self.portsList[i].pid==PIDin:
				if i_stored!=-1:
					print("Serial: Multiple match found")
					return None
				i_stored=i

		#match found
		if i_stored>=0:
			return self.portsList[i_stored].device

		print("Serial: PID Not found.")
		return None


	"""
	function: print out all existing port on this computer
	return: all port object
	"""
	def listAllPort(self):
		if self.portsList==None:
			print("Serial: Port list not yet updated.")
			self.updatePortList()

		print("Serial: Listing ports...")
		for i in range(self.n_portsList):
			print("\t%s\t%s\t%s"%(self.portsList[i].device.ljust(31), self.portsList[i].vid, self.portsList[i].pid))

		return self.portsList


	"""
	Function: Initiate connection
	return: true for successful connection, false for failed
	"""
	def connectDevice(self,devPath):
		if self.portConnected==True:
			print("Serial: port already open, clearing now")
			self.reset()

		try:
			self.serialLink = serial.Serial(devPath, 9600, timeout=0.1, parity=serial.PARITY_NONE, 
										stopbits=serial.STOPBITS_ONE,
										bytesize=serial.EIGHTBITS)
		except (OSError, serial.SerialException, ValueError):
			print("SerialApp: Connection Failed")
			self.reset()
			return False

		#serial successfully connected
		self.portConnected = True

		#short sleep for arduino to ready
		time.sleep(INITIAL_SLEEP)

		return True

	"""
	Function: reset Input buffer
	"""
	def resetBuffer(self):
		if self.portConnected==False:
			print("Serial: device not found.")
			return False
		if self.serialLink.in_waiting>0:
			self.serialLink.reset_input_buffer()
		return True

	"""
	Function: sent byte
		c: bytes array
		n: number of byte
		type: command type, 
	return False for failed, -1 for unavaliable
	"""
	def sentBytes(self, c, n):
		#print("fcheck: %.4f"%(time.time()-self.lastTimeCalled))
		#if (time.time()-self.lastTimeCalled)*1000<MIN_INTERVAL:
		#	if VERBOSE_LEVEL>0:
		#		print("Serial: Update frequency limit reached")
		#	return -1
		if(n<=0) or len(c)!=n:
			print("Serial: Parameter error")
			return False
		if self.portConnected==False:
			print("Serial: device not found.")
			return False

		retnum=[0 for x in range(n)]
		try:
			for i in range(n):
				retnum[i]=self.serialLink.write(c[i])
		except (serial.SerialTimeoutException):
			self.reset()
		except TypeError:
			print("Serial: input error.")
		#update timer
		#self.lastTimeCalled=time.time()
		return True


	"""
	Function: sent byte
		c: byte to sent
	return False for failed
	"""
	def sentByte(self, c):
		#if (time.time()-self.lastTimeCalled)*1000<MIN_INTERVAL:
		#	if VERBOSE_LEVEL>0:
		#		print("Serial: Update frequency limit reached")
		#	return -1
		if self.portConnected==False:
			print("Serial: device not found.")
			return False
		try:
			retnum=self.serialLink.write(c)
		except (serial.SerialTimeoutException):
			self.reset()
		except TypeError:
			print("Serial: input error.")
		#update timer
		#self.lastTimeCalled=time.time()
		#return retnum


	def readByte(self):
		if self.portConnected==False:
			print("Serial: device not found.")
			return False
		b='0'
		try:
			b=self.serialLink.read()
			return b
		except (serial.SerialTimeoutException):
			print("Serial: device timed out")
			return 0


	def getStatus(self):
		if self.portConnected==True: 
			return True
		else:
			return False

	def testConnection(self):
		try:
			if self.serialLink.isOpen()==False:
				print("Serial: Connection Dropped")
				self.reset()
		except AttributeError:
			pass

 	#reset only serial connection
	def reset(self):
		self.portConnected = False
		try:
			self.serialLink.close()
			self.serialLink.__del__()
		except (AttributeError, OSError, serial.SerialException):
			print("Serial: Serial port is already closed")
		self.serialLink = None

	#deep reset
	def resetAll(self):
		self.portsList=None
		self.n_portsList=0
		self.portConnected = False
		try:
			self.serialLink.close()
			self.serialLink.__del__()
		except (AttributeError, OSError, serial.SerialException):
			print("SerialApp: Serial port is already closed")
		self.serialLink = None

#for testing purpose
def main():
	serInt=SerialInterface()
	devname=serInt.getPathFromPID(29987)
	serInt.listAllPort()
	serInt.sentBytes([23],2)
	if serInt.connectDevice("/dev/cu.wchusbserial14120")==True:
		print("Successful")
	serInt.sentBytes([50,100],2)
	if serInt.sentBytes([50,100],2)==-1:
		print("too Soon")
		while serInt.sentBytes([50,100],2)==-1:
			pass

	print("done")

	serInt.reset()



if __name__=='__main__':
	main()





	