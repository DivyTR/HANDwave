import cv2
import numpy as np
import HandTrackingModule as htm
import time
import datetime
import autopy
import pyttsx3
import webbrowser

##########################
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)


def speak(audio):
    engine.say(audio)
    engine.runAndWait()


def wishMe():
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak("Good Morning")

    elif 12 <= hour < 18:
        speak("Good Afternoon")

    else:
        speak("Good Evening")
    speak("Welcome to your personal VR system. Activating Virtual Mouse")



wCam, hCam = 640, 480
frameR = 100  # Frame Reduction
smoothening = 7
#########################

pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
detector = htm.handDetector(maxHands=1)
wScr, hScr = autopy.screen.size()
hel=0
# Variable to store the time of the last speech command
last_speech_time = time.time()
# Variable to store the time when the last hand was detected
last_hand_detection_time = time.time()

finger_up_threshold = 0.9
while True:
    # 1. Find hand Landmarks
    if(hel==2):
        wishMe()
        speak("Show 5 fingers if you want to open YouTube and 0 for Google")
    hel+=1
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)
    # 2. Get the tip of the index and middle fingers

    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]

        # Update the last hand detection time
        last_hand_detection_time = time.time()

    # 3. Check which fingers are up
    fingers = detector.fingersUp()
    cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),
                  (255, 0, 255), 2)

    # Open YouTube logic
    if all(fingers):
        # Add a delay of 3 seconds between speech commands
        if time.time() - last_speech_time > 3:
            speak("Opening YouTube")
            webbrowser.open("https://www.youtube.com")  # Open YouTube in the default browser
            last_speech_time = time.time()  # Update the last speech time

    # Open Google logic
    elif all(not finger for finger in fingers) and lmList:
        # Check if no fingers are up and a hand is detected
        # Add a delay of 3 seconds between speech commands
        if time.time() - last_speech_time > 3:
            speak("Opening Google")
            webbrowser.open("https://www.google.com")  # Open Google in the default browser
            last_speech_time = time.time()  # Update the last speech time

    # Moving Mode
    if fingers[1] == 1 and fingers[2] == 0:
        # 5. Convert Coordinates
        x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
        y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
        # 6. Smoothen Values
        clocX = plocX + (x3 - plocX) / smoothening
        clocY = plocY + (y3 - plocY) / smoothening

        # 7. Move Mouse
        autopy.mouse.move(wScr - clocX, clocY)
        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        plocX, plocY = clocX, clocY

    # Clicking Mode
    if fingers[1] == 1 and fingers[2] == 1:
        length, img, lineInfo = detector.findDistance(8, 12, img)
        # 10. Click mouse if distance short
        if length < 40:
            cv2.circle(img, (lineInfo[4], lineInfo[5]),
                       15, (0, 255, 0), cv2.FILLED)
            autopy.mouse.click()

    # Frame Rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                (255, 0, 0), 3)
    # Display
    cv2.imshow("Image", img)
    cv2.waitKey(1)

    # Check if no hand is detected for 5 seconds
    if time.time() - last_hand_detection_time > 20:
        speak("Goodbye")
        break

# Release the video capture and close all windows
cap.release()
cv2.destroyAllWindows()