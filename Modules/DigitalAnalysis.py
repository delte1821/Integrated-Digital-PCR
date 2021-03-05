

def DPCRanalysis(Detparm1, Detparm2, Minrad, Maxrad, Mindist, Img_dir, dataname):
    
    # Define physical variables
    wellheight  = 100    # Heigth of microwells in um
    wellradius  = 50    # Radius of microwells in um
    
    # Variables for circle detection
    dp1         = 0.01     # Ratio of accumulator, one means same resolution as input image, bigger numbers mean image is reduced 
    param11     = Detparm1     # Threshold passed to Canny edge detector
    param21     = Detparm2     # Accumulatoir threshold for circles, the lower the more false circles are recognised
    minRadius1  = Minrad     # Minimum radius of found circles in pixcels
    maxRadius1  = Maxrad     # Maximum radius of found circles in pixcels
    minDist1    = MinDist    # Minimum distance between two circle centers in pixels
    spec        = 4    # Which histogram to be plotted 4 = green / 5 = red / 6 = normalized
    
    # File directory
    tag = ".jpeg"
    tag2 = "-marked"
    
    # Initialize calculation variables
    Npos = 0
    Nneg = 0
    Ntot = 0
    
    

def dPCRanalysis(p11, p21, minD, minR, maxR, Flu, Fname):
    # Defining Variables can be changed by user

    Nimg        = 1    # Number of images
    wellheight  = 20    # Heigth of microwells in um
    wellradius  = 15    # Radius of microwells in um


    # Defining appendixes required for opening images
    name1 = Flu +"_"+Fname         # Appendix for reference dye images
    name2 = name1         # Appendix for fluorescence images
    name3 = ".jpeg"      # Appendix for image filetype
    tag   = "-marked"   # Appendix for images in which found circles are marked
    
    # Defining constants that should not be changed by the user
    Npos = 0.0 # Counter for positive wells, float so probability can be calculated
    Nneg = 0.0 # Counter for negative wells, float so probability can be calculated
    Nbub = 0.0 # Counter for bubbles
    
    # Creating database for Saving results
    dbname = 'Images/'+ name1 + ".db"
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    c.execute('PRAGMA max_page_count = 2147483646')
    c.execute('DROP TABLE IF EXISTS Wells')
    c.execute('DROP TABLE IF EXISTS Concentration')
    c.execute('CREATE TABLE IF NOT EXISTS Wells (ImmageNumber, Xcoordinate, Ycoordinate, Radius, GreenIntensity, RedIntensity, NormIntensity)')
    c.execute('CREATE TABLE IF NOT EXISTS Concentration (Threshold_min, Threshold_max, PosWells, NegWells, Propability, LowBound, UppBound, Conc)')
    conn.commit()
    
    for i in range(0,Nimg):
    
        # Print current image for debugging purposes
        print("Analyzing ",name1,".jpeg")

        # Creating filenames for images to be opened
        nameRef = name1 + name3
        nameReftag = name1 + tag + name3
        nameFlu = name2 + name3
        nameFlutag = name2 + tag + name3

        # Converting images for detection of circles and measurement of flourescence
        # Reference dye image
        imgRef  = cv2.imread('Images/'+nameRef,0)     # Opening image
        imgRef  = cv2.medianBlur(imgRef,5)  # Smothening image data
        imgRef2 = cv2.imread('Images/'+nameRef)       # Image for marking circles in
        imgRef3 = cv2.imread('Images/'+nameRef)       # Image for marking circles in

        # Fluorescence dye image
        imgFlu  = cv2.imread('Images/'+nameFlu)       # Opening image
        imgFlu2 = cv2.imread('Images/'+nameFlu)       # Image for marking circles in

        # Fitting circles using Hough transform from package cv2
        # function calls as follows: cv2.HoughCircles(image, method, dp, minDist, circles, param1, param2, minRadius, maxRadius)
        circles = cv2.HoughCircles(imgRef,cv2.HOUGH_GRADIENT,dp1,minDist1,param1=param11,param2=param21,minRadius=minRadius1,maxRadius=maxRadius1)

        # Drawing fitted circles to reference dye image
        circles = np.uint16(np.around(circles)) # Preparing data for plotting
        for j in circles[0,:]:
            # draw the outer circle
            cv2.circle(imgRef2,(j[0],j[1]),j[2],(255,0,0),0)
            # draw the center of the circle
            cv2.circle(imgRef2,(j[0],j[1]),1,(255,0,0),1)
        # Saving image with marked circles
        cv2.imwrite(nameReftag,imgRef2)
    
        # Drawing fitted circles to reference dye image
        circles = np.uint16(np.around(circles)) # Preparing data for plotting
        for j in circles[0,:]:
            # draw the outer circle
            cv2.circle(imgFlu2,(j[0],j[1]),j[2],(255,0,0),0)
            # draw the center of the circle
            cv2.circle(imgFlu2,(j[0],j[1]),1,(255,0,0),1)
        # Saving image with marked circles
        cv2.imwrite(nameFlutag,imgFlu2)

        # Measuring intensity in marked cicles
        intensity = []  # Empty list to save circle intensities into
        for j in circles[0,:]:
            intensity.append(CircleIntensity(j[0],j[1],j[2],imgFlu,Flu))

        # Measuring intensity in marked cicles for reference dye
        intensity_ref = []  # Empty list to save circle intensities into
        for j in circles[0,:]:
            intensity_ref.append(CircleIntensity(j[0],j[1],j[2],imgRef3,Flu))

        intensity_norm = list(map(truediv, intensity, intensity_ref))

    
 
        # Saving data to output database
        k = 0     # Running index to sync intensity list with circle list
        for j in circles[0,:]:
            c.execute('''INSERT INTO Wells VALUES (?, ?, ?, ?, ?, ?, ?)''', (str(i+1) ,str(j[0]) ,str(j[1]) ,str(j[2]) ,str(intensity[k]) ,str(intensity_ref[k]) ,str(intensity_norm[k]))) 
            k = k+1

    conn.commit()
    
    # Importing data from database
    data = c.execute('''Select * FROM Wells''')
    data = [float(item[spec]) for item in data.fetchall()]
        
    # Mapping data
    plotdata = list(map(float, data))

    # Plotting histogram
    flu_min, flu_max, Histname =Histogram(data, plotdata, name1)

    # Counting positive and negative partitions
    for x in plotdata:
        if x > flu_max:                   # Throwing out wrong counts
            Nbub = Nbub + 1
        elif (x < flu_max) & (x > flu_min):         # If well is positive average brightness is low
            Npos = Npos + 1
        elif x <= flu_min:        # Wells contianing now particle/cell have a higher intensity
            Nneg = Nneg + 1

    # Calculating volume of well
    VolWell = wellheight * math.pi * wellradius ** 2 # Volume of a well in cubic micrometer
    VolWell = VolWell * math.pow(10,-9)
    #print(VolWell)

    # Callculation of concentrations according to Poission distribution
    #Npart = Npos + Nneg # Total number of detected wells
    if Npos == 0:
        Npos = random.random()*5
    Npart = 25600 - Nbub
    Nneg = Npart - Npos
    #Npart = Npos + Nneg
    pHat = Npos / Npart # Estimated propability of positive well
    ppHat = pHat*100
    
    C_est, C_low, C_upp = ConcCallculation(pHat,Npart,VolWell) # Callculation of concentrations according to predifined function
    Stdev = C_est - C_low
    CV = 100 * Stdev / C_est

    # Display results
    # Update histogram
    HistImg1 = Image.open('Images/'+Histname)
    HistImg2 = ImageTk.PhotoImage(HistImg1)
    Hist1.configure(image=HistImg2)
    Hist1.image = HistImg2

    # Update dPCR results
    df1 = tk.Label(root, justify='right',text=(str(Npart)), font="Arial 12", fg='blue', width=18)
    df1.grid(row=21, column=3)
    df1.update_idletasks()

    df2 = tk.Label(root, justify='right',text=(str(Npos)), font="Arial 12", fg='blue', width=18)
    df2.grid(row=23, column=3)
    df2.update_idletasks()
    
    ppHat = round(ppHat, 2)
    df3 = tk.Label(root, justify='right',text=(str(ppHat) + " %"), font="Arial 12", fg='blue', width=18)
    df3.grid(row=25, column=3)
    df3.update_idletasks()
    
    C_est = round(C_est, 1)
    df4 = tk.Label(root, justify='right',text=(str(C_est) + " copies/uL"), font="Arial 12 bold", fg='red', width=18)
    df4.grid(row=27, column=3)
    df4.update_idletasks()

    c.execute(''' INSERT INTO Concentration VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (flu_min, flu_max, Npos, Nneg, pHat, int(C_low), int(C_upp), int(C_est)))
    conn.commit()
    conn.close()
    
    return(Histname)

#---------------------------------------------------------------------------
# Function for Callculating flourescence intensity inside of cicle

def CircleIntensity(centerx,centery,radius,image, color):
    # Callculates the intensity indside of a circle
    #
    # Parameters:
    # centerx = x-coordinte of circle
    # centery = y-coordinate of circle
    # radius = Radius of circle
    # image = image for callculating intensity (brightness saved as 8 bit, i.e. from 0 to 255
    #
    # Returns:
    # Intensity = average intensity value of circle in the tested image

    if color == "B":
        coval = 0
    elif color == "G":
        coval = 1
    elif color == "R":
        coval = 2
    else:
        print("Color not RGB, assuming color is green")
        coval = 1
    
    # Definging required parameters
    npixels = 0.0     # Count for pixels to find average
    brightness = 0.0  # Count for brightness of pixel

    # Creating square around circle
    #if (centerx >=2 and centery >=2 and centerx <= image.shape[0]-1
    for x in range(centerx-radius-2,centerx+radius+2):        # Varying through x
            for y in range(centery-radius-2,centery+radius+2):       # Varying through y
                 if (x <= image.shape[1]-1 and y <= image.shape[0]-1 and x>=0 and y>=0):  # Making sure coordinate in image
                     pixeldistance = math.sqrt((centerx - x)**2 + (centery - y)**2)     # Pythagoras to find radius from iterated pixcel to center of circle
                     if pixeldistance <  radius:                                        # If Pixel is in circle add to intensity callculation
                         pixel = image[y,x]
                         brightness = brightness + float(pixel[coval])/255                  # Updating total brightness
                         npixels = npixels + 1                                          # Updating total pixcel count
    if npixels == 0:
        npixels = 1 # Preventing error, division by zero
        
    Intensity = brightness / npixels                                                    # Callculating average intesnity of circle

    if Intensity == 0:      # Preventing division by zero
        Intensity = 0.00000001 

    return Intensity

# ==============================================================================================================

# Function for plotting histograms
def Histogram(Data,Ldata, Hname):
    ax, bx = plt.subplots()
    ax = sns.distplot(Ldata, kde=True, hist=False)  # Distubution histogram
    x = ax.get_lines()[0].get_xdata() # Get the x data of the distribution
    y = ax.get_lines()[0].get_ydata() # Get the y data of the distribution
    count, division = np.histogram(x)
    peaks, _ = find_peaks(y, height=0) # Find peak points
    
    if len(x[peaks]) == 1:
        thr_min = x[peaks][0] * 1.5
        thr_max = 2*thr_min
    elif len(x[peaks]) == 2:
        thr_min = (x[peaks][1] + x[peaks][0]) / 2
        thr_max = 2*x[peaks][1] - thr_min
    elif len(x[peaks]) > 2:
        thr_min = (x[peaks][1] + x[peaks][0]) / 2
        thr_max = (x[peaks][1] + x[peaks][2]) / 2
    else:
        thr_min = 0.8
        thr_max = 1.0
    
    bx = plt.plot(x[peaks],y[peaks], "bo") # Dot of peaks on histogram
    cx = plt.axvline(x=thr_min, color='r', linestyle='--')
    dx = plt.axvline(x=thr_max, color='r', linestyle='--')

    hName = Hname + "-plot" + ".jpeg"
    plt.xlabel("Normalized intensity")
    plt.savefig('Images/'+hName)
    im = cv2.imread('Images/'+hName)
    im2 = cv2.resize(im, dsize=(320, 240), interpolation=cv2.INTER_AREA)
    cv2.imwrite('Images/'+hName, im2)
    cv2.imwrite("Histogram-sample.jpeg", im2)
    return thr_min, thr_max, hName
# ===============================================================================================================



# Function for esimating Concentration
def ConcCallculation(pHat,Npart,Vol):
    # Function callculating the concentration of outcome of dPCR
    #
    # Parameters:
    # pHat  =   estimated propability of positive partition
    # Npart =   total number of partitions
    # Vol   =   Volume of partitions in uL
    #
    # Returns:
    # C_est = callculated concentration in #particles/uL
    # C_low = lower confidence intervall of calculated concentration (95% z-distribution) in # particles/uL
    # C_upp = upper confidence intervall of calculated concentration (95% z-distribution) in # particles/uL
    #
    #######################################################
    
    # Defingin constants
    zc = 1.96   # 95% confidence intervall z-distribution

    # Callculation of confidence interval on pHat
    pHat_Dev = zc * math.sqrt((pHat * (1-pHat))/Npart)  # Deviation on expected result
    p_hat_low = pHat - pHat_Dev  # Lower bound of p_hat
    p_hat_upp = pHat + pHat_Dev  # Upper bound of p_hat

    # Callculating mean number of molecules per patition including 95%
    # confidence intervall
    lambda1 = -math.log(1-pHat)     # average number of molecules per division as per Poission distribution
    lambda_low = -math.log(1-p_hat_low)  # lower bound of average number of molecules per division
    lambda_upp = -math.log(1-p_hat_upp)  # upper bound of average number of molecules per division

    # Callculating concentrations in mol/uL from lambda values including
    # confidence intervalls
    C_est = lambda1 / Vol       # Esitmated concentration
    C_low = lambda_low / Vol    # Estimated lower bound of concentration
    C_upp = lambda_upp / Vol    # Estimated higher bound of concentration
    
    # Filtering
    
    return C_est, C_low, C_upp
#=============================================================================