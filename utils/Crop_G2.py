import cv2
import numpy as np
import time


cropping = False
x_start, y_start, x_end, y_end = 0, 0, 0, 0
j = 0
image = cv2.imread('G1.jpeg')
oriImage = image


def crop_img():
    
    global cropping, x_start, y_start, x_end, y_end, j, image, oriImage
    image = cv2.imread('G1.jpeg')
    
    '''
    # Sharpen the image
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    image = cv2.filter2D(image, -1, kernel)
    
    
    # Increase the brightness
    value = 30
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    lim = 255 - value
    v[v > lim] = 255
    v[v <= lim] += value
    hsv2 = cv2.merge((h, s, v))
    image = cv2.cvtColor(hsv2, cv2.COLOR_HSV2BGR)
    '''

    oriImage = image.copy()
    def mouse_crop(event, x, y, flags, param):
        # grab references to the global variables
        global x_start, y_start, x_end, y_end, cropping, j, image, oriImage
     
        # if the left mouse button was DOWN, start RECORDING
        # (x, y) coordinates and indicate that cropping is being
        if event == cv2.EVENT_LBUTTONDOWN:
            x_start, y_start, x_end, y_end = x, y, x, y
            cropping = True
            j = 1
     
        # Mouse is Moving
        elif event == cv2.EVENT_MOUSEMOVE:
            if cropping == True:
                x_end, y_end = x, y
     
        # if the left mouse button was released
        elif event == cv2.EVENT_LBUTTONUP:
            # record the ending (x, y) coordinates
            x_end, y_end = x, y
            cropping = False # cropping is finished
            j = 0
     
            refPoint = [(x_start, y_start), (x_end, y_end)]
     
            if len(refPoint) == 2: #when two points were found
                roi = oriImage[refPoint[0][1]:refPoint[1][1], refPoint[0][0]:refPoint[1][0]]
                cv2.imwrite('G1-crop.jpeg', roi)
                cv2.destroyAllWindows()
                print('Green image was cropped')
                j = 2
                
                return j
    
    cv2.namedWindow("image", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("image", 1640,1232)
    cv2.setMouseCallback("image", mouse_crop)

    while True:
        i = image.copy()
        if not cropping:
            cv2.imshow("image", image)
        elif cropping:
            cv2.rectangle(i, (x_start, y_start), (x_end, y_end), (255, 0, 0), 2)
            cv2.imshow("image", i)
        cv2.waitKey(1)
        if j == 2:
            cv2.destroyAllWindows()
            j = 0
            break
