import cv2
from led import tree
import numpy as np
import time

def find_blue():
    cam = cv2.VideoCapture(1)

    do_it = False
    for i in range(60):
        for j in range(10):
            if do_it:
                tree.highlight_led(i)
            else:
                tree.highlight_led(None)
            do_it = not do_it
            ret = False
            while ret is False:
                ret, frame_on = cam.read()
                if ret is False:
                    print("RETRY")

            # Convert the image to the HSV color space
            hsv = cv2.cvtColor(frame_on, cv2.COLOR_BGR2HSV)

            # Define the range of blue color in HSV
            lower_blue = np.array([100, 100, 100])
            upper_blue = np.array([130, 255, 255])

            # Threshold the image to get only blue pixels
            mask = cv2.inRange(hsv, lower_blue, upper_blue)

            # Find contours in the mask
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Get the center coordinates of the contours
            centers = []
            for contour in contours:
                moments = cv2.moments(contour)
                if moments["m00"] != 0:
                    x = int(moments["m10"] / moments["m00"])
                    y = int(moments["m01"] / moments["m00"])
                    centers.append((x, y))

            for center in centers:
                cv2.circle(frame_on, center, 5, (0, 255, 0), -1)
            if do_it and len(centers) == 1:
                print(f"LED {i}: {centers[0]}")

            cv2.imshow("Image", frame_on)


            # Press 'q' to exit the loop
            if cv2.waitKey(1) == ord('q'):
                break


    # Release the capture and writer objects
    cam.release()
    # out.release()
    cv2.destroyAllWindows()


def find_led():
    # for i in range(10):
    #     time.sleep(1)
    #     tree.highlight_led(None)
    #     time.sleep(1)
    #     tree.highlight_led(5)
    # return

    # Open the default camera
    cam = cv2.VideoCapture(1)

    while True:
        tree.highlight_led(None)
        ret = False
        while ret is False:
            ret, frame_off = cam.read()
            print(f"ret: {ret}")
        tree.highlight_led(5)
        _, frame_on = cam.read()

        gray1 = cv2.cvtColor(frame_on, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame_off, cv2.COLOR_BGR2GRAY)

        # Compute the absolute difference between the two images
        diff = cv2.absdiff(gray1, gray2)

        # # Apply Gaussian blur to reduce noise
        # blurred = cv2.GaussianBlur(diff, (5, 5), 0)

        # # Use SimpleBlobDetector to detect blobs (dots)
        # params = cv2.SimpleBlobDetector_Params()
        # params.filterByArea = True
        # params.minArea = 3  # Adjust based on dot size
        # params.maxArea = 20 # Adjust based on dot size
        # params.filterByCircularity = False
        # params.minCircularity = 0.8  # Adjust based on dot shape

        # detector = cv2.SimpleBlobDetector_create(params)
        # keypoints = detector.detect(blurred)

        # # Draw circles around detected dots
        # for kp in keypoints:
        #     x, y = int(kp.pt[0]), int(kp.pt[1])
        #     r = int(kp.size / 2)
        #     cv2.circle(frame_off, (x, y), r, (0, 255, 0), 2)
        #     cv2.circle(diff, (x, y), r, (0, 255, 0), 2)

### CONTOUR VERSION
        # Find contours
        contours, _ = cv2.findContours(diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter contours based on size or shape
        for contour in contours:
            print(f"Contour: {contour}")
            if cv2.contourArea(contour) > 1:  # Adjust based on dot size
                # Draw a circle around the contour
                (x, y), radius = cv2.minEnclosingCircle(contour)
                center = (int(x), int(y))
                radius = int(radius)
                cv2.circle(frame_off, center, radius, (0, 255, 0), 2)
                cv2.circle(diff, center, radius, (255, 255, 255), 2)


        # Display the image
        cv2.imshow('Detected Dots', frame_off)
        cv2.imshow('DIff', diff)

        # Press 'q' to exit the loop
        if cv2.waitKey(1) == ord('q'):
            break


    # Release the capture and writer objects
    cam.release()
    # out.release()
    cv2.destroyAllWindows()