from sys import version_info
import time
from FCB import FCB





# set the channel High threshold here:
CH01_H =170
CH02_H =320
CH03_H =124
CH04_H =180
CH05_H =157
CH06_H =116
BA_H =170
G1_H =320
G2_H =124
G3_H =180
G4_H =157
G5_H =116
G6_H =116
#Midium threshold
CH01_M = CH01_H*0.2
CH02_M = CH02_H*0.2
CH03_M = CH03_H*0.2
CH04_M = CH04_H*0.2
CH05_M = CH05_H*0.2
CH06_M = CH06_H*0.2
BA_M = BA_H*0.2
G1_M = G1_H*0.2
G2_M = G2_H*0.2
G3_M = G3_H*0.2
G4_M = G4_H*0.2
G5_M = G5_H*0.2
G6_M = G6_H*0.2

#Channel Index confirguation
CH1 = 0	#channel 1
CH2 = 1	#channel 2
CH3 = 2	#channel 3
CH4 = 3	#channel 4
CH5 = 4	#channel 5
CH6 = 5	#channel 6
BA =  6 #channel 7
G1 =  7 #channel 8
G2 =  8 #channel 9
G3 =  9 #channel 10
G4 =  10 #channel 11
G5 =  11 #channel 12
G6 =  12 #channel 13
 

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
			self.board.addChannel(-1, 30, x+1)
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

	#t=delay time 
	#n=  1:Right 0:Left
	def idle(self, n, t):
		if n==1:
			self.board.setChannelVal(CH1,CH01_H)
			self.board.setChannelVal(CH2,0)
			self.board.setChannelVal(CH3,CH03_H)
		else:
			self.board.setChannelVal(CH4,CH04_H)
			self.board.setChannelVal(CH5,0)
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
	def frontFirst(self, n, t):
		if n==1:
			self.board.setChannelVal(CH1,CH01_H)
			self.board.setChannelVal(CH2,0)
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
			self.board.setChannelVal(CH5,0)
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


	def frontSecond(self, n, t):
		if n==1:
			self.board.setChannelVal(CH1,CH01_H)
			self.board.setChannelVal(CH2,CH02_H)
			self.board.setChannelVal(CH3,CH03_M)
			time.sleep(t)
			#self.board.setChannelVal(CH1,CH01_H)
			self.board.setChannelVal(CH2,0)
			#self.board.setChannelVal(CH3,CH03_M)
			time.sleep(t)
			#self.board.setChannelVal(CH1,CH01_H)
			#self.board.setChannelVal(CH2,CH02_H)
			self.board.setChannelVal(CH3,CH03_H)
		else:
			self.board.setChannelVal(CH6,CH06_H)
			self.board.setChannelVal(CH5,CH05_H)
			self.board.setChannelVal(CH4,CH04_M)
			time.sleep(t)
			#self.board.setChannelVal(CH6,CH06_H)
			self.board.setChannelVal(CH5,0)
			#self.board.setChannelVal(CH4,CH04_M)
			time.sleep(t)
			#self.board.setChannelVal(CH6,CH06_H)
			#self.board.setChannelVal(CH5,CH05_H)
			self.board.setChannelVal(CH4,CH04_H)
		time.sleep(t)


	def backFirst(self, n, t):
		if n==1:
			self.board.setChannelVal(CH1,CH01_M)
			self.board.setChannelVal(CH2,0)
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
			self.board.setChannelVal(CH5,0)
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


	def backSecond(self, n, t):
		if n==1:
			self.board.setChannelVal(CH1,CH01_M)
			self.board.setChannelVal(CH2,CH02_H)
			self.board.setChannelVal(CH3,CH03_H)
			time.sleep(t)
			#self.board.setChannelVal(CH1,CH01_M)
			self.board.setChannelVal(CH2,0)
			#self.board.setChannelVal(CH3,CH03_H)
			time.sleep(t)
			self.board.setChannelVal(CH1,CH01_H)
			#self.board.setChannelVal(CH2,CH02_H)
			#self.board.setChannelVal(CH3,CH03_H)
		else:
			self.board.setChannelVal(CH6,CH06_M)
			self.board.setChannelVal(CH5,CH05_H)
			self.board.setChannelVal(CH4,CH04_H)
			time.sleep(t)
			#self.board.setChannelVal(CH6,CH06_M)
			self.board.setChannelVal(CH5,0)
			#self.board.setChannelVal(CH4,CH04_H)
			
			self.board.setChannelVal(CH6,CH06_H)
			#self.board.setChannelVal(CH5,CH05_H)
			#self.board.setChannelVal(CH4,CH04_H)
		time.sleep(t)


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

	def largeGrasp(self, t)
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

	def release(self, t)
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


def main():

	SERIAL_PORT="/dev/cu.wchusbserial14120"   ##########replace this with actual serial port

	robot=Robot(SERIAL_PORT)
	robot.inititalizeAllChannels()
	########################################write your program here...########################################
	##########################################################################################################
	##########################################################################################################
	#call function with apporiate input, ignore the "self"
	#ex: robot.fullyActuated(1, 2)











	quit()   ###program terminate





if __name__=='__main__':
	main()