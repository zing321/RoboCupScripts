#use cv2 methods, its current. cv2 images are numpy arrays while cv images are cvmats and that weird stuff
import cv2

#cv is legacy but sometime's its variables are needed for some functions
import cv2.cv as cv

#sets camera to a video capture device on the system. the parameter is which camera to use if there are multiple cameras
#0 is the primary camera, 1 is secondary and so on...
camera = cv2.VideoCapture(0)

#these are just for debugging. creates two windows, one for the mask and one for the color image the detected circles are displayed on.
cv2.namedWindow('mask',flags=cv.CV_WINDOW_AUTOSIZE)
cv2.namedWindow('cimg',flags=cv.CV_WINDOW_AUTOSIZE)

def trackBall():
    #takes one frame of the camera and stores it in cimg (color image). r is not used.
    r,cimg=camera.read()

    #converts cimg to a HSV image (Hue, Saturation, Value)
    hsvimg=cv2.cvtColor(cimg,cv2.COLOR_BGR2HSV)

    #These lines creates an image consisting of only two colors, black or white. white is a pixel that falls into the range discribed in the parameters
    #and black is a pixel that does not. The 2nd parameter is the min threshold for color and the 3rd is the max. Both are in the format
    #(H,S,V). The standard for most programs such as photoshop is H: 0-360 S:0-100% V:0-100% (V is sometimes known as B in some programs).
    #In opencv its H:0-180 S:0-255 V:0-255
    #The first mask shows the dark areas of the ball
    mask=cv2.inRange(hsvimg,(0,200,200),(10,255,255))
    #The second mask shows the light areas of the ball
    mask2=cv2.inRange(hsvimg,(5,128,200),(15,200,255))

    #masks are merged together to get a whole ball. Remember these are numpy arrays so yeah you can add pictures together
    mask=mask+mask2

    #This line creats a structure in the shape of a 5x5 rectangle using cv2.MORPH_RECT.
    #The structure type can be changed to cv2.MORPH_ELLIPSE or cv2.MORPH_CROSS if you dont like rectangles... I used rectangles because they looked cleaner.
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(5,5))

    #These next two lines apply a close morphology and then an open morphology to the mask. 
    #other morphs are cv2.MORPH_GRADIENT, cv2.MORPH_TOPHAT, cv2.MORPH_BLACKHAT... no idea what those do, you can look into it
    #http://en.wikipedia.org/wiki/Opening_(morphology)
    #http://en.wikipedia.org/wiki/Closing_(morphology)
    #the morphologies uses the kernel struct to replace pixels. so with the current kernel struct pixels will be replaced with 5x5 rectangles.
    mask=cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask=cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    #A median blur of 3 is applied to smooth out the edges so the circle detection can work better, other blurs such as a Gaussian blur (cv2.GaussianBlur) can be used.
    #Median blur can only use odd numbers starting at 3 and makes the image more blurry at higher numbers, I'd keep it at 3 if I were you.
    mask=cv2.medianBlur(mask,3)

    #The part that detects the ball, yayyy!
    #HoughCircles can only accept a image that has one channel (black and white) so dont try plugging in a color image.
    #full documentation on houghcircles can be found in the opencv database but after playing around with it here's my simple explanation.
    #param1 image
    #param2 cv.CV_HOUGH_GRADIENT I dont know if there is anything else besides that
    #param3 macro sensitivity (big sensitivity). sensitivity meaning how sensitive is it to detecting circles, the docs say something else but this is my take on it after fiddling with it.
    #   increasing it from 1 will change the sensitivity greatly per each integer increment. 1 didnt even detect the ball but 2 did so I left it there
    #param4 minimum distance between two detected circles. I put this at 400 because I only want 1 circle detected in the image (only one ball)
    #param5 no idea, all I read was it has to be bigger than something, docs didnt really explain well what it did, nor did I mess with it so I left it at 100 which most people used.
    #param6 micro sensitivity, the bigger this is the less sensitive HoughCircles will be, the smaller this is the more sensitive it will be.
    #    This doesnt change the sensitivity as much as param3
    #param7 minimum radius, if a circle is smaller than this it will not be detected by houghCircles
    #param8 maximum radius, if a circle is bigger than this it will not be detected by houghCircles
    #all circles detected are returned as a multidimentional array
    circles=cv2.HoughCircles(mask,cv.CV_HOUGH_GRADIENT,2,400,param1=100,param2=30,minRadius=10,maxRadius=100)

    #if there are no circles skip
    if circles!=None:
        #for each circle in the circles array draw them on cimg
        #the first circle is the biggest circle and second is the next biggest and so on... i'm not sure though, thats what I read somewhere
        #anyway there shouldnt be more than one circle since I gave the min distance between circles as 400
        for i in circles[0,:]:
            #i[0] is x, i[1] is y, i[2] is radius
            #draws a "circle" on cimg at point (i[0],i[1]) with a radius of 2 pixels also with a color of (0,255,0) (green) and a thickness of 3 pixels.
            #so it looks like a point more than a circle, this marks the center
            cv2.circle(cimg,(i[0],i[1]),2,(0,255,0),3)
            #draws a circle on cimg that represents the detected circle with the color red 
            cv2.circle(cimg,(i[0],i[1]),i[2],(0,0,255),1)

        #TODO: return the circle array 

    #displays the mask in the mask window and cimg in the cimg window... purely for debugging purposes.
    #any image can be used here even the HSV image
    cv2.imshow('mask',mask)
    cv2.imshow('cimg',cimg)

#loops trackball so its a constant video feed rather than a single image.
while True:
    trackBall()
    #pauses the loop for 25ms, this allows the camera to keep up will the polling requests from the cpu, otherwise this would crash.
    #if you press esc the loop will break
    if cv2.waitKey(25)==27:
        break

#obvious what these do
cv2.destroyAllWindows()
camera.release()