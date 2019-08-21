from sys import version_info
if version_info.major == 2:
	import Tkinter as tk
elif version_info.major == 3:
	import tkinter as tk

import time

from functools import partial


N_CHANNEL=5
VAL_MAX=200
VAL_MIN=0
VERBOSE_LEVEL=0
MIN_INTERVAL=100 	# update limmit in ms
#TIMER_INTERVAL=500	#in ms

mode=0 #0: discontinous mode, 1:continous mode
lastTimeCalled=time.clock()


window = tk.Tk()
#window.geometry('6500x600')

window.title("Fluid Contorl Board UI")


chVal=[0 for x in xrange(N_CHANNEL)]


def timer_call():
	#print("\t\t\t%.10f"%(time.clock()*1000))
	global lastTimeCalled

	i=0
	while i < N_CHANNEL:
		if chVal[i] != slider[i].get():
			if (time.clock()-lastTimeCalled)*1000>MIN_INTERVAL:
				set_channel(i)
				lastTimeCalled=time.clock()
			else:
				ct=time.clock();
				while (time.clock()-ct)*1000<MIN_INTERVAL:
					pass
				i -= 1
		i += 1

	if mode==1:				#set recall timer if only in continous mode
		window.after(MIN_INTERVAL, timer_call)



def read_field(x, src, dc):  #src define source 0: entry, 1: slider 

	global mode, lastTimeCalled #set mode to global

	#print("!%s!\t!%s!\t\t!%s!"%(x, src, val))
	if src == 0:
		if VERBOSE_LEVEL>1:
			print("channel %d recive value from entry"%(x+1))

		try: 		#try reading ENtry field data
			setVal = int(chValEntryField[x].get())
		except ValueError:
			print("Value enter is not integer")
			setVal=slider[x].get()			 #error set to Slide bar value

		if setVal>VAL_MAX:
			print("Value enter is not in range")
			setVal=VAL_MAX
		elif setVal<VAL_MIN:
			print("Value enter is not in range")
			setVal=VAL_MIN
		chValEntryField[x].set(setVal)
		slider[x].set(setVal)

	elif src == 1:
		if VERBOSE_LEVEL>1:
			print("channel %d recive value from slider"%(x+1))
		chValEntryField[x].set(slider[x].get())

	update_label(x) #update label Color


def set_mn(x, val):
	if val==0:
		if VERBOSE_LEVEL>0:
			print("channel %d set to min"%(x+1))
		setVal=VAL_MIN
	else:
		if VERBOSE_LEVEL>0:
			print("channel %d set to max"%(x+1))
		setVal=VAL_MAX

	chValEntryField[x].set(setVal)
	slider[x].set(setVal)
	set_channel(x)

def update_label(x):		#Update Label Color to show state


	if chVal[x]==slider[x].get():
		if chVal[x]==VAL_MAX:
			sliderLabel[x].config(bg="yellow")
		else:
			sliderLabel[x].config(bg="green")
	else:
		sliderLabel[x].config(bg="tan1")


def set_channel(x):					####communication done here
	if chVal[x]!=slider[x].get():
		print("Channel %d is set to %d"%(x+1, slider[x].get()))
		chVal[x]=slider[x].get()
		update_label(x)


		#Serial added here










def set_mode():
	global mode #set mode to global
	print("setmode function call") 
	if mode==0:	#set to Continous mode
		contBtn.config(text="  Continous   ")
		mode=1
		for i in range(N_CHANNEL):
			sliderSetBtn[i].config(state='disabled')
		window.after(MIN_INTERVAL, timer_call)

	else:		#set to Discontinous mode
		contBtn.config(text="Discontinous")
		mode=0
		for i in range(N_CHANNEL):
			sliderSetBtn[i].config(state='normal')
		#window.after_cancel(timer_call)



def read_scales():
	print("\n\t"),
	for i in range(N_CHANNEL):
		print("Ch %d\t"%(i+1)),
	print("\nUI\t"),
	for i in range(N_CHANNEL):
		print("%d\t" %(slider[i].get())),
	print("\nChannel\t"),
	for i in range(N_CHANNEL):
		print("%d\t" %(chVal[i])),
	print("\n")


def zero_all():
	print("Zero all channel"),
	for i in range(N_CHANNEL):
		slider[i].set(0)
		chValEntryField[i].set("0")
		set_channel(i)
		print("."),
		time.sleep(MIN_INTERVAL/1000.0)

	print("Done")


UILabel=tk.Label(window, text="Control")
UILabel.grid(row=0, column=0, columnspan=N_CHANNEL+1)

sliderFrame=tk.Frame(window)
sliderFrame.grid(row=1, column=0, columnspan=N_CHANNEL+1)

slider=[0 for x in xrange(N_CHANNEL)]
sliderLabel=[0 for x in xrange(N_CHANNEL)]
sliderSetBtn =[0 for x in xrange(N_CHANNEL)]
sliderEntry=[0 for x in xrange(N_CHANNEL)]
setMaxBtn=[0 for x in xrange(N_CHANNEL)]
setMinBtn=[0 for x in xrange(N_CHANNEL)]
chValEntryField=[0 for x in xrange(N_CHANNEL)]

slabel=tk.Label(sliderFrame, text="Slider")
slabel.grid(column=0, row=1)
elabel=tk.Label(sliderFrame, text="Entry Field")
elabel.grid(column=0, row=2)
btnlabel=tk.Label(sliderFrame, text="Update")
btnlabel.grid(column=0, row=4)

readallBtn=tk.Button(window,text="Read all",command=read_scales) # button to read values
readallBtn.grid(row=6,column=N_CHANNEL)
zeroBtn=tk.Button(window,text="Zero",command=zero_all) # button to read values
zeroBtn.grid(row=6,column=N_CHANNEL-1)
contLabel=tk.Label(window, text="Mode: ")
contLabel.grid(row=3, column=0)
contBtn=tk.Button(window, text="Discontinous", command=set_mode)
contBtn.grid(row=3, column=1)


colorLabel1=tk.Label(window, text="Channel Label Color Code", font=("Courier", 16))
colorLabel1.grid(row=2, column=N_CHANNEL-1, columnspan=2 )
matchLabel1=tk.Label(window,text="        ", bg="green", borderwidth=3, relief="groove")
matchLabel1.grid(row=3, column=N_CHANNEL-1)
mismatchLabel1=tk.Label(window,text="        ", bg="tan1", borderwidth=3, relief="groove")
mismatchLabel1.grid(row=4, column=N_CHANNEL-1)
maxLabel1=tk.Label(window,text="        ", bg="yellow", borderwidth=3, relief="groove")
maxLabel1.grid(row=5, column=N_CHANNEL-1)
matchLabel2=tk.Label(window,text="Up to Date")
matchLabel2.grid(row=3, column=N_CHANNEL)
mismatchLabel2=tk.Label(window,text="Update Require")
mismatchLabel2.grid(row=4, column=N_CHANNEL)
maxLabel2=tk.Label(window,text="Always On")
maxLabel2.grid(row=5, column=N_CHANNEL)


for i in range(N_CHANNEL):
	#channel Label
	sliderLabel[i]=tk.Label(sliderFrame, bg="grey", borderwidth=3, relief="groove", text="Channel %d"%(i+1))
	sliderLabel[i].grid(column=i*2+1, row=0, columnspan=2)
	#Entry Field
	chValEntryField[i]=tk.StringVar()
	sliderEntry[i]=tk.Entry(sliderFrame, width=5, textvariable=chValEntryField[i])#, validate="all", validatecommand=partial(read_field, i, 0, 0))
	chValEntryField[i].set("0")
	sliderEntry[i].bind ("<Return>",partial(read_field, i, 0))
	sliderEntry[i].grid(column=i*2+1, row=2, columnspan=2)
	#slider
	slider[i]=tk.Scale(sliderFrame, from_=VAL_MAX, to=VAL_MIN, length=200, command=partial(read_field, i, 1)) # creates widget
	slider[i].grid(column=i*2+1, row=1, columnspan=2)
	#min max btn
	setMinBtn[i]=tk.Button(sliderFrame, text="Min", command=partial(set_mn, i, 0))
	setMinBtn[i].grid(column=i*2+1, row=3)
	setMaxBtn[i]=tk.Button(sliderFrame, text="Max", command=partial(set_mn, i, 1))
	setMaxBtn[i].grid(column=(i+1)*2, row=3)

	#set Button
	sliderSetBtn[i]=tk.Button(sliderFrame, text="Set" , disabledforeground='grey', command=partial(set_channel, i))
	sliderSetBtn[i].grid(column=i*2+1, row=4, columnspan=2)




window.mainloop()
