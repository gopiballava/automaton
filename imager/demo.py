import cv2
from led import tree

def demo_loop():

    # Open the default camera
    cam = cv2.VideoCapture(0)

    # Get the default frame width and height
    frame_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (frame_width, frame_height))

    # creating object 
    # fgbg1 = cv2.bgsegm.createBackgroundSubtractorMOG();    
    fgbg2 = cv2.createBackgroundSubtractorMOG2(); 
    # fgbg3 = cv2.bgsegm.createBackgroundSubtractorGMG(); 
    
    _, bg_frame = cam.read()

    while True:
        ret = False
        while ret == False:
            ret, frame = cam.read()
            print(f"ret: {ret}")
        # Write the frame to the output file
        out.write(frame)

        # Convert the images to grayscale
        gray1 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(bg_frame, cv2.COLOR_BGR2GRAY)

        # Compute the absolute difference between the two images
        diff = cv2.absdiff(gray1, gray2)

        # Apply thresholding to highlight the differences
        _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)


        # Display the captured frame
        # cv2.imshow('Camera', frame)
        # fgmask = fgbg2.apply(frame) 
    
        # cv2.imshow('fgmask', fgmask) 
        cv2.imshow('diff', diff)
        # cv2.imshow('frame',frame) 

        # Press 'q' to exit the loop
        if cv2.waitKey(1) == ord('q'):
            break
        if cv2.waitKey(1) == ord('b'):
            print("DIFF!")
            _, bg_frame = cam.read()


        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(diff, (5, 5), 0)

        # Use SimpleBlobDetector to detect blobs (dots)
        params = cv2.SimpleBlobDetector_Params()
        params.filterByArea = True
        params.minArea = 10  # Adjust based on dot size
        params.maxArea = 100 # Adjust based on dot size
        params.filterByCircularity = True
        params.minCircularity = 0.8  # Adjust based on dot shape

        detector = cv2.SimpleBlobDetector_create(params)
        keypoints = detector.detect(blurred)

        # Draw circles around detected dots
        for kp in keypoints:
            x, y = int(kp.pt[0]), int(kp.pt[1])
            r = int(kp.size / 2)
            cv2.circle(frame, (x, y), r, (0, 255, 0), 2)

        # Display the image
        cv2.imshow('Detected Dots', frame)


    # Release the capture and writer objects
    cam.release()
    # out.release()
    cv2.destroyAllWindows()