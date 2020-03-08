#date start: 2020-01-31
#TODO: seperate serial processes into different files, make things gooder-er
import numpy as np
import cv2 as cv
import serial


def nothing(x):
	pass

#serial portion start
#ser = serial.Serial('COM3')#USB port my arduino on windows is using, may need to change for diff computers
ser = serial.Serial('/dev/ttyACM0') #jetson nano arduino port
ser.baudrate = 9600
#end serial initilization code

def gstreamer_pipeline(
    capture_width=640,#3280,
    capture_height=640,#2464,
    display_width=820,
    display_height=616,
    framerate=21,
    flip_method=0,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )

#cap = cv.VideoCapture('/dev/video0')#,cv.CAP_V4L2)
cap = cv.VideoCapture(gstreamer_pipeline(), cv.CAP_GSTREAMER)


#camera resolution settings
#cap.set(3, 640) #width
#cap.set(4, 640) #height

#pixel value x-intercept of vertical boundary lines to use for brick distance matching
left_bar = 160
right_bar = 480

#initial values for left_edge, right_edge to make robot do a certain command by default, and command flags
left_edge = -1
right_edge = -1
left_aligned = False
right_aligned = False
motorCommand = '0'
#TASK VARIABLE, used for telling robot what to do
task = 'start'


cv.namedWindow("Trackbars")
cv.createTrackbar("L-H", "Trackbars", 27, 180, nothing)
cv.createTrackbar("L-S", "Trackbars", 21, 255, nothing)
cv.createTrackbar("L-V", "Trackbars", 94, 255, nothing)
cv.createTrackbar("U-H", "Trackbars", 131, 180, nothing)
cv.createTrackbar("U-S", "Trackbars", 196, 255, nothing)
cv.createTrackbar("U-V", "Trackbars", 213, 255, nothing)

font = cv.FONT_HERSHEY_COMPLEX

while True:
	_, frame = cap.read()
	hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

	l_h = cv.getTrackbarPos("L-H", "Trackbars")
	l_s = cv.getTrackbarPos("L-S", "Trackbars")
	l_v = cv.getTrackbarPos("L-V", "Trackbars")
	u_h = cv.getTrackbarPos("U-H", "Trackbars")
	u_s = cv.getTrackbarPos("U-S", "Trackbars")
	u_v = cv.getTrackbarPos("U-V", "Trackbars")
#black lego HSV range
#	lower HSV: (0,0,0)
#	upper HSV: (180,255,44)
#brown lego HSV range
#	lower HSV: 
#red lego HSV range
#	lower HSV: (0,119,49)
#	upper HSV: (180,25,87)
#orange lego hsv range
#	lower HSV: (0,108,91)
#	upper HSV: (19,255,255)
#yellow lego hsv range
#	lower HSV: (14,57,80)
#       upper HSV: (76,255,255)
#green lego hsv range
#	lower HSV: (26,59,20)
#	upper HSV: (103,255,255)
#blue lego HSV range
#	lower HSV: (92,101,7)
#	upper HSV: (118,255,255)
#indigo lego HSV range
#	lower HSV: (
#	upper HSV: (
#grey (baby blue actually) lego HSV range
#	lower HSV: (0,26,75)
#	upper HSV: (144,94,134)
#white lego HSV range
#	lower HSV: (0,0,209)
#	upper HSV: (180,39,162)
	
	#cv.line(image, start_point, end_point, color, thickness)
	cv.line(frame, (left_bar,0), (left_bar,640), (0, 255, 0), 3) #left test line
	cv.line(frame, (right_bar,0), (right_bar,640), (0, 255, 0), 3) #right test line
	
	
	lower_color = np.array([l_h, l_s, l_v])
	upper_color = np.array([u_h, u_s, u_v])

	mask = cv.inRange(hsv, lower_color, upper_color)
	kernel = np.ones((5, 5), np.uint8)
	mask = cv.erode(mask, kernel)
	
	contours, _ = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
	
	for cnt in contours:
		area = cv.contourArea(cnt)
		approx = cv.approxPolyDP(cnt, 0.02*cv.arcLength(cnt, True), True)
		x = approx.ravel()[0]
		y = approx.ravel()[1]
	
		if area > 400:
			cv.drawContours(frame, [approx], 0, (0, 0, 0), 5)
			
			(xx, yy, w, h) = cv.boundingRect(cnt) #this creates a rectangle to bound the detected object
			cv.rectangle(frame, (xx,yy),(xx+w,yy+h),(255,0,0),2) #THIS DRAWS THE BOUNDING RECTANGLE
			left_edge = int(xx) #X position of the left edge of detected rectangle
			right_edge = int(xx) + int(w) #adds width of detected rectangle to left edge coordinate to obtain right edge
			
			if len(approx) == 4:
				cv.putText(frame, "Rectangle", (x, y), font, 1, (0, 0, 0))#label it on 'frame' window
	
	#these next if statements will compare the detected rectangle edges against the static bars
	if (0.9*left_bar) < left_edge < (1.1*left_bar):
		cv.putText(frame, "LEFT ALIGNED", (320,320), font, 1, (0, 0, 0))
		left_aligned = True
	else:
		left_aligned = False
		
	if (0.9*right_bar) < right_edge < (1.1*right_bar):
		cv.putText(frame, "RIGHT ALIGNED", (320, 420), font, 1, (0, 0, 0))
		right_aligned = True
	else:
		right_aligned = False
		
	#next if statements should be refined later, to be used for sending serial commands based on alignment
	if (right_aligned and left_aligned) == 1: #stop motor when both sides aligned
		motorCommand = 'S'
	
	elif (not right_aligned and not left_aligned) == 1: #spin robot clockwise if no sides aligned
		motorCommand = 'C'
	#end serial command if statements
	#ser.write(motorCommand.encode('ascii'))
	
	cv.imshow("Frame", frame)#both of these display capture windows
	cv.imshow("Mask", mask)

	key = cv.waitKey(1)
	if key == 27: #hit ESC KEY to terminate
		break

cap.release()
cv.destroyAllWindows()
