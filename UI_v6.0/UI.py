from sys import version_info
import optparse
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
from os import listdir
from os.path import isfile, join

VERBOSE=0 #debugger
VERSION='5.4'#version number

################################critical Parameter########################################
#dont modify unless you are sure.

SLIDER_LENGTH=350	#hight of the slider 
MIN_INTERVAL=50 	#Serial update limmit in ms
VACUM_OFFSET=80		#amount of negative offset to vacum
#value for binary control setpoint
BINARY_SETPOINT_ON=1023
BINARY_SETPOINT_OFF=1022	
UPSTREAM_REG_DISABLE_VAL=2047


################################non-critical Parameter########################################
#Number of channel can be added here
N_CHANNEL_D=13

#if using sensor with different maximum set to true
SENSOR_MIXING=False 
#use the first line of Mixing sensor, Second line if all sensors are the same
#SENSOR_RANGE=[100, 30, 30, 30, 30, 30, 30, 30, 30, 30]
SENSOR_RANGE=30 #sensor maximum range in PSI

#False if wish to remove Max btn
MAX_BTN_PRESENT=True 

#default setting file save path
DEFAULT_SAVE_PATH="./SaveData/"

#if Vacum is enable on the given channel, set the corrsponding array value to True
VACUM_ENABLE=[False, False, False, False, False, False, False, False, False, False, False, False, False] 

#abs min max of the input value, 830 should be abs max
VAL_MAX_D=820			

#mininum value for different channel type
VACUM_MIN=-VACUM_OFFSET		#must be higher then -VACUM_OFFSET	
REG_MIN=0					

#offset for the Down/Up Btn
BTN_OFFSET=2 

#default serial port, Change if different arduino is used
DEFULT_SER_PID=66




def main():
	#object initialization
	serialApp=SerialInterface()

	#take care of the pass in arguments
	parser = optparse.OptionParser(usage='%prog [options] <arg1> ...',
                               version=VERSION)
	parser.add_option('-v', action="count", dest='verbosity', default=0, help="Increase verbosity")
	parser.add_option('-q', action='store_const', const=0, dest='verbosity', help="Suppress output")
	parser.add_option('--n-channel', '-n', action='store', default=N_CHANNEL_D, 
						type="int", dest='nChannel', help="Set number of channels")
	parser.add_option('--max', '-m', action='store', default=VAL_MAX_D, 
						type="int", dest='valMax', help="Set maximum pressure")
	parser.add_option('-l', '--list-serial', action='store_true', dest='listSerial', help="Print out list of serial ports")
	


	options, args = parser.parse_args()


	#one off command excutation
	if(options.listSerial):
		serialApp.listAllPort()
		return

	#transfereing arguments value
	VERBOSE=options.verbosity
	global N_CHANNEL
	if(options.nChannel>0 and options.nChannel<=13):
		N_CHANNEL=options.nChannel
	else:
		N_CHANNEL=N_CHANNEL_D

	global VAL_MAX
	if(options.valMax>10 and options.valMax<=VAL_MAX_D):
		VAL_MAX=options.valMax
	else:
		VAL_MAX=VAL_MAX_D

	#display argument
	if(VERBOSE>0):
		print("verbosity=%d"%VERBOSE)
		print("nChannel=%d"%N_CHANNEL)
		print("maximum value=%d"%VAL_MAX)

	#run main program
	UIApp=App(tk.Tk(),serialApp)
	

class App:

	def __init__(self, masterWindow, serialApp):	
		###############################Initializer##############################
		#Intialize Global variabel 
		self.usRegPressureVal=0; 
		self.usRegPressureCurrentVal=0; 
		self.chVal=		[VACUM_OFFSET 	for i in range(N_CHANNEL)]
		self.valMax=	[VAL_MAX 		for i in range(N_CHANNEL)]
		self.binStatus=	[False 			for i in range(N_CHANNEL)]
		self.binState= 	[False			for i in range(N_CHANNEL)]

		#misc variable
		self.currentState=False   #current state of the program

		self.SerialApp=serialApp

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
									activebackground='blue', command=partial(self.toggle_UI_State, False))
		self.disableAllBtn.grid(row=2, column=0)
		self.enableAllBtn=tk.Button(self.smFrame, text="enableAll", state='disabled',
									activebackground='blue', command=partial(self.toggle_UI_State, True))
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
		self.binaryLabel1=tk.Label(self.infoFrame,text="        ", bg="yellow", borderwidth=3, relief="groove")
		self.binaryLabel1.grid(row=4, column=1)
		self.matchLabel2=tk.Label(self.infoFrame,text="Set")
		self.matchLabel2.grid(row=1, column=0)
		self.mismatchLabel2=tk.Label(self.infoFrame,text="Mismatch")
		self.mismatchLabel2.grid(row=2, column=0)
		self.errorLabel2=tk.Label(self.infoFrame,text="Error")
		self.errorLabel2.grid(row=3, column=0)
		self.binaryLabel2=tk.Label(self.infoFrame,text="Binary Control")
		self.binaryLabel2.grid(row=4, column=0)


		#Serial Frame
		self.serialFrame=tk.Frame(self.masterWindow, bd=1)
		self.serialFrame.grid(row=3, column=2, columnspan=2)
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
		self.saveFrame.grid(row=3, column=4, columnspan=2)
		#item initialization
		self.saveBtn=tk.Button(self.saveFrame, text='Save', command=self.save_Parameter, width=7)
		self.saveBtn.grid(row=0, column=0)
		self.loadBtn=tk.Button(self.saveFrame, text='Load', command=self.load_Parameter, width=7)
		self.loadBtn.grid(row=0, column=1)
		self.savePathVar=tk.StringVar(self.saveFrame)
		self.savePathEntry=tk.Entry(self.saveFrame, textvariable=self.savePathVar)
		self.savePathEntry.grid(row=1, column=0, columnspan=2)
		self.savePathVar.set(DEFAULT_SAVE_PATH+"Temp.fcbset")



		#Upstream regulator control frame
		self.usRegulatorFrame=tk.Frame(self.masterWindow)
		self.usRegulatorFrame.grid(row=3, column=6, columnspan=2)
		#items initialization
		usRegulatorFrameLabel=tk.Label(self.usRegulatorFrame, text='Upstream Pressure Control Panel')
		usRegulatorFrameLabel.grid(row=0, column=0, columnspan=2)
		usRegToggleBtnLabel=tk.Label(self.usRegulatorFrame, text='Status: ')
		usRegToggleBtnLabel.grid(row=1, column=0)
		self.usRegToggleBtn=tk.Button(self.usRegulatorFrame, text='ON', width=7, fg='green', command=self.us_Clt_Toggle)
		self.usRegToggleBtn.grid(row=1, column=1)
		usRegPressureEntryLabel=tk.Label(self.usRegulatorFrame, text='Value: ')
		usRegPressureEntryLabel.grid(row=2, column=0)
		self.usRegPressureTxtVar=tk.StringVar(self.usRegulatorFrame)
		self.usRegPressureEntry=tk.Entry(self.usRegulatorFrame, textvariable=self.usRegPressureTxtVar)
		self.usRegPressureEntry.grid(row=2, column=1)
		self.usRegPressureTxtVar.set(0)
		self.usRegPressureEntry.bind("<Return>", self.us_Reg_Pressure_Entry_Command)
		self.usRegPressureLabelkpa=tk.Label(self.usRegulatorFrame, text='0')
		self.usRegPressureLabelkpa.grid(row=3, column=0)
		usRegPressureLabelkpaLabel=tk.Label(self.usRegulatorFrame, text='kPa')
		usRegPressureLabelkpaLabel.grid(row=3, column=1)
		self.usRegPressureLabelpsi=tk.Label(self.usRegulatorFrame, text='0')
		self.usRegPressureLabelpsi.grid(row=4, column=0)
		usRegPressureLabelpsiLabel=tk.Label(self.usRegulatorFrame, text='psi')
		usRegPressureLabelpsiLabel.grid(row=4, column=1)

		#individual Channel Frame
		self.channelsFrame=tk.Frame(self.masterWindow)
		self.channelsFrame.grid(row=1, column=0, columnspan=8)
		#channelsFrame Items Initialization
		self.chNameEntry	=[0 for i in range(N_CHANNEL)]
		self.chNameEntryVar	=[0 for i in range(N_CHANNEL)]
		self.slider 		=[0 for i in range(N_CHANNEL)]
		self.chValkPaLabel	=[0 for i in range(N_CHANNEL)]
		self.chValEntry		=[0 for i in range(N_CHANNEL)]
		self.chValEntryVar	=[0 for i in range(N_CHANNEL)]
		self.upBtn			=[0 for i in range(N_CHANNEL)]
		self.downBtn		=[0 for i in range(N_CHANNEL)]
		if (MAX_BTN_PRESENT):
			self.setMaxBtn		=[0 for i in range(N_CHANNEL)]
		self.binOnBtn		=[0 for i in range(N_CHANNEL)]
		self.binOffBtn		=[0 for i in range(N_CHANNEL)]
		self.setMinBtn		=[0 for i in range(N_CHANNEL)]
		self.sliderMaxEntry =[0 for i in range(N_CHANNEL)]
		self.maxEntryVar 	=[0 for i in range(N_CHANNEL)]
		self.statusLabel	=[0 for i in range(N_CHANNEL)]
		self.binaryOnBtn 	=[0 for i in range(N_CHANNEL)]

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
		self.binLabel=tk.Label(self.channelsFrame, text="Binary")
		self.binLabel.grid(column=0, row=8)


		#initialize channel array

		for i in range(N_CHANNEL):

			#channel Name
			self.chNameEntryVar[i]=tk.StringVar()
			self.chNameEntry[i]=tk.Entry(self.channelsFrame, bg='white', width=9, bd=3,
											fg='blue', textvariable=self.chNameEntryVar[i])
			self.chNameEntry[i].grid(column=i*2+1, row=0, columnspan=2)
			self.chNameEntryVar[i].set("Channel %d"%(i+1))

			#slider
			self.slider[i]=tk.Scale(self.channelsFrame, from_=VAL_MAX, to=(VACUM_MIN if VACUM_ENABLE[i] else REG_MIN),
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

			#min max
			self.setMinBtn[i]=tk.Button(self.channelsFrame, text="Min", command=partial(self.set_Mn, i, 0),
										activebackground='blue')
			self.setMinBtn[i].grid(column=i*2+1, row=4)
			if (MAX_BTN_PRESENT):
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

			#Binary Button
			self.binaryOnBtn[i]=tk.Button(self.channelsFrame, text="On", command=partial(self.toggle_Binary_State, i))		
			self.binaryOnBtn[i].grid(column=i*2+1, row=8, columnspan=2)	

			#binary on off btn
			self.binOnBtn[i]=tk.Button(self.channelsFrame, text="On", 
										command=partial(self.binary_Toggle, i, 1), state="disabled")
			self.binOnBtn[i].grid(column=(i+1)*2, row=9)
			self.binOffBtn[i]=tk.Button(self.channelsFrame, text="Off", 
										command=partial(self.binary_Toggle, i, 0), state="disabled")
			self.binOffBtn[i].grid(column=i*2+1, row=9)


		#first time Function 
		self.refresh_Serial() #refresh Serial List

		self.toggle_UI_State(False)


		print("Program initialization Complete!\n")
		print("Program begin")
		self.masterWindow.mainloop()

	def timer_Call(self):
		#this is a routine function call
		#update Status before set
		self.request_Channel_Status()

		if(self.usRegPressureVal!=self.usRegPressureCurrentVal):
			self.set_Upstream()

		#set channel
		for i in range(N_CHANNEL):
			if self.chVal[i] != self.slider[i].get() and not self.binState[i]:
				time.sleep(MIN_INTERVAL/2000.0)
				self.set_Channel(i)

				#check if some error occured
				if not self.currentState:
					self.reset_Serial()
					return

		if self.currentState:
			self.masterWindow.after(MIN_INTERVAL, self.timer_Call)

	def set_Channel(self, ind, force=False):
		if self.SerialApp.getStatus():
			valIn=self.slider[ind].get()
			if self.chVal[ind]!=valIn or force==True:
				self.statusLabel[ind].config(bg="red") 
				val=valIn+VACUM_OFFSET
				if(self.binState[ind]):
					if(self.binStatus[ind]):
						val=BINARY_SETPOINT_ON
					else:
						val=BINARY_SETPOINT_OFF

				################### Serial processing ############################
				#parity calculation
				par=ind<<10|val
				par ^= par >> 8
				par ^= par >> 4
				par ^= par >> 2
				par ^= par >> 1
				parity=(~par)

				c=[0,0]
				#two byte of data: channel 5bits, value 10bits, parity 1bit (set on even)
				c[0]= struct.pack("B",(((ind&0x1F)<<3)|((val>>7)&0x7))&0xff)
				c[1]= struct.pack("B",(val<<1|(parity&0x1))&0xff)

				#initiate communication
				self.SerialApp.resetBuffer()
				self.SerialApp.sentByte(b's')
				#account for frequency limit, repeat until sent
				self.SerialApp.sentBytes(c, 2)

				b=0
				b=self.SerialApp.readByte()

				if b==b'k':
					if VERBOSE>1 and self.binState[ind]:
						if(self.binStatus[ind]):
							print("Channel %d is set to ON"%(ind+1))
						else:
							print("Channel %d is set to OFF"%(ind+1))
					elif VERBOSE>1 :
							print("Channel %d is set to %d"%(ind+1, self.chVal[ind]))
					if(not self.binState[ind]):
						self.chVal[ind]=valIn
						self.statusLabel[ind].config(bg="tan1")  #Update channel status
				else:	#return string mismatch
					if VERBOSE>0:
						print("Return string mismatch")

		else:
			self.reset_Serial()
			print("Serial Not Connected!")

	def set_Upstream(self, force=False):
		if self.SerialApp.getStatus():
			valIn=self.usRegPressureVal
			print("Setting Upstream to : %d"%valIn)

			c=[0,0]
			#two byte of data: channel 5bits, value 10bits, parity 1bit (set on even)
			c[0]= struct.pack("B",(valIn>>8))
			c[1]= struct.pack("B",(valIn&0xff))

			#initiate communication
			self.SerialApp.resetBuffer()
			self.SerialApp.sentByte(b'u')
			#account for frequency limit, repeat until sent
			self.SerialApp.sentBytes(c, 2)

			b=0
			b=self.SerialApp.readByte()

			if b==b'k':
				if VERBOSE>1 :
					print("Setting Upstream to : %d"%valIn)
					self.usRegPressureCurrentVal=self.usRegPressureVal;
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
			try:
				c=(ord(c0)<<8)|ord(c1)
			except TypeError:
				if VERBOSE>0:
					print("Return Val Invalid")
				return
			if c==0:
				if VERBOSE>3:
					print("allSet")
			c=c>>16-N_CHANNEL
			for i in reversed(range(N_CHANNEL)):
				if (self.binState[i]):
					self.statusLabel[i].config(bg="yellow")
				elif (c&0x1)==0:
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
			elif setVal<(VACUM_MIN if VACUM_ENABLE[ind] else REG_MIN):
				print("Value enter is not in range")
				setVal=(VACUM_MIN if VACUM_ENABLE[ind] else REG_MIN)

			self.chValEntryVar[ind].set(setVal)
			self.slider[ind].set(setVal)

		#Unit/Value conversion
		if SENSOR_MIXING:
			self.chValkPaLabel[ind].config(text="%.2f"%(self.slider[ind].get()*SENSOR_RANGE[ind]*0.007013712565))
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
			self.slider[ind].set(VACUM_MIN if VACUM_ENABLE[ind] else REG_MIN)

	def set_Offset(self, ind, direc):
		if VERBOSE>1:
			print("Offset Applied for %d"%direc)

		newVal=BTN_OFFSET*direc+self.slider[ind].get()
		if newVal<=self.valMax[ind] and newVal>=(VACUM_MIN if VACUM_ENABLE[ind] else REG_MIN):
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

	def toggle_UI_State(self, state):
		if (state==False):
			self.currentState=False
			print("Disabling all input")
			#self.disableAllBtn.config(state='disabled')
			#self.enableAllBtn.config(state='normal')
			self.loadBtn.config(state='normal')
			self.zeroAllBtn.config(state='disabled')
			self.usRegToggleBtn.config(state='disabled')
			self.usRegPressureEntry.config(state='disabled')
			for i in range(N_CHANNEL):
				self.slider[i].config(state='disabled')
				self.setMinBtn[i].config(state='disabled')
				if (MAX_BTN_PRESENT):
					self.setMaxBtn[i].config(state='disabled')
				self.chValEntry[i].config(state='disabled')
				self.downBtn[i].config(state='disabled')
				self.upBtn[i].config(state='disabled')
				self.binaryOnBtn[i].config(state='disabled')
				self.binOnBtn[i].config(state='disabled')
				self.binOffBtn[i].config(state='disabled')
		else:
			self.currentState=True
			print("Re-enabling all input")
			#self.disableAllBtn.config(state='normal')
			#self.enableAllBtn.config(state='disabled')
			self.loadBtn.config(state='disabled')
			self.zeroAllBtn.config(state='normal')
			self.usRegToggleBtn.config(state='normal')
			self.usRegPressureEntry.config(state='normal')
			self.usRegPressureTxtVar.set(0)
			for i in range(N_CHANNEL):
				self.slider[i].set(0)
				self.slider[i].config(state='normal')
				self.setMinBtn[i].config(state='normal')
				if (MAX_BTN_PRESENT):
					self.setMaxBtn[i].config(state='normal')
				self.chValEntry[i].config(state='normal')
				self.downBtn[i].config(state='normal')
				self.upBtn[i].config(state='normal')
				self.binaryOnBtn[i].config(state='normal')
				self.binState[i]=False
				self.binaryOnBtn[i].config(text="On")
				self.binOnBtn[i].config(state='disabled')
				self.binOffBtn[i].config(state='disabled')


			#initialize routine function
			self.masterWindow.after(MIN_INTERVAL, self.timer_Call)

	#toggle binary control
	def toggle_Binary_State(self, ind):
		if (not self.binState[ind]):
			print("set channel %d to Binary Control"%(ind+1))
			self.binState[ind]=True
			self.binStatus[ind]=False
			self.binaryOnBtn[ind].config(text="Off")
			self.binOnBtn[ind].config(state='normal')
			self.binOffBtn[ind].config(state='normal')
			self.set_Channel(ind, True)

			#disable give channel control
			self.slider[ind].config(state='disabled')
			self.setMinBtn[ind].config(state='disabled')
			if (MAX_BTN_PRESENT):
				self.setMaxBtn[ind].config(state='disabled')
			self.chValEntry[ind].config(state='disabled')
			self.downBtn[ind].config(state='disabled')
			self.upBtn[ind].config(state='disabled')
		else:
			print("set channel %d to Propotional Control"%(ind+1))
			self.binState[ind]=False
			self.binaryOnBtn[ind].config(text="On")
			self.binOnBtn[ind].config(state='disabled')
			self.binOffBtn[ind].config(state='disabled')
			#reenable channel control
			self.slider[ind].config(state='normal')
			self.setMinBtn[ind].config(state='normal')
			if (MAX_BTN_PRESENT):
				self.setMaxBtn[ind].config(state='normal')
			self.chValEntry[ind].config(state='normal')
			self.downBtn[ind].config(state='normal')
			self.upBtn[ind].config(state='normal')
			#zero channel
			self.set_Mn(ind, 0)
			self.set_Channel(ind, True)

	#Toggle Binary State
	def binary_Toggle(self, ind, state):
		if (state):
			self.binStatus[ind]=True
		else:
			self.binStatus[ind]=False
		self.set_Channel(ind, True)

	def us_Clt_Toggle(self):
		if (self.usRegToggleBtn['text']=='ON'):
			self.usRegToggleBtn.config(text='OFF', fg='red')
			self.usRegPressureEntry.config(state='disabled')
			self.usRegPressureLabelpsi.config(text='max')
			self.usRegPressureLabelkpa.config(text='max') 
			self.usRegPressureVal=UPSTREAM_REG_DISABLE_VAL
			self.set_Upstream()
			print("Upstream control set to OFF")

		elif (self.usRegToggleBtn['text']=='OFF'):
			self.usRegToggleBtn.config(text='ON', fg='green')
			self.usRegPressureEntry.config(state='normal')
			self.us_Reg_Pressure_Entry_Command(3)
			self.set_Upstream()
			print("Upstream control set to ON")

	def us_Reg_Pressure_Entry_Command(self, dc):
		print("Changing Up Stream Regulator Setting")
		try:
			setVal=int(self.usRegPressureTxtVar.get())
		except ValueError:
			print("Value entered is invalid")
			self.usRegPressureTxtVar.set(int(float(self.usRegPressureLabelpsi['text'])/(100/819.2) ))
			return

		if(setVal>VAL_MAX):
			print("Value is over maximum")
			self.usRegPressureTxtVar.set(int(float(self.usRegPressureLabelpsi['text'])/(100/819.2) ))
			return
		elif(setVal<0):
			print("Value is negative")
			self.usRegPressureTxtVar.set(int(float(self.usRegPressureLabelpsi['text'])/(100/819.2) ))
			return
		else:
			self.usRegPressureLabelpsi.config(text='%.2f'%(setVal*(100/819.2)) )
			self.usRegPressureLabelkpa.config(text='%.2f'%(setVal*(100/819.2)*6.89476) ) 
			self.usRegPressureVal=setVal


			
	def zero_All(self):
		if VERBOSE>1:
			print("Zero all Channels")

		for i in range(N_CHANNEL):
			self.slider[i].set(0)


	def refresh_Serial(self):
		if VERBOSE>1:
			print("Refreshing Serial List")
		#ports = list(serialList.comports())
		self.SerialApp.updatePortList()
		if VERBOSE>1:
			self.SerialApp.listAllPort()
		pList=["" for x in range(self.SerialApp.n_portsList)]
		if (self.SerialApp.n_portsList!=0):
			selecInd=-1
			for i in range(self.SerialApp.n_portsList):
				pList[i]=self.SerialApp.portsList[i].device
				if(self.SerialApp.portsList[i].pid==DEFULT_SER_PID): selecInd=i
			self.SerialList.destroy()
			self.SerialList=tk.OptionMenu(self.serialFrame, self.serialPort, *pList)
			self.SerialList.grid(row=3, column=0, columnspan=4)
			if(selecInd>=0): 
				if(VERBOSE>1): print("Default serial port found")
				self.serialPort.set(pList[selecInd])
			elif(VERBOSE>1): print("Default serial option not found")


	def initialize_Serial(self):
		if self.SerialApp.getStatus()==False:
			print("Initialize Serial Conenction to %s"%self.serialPort.get())
			time.sleep(0.1)
			if self.SerialApp.connectDevice(self.serialPort.get()):
				print("Serial Connection Successful")
				self.serialDisconnectBtn.config(state='normal')
				self.serialConnectBtn.config(state='disabled')
				self.serialStatusLabel.config(bg='green')
				self.toggle_UI_State(True)
				self.zero_All()
			else:
				self.serialStatusLabel.config(bg='red')
				self.toggle_UI_State(False)

	def reset_Serial(self):
		if self.SerialApp.getStatus()==True:
			self.serialDisconnectBtn.config(state='disabled')
			self.serialConnectBtn.config(state='normal')
			self.serialStatusLabel.config(bg='red')
			self.SerialApp.reset()
			self.toggle_UI_State(False)


	def save_Parameter(self):
		#self.valMax
		#self.chNameEntryVar
		#self.savePathVar

		if os.path.isfile(self.savePathVar.get()): #check if file already exist
			result = messagebox.askquestion("Saving Channels Parameter", 
											"Data file with the same name exist.\nDo you want to overwrite?", icon='warning')
			if result == 'yes':
				print("Overwriting old saved parameter")
				os.remove(self.savePathVar.get())
			else:
				print("Save Cancelled")
				return

		print("Storing Parameter to:", self.savePathVar.get(), " ....", end="", sep="")
		storedVec=["" for i in range(N_CHANNEL*2+1)]
		storedVec[0]=N_CHANNEL

		for i in range(N_CHANNEL):
			storedVec[i*2+1]=self.valMax[i]
			storedVec[i*2+2]=self.chNameEntryVar[i].get()
		
		with open(self.savePathVar.get(), 'wb') as f:
			pickle.dump(storedVec, f)

		print("done")	


	def s_selection_callback(self, inputPath):
		self.savePathVar.set(join(DEFAULT_SAVE_PATH, inputPath))
		self.loadBtn.config(state='normal')
		self.saveBtn.config(state='normal')
		#destroy popup
		self.fListPopup.destroy()

		#begin Loading
		storedVec=["" for i in range(N_CHANNEL*2+1)]
		try:
			with open(self.savePathVar.get(), 'rb') as f:
				storedVec = pickle.load(f)
		except FileNotFoundError:
			print("Error: File does not exist")
			return	

		if int(storedVec[0])!=N_CHANNEL:
			print("Error: Number of channel mismatch")
			print("Stored data: %d channels"%storedVec[0])
			return

		print("Loading... ", end="")
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

		print("Parameter Loaded")

	def _delete_f_windows(self):
		self.loadBtn.config(state='normal')
		self.saveBtn.config(state='normal')
		self.fListPopup.destroy()

	def load_Parameter(self):

		if self.currentState==True:
			print("Board can't be active when load")
			return

		#file check 
		try:
			pFiles = [f for f in listdir(DEFAULT_SAVE_PATH) if isfile(join(DEFAULT_SAVE_PATH, f))]
		except FileNotFoundError:
			print("Save Folder does not exist! creating folder")
			os.mkdir(DEFAULT_SAVE_PATH)
			pFiles = [f for f in listdir(DEFAULT_SAVE_PATH) if isfile(join(DEFAULT_SAVE_PATH, f))]
		if (len(pFiles)==0):
			print("Saved parameter does not exist")
			return

		self.loadBtn.config(state='disabled')
		self.saveBtn.config(state='disabled')

		self.fListPopup=tk.Toplevel()
		self.fListPopup.protocol("WM_DELETE_WINDOW", self._delete_f_windows)
		self.fListPopup.title("File Selection Windows")

		popupLabel=tk.Label(self.fListPopup, text="List of Saved Parameter\n")
		popupLabel.grid(row=0, column=1)
		popupSpace1=tk.Label(self.fListPopup, text="    ")
		popupSpace1.grid(row=0, column=0)
		popupSpace2=tk.Label(self.fListPopup, text="    ")
		popupSpace2.grid(row=0, column=2)

		
		pFiles
		pFilesBtn=[0 for i in range(len(pFiles))]
		for i in range(len(pFiles)):
			pFilesBtn[i]=tk.Button(self.fListPopup, text=pFiles[i], command=partial(self.s_selection_callback, pFiles[i]))
			pFilesBtn[i].grid(row=i+1, column=1)

	def close_Window(self):
		print("\nExiting Program\n")
		self.masterWindow.destroy()
		quit()


if __name__=='__main__':
	main()












