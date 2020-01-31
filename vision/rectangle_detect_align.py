#date: 2020-01-31
import numpy as np
import cv2 as cv

def nothing(x):
	pass

cap = cv.VideoCapture(0)

#camera resolution settings
cap.set(3, 640) #width
cap.set(4, 640) #height

#pixel value x-intercept of vertical boundary lines to use for brick distance matching
left_bar = 160
right_bar = 480

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
#note: Blue sticky note pad in my room falls in HSV range of
#    lower HSV: (27, 21, 94)
#    upper HSV: (131, 196, 213)
	l_h = cv.getTrackbarPos("L-H", "Trackbars")
	l_s = cv.getTrackbarPos("L-S", "Trackbars")
	l_v = cv.getTrackbarPos("L-V", "Trackbars")
	u_h = cv.getTrackbarPos("U-H", "Trackbars")
	u_s = cv.getTrackbarPos("U-S", "Trackbars")
	u_v = cv.getTrackbarPos("U-V", "Trackbars")
	
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
		
	if (0.9*right_bar) < right_edge < (1.1*right_bar):
		cv.putText(frame, "RIGHT ALIGNED", (320, 420), font, 1, (0, 0, 0))
	
	cv.imshow("Frame", frame)#both of these display capture windows
	cv.imshow("Mask", mask)# ""

	key = cv.waitKey(1)
	if key == 27: #hit ESC KEY to terminate
		break

cap.release()
cv.destroyAllWindows()