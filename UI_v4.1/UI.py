from sys import version_info
if version_info.major == 2:
	import Tkinter as tk
	from Tkinter import messagebox
elif version_info.major == 3:
	import tkinter as tk
	from tkinter import messagebox

import time
from functools import partial
from SerialInterface import SerialInterface
import struct
import pickle
import os


VERBOSE=0 #debugger

N_CHANNEL=13
MAX_BTN_PRESENT=True #False if want to remove Max btn

SENSOR_MIX=False #if using sensor with different maximum set to true
SENSOR_RANGE=30 #sensor maximum range in PSI
#SENSOR_RANGE=[100, 30, 30, 30, 30, 30, 30, 30, 30, 30]


#default setting file save path
DEFAULT_SAVE_PATH="./SaveData/Temp.fcbset"


VAL_MAX=800			#abs min max of the input value, 800 should be abs max
VAL_MIN=0
SLIDER_LENGTH=350	#hight of the slider 
BTN_OFFSET=2 		#offset for the Down/Up Btn

MIN_INTERVAL=50 	#Serial update limmit in ms

def main():
	UIApp=App(tk.Tk())

class App:

	def __init__(self, masterWindow):	
		###############################Initializer##############################
		#Intialize Global variabel 
		self.chVal=[0 for x in range(N_CHANNEL)]
		self.valMax=[VAL_MAX for i in range(N_CHANNEL)]

		#misc variable
		self.currentState=False   #current state of the program

		self.SerialApp=SerialInterface()

		#Window
		self.masterWindow=masterWindow
		#assign title
		self.masterWindow.title("Fluid Control Board UI")

		####UI layout setup
		self.UILabel=tk.Label(self.masterWindow, text="Control Panel")
		self.UILabel.grid(row=0, column=0, columnspan=7)

		self.spacer1=tk.Label(self.masterWindow, text="")
		self.spacer1.grid(row=2, column=0, columnspan=7)

		#state/mode Frame
		self.smFrame=tk.Frame(self.masterWindow)
		self.smFrame.grid(row=3, column=1)
		#item Initialization
		self.quitBtn=tk.Button(self.smFrame, text="Quit", command=self.close_Window)
		self.quitBtn.grid(row=0, column=0)
		self.zeroAllBtn=tk.Button(self.smFrame, text="Zero All", command=self.zero_All)
		self.zeroAllBtn.grid(row=1, column=0)
		"""
		self.disableAllBtn=tk.Button(self.smFrame, text="disableAll", 
									activebackground='blue', command=partial(self.toggle_State, False))
		self.disableAllBtn.grid(row=2, column=0)
		self.enableAllBtn=tk.Button(self.smFrame, text="enableAll", state='disabled',
									activebackground='blue', command=partial(self.toggle_State, True))
		self.enableAllBtn.grid(row=3, column=0)
		"""


		#information Frame
		self.infoFrame=tk.Frame(self.masterWindow)
		self.infoFrame.grid(row=3, column=0)
		#information item
		self.colorLabel1=tk.Label(self.infoFrame, text="Channel Status Code", font=("Courier", 16))
		self.colorLabel1.grid(row=0, column=0, columnspan=2 )
		self.matchLabel1=tk.Label(self.infoFrame,text="        ", bg="green", borderwidth=3, relief="groove")
		self.matchLabel1.grid(row=1, column=1)
		self.mismatchLabel1=tk.Label(self.infoFrame,text="        ", bg="tan1", borderwidth=3, relief="groove")
		self.mismatchLabel1.grid(row=2, column=1)
		self.errorLabel1=tk.Label(self.infoFrame,text="        ", bg="red", borderwidth=3, relief="groove")
		self.errorLabel1.grid(row=3, column=1)
		self.matchLabel2=tk.Label(self.infoFrame,text="Set")
		self.matchLabel2.grid(row=1, column=0)
		self.mismatchLabel2=tk.Label(self.infoFrame,text="Mismatch")
		self.mismatchLabel2.grid(row=2, column=0)
		self.errorLabel2=tk.Label(self.infoFrame,text="Error")
		self.errorLabel2.grid(row=3, column=0)


		#Serial Frame
		self.serialFrame=tk.Frame(self.masterWindow, bd=1)
		self.serialFrame.grid(row=3, column=3, columnspan=2)
		#Serial Frame Initialization
		self.sfLabel=tk.Label(self.serialFrame, text="Serial Port Selection")
		self.sfLabel.grid(row=0, column=0, columnspan=4)
		self.serialConnectBtn=tk.Button(self.serialFrame, text="Connect", command=self.initialize_Serial)
		self.serialConnectBtn.grid(row=1, column=0)
		self.serialDisconnectBtn=tk.Button(self.serialFrame, text="Disonnect", 
											command=self.reset_Serial, state='disabled')
		self.serialDisconnectBtn.grid(row=2, column=0)
		self.serialSL=tk.Label(self.serialFrame, text="Status:")
		self.serialSL.grid(row=1, column=1, rowspan=2)
		self.serialStatusLabel=tk.Label(self.serialFrame, text="           ", bg='red')
		self.serialStatusLabel.grid(row=1, column=2, rowspan=2)
		self.serialRefreshBtn=tk.Button(self.serialFrame, text="Refresh", command=self.refresh_Serial)
		self.serialRefreshBtn.grid(row=1, column=3, rowspan=2)
		self.serialPort=tk.StringVar()
		#self.portlist=["PlaceHolder1", "PlaceHolder2"]
		self.SerialList=tk.OptionMenu(self.serialFrame, self.serialPort, "PlaceHolder1", "PlaceHolder2")
		self.SerialList.grid(row=3, column=0, columnspan=4)


		#Save frame
		self.saveFrame=tk.Frame(self.masterWindow)
		self.saveFrame.grid(row=3, column=5, columnspan=2)
		#item initialization
		self.saveBtn=tk.Button(self.saveFrame, text='Save', command=self.save_Parameter, width=7)
		self.saveBtn.grid(row=0, column=0)
		self.loadBtn=tk.Button(self.saveFrame, text='Load', command=self.load_Parameter, width=7)
		self.loadBtn.grid(row=0, column=1)
		self.savePathVar=tk.StringVar(self.saveFrame)
		self.savePathEntry=tk.Entry(self.saveFrame, textvariable=self.savePathVar)
		self.savePathEntry.grid(row=1, column=0, columnspan=2)
		self.savePathVar.set(DEFAULT_SAVE_PATH)


		#individual Channel Frame
		self.channelsFrame=tk.Frame(self.masterWindow)
		self.channelsFrame.grid(row=1, column=0, columnspan=7)
		#channelsFrame Items Initialization
		self.chNameEntry	=[0 for i in range(N_CHANNEL)]
		self.chNameEntryVar	=[0 for i in range(N_CHANNEL)]
		self.slider 		=[0 for i in range(N_CHANNEL)]
		self.chValkPaLabel	=[0 for i in range(N_CHANNEL)]
		self.chValEntry		=[0 for i in range(N_CHANNEL)]
		self.chValEntryVar	=[0 for i in range(N_CHANNEL)]
		self.upBtn			=[0 for i in range(N_CHANNEL)]
		self.downBtn		=[0 for i in range(N_CHANNEL)]
		self.setMaxBtn		=[0 for i in range(N_CHANNEL)]
		self.setMinBtn		=[0 for i in range(N_CHANNEL)]
		self.sliderMaxEntry =[0 for i in range(N_CHANNEL)]
		self.maxEntryVar 	=[0 for i in range(N_CHANNEL)]
		self.statusLabel	=[0 for i in range(N_CHANNEL)]

		#Channel Frame Label
		self.nameLabel=tk.Label(self.channelsFrame, text="Name")
		self.nameLabel.grid(column=0, row=0)
		self.sliderLabel=tk.Label(self.channelsFrame, text="Slider")
		self.sliderLabel.grid(column=0, row=1)
		self.unitLabel=tk.Label(self.channelsFrame, text="kPa")
		self.unitLabel.grid(column=0, row=2)
		self.entryLabel=tk.Label(self.channelsFrame, text="Entry")
		self.entryLabel.grid(column=0, row=3)
		self.rangeLabel=tk.Label(self.channelsFrame, text="Max Val")
		self.rangeLabel.grid(column=0, row=6)
		self.stLLabel=tk.Label(self.channelsFrame, text="Status")
		self.stLLabel.grid(column=0, row=7)


		#initialize channel array

		for i in range(N_CHANNEL):

			#channel Name
			self.chNameEntryVar[i]=tk.StringVar()
			self.chNameEntry[i]=tk.Entry(self.channelsFrame, bg='white', width=9, bd=3,
											fg='blue', textvariable=self.chNameEntryVar[i])
			self.chNameEntry[i].grid(column=i*2+1, row=0, columnspan=2)
			self.chNameEntryVar[i].set("Channel %d"%(i+1))

			#slider
			self.slider[i]=tk.Scale(self.channelsFrame, from_=VAL_MAX, to=VAL_MIN,
									length=SLIDER_LENGTH, command=partial(self.read_Val, i, 0))
			self.slider[i].set(0)
			self.slider[i].grid(column=i*2+1, row=1, columnspan=2)

			#label pressure in kPa 
			self.chValkPaLabel[i]=tk.Label(self.channelsFrame,text="%.2f"%0)
			self.chValkPaLabel[i].grid(column=i*2+1, row=2, columnspan=2)

			#Channel Value entry Field
			self.chValEntryVar[i]=tk.StringVar()
			self.chValEntry[i]=tk.Entry(self.channelsFrame, width=5, textvariable=self.chValEntryVar[i])
			self.chValEntryVar[i].set(0)
			self.chValEntry[i].grid(column=i*2+1, row=3, columnspan=2)
			#binding function key
			self.chValEntry[i].bind("<Return>", partial(self.read_Val, i, 1))

			#min max btn
			self.setMinBtn[i]=tk.Button(self.channelsFrame, text="Min", command=partial(self.set_Mn, i, 0),
										activebackground='blue')
			self.setMinBtn[i].grid(column=i*2+1, row=4)
			self.setMaxBtn[i]=tk.Button(self.channelsFrame, text="Max", command=partial(self.set_Mn, i, 1),
										activebackground='blue')
			self.setMaxBtn[i].grid(column=(i+1)*2, row=4)

			#up/down Btn
			self.downBtn[i]=tk.Button(self.channelsFrame, text="Down", command=partial(self.set_Offset, i, -1),
										activebackground='blue')
			self.downBtn[i].grid(column=i*2+1, row=5)
			self.upBtn[i]=tk.Button(self.channelsFrame, text="Up", command=partial(self.set_Offset, i, 1),
										activebackground='blue')
			self.upBtn[i].grid(column=(i+1)*2, row=5)

			#max field
			self.maxEntryVar[i]=tk.StringVar()
			self.sliderMaxEntry[i]=tk.Entry(self.channelsFrame, width=5, textvariable=self.maxEntryVar[i])
			self.sliderMaxEntry[i].grid(column=i*2+1, row=6, columnspan=2)
			self.maxEntryVar[i].set(self.valMax[i])
			#binding kay
			self.sliderMaxEntry[i].bind("<Return>", partial(self.set_Max, i))

			#status Label
			self.statusLabel[i]=tk.Label(self.channelsFrame, text="             ",bg="green")
			self.statusLabel[i].grid(column=i*2+1, row=7, columnspan=2)			


		#first time Function 
		self.refresh_Serial() #refresh Serial List

		self.toggle_State(False)


		print("Program initialization Complete!\n")
		self.masterWindow.mainloop()


	def timer_Call(self):
		#this is a routine function call
		#update Status before set
		self.request_Channel_Status()
		#set channel
		for i in range(N_CHANNEL):
			if self.chVal[i] != self.slider[i].get():
				time.sleep(MIN_INTERVAL/2000.0)
				self.set_Channel(i)

				#check if some error occured
				if not self.currentState:
					self.reset_Serial()
					return

		if self.currentState:
			self.masterWindow.after(MIN_INTERVAL, self.timer_Call)

	def set_Channel(self, x):
		if self.SerialApp.getStatus():
			val=self.slider[x].get();
			if self.chVal[x]!=val:
				self.statusLabel[x].config(bg="red") 
				################### Serial processing ############################
				#parity calculation
				par=x<<10|val
				par ^= par >> 8
				par ^= par >> 4
				par ^= par >> 2
				par ^= par >> 1
				parity=(~par)

				c=[0,0]
				#two byte of data: channel 5bits, value 10bits, parity 1bit (set on even)
				c[0]= struct.pack("B",(((x&0x1F)<<3)|((val>>7)&0x7))&0xff)
				c[1]= struct.pack("B",(val<<1|(parity&0x1))&0xff)

				#initiate communication
				self.SerialApp.resetBuffer()
				self.SerialApp.sentByte(b's')
				#account for frequency limit, repeat until sent
				self.SerialApp.sentBytes(c, 2)

				b=0
				b=self.SerialApp.readByte()

				if b==b'k':
					if VERBOSE>1:
						print("Channel %d is set to %d"%(x+1, val))
					self.chVal[x]=val
					self.statusLabel[x].config(bg="tan1")  #Update channel status
				else:	#return string mismatch
					if VERBOSE>0:
						print("Return string mismatch")
		else:
			self.reset_Serial()
			print("Serial Not Connected!")

	def request_Channel_Status(self):
		if self.SerialApp.getStatus():

			self.SerialApp.resetBuffer() #reset Read Buffer
			self.SerialApp.sentByte(b'p') #set command type

			c0 = self.SerialApp.readByte() #read status
			c1 = self.SerialApp.readByte()
			#check Serial fail
			if c0==None or c1==None:
				print("Serial Failed!")
				self.reset_Serial()
				return
			#print(c0)
			#print(c1)
			try:
				c=(ord(c0)<<8)|ord(c1)
			except TypeError:
				if VERBOSE>0:
					print("Return Val Invalid")
				return
			#print(bin(c))
			if c==0:
				if VERBOSE>0:
					pass
					#print("allSet")
			c=c>>16-N_CHANNEL
			for i in reversed(range(N_CHANNEL)):
				if (c&0x1)==0:
					self.statusLabel[i].config(bg="green")
				else:
					self.statusLabel[i].config(bg="tan1")
				c=c>>1


	def read_Val(self, ind, src, dc):
		#src=0: source from slider
		#src=1: source from Entry Field
		if src==0:
			if VERBOSE>1:
				print("read_Val Called by ch %d Slider"%(ind+1))
			self.chValEntryVar[ind].set(self.slider[ind].get())

		if src == 1:	#source from entry field
			if VERBOSE>1:
				print("read_Val Called by ch %d Entry"%(ind+1))

			try: 		#try reading Entry field data
				setVal = int(self.chValEntryVar[ind].get())
			except ValueError:
				print("Value enter is not integer")
				setVal=self.slider[ind].get()			 #error set to Slide bar value

			if setVal>self.valMax[ind]:
				print("Value enter is not in range")
				setVal=self.valMax[ind]
			elif setVal<VAL_MIN:
				print("Value enter is not in range")
				setVal=VAL_MIN

			self.chValEntryVar[ind].set(setVal)
			self.slider[ind].set(setVal)

		#Unit/Value conversion
		if SENSOR_MIX:
			self.chValkPaLabel[ind].config(text="%.2f"%(self.slider[ind].get()*SENSOR_RANGE[x]*0.007013712565))
		else:
			self.chValkPaLabel[ind].config(text="%.2f"%(self.slider[ind].get()*SENSOR_RANGE*0.007013712565))

	def set_Mn(self, ind, target):
		if target==1:
			if VERBOSE>1:
				print("set ch %d to Max"%(ind+1))
			self.slider[ind].set(self.valMax[ind])
		else:
			if VERBOSE>1:
				print("set ch %d to Min"%(ind+1))
			self.slider[ind].set(VAL_MIN)

	def set_Offset(self, ind, direc):
		if VERBOSE>1:
			print("Offset Applied for %d"%direc)

		newVal=BTN_OFFSET*direc+self.slider[ind].get()
		if newVal<=self.valMax[ind] and newVal>=VAL_MIN:
			self.slider[ind].set(newVal)

	def set_Max(self, ind, dc):
		if VERBOSE>1:
			print("change ch %d Max settting"%(ind+1))
		try:
			setVal=int(self.maxEntryVar[ind].get())
		except ValueError:
			print("Value entered is invalid")
			self.valMax[ind]=VAL_MAX
			self.slider[ind].config(from_=VAL_MAX)
			self.maxEntryVar[ind].set(VAL_MAX)
			return
		if VAL_MAX<setVal:
			print("Error, out of bound")
			self.valMax[ind]=VAL_MAX
			self.slider[ind].config(from_=VAL_MAX)
			self.maxEntryVar[ind].set(VAL_MAX)
		elif self.slider[ind].get()<=setVal:
			self.valMax[ind]=setVal
			self.slider[ind].config(from_=setVal)
		else:
			print("Error, smaller than current value")
			self.valMax[ind]=self.slider[ind].get()
			self.slider[ind].config(from_=self.slider[ind].get())
			self.maxEntryVar[ind].set(self.slider[ind].get())	

	def zero_All(self):
		if VERBOSE>1:
			print("Zero all Channels")

		for i in range(N_CHANNEL):
			self.slider[i].set(VAL_MIN)


	def refresh_Serial(self):
		if VERBOSE>1:
			print("Refreshing Serial List")
		#ports = list(serialList.comports())
		self.SerialApp.updatePortList()
		if VERBOSE>1:
			self.SerialApp.listAllPort()
		pList=["" for x in range(self.SerialApp.n_portsList)]
		for i in range(self.SerialApp.n_portsList):
			pList[i]=self.SerialApp.portsList[i].device
		self.SerialList.destroy()
		self.SerialList=tk.OptionMenu(self.serialFrame, self.serialPort, *pList)
		self.SerialList.grid(row=3, column=0, columnspan=4)

	def initialize_Serial(self):
		if self.SerialApp.getStatus()==False:
			print("Initialize Serial Conenction to %s"%self.serialPort.get())
			time.sleep(0.1)
			if self.SerialApp.connectDevice(self.serialPort.get()):
				print("Serial Connection Successful")
				self.serialDisconnectBtn.config(state='normal')
				self.serialConnectBtn.config(state='disabled')
				self.serialStatusLabel.config(bg='green')
				self.toggle_State(True)
				self.zero_All()
			else:
				self.serialStatusLabel.config(bg='red')
				self.toggle_State(False)

	def reset_Serial(self):
		if self.SerialApp.getStatus()==True:
			self.serialDisconnectBtn.config(state='disabled')
			self.serialConnectBtn.config(state='normal')
			self.serialStatusLabel.config(bg='red')
			self.SerialApp.reset()
			self.toggle_State(False)


	def save_Parameter(self):
		#self.valMax
		#self.chNameEntryVar
		#self.savePathVar

		if os.path.isfile(self.savePathVar.get()): #check if file already exist
			result = messagebox.askquestion("Saving Channels Setting", 
											"Data file with the same name exist.\nDo you want to overwrite?", icon='warning')
			if result == 'yes':
				print("Overwriting old saved parameter")
				os.remove(self.savePathVar.get())
			else:
				print("Parameter is not saved")
				return

		print("Storing Parameter....", end="")
		storedVec=["" for i in range(N_CHANNEL*2+1)]
		storedVec[0]=N_CHANNEL

		for i in range(N_CHANNEL):
			storedVec[i*2+1]=self.valMax[i]
			storedVec[i*2+2]=self.chNameEntryVar[i].get()
		
		with open(self.savePathVar.get(), 'wb') as f:
			pickle.dump(storedVec, f)

		print("done")	

	def load_Parameter(self):
		storedVec=["" for i in range(N_CHANNEL*2+1)]
		if self.currentState==False:
			try:
				with open(self.savePathVar.get(), 'rb') as f:
					storedVec = pickle.load(f)
			except FileNotFoundError:
				print("Error: File does not exist")
				return
		else:
			print("Board can't be active when load")
			return

		if int(storedVec[0])!=N_CHANNEL:
			print("Error: Number of channel mismatch")
			print("Stored data: %d channels"%storedVec[0])
			return

		self.zero_All()
		for i in range(N_CHANNEL):
			if int(storedVec[i*2+1])>VAL_MAX:
				chMax=VAL_MAX
				print("VAL_MAX mismatch")
			else:
				chMax=int(storedVec[i*2+1])
			self.maxEntryVar[i].set(chMax)
			self.set_Max(i, 0)
			self.chNameEntryVar[i].set(storedVec[i*2+2])


	def toggle_State(self, inVal):
		if (inVal==False):
			self.currentState=False
			print("Disabling all input")
			#self.disableAllBtn.config(state='disabled')
			#self.enableAllBtn.config(state='normal')
			self.loadBtn.config(state='normal')
			self.zeroAllBtn.config(state='disabled')
			for i in range(N_CHANNEL):
				self.slider[i].config(state='disabled')
				self.setMinBtn[i].config(state='disabled')
				self.setMaxBtn[i].config(state='disabled')
				self.chValEntry[i].config(state='disabled')
				self.downBtn[i].config(state='disabled')
				self.upBtn[i].config(state='disabled')
		else:
			self.currentState=True
			print("Re-enabling all input")
			#self.disableAllBtn.config(state='normal')
			#self.enableAllBtn.config(state='disabled')
			self.loadBtn.config(state='disabled')
			self.zeroAllBtn.config(state='normal')
			for i in range(N_CHANNEL):
				self.slider[i].config(state='normal')
				self.setMinBtn[i].config(state='normal')
				self.setMaxBtn[i].config(state='normal')
				self.chValEntry[i].config(state='normal')
				self.downBtn[i].config(state='normal')
				self.upBtn[i].config(state='normal')

			#initialize routine function
			self.masterWindow.after(MIN_INTERVAL, self.timer_Call)

	def close_Window(self):
		print("\nExiting Program\n")
		self.masterWindow.destroy()
		quit()


if __name__=='__main__':
	main()












