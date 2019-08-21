from sys import version_info
if version_info.major == 2:
	import Tkinter as tk
elif version_info.major == 3:
	import tkinter as tk
import time
from FCB import FCB
from functools import partial






# set the channel High threshold here:
CH01_H = 120 #280
CH02_H = 420
CH03_H = 120 #294
CH04_H = 160 #290
CH05_H = 430
CH06_H = 110 #220
BA_H =42
G1_H =250
G2_H =250
G3_H =220
G4_H =260
G5_H =210
G6_H =210
#Midium threshold
CH01_M = CH01_H*0.2
CH02_M = 200
CH03_M = CH03_H*0.2
CH04_M = CH04_H*0.2
CH05_M = 200
CH06_M = CH06_H*0.2
BA_M = BA_H*0.2
G1_M = G1_H*0.2
G2_M = G2_H*0.2
G3_M = G3_H*0.2
G4_M = G4_H*0.2
G5_M = G5_H*0.2
G6_M = G6_H*0.2

#Low Threshold
CH02_L = 200
CH05_L = 200

#Channel Index confirguation
CH1 = 0	#channel 1
CH2 = 1	#channel 2
CH3 = 2	#channel 3
CH4 = 3	#channel 4
CH5 = 4	#channel 5
CH6 = 5	#channel 6
G1 =  6 #channel 7
G2 =  7 #channel 8
G3 =  8 #channel 9
G4 =  9 #channel 10
G5 =  10 #channel 11
G6 =  11 #channel 12
BA =  12 #channel 13
 

class Robot:
	def __init__(self, SerialPort):

		#initialize serial connection
		self.board=FCB()
		self.board.listAllSerialPort()
		if self.board.startLink(SerialPort)==True:
			print("Serial Connected")
		else: #if Serial device not found, terminate the program
			print("\tSerial not Connected")
			quit()

	def inititalizeAllChannels(self):
		#adding all 13 channels
		for x in range(13):
			self.board.addChannel(-1, 30, x)
		self.zeroAll()

	def zeroAll(self):
		for x in range(13):
			self.board.setChannelVal(x,0)

	#begining of the function

	#t=delay time 
	def flat(self, t):
		self.board.setChannelVal(CH1,0)
		self.board.setChannelVal(CH2,0)
		self.board.setChannelVal(CH3,0)
		self.board.setChannelVal(CH4,0)
		self.board.setChannelVal(CH5,0)
		self.board.setChannelVal(CH6,0)
		time.sleep(t)

	def flat(self):
		self.board.setChannelVal(CH1,0)
		self.board.setChannelVal(CH2,0)
		self.board.setChannelVal(CH3,0)
		self.board.setChannelVal(CH4,0)
		self.board.setChannelVal(CH5,0)
		self.board.setChannelVal(CH6,0)
		self.board.requestStatus()

	#t=delay time 
	#n=  1:Right 2:Left
	def idle(self, n, t):
		if n==1:
			self.board.setChannelVal(CH1,CH01_H)
			self.board.setChannelVal(CH2,CH02_L)
			self.board.setChannelVal(CH3,CH03_H)
		elif n==2:
			self.board.setChannelVal(CH4,CH04_H)
			self.board.setChannelVal(CH5,CH05_L)
			self.board.setChannelVal(CH6,CH06_H)
		else:
			self.board.setChannelVal(CH1,CH01_H)
			self.board.setChannelVal(CH2,CH02_L)
			self.board.setChannelVal(CH3,CH03_H)
			self.board.setChannelVal(CH4,CH04_H)
			self.board.setChannelVal(CH5,CH05_L)
			self.board.setChannelVal(CH6,CH06_H)
		time.sleep(t)

	#t=delay time 
	#n=  1:Right 0:Left
	def fullyActuated(self, n, t):
		if n==1:
			self.board.setChannelVal(CH1,CH01_H)
			self.board.setChannelVal(CH2,CH02_H)
			self.board.setChannelVal(CH3,CH03_H)
		else:
			self.board.setChannelVal(CH4,CH04_H)
			self.board.setChannelVal(CH5,CH05_H)
			self.board.setChannelVal(CH6,CH06_H)
		time.sleep(t)

	#t=delay time 
	#n=  1:Right 0:Left
	def frontExtend(self, n, t):
		if n==1:
			self.board.setChannelVal(CH1,CH01_H)
			self.board.setChannelVal(CH2,CH02_L)
			self.board.setChannelVal(CH3,CH03_M)
			time.sleep(t)
			#self.board.setChannelVal(CH1,CH01_H)
			self.board.setChannelVal(CH2,CH02_H)
			#self.board.setChannelVal(CH3,CH03_M)
			time.sleep(t)
			#self.board.setChannelVal(CH1,CH01_H)
			#self.board.setChannelVal(CH2,CH02_H)
			self.board.setChannelVal(CH3,CH03_H)
		else:
			self.board.setChannelVal(CH6,CH06_H)
			self.board.setChannelVal(CH5,CH05_L)
			self.board.setChannelVal(CH4,CH04_M)
			time.sleep(t)
			#self.board.setChannelVal(CH6,CH06_H)
			self.board.setChannelVal(CH5,CH05_H)
			#self.board.setChannelVal(CH4,CH04_M)
			time.sleep(t)
			#self.board.setChannelVal(CH6,CH06_H)
			#self.board.setChannelVal(CH5,CH05_H)
			self.board.setChannelVal(CH4,CH04_H)
		time.sleep(t)


	def frontRetract(self, n, t):
		if n==1:
			self.board.setChannelVal(CH1,CH01_H)
			self.board.setChannelVal(CH2,CH02_H)
			self.board.setChannelVal(CH3,CH03_M)
			time.sleep(t)
			#self.board.setChannelVal(CH1,CH01_H)
			self.board.setChannelVal(CH2,CH02_L)
			#self.board.setChannelVal(CH3,CH03_M)
			time.sleep(t)
			#self.board.setChannelVal(CH1,CH01_H)
			#self.board.setChannelVal(CH2,CH02_M)
			self.board.setChannelVal(CH3,CH03_H)
		else:
			self.board.setChannelVal(CH6,CH06_H)
			self.board.setChannelVal(CH5,CH05_H)
			self.board.setChannelVal(CH4,CH04_M)
			time.sleep(t)
			#self.board.setChannelVal(CH6,CH06_H)
			self.board.setChannelVal(CH5,CH05_L)
			#self.board.setChannelVal(CH4,CH04_M)
			time.sleep(t)
			#self.board.setChannelVal(CH6,CH06_H)
			#self.board.setChannelVal(CH5,CH05_L)
			self.board.setChannelVal(CH4,CH04_H)
		time.sleep(t)


	def backExtend(self, n, t):
		if n==1:
			self.board.setChannelVal(CH1,CH01_M)
			self.board.setChannelVal(CH2,CH02_L)
			self.board.setChannelVal(CH3,CH03_H)
			time.sleep(t)
			#self.board.setChannelVal(CH1,CH01_M)
			self.board.setChannelVal(CH2,CH02_H)
			#self.board.setChannelVal(CH3,CH03_H)
			time.sleep(t)
			self.board.setChannelVal(CH1,CH01_H)
			#self.board.setChannelVal(CH2,CH02_H)
			#self.board.setChannelVal(CH3,CH03_H)
		else:
			self.board.setChannelVal(CH6,CH06_M)
			self.board.setChannelVal(CH5,CH05_L)
			self.board.setChannelVal(CH4,CH04_H)
			time.sleep(t)
			#self.board.setChannelVal(CH6,CH06_M)
			self.board.setChannelVal(CH5,CH05_H)
			#self.board.setChannelVal(CH4,CH04_H)
			time.sleep(t)
			self.board.setChannelVal(CH6,CH06_H)
			#self.board.setChannelVal(CH5,CH05_H)
			#self.board.setChannelVal(CH4,CH04_H)
			time.sleep(t)


	def backRetract(self, n, t):
		if n==1:
			self.board.setChannelVal(CH1,CH01_M)
			self.board.setChannelVal(CH2,CH02_H)
			self.board.setChannelVal(CH3,CH03_H)
			time.sleep(t)
			#self.board.setChannelVal(CH1,CH01_M)
			self.board.setChannelVal(CH2,CH02_L)
			#self.board.setChannelVal(CH3,CH03_H)
			time.sleep(t)
			self.board.setChannelVal(CH1,CH01_H)
			#self.board.setChannelVal(CH2,CH02_L)
			#self.board.setChannelVal(CH3,CH03_H)
			time.sleep(t)
		else:
			self.board.setChannelVal(CH6,CH06_M)
			self.board.setChannelVal(CH5,CH05_H)
			self.board.setChannelVal(CH4,CH04_H)
			time.sleep(t)
			#self.board.setChannelVal(CH6,CH06_M)
			self.board.setChannelVal(CH5,CH05_L)
			#self.board.setChannelVal(CH4,CH04_H)
			time.sleep(t)
			self.board.setChannelVal(CH6,CH06_H)
			#self.board.setChannelVal(CH5,CH05_M)
			#self.board.setChannelVal(CH4,CH04_H)
			time.sleep(t)

	def graspPosition(self, t):
		self.board.setChannelVal(CH1, CH01_H)
		self.board.setChannelVal(CH6, CH06_H)

	def forwardStep(self, s,t):
		#Step Front Right foot extend
		self.idle(2,s)
		self.frontExtend(1,t)

		#Step Front Left foot extend
		self.fullyActuated(1,s)
		self.frontExtend(2,t)

		#Step Back Right foot retract
		self.fullyActuated(2,s)
		self.backRetract(1,t)

		#Step Back Left foot retract
		self.idle(1,s)
		self.backRetract(2,t)

		#Return to idle
		self.idle(3,s)

	def forwardStepAlt(self, s,t):
		#Step Front Right foot extend
		self.idle(2,s)
		self.frontExtend(1,t)

		#Step Back Right foot retract
		self.idle(2,s)
		self.backRetract(1,t)

		#Step Front Left foot extend
		self.idle(1,s)
		self.frontExtend(2,t)

		#Step Back Left foot retract
		self.idle(1,s)
		self.backRetract(2,t)

		#Return to idle
		self.idle(3,s)

	def backwardStep(self, s,t):
		#Step Back Right foot extend
		self.idle(2,s)
		self.backExtend(1,t)

		#Step Back Left foot extend
		self.fullyActuated(1,s)
		self.backExtend(2,t)

		#Step Front Right foot retract
		self.fullyActuated(2,s)
		self.frontRetract(1,t)

		#Step Back Left foot retract
		self.idle(1,s)
		self.frontRetract(2,t)

		#Return to idle
		self.idle(3,s)
	

	def forwardRight(self, s,t):
		#Step Front Left foot extend
		self.frontExtend(2,t)

		#Step Back Left foot retract
		self.idle(1,s)
		self.backRetract(2,t)

		#Return to idle
		self.idle(3,s)

	def forwardLeft(self, s,t):
		#Step Front Right foot extend
		self.frontExtend(1,t)

		#Step Back Right foot retract
		self.idle(2,s)
		self.backRetract(1,t)

		#Return to idle
		self.idle(3,s)


	def backwardRight(self, s,t):
		#Step Back Left foot extend
		self.backExtend(2,t)

		#Step Back Left foot retract
		self.idle(1,s)
		self.frontRetract(2,t)

		#Return to idle
		self.idle(3,s)


	def backwardLeft(self, s,t):
		#Step Back Right foot extend
		self.backExtend(1,t)

		#Step Front Right foot retract
		self.idle(2,s)
		self.frontRetract(1,t)

		#Return to idle
		self.idle(3,s)



	#hand motion

	def zeroHand(self, t):
		self.board.setChannelVal(BA,0)
		self.board.setChannelVal(G1,0)
		self.board.setChannelVal(G2,0)
		self.board.setChannelVal(G3,0)
		self.board.setChannelVal(G4,0)
		self.board.setChannelVal(G5,0)
		self.board.setChannelVal(G6,0)
		time.sleep(t)

	def smallGrasp(self, t):
		self.board.setChannelVal(BA,0)
		self.board.setChannelVal(G1,G1_H)
		self.board.setChannelVal(G2,0)
		self.board.setChannelVal(G3,G3_H)
		self.board.setChannelVal(G4,G4_H)
		self.board.setChannelVal(G5,0)
		self.board.setChannelVal(G6,G6_H)
		######
		time.sleep(t)
		#self.board.setChannelVal(G1,G1_H)
		self.board.setChannelVal(G2,G2_H)
		#self.board.setChannelVal(G3,G3_H)
		#self.board.setChannelVal(G4,G4_H)
		self.board.setChannelVal(G5,G5_H)
		#self.board.setChannelVal(G6,G6_H)
		######
		time.sleep(t)
		self.board.setChannelVal(BA,BA_H)
		time.sleep(t)

	def largeGrasp(self, t):
		self.board.setChannelVal(BA,0)
		self.board.setChannelVal(G1,0)
		self.board.setChannelVal(G2,G2_H)
		self.board.setChannelVal(G3,0)
		self.board.setChannelVal(G4,0)
		self.board.setChannelVal(G5,G5_H)
		self.board.setChannelVal(G6,0)
		######
		time.sleep(t)
		self.board.setChannelVal(G1,G1_H)
		#self.board.setChannelVal(G2,G2_H)
		self.board.setChannelVal(G3,G3_H)
		self.board.setChannelVal(G4,G4_H)
		#self.board.setChannelVal(G5,G5_H)
		self.board.setChannelVal(G6,G6_H)
		######
		time.sleep(t)
		self.board.setChannelVal(BA,BA_H)
		time.sleep(t)

	def release(self, t):
		self.board.setChannelVal(BA,BA_H)
		self.board.setChannelVal(G1,G1_H)
		self.board.setChannelVal(G2,G2_H)
		self.board.setChannelVal(G3,G3_H)
		self.board.setChannelVal(G4,G4_H)
		self.board.setChannelVal(G5,G5_H)
		self.board.setChannelVal(G6,G6_H)
		#######
		time.sleep(t)
		self.board.setChannelVal(BA,0)
		#######
		time.sleep(t)
		#self.board.setChannelVal(G1,G1_H)
		self.board.setChannelVal(G2,0)
		self.board.setChannelVal(G3,0)
		self.board.setChannelVal(G4,0)
		self.board.setChannelVal(G5,0)
		#self.board.setChannelVal(G6,G6_H)
		#######
		time.sleep(t)
		self.board.setChannelVal(G1,0)
		self.board.setChannelVal(G6,0)
		#######
		time.sleep(t)


stop = False

# def flatfunction(robot):

# 	t = 3
# 	s = 1

# 	print("flat start")
# 	robot.flat(s)
# 	print("flat done")

# def idlefunction(robot):

# 	t = 3
# 	s = 1

# 	print("flat start")
# 	robot.idle(3,s)
# 	print("flat done")

# def mainForwardStep(robot):

# 	t = 3
# 	s = 1

# 	print("forward step start")
# 	robot.forwardStep(s,t)
# 	print("forward step Done")

# def mainForwardAlt(robot):

# 	t = 3
# 	s = 1

# 	print("forward step alt start")
# 	robot.forwardStepAlt(s,t)
# 	print("forward step alt Done")

# def mainForwardLeft(robot):

# 	t = 3
# 	s = 1

# 	print("forward left Start")
# 	robot.forwardLeft(s,t)
# 	print("forward left Done")

# def mainForwardRight(robot):
	
# 	t = 3
# 	s = 1
	
# 	print("forward right Start")
# 	robot.forwardRight(s,t)
# 	print("forward right Done")

# def mainBackwardStep(robot):

# 	t = 3
# 	s = 1

# 	print("backward step Start")
# 	robot.backwardStep(s,t)
# 	print("backward step Done")

# def mainBackwardLeft(robot):

# 	t = 3
# 	s = 1

# 	print("backward left Start")
# 	robot.backwardLeft(s,t)
# 	print("backward left Done")

# def mainBackwardRight(robot):

# 	t = 3
# 	s = 1

# 	print("backward right Start")
# 	robot.backwardRight(s,t)
# 	print("backward right Done")

# def graspPositionSet(robot):
# 	t = 3
# 	s = 1

# 	print("grasp position Start")
# 	robot.graspPosition(t)
# 	print("grasp position Done")

def flatfunction(robot):

	t = 3
	s = 1

	print("flat start")
	robot.flat(s)
	print("flat done")

def idlefunction(robot):

	t = 3
	s = 1

	print("flat start")
	robot.idle(3,s)
	print("flat done")

def mainForwardStep(robot):

	t = 3
	s = 1

	print("forward step start")
	robot.forwardStep(s,t)
	print("forward step Done")

def mainForwardAlt(robot):

	t = 3
	s = 1

	print("forward step alt start")
	robot.forwardStepAlt(s,t)
	print("forward step alt Done")

def mainForwardLeft(robot):

	t = 3
	s = 1

	print("forward left Start")
	robot.forwardLeft(s,t)
	print("forward left Done")

def mainForwardRight(robot):
	
	t = 3
	s = 1
	
	print("forward right Start")
	robot.forwardRight(s,t)
	print("forward right Done")

def mainBackwardStep(robot):

	t = 3
	s = 1

	print("backward step Start")
	robot.backwardStep(s,t)
	print("backward step Done")

def mainBackwardLeft(robot):

	t = 3
	s = 1

	print("backward left Start")
	robot.backwardLeft(s,t)
	print("backward left Done")

def mainBackwardRight(robot):

	t = 3
	s = 1

	print("backward right Start")
	robot.backwardRight(s,t)
	print("backward right Done")

def graspPositionSet(robot):
	t = 3
	s = 1

	print("grasp position Start")
	robot.graspPosition(t)
	print("grasp position Done")

def largeGrasp(robot):
	t = 5

	print("large grasp Start")
	robot.largeGrasp(t)
	print("lage grasp Done")

def release(robot):
	t = 3

	print("release Start")
	robot.release(t)
	print("release Done")


def main():
	masterwindows = tk.Tk()
	masterwindows.title("Control Input")

	SERIAL_PORT="/dev/cu.usbmodem14101"
	#SERIAL_PORT="COM7"   ##################################replace this with actual serial port

	robot=Robot(SERIAL_PORT)
	robot.inititalizeAllChannels()

	t = 3
	s = 1


	flatButton = tk.Button(masterwindows, text = "Flat", command = partial(flatfunction, robot))
	flatButton.grid(row=0, column=0)
	idleButton = tk.Button(masterwindows, text = "Idle", command = partial(idlefunction, robot))
	idleButton.grid(row=0, column=1)
	graspPositionButton = tk.Button(masterwindows, text = "Grasp Position", command = partial(graspPositionSet, robot))
	graspPositionButton.grid(row=0, column=2)
	forwardLeftButton = tk.Button(masterwindows, text = "Forward Left", command = partial(mainForwardLeft, robot))
	forwardLeftButton.grid(row=1, column=0)
	forwardStepButton = tk.Button(masterwindows, text = "Forward Step", command = partial(mainForwardStep, robot))
	forwardStepButton.grid(row=1, column=1)
	forwardRightButton = tk.Button(masterwindows, text = "Forward Right", command = partial(mainForwardRight, robot))
	forwardRightButton.grid(row=1, column=2)
	forwardAltButton = tk.Button(masterwindows, text = "Forward Alt", command = partial(mainForwardAlt, robot))
	forwardAltButton.grid(row=1, column=3)	
	backwardLeftButton = tk.Button(masterwindows, text = "Backward Left", command = partial(mainBackwardLeft, robot))
	backwardLeftButton.grid(row=2, column=0)
	backwardStepButton = tk.Button(masterwindows, text = "Backward Step", command = partial(mainBackwardStep, robot))
	backwardStepButton.grid(row=2, column=1)
	backwardRightButton = tk.Button(masterwindows, text = "Backward Right", command = partial(mainBackwardRight, robot))
	backwardRightButton.grid(row=2, column=2)
	largeGraspButton = tk.Button(masterwindows, text = "Large Grasp", command = partial(largeGrasp, robot))
	largeGraspButton.grid(row=3, column=0)
	releaseButton = tk.Button(masterwindows, text = "Release", command = partial(release, robot))
	releaseButton.grid(row=3, column=1)

	masterwindows.mainloop()



#------------------------------------------

# 	#Step Front Right foot forward
# 	robot.idle(2,s)
# 	robot.frontExtend(1,t)

# 	#Step Front Left foot forward
# 	robot.fullyActuated(1,s)
# 	robot.frontExtend(2,t)

# 	#Step Back Right foot forward
# 	robot.fullyActuated(2,s)
# 	robot.backRetract(1,t)

# 	#Step Back Left foot forward
# 	robot.idle(1,s)
# 	robot.backRetract(2,t)

# 	#Return to idle
# 	robot.idle(1,s)
# 	robot.idle(2,s)

# #------------------------------------------

# 	#Step Front Right foot forward
# 	robot.idle(2,s)
# 	robot.frontExtend(1,t)

# 	#Step Front Left foot forward
# 	robot.fullyActuated(1,s)
# 	robot.frontExtend(2,t)

# 	#Step Back Right foot forward
# 	robot.fullyActuated(2,s)
# 	robot.backRetract(1,t)

# 	#Step Back Left foot forward
# 	robot.idle(1,s)
# 	robot.backRetract(2,t)

# 	#Return to idle
# 	robot.idle(1,s)
# 	robot.idle(2,s)

	









	quit()   ###program terminate





if __name__=='__main__':
	main()