import cv2
import numpy as np

THRESHOLD_TAB = 40
THRESHOLD_HOVER = 75


def main():
    cap = cv2.VideoCapture(6)
    kernel = np.ones((10, 10), dtype=np.float64)
    while (True):
        ret, frame = cap.read()
        # frame = cv2.imread(
        # 'picture_transformation_testing/webcam_touchscreen.jpg')
        # print(frame)
        img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        contours = []
        # Threshold Tab
        ret, thresh_01 = cv2.threshold(
            img_gray, THRESHOLD_TAB, 255, cv2.THRESH_BINARY)
        # thresh = cv2.adaptiveThreshold(
        #     img_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
        contours, hierarchy = cv2.findContours(
            thresh_01, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            (x, y), radius = cv2.minEnclosingCircle(contour)
            if (radius > 80):
                continue
            # cv2.rectangle(thresh, (x,y), (x+w, y+h), (0,255,0), 2)
            center = (int(x), int(y))
            radius = int(radius)
            cv2.circle(thresh_01, center, radius, (0, 255, 0), 2)

        # Threshold hover
        ret, thresh = cv2.threshold(
            img_gray, THRESHOLD_HOVER, 255, cv2.THRESH_BINARY)
        # thresh = cv2.adaptiveThreshold(
        #     img_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
        contours, hierarchy = cv2.findContours(
            thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        hulls = []
        approximates = []
        # print(f"Anzahl Konturen: {len(contours)}")
        for contour in contours:
            # hull = cv2.convexHull(contour)
            # hulls.append(hull)
            epsilon = 0.005*cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            area = cv2.contourArea(approx)
            if area > 10000 and area < 15000:
                (x, y), radius = cv2.minEnclosingCircle(approx)
                # if (radius > 80) or (radius < 10):
                #     continue
                approximates.append(approx)
            # approximates.append(approx)

            # (x, y), radius = cv2.minEnclosingCircle(approx)
            # if (radius > 40):
            #     continue
            # if not cv2.isContourConvex(contour):
            #     continue
            # x, y, w, h = cv2.boundingRect(approx)
            cv2.rectangle(thresh, (x, y), (x+w, y+h), (0, 255, 0), 2)
            center = (int(x), int(y))
            radius = int(radius)
            # cv2.circle(thresh_01, center, radius, (0, 0, 255), 2)
        # print(f"Anzahl reduzierte Konturen: {len(approximates)}")
        for cont in approximates:
            x, y, w, h = cv2.boundingRect(cont)
            cv2.rectangle(thresh, (x, y), (x+w, y+h), (0, 255, 0), 2)
            print(cv2.contourArea(cont))

        dilation = cv2.dilate(thresh_01, kernel)

        closing = cv2.erode(dilation, kernel)

        img_contours = cv2.cvtColor(closing, cv2.COLOR_BGR2RGB)
        img_contours = cv2.drawContours(
            img_contours, approximates, -1, (255, 0, 0), 3)

        cv2.imshow('frame', img_contours)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # to quite the program
            break


def filter_contours(contours):
    filtered_contours = []
    for cont in contours:
        epsilon = 0.005*cv2.arcLength(cont, True)
        approx = cv2.approxPolyDP(cont, epsilon, True)
        area = cv2.contourArea(approx)
        if area > 10000 and area < 15000:
            (x, y), radius = cv2.minEnclosingCircle(approx)
            filtered_contours.append(approx)
    return filtered_contours


main()
