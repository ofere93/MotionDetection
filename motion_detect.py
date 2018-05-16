import cv2
import numpy as np
import sys

def MotionDetection(inVideo, firstFrame, lastFrame):
	font= cv2.FONT_HERSHEY_SIMPLEX
	fontScale= 0.55

	position=(5,35)
	lineType= 2

	outVideo='video.avi'
	cap = cv2.VideoCapture(inVideo)
	
	
	#ERROR CHECKING
	if(firstFrame>lastFrame):
		print("\033[31mThe value of the first frame can't be greater than the value of the last frame")
		sys.exit()
	
	if(firstFrame<0 or lastFrame<0):
		print("\033[31mThe values of the frames can't be negative")
		sys.exit()
	
	if(lastFrame>cap.get(7)):
		print("\033[31mThe maximum value allow for the last frame is:",cap.get(7))
		sys.exit()
	
	
	video = cv2.VideoWriter(outVideo, cv2.VideoWriter_fourcc(*'XVID'), cap.get(5), (int(cap.get(3)),int(cap.get(4))))

	fgbg = cv2.createBackgroundSubtractorMOG2(varThreshold = 40, detectShadows = False )
	fgbg.setHistory(1000)

	frame = cap.get(7)

	start=firstFrame
	end=lastFrame
	i=0

	xt=[-1.0]*100
	yt=[-1.0]*100
	stringPers=[None]*100
	stringCars=[None]*100
	#string[0]=''
	valuePers=0
	valueCars=0

	#-------- matrix=[[x, y, name, number frame, used, last frame]] --------#
	matrixPers=[[0,0,0,0,0,0]]
	matrixCars=[[0,0,0,0,0,0]]

	while(i<end):
		length,next = cap.read()
		
		
		
		if((i>=start)):
			
			
			mask1=fgbg.apply(next)
			#cv2.imshow('mask1',mask1)
			
			mask = cv2.medianBlur(mask1,7)
			cv2.imshow('mask',mask)
			
			
			kernel=cv2.getStructuringElement(cv2.MORPH_RECT,(20,20))
			morph=cv2.dilate(mask,kernel)
			kernel=cv2.getStructuringElement(cv2.MORPH_RECT,(15,15))
			morph=cv2.erode(morph,kernel,iterations=1)
			
			blur=morph

			im2, contours, hierarchy=cv2.findContours(blur,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
			cv2.drawContours(next,contours,-1, (255,255,0), 1)
			
			
			
			
			for c in contours:
				
				x,y,w,h = cv2.boundingRect(c)
				
				position=(x,y-5)
				
				M = cv2.moments(c)
				
				cx = int(M['m10']/(M['m00']))
				cy = int(M['m01']/(M['m00']))
				
				if(i>start):
					k=0
					find=False
					
					if(cx>50):
						#PEOPLE
						if((h>15)and(w>15)and(h>w)):
							cv2.rectangle(next,(x,y),(x+w,y+h),(0,255,0),2)
							fontColor= (0,255,0)
							
							k=len(matrixPers)-1
							while(k>-1):
							
							#check if the rectangle is already present								
								if((abs(matrixPers[k][0]-cx)<20)and(abs(matrixPers[k][1]-cy)<20)):
									#print("Found it")
									matrixPers[k][0]=cx
									matrixPers[k][1]=cy
									matrixPers[k][3]=matrixPers[k][3]+1
									matrixPers[k][5]=i
									if(matrixPers[k][3]>37):
										if(matrixPers[k][4]==0):
											valuePers=valuePers+1
											matrixPers[k][2]=valuePers
											matrixPers[k][4]=1
										
										cv2.putText(next,"P"+str(matrixPers[k][2]), position, font, fontScale, fontColor, lineType)
									find=True
									break
								k=k-1
								
							#Region not present
							if(find==False):
								matrixPers.append([cx,cy,valuePers,1,0,i])
								
						#CARS
						elif((h>20)and(w>20)and(w>h)):
							fontColor= (255,0,0)
							cv2.rectangle(next,(x,y),(x+w,y+h),(255,0,0),2)
							
							
							k=len(matrixCars)-1
							while(k>-1):
							#check if the rectangle is already present
								if((abs(matrixCars[k][0]-cx)<30)and(abs(matrixCars[k][1]-cy)<30)):
									#print("Found it")
									matrixCars[k][0]=cx
									matrixCars[k][1]=cy
									matrixCars[k][3]=matrixCars[k][3]+1
									matrixCars[k][5]=i
									if(matrixCars[k][3]>12):
										if(matrixCars[k][4]==0):
											valueCars=valueCars+1
											matrixCars[k][2]=valueCars
											matrixCars[k][4]=1
											
										cv2.putText(next,"C"+str(matrixCars[k][2]), position, font, fontScale, fontColor, lineType)
									find=True
									break
								k=k-1
								
							#Region not present
							if(find==False):
								matrixCars.append([cx,cy,valueCars,1,0,i])
								
						else:
							cv2.rectangle(next,(x,y),(x+w,y+h),(0,0,255),2)
					#OTHERS
					else:
						cv2.rectangle(next,(x,y),(x+w,y+h),(0,0,255),2)
			
					
			cv2.putText(next,"Frame: "+str(i), (20,30), font, fontScale, (0,0,0), lineType)
			cv2.imshow('video',next)
			
			#Write the result
			video.write(next)
			
			
			#Deleting objects to the matrix
			j=0
			while(j<len(matrixCars)):
				if(i-matrixCars[j][5]>150):
					del matrixCars[j]
				j=j+1
			
			j=0
			while(j<len(matrixPers)):
				if(i-matrixPers[j][5]>150):
					del matrixPers[j]
				j=j+1
			
			
			if cv2.waitKey(25) & 0xFF == ord('q'):
				break
		i=i+1

	

	video.release()
	cap.release()

	cv2.destroyAllWindows()
	return outVideo
	
	
if __name__ == "__main__":
   outVideo=MotionDetection('camera1.mov',0,3064)
