import numpy as np
import imutils
import cv2


class MotionDetector:
    def __init__(self, weight=0.5):
        self.weight = weight
        self.background = None

    def update(self, image):
        # initialize background frame
        if self.background is None:
            self.background = image.copy().astype("float")
            return

        # update the background frame
        cv2.accumulateWeighted(image, self.background, self.weight)

    def detect(self, image, area_threshold, threshold=13):
        # compute the absolute difference between the background frame and
        # and the image passed in, then threshold the delta image
        frame_diff = cv2.absdiff(self.background.astype("uint8"), image)
        frame_threshold = cv2.threshold(frame_diff, threshold, 255, cv2.THRESH_BINARY)[1]

        # erosions and dilations to remove small blobs
        frame_threshold = cv2.erode(frame_threshold, None, iterations=2)
        frame_threshold = cv2.dilate(frame_threshold, None, iterations=2)

        # find contours in the thresholded image
        cnts = cv2.findContours(frame_threshold.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        # set edges of bounding box to inf as edge of the image
        (minX, minY) = (np.inf, np.inf)
        (maxX, maxY) = (-np.inf, -np.inf)

        # if no contour found
        if len(cnts) == 0:
            return None
        # all contours found smaller than the area threshold
        elif all([True if cv2.contourArea(cnt) < area_threshold else False for cnt in cnts]):
            return None

        # contour found and looping through them
        for cnt in cnts:
            # filter out too small  contours
            if cv2.contourArea(cnt) < area_threshold:
                continue
            # update the minimum and maximum bounding box regions
            (x, y, w, h) = cv2.boundingRect(cnt)
            (minX, minY) = (min(minX, x), min(minY, y))
            (maxX, maxY) = (max(maxX, x + w), max(maxY, y + h))

        return (frame_threshold, (minX, minY, maxX, maxY))
