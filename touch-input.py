import cv2

THRESHOLD_TAB = 40
THRESHOLD_HOVER = 60

def main():
    cap = cv2.VideoCapture(2)
    while(True):
        ret, frame = cap.read()
        #print(frame)
        img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        contours = []
        #Threshold Tab
        #ret, thresh = cv2.threshold(img_gray, THRESHOLD_TAB, 255, cv2.THRESH_BINARY)
        thresh = cv2.adaptiveThreshold(img_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
        #contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            (x, y), radius = cv2.minEnclosingCircle(contour)
            if(radius > 40):
                continue
            #cv2.rectangle(thresh, (x,y), (x+w, y+h), (0,255,0), 2)
            center = (int(x), int(y))
            radius = int(radius)
            cv2.circle(thresh, center, radius, (0,255,0), 2)

        #Threshold hover
        #ret, thresh = cv2.threshold(img_gray, THRESHOLD_HOVER, 255, cv2.THRESH_BINARY)
        thresh = cv2.adaptiveThreshold(img_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
        #contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            (x, y), radius = cv2.minEnclosingCircle(contour)
            if(radius > 40):
                continue
            #cv2.rectangle(thresh, (x,y), (x+w, y+h), (0,255,0), 2)
            center = (int(x), int(y))
            radius = int(radius)
            cv2.circle(thresh, center, radius, (0,0,255), 2)


        img_contours = cv2.cvtColor(thresh, cv2.COLOR_BGR2RGB)
        img_contours = cv2.drawContours(img_contours, contours, -1, (255, 0, 0), 3)
        #cv2.drawContours(img_contours, contours, -1, (255, 0, 0), 3)
        cv2.imshow('frame', img_contours)
        if cv2.waitKey(1) & 0xFF == ord('q'): # to quite the program
            break

main()