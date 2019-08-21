from sys import version_info
if version_info.major == 2:
	import Tkinter as tk
elif version_info.major == 3:
	import tkinter as tk

import time
from functools import partial
import serial.tools.list_ports as serialList
import serial
from SerialApp import SerialApp
from threading import Thread
import struct


VERBOSE_LEVEL=0 #debugger


N_CHANNEL=4
VAL_MAX=200
VAL_MIN=0
SLIDER_LENGTH=250

MIN_INTERVAL=50 	#Serial update limmit in ms

#create Global Channel Value
chVal=[0 for x in xrange(N_CHANNEL)]

def main():
	UIApp=App(tk.Tk(), tk.Tk())

class App:

	def __init__(self, masterWindow, serialWindow):			################Initializer


		self.lastTimeCalled=time.clock()
		
		#self.masterWindow = tk.Tk() #initialize Tkinter
		self.masterWindow=masterWindow

		self.masterWindow.title("Fluid Contorl Board UI") 
		self.mode=0 #0: discontinous mode, 1:continous mode

		#UI setup
		self.UILabel=tk.Label(self.masterWindow, text="Control Panel")
		self.UILabel.grid(row=0, column=0, columnspan=N_CHANNEL+1)


		#channel frame
		self.channelFrame=tk.Frame(self.masterWindow)
		self.channelFrame.grid(row=1, column=0, columnspan=N_CHANNEL+1)

		#etc
		self.readallBtn=tk.Button(self.masterWindow,text="Read all",command=self.read_scales) # button to read values
		self.readallBtn.grid(row=6,column=N_CHANNEL)
		self.zeroBtn=tk.Button(self.masterWindow,text="Zero",command=self.zero_all) # button to read values
		self.zeroBtn.grid(row=6,column=N_CHANNEL-1)
		
		#mode Selection
		self.modeFrame=tk.Frame(self.masterWindow)
		self.modeFrame.grid(row=3, column=0, columnspan=2)
		self.modeLabel=tk.Label(self.modeFrame, text="Mode: ")
		self.modeLabel.grid(row=0, column=0)
		self.modeBtn=tk.Button(self.modeFrame, text="Discontinous", command=self.set_mode)
		self.modeBtn.grid(row=0, column=1)

		#label Information
		self.colorLabel1=tk.Label(self.masterWindow, text="Channel Label Color Code", font=("Courier", 16))
		self.colorLabel1.grid(row=2, column=N_CHANNEL-1, columnspan=2 )
		self.matchLabel1=tk.Label(self.masterWindow,text="        ", bg="green", borderwidth=3, relief="groove")
		self.matchLabel1.grid(row=3, column=N_CHANNEL-1)
		self.mismatchLabel1=tk.Label(self.masterWindow,text="        ", bg="tan1", borderwidth=3, relief="groove")
		self.mismatchLabel1.grid(row=4, column=N_CHANNEL-1)
		self.maxLabel1=tk.Label(self.masterWindow,text="        ", bg="yellow", borderwidth=3, relief="groove")
		self.maxLabel1.grid(row=5, column=N_CHANNEL-1)
		self.matchLabel2=tk.Label(self.masterWindow,text="Up to Date")
		self.matchLabel2.grid(row=3, column=N_CHANNEL)
		self.mismatchLabel2=tk.Label(self.masterWindow,text="Update Require")
		self.mismatchLabel2.grid(row=4, column=N_CHANNEL)
		self.maxLabel2=tk.Label(self.masterWindow,text="Always On")
		self.maxLabel2.grid(row=5, column=N_CHANNEL)

		#Variable Channel Contorl Array
		self.slider=[0 for x in xrange(N_CHANNEL)]
		self.sliderLabel=[0 for x in xrange(N_CHANNEL)]
		self.sliderSetBtn =[0 for x in xrange(N_CHANNEL)]
		self.sliderEntry=[0 for x in xrange(N_CHANNEL)]
		self.setMaxBtn=[0 for x in xrange(N_CHANNEL)]
		self.setMinBtn=[0 for x in xrange(N_CHANNEL)]
		self.chValEntryField=[0 for x in xrange(N_CHANNEL)]

		#additional Label
		self.slabel=tk.Label(self.channelFrame, text="Slider")
		self.slabel.grid(column=0, row=1)
		self.elabel=tk.Label(self.channelFrame, text="Entry Field")
		self.elabel.grid(column=0, row=2)
		self.btnlabel=tk.Label(self.channelFrame, text="Update")
		self.btnlabel.grid(column=0, row=4)

		for i in range(N_CHANNEL):	#initialization of channel array
			#Channel Label
			self.sliderLabel[i]=tk.Label(self.channelFrame, bg="grey", borderwidth=3, relief="groove", text="Channel %d"%(i+1))
			self.sliderLabel[i].grid(column=i*2+1, row=0, columnspan=2)
			
			#Entry Field
			self.chValEntryField[i]=tk.StringVar()
			self.sliderEntry[i]=tk.Entry(self.channelFrame, width=5, textvariable=self.chValEntryField[i])#, validate="all", validatecommand=partial(read_field, i, 0, 0))
			self.chValEntryField[i].set("0")
			#bind Return carage to Entry
			self.sliderEntry[i].bind ("<Return>",partial(self.read_field, i, 0))
			self.sliderEntry[i].grid(column=i*2+1, row=2, columnspan=2)
			
			#slider
			self.slider[i]=tk.Scale(self.channelFrame, from_=VAL_MAX, to=VAL_MIN, length=SLIDER_LENGTH, command=partial(self.read_field, i, 1)) # creates widget
			self.slider[i].grid(column=i*2+1, row=1, columnspan=2)
			
			#min max btn
			self.setMinBtn[i]=tk.Button(self.channelFrame, text="Min", command=partial(self.set_mn, i, 0))
			self.setMinBtn[i].grid(column=i*2+1, row=3)
			self.setMaxBtn[i]=tk.Button(self.channelFrame, text="Max", command=partial(self.set_mn, i, 1))
			self.setMaxBtn[i].grid(column=(i+1)*2, row=3)

			#Set Button
			self.sliderSetBtn[i]=tk.Button(self.channelFrame, text="Set" , command=partial(self.set_channel, i))
			self.sliderSetBtn[i].grid(column=i*2+1, row=4, columnspan=2)

		####initialize Serial App
		self.serialApp=SerialApp(serialWindow)


		print("Program initialization Complete!\n")
		self.masterWindow.mainloop()

	def timer_call(self):									################Timed update function for Continous mode
		#print("\t\t\t%.10f"%(time.clock()*1000))
		#global chVal
		self.serialApp.test_connection() #Test Serial Connection, if failed disconnect Serial from SerialUI
		i=0
		while i < N_CHANNEL:
			if chVal[i] != self.slider[i].get():
				if (time.clock()-self.lastTimeCalled)*1000>MIN_INTERVAL:
					self.set_channel(i)
					self.lastTimeCalled=time.clock()
				else:
					ct=time.clock();
					while (time.clock()-ct)*1000<MIN_INTERVAL:
						pass
					i -= 1
			i += 1

		if self.serialApp.status()==0:
			self.set_to_discontinous()

		if self.mode==1:				#set recall timer if only in continous mode
			self.masterWindow.after(MIN_INTERVAL, self.timer_call)

	def read_field(self, x, src, dc):  						################src define source 0: entry, 1: slider 

		#print("!%s!\t!%s!\t\t!%s!"%(x, src, val))
		if src == 0:
			if VERBOSE_LEVEL>1:
				print("channel %d recive value from entry"%(x+1))

			try: 		#try reading ENtry field data
				setVal = int(self.chValEntryField[x].get())
			except ValueError:
				print("Value enter is not integer")
				setVal=self.slider[x].get()			 #error set to Slide bar value

			if setVal>VAL_MAX:
				print("Value enter is not in range")
				setVal=VAL_MAX
			elif setVal<VAL_MIN:
				print("Value enter is not in range")
				setVal=VAL_MIN
			self.chValEntryField[x].set(setVal)
			self.slider[x].set(setVal)

		elif src == 1:
			if VERBOSE_LEVEL>1:
				print("channel %d recive value from slider"%(x+1))
			self.chValEntryField[x].set(self.slider[x].get())

		self.update_label(x) #update label Color

	def set_mn(self, x, val):								################set min/Max Button
		if val==0:
			if VERBOSE_LEVEL>0:
				print("channel %d set to min"%(x+1))
			setVal=VAL_MIN
		else:
			if VERBOSE_LEVEL>0:
				print("channel %d set to max"%(x+1))
			setVal=VAL_MAX

		self.chValEntryField[x].set(setVal)
		self.slider[x].set(setVal)
		self.set_channel(x)

	def update_label(self, x):								################Update Label Color to show state
		if chVal[x]==self.slider[x].get():
			if chVal[x]==VAL_MAX:
				self.sliderLabel[x].config(bg="yellow")
			else:
				self.sliderLabel[x].config(bg="green")
		else:
			self.sliderLabel[x].config(bg="tan1")

	def set_channel(self, x):								################communication done here
		self.serialApp.test_connection() #Test Serial Connection, if failed disconnect Serial from SerialUI
		if self.serialApp.status()==1:
			if chVal[x]!=self.slider[x].get() :
				val=self.slider[x].get();
				##########################################Serial added here##################################################################

				par=x<<10|val
				par ^= par >> 8
				par ^= par >> 4
				par ^= par >> 2
				par ^= par >> 1
				parity=(~par)
				c0= struct.pack("B",(((x&0x1F)<<3)|((val>>7)&0x7))&0xff)
				c1= struct.pack("B",(val<<1|(parity&0x1))&0xff)
				
				self.serialApp.reset_buffer() #reset Rea Buffer
				self.serialApp.sent_bytes(c0, c1)
				b=0
				b=self.serialApp.read_bytes()

				if b=='k' and self.serialApp.status()==1:					#return String match
					print("Channel %d is set to %d"%(x+1, val))
					chVal[x]=val
					self.update_label(x)
				else:
					print("return string mismatch")


		else:
			print("Serial Not Connected!")

	def set_to_discontinous(self):							################ Force all to discontinous mode
		self.modeBtn.config(text="Discontinous")
		self.mode=0
		for i in range(N_CHANNEL):
			self.sliderSetBtn[i].config(state='normal')
		#self.masterWindow.after_cancel(timer_call)

	def set_mode(self):										################set Continous/Discontinous Mode
		if VERBOSE_LEVEL>0:
			print("setmode function call") 
		if self.mode==0 and self.serialApp.status()==1:	#set to Continous mode
			self.modeBtn.config(text="  Continous   ")
			self.mode=1
			for i in range(N_CHANNEL):
			#	set_channel(i)
				self.sliderSetBtn[i].config(state='disabled')
			self.masterWindow.after(MIN_INTERVAL, self.timer_call)

		elif self.mode==1 :		#set to Discontinous mode
			self.set_to_discontinous()
		else: 
			print("MainUI: Serial Not Connected!")

	def read_scales(self):									################read Slider Value (Debugging)
		#global chVal
		print("\n\t"),
		for i in range(N_CHANNEL):
			print("Ch %d\t"%(i+1)),
		print("\nUI\t"),
		for i in range(N_CHANNEL):
			print("%d\t" %(self.slider[i].get())),
		print("\nChannel\t"),
		for i in range(N_CHANNEL):
			print("%d\t" %(chVal[i])),
		print("\n")

	def zero_all(self):										################zero all Channel
		print("Zero all channel"),
		for i in range(N_CHANNEL):
			self.slider[i].set(0)
			self.chValEntryField[i].set("0")
			self.set_channel(i)
			print("."),
			time.sleep(MIN_INTERVAL/1000.0)

		print("Done")

	def close_window(self):
		self.masterWindow.destroy()


if __name__=='__main__':
	main()












