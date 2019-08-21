import serial.tools.list_ports as serialList
from functools import partial
import time
import serial
import threading


from sys import version_info
if version_info.major == 2:
	import Tkinter as tk
elif version_info.major == 3:
	import tkinter as tk



class SerialApp():

	portSelection=-1
	serLink=None

	def __init__(self, serialWindow):

		self.serialWindow=serialWindow
		#self.serialWindow = tk.Tk() #initialize Tkinter
		self.serialWindow.title("Serial Port Selection ") 
		self.serialWindow.geometry('+600+700')
	
		#find all serial port
		self.ports = list(serialList.comports())
		#for p in ports:
		#   print("%s\t%s"%(p, p.serial_number))

		self.n_Serial_Port=len(self.ports)
		print("SerialApp: Total %d Port Found"%(self.n_Serial_Port))

		#seperator
		self.separator = tk.Frame(self.serialWindow,  height=2, width=400, bg='black')
		self.separator.grid(row=1, column=0, columnspan=4, pady=5)
		

		#connect
		self.connectBtn=tk.Button(self.serialWindow, text="connect", command=self.connection_btn)
		self.connectBtn.grid(column=0, row=2)
		self.statusLabel1=tk.Label(self.serialWindow, text="status:")
		self.statusLabel1.grid(column=2, row=2)
		self.statusLabel2=tk.Label(self.serialWindow, text="Disconnected", bg="red")
		self.statusLabel2.grid(column=3, row=2)

		#self.readSerial=tk.Button(self.serialWindow, text="read", command=self.read)
		#self.readSerial.grid(column=0, row=3)

		#for testing
		#self.sentBtn=tk.Button(self.serialWindow, text="sent", command=partial(self.sent_byte, '1'))
		#self.sentBtn.grid(row=3)

		self.serialFrame=tk.Frame(self.serialWindow)
		self.serialFrame.grid(column=0, row=0, columnspan=4)

		self.serialBtn=[0 for x in range(self.n_Serial_Port)]
		self.serialBtnLabel=[0 for x in range(self.n_Serial_Port)]

		for i in range(self.n_Serial_Port):
			self.serialBtn[i]=tk.Button(self.serialFrame, text="%s"%(self.ports[i]), command=partial(self.selection_btn, i))
			self.serialBtn[i].grid(column=1, row=i, columnspan=4)
			self.serialBtnLabel[i]=tk.Label(self.serialFrame, text=" ", bg='grey')
			self.serialBtnLabel[i].grid(column=0, row=i)


		#########main loop disable to prevent huging process
		#self.serialWindow.mainloop()

	def selection_btn(self, x):
		self.portSelection=x
		self.update_serial_btn_label()

	def update_serial_btn_label(self):
		for i in range(self.n_Serial_Port):
			if i!=self.portSelection:
				self.serialBtnLabel[i].config(bg='grey')
			else:
				self.serialBtnLabel[i].config(bg='blue')

	def disable_serial_btn(self, action):
		for i in range(self.n_Serial_Port):
			if action==0:
				self.serialBtn[i].config(state='disabled')
			else:
				self.serialBtn[i].config(state='normal')

	def reset_all(self):
		print("SerialApp: resettign all...")
		self.connectBtn.config(state='disabled')
		try:
			self.serLink.close()
			self.serLink.__del__()
		except (AttributeError, OSError, serial.SerialException):
			print("SerialApp: Serial port is already closed")
		self.serLink=None
		self.disable_serial_btn(1)
		self.portSelection=-1
		self.update_serial_btn_label()
		self.statusLabel2.config(text="Disconnected", bg='Red')
		self.connectBtn.config(state='normal', text="connect")

	def connection_btn(self):
		if self.serLink==None:
			self.connectBtn.config(state='disabled')
			if self.portSelection<0:
				print("SerialApp: Failed! No COM Port were selected")
			else:
				#################################################establish connection here###################################
				#self.serLink=1
				try:
					self.serLink = serial.Serial(self.ports[self.portSelection].device, 9600, timeout=0.1, parity=serial.PARITY_NONE, 
												stopbits=serial.STOPBITS_ONE,
												bytesize=serial.EIGHTBITS)
				except (OSError, serial.SerialException, ValueError):
		 			print("SerialApp: Connection Failed")
		 			try:
		 				self.serLink.close()
		 				self.serLink.__del__()
		 			except AttributeError:
		 				pass
		 			self.serLink=None
				time.sleep(1)


				if self.serLink!=None:
					print("SerialApp: Connection Successful...\n\tat: %s\n"%(self.ports[self.portSelection]))
					self.disable_serial_btn(0)
					self.statusLabel2.config(text="  Connected  ", bg='green')
					self.connectBtn.config(text="disconnect")
					#self.serLink.reset_input_buffer()
				else:
					print("SerialApp: Connection failed for some reason")
					self.reset_all()

			self.connectBtn.config(state='normal')
		else:
			self.reset_all()

	def reset_buffer(self):
		#print("Byte in waiting: %d"%(self.serLink.in_waiting))
		if self.serLink!=None:
			if self.serLink.in_waiting>0:
				self.serLink.reset_input_buffer()
		else:
			print("SerialApp: port not found")

	def sent_byte(self, c0):
		if self.serLink!=None: 
			#print("SerialApp: senting %s"%(b))
			try:
				num=self.serLink.write(c0)
				#print("%d byte written"%(num+num2))
				#self.serLink.write(d)
			except serial.SerialTimeoutException:
				self.reset_all()
		else:
			print("SerialApp: port not found")

	def sent_bytes(self, c0, c1):
		if self.serLink!=None: 
			#print("SerialApp: senting %s"%(b))
			try:
				num=self.serLink.write(c0)
				num2=self.serLink.write(c1)
				#print("%d byte written"%(num+num2))
				#self.serLink.write(d)
			except serial.SerialTimeoutException:
				self.reset_all()
		else:
			print("SerialApp: port not found")
	def read_bytes(self):
		if self.serLink!=None: 
			#print("SerialApp: senting %s"%(b))
			b=self.serLink.read()
#			print(b)
			return b
		else:
#			print("Serial timeout")
			print("SerialApp: port not found")
			return 0
	#def read(self):
	#	self.read_bytes()


	def status(self):
		if self.serLink!=None: 
			return 1
		else:
			return 0

	def test_connection(self):
		try:
			if self.serLink.isOpen()==False:
				print("SerialApp: Connection Dropped")
				self.reset_all()
		except AttributeError:
			pass


def main():
	serialApp=SerialApp()

if __name__=='__main__':
	main()