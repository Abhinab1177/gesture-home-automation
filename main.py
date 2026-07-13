"""
Hand Gesture Home Automation

This project uses a Raspberry Pi Zero 2W and a Pi Camera Module to
detect hand gestures in real time. Based on the detected gesture,
GPIO pins control relay modules to switch a bulb and a fan ON or OFF.

Developed using:
- OpenCV
- CVZone
- MediaPipe
- Picamera2
- gpiozero
"""
import cv2
from cvzone.HandTrackingModule import HandDetector
from picamera2 import Picamera2
import time
from gpiozero import OutputDevice

# Initialize relay outputs (Active LOW)
bulb = OutputDevice(24, active_high=False, initial_value=False)   # GPIO24 → Bulb
fan = OutputDevice(23, active_high=False, initial_value=False)    # GPIO23 → Fan

# Configure Pi Camera
picam2 = Picamera2()
picam2.preview_configuration.main.size = (320, 240)
picam2.preview_configuration.main.format = "BGR888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()
time.sleep(2)

# Initialize hand detector
detector = HandDetector(maxHands=1, detectionCon=0.8)

font = cv2.FONT_HERSHEY_SIMPLEX
org = (10, 40)
fontScale = 0.8
color = (255, 255, 255)
thickness = 2

try:
    while True:
        # Capture and mirror camera frame
        img = picam2.capture_array()
        img = cv2.flip(img, 1)

        # Detect hand and identify raised fingers
        hands, _ = detector.findHands(img, draw=False)
        text = "Show Finger"

        if hands:
            hand = hands[0]
            fingers = detector.fingersUp(hand)

            # Gesture-based appliance control
            if fingers == [0, 1, 0, 0, 0]:        # Index Finger
                text = "Bulb ON"
                bulb.on()
            elif fingers == [0, 0, 1, 0, 0]:      # Middle Finger
                text = "Bulb OFF"
                bulb.off()
            elif fingers == [0, 0, 0, 1, 0]:      # Ring Finger
                text = "Fan ON"
                fan.on()
            elif fingers == [0, 0, 0, 0, 1]:      # Pinky Finger
                text = "Fan OFF"
                fan.off()
            elif fingers == [1, 1, 1, 1, 1]:      # All Fingers
                text = "All OFF"
                bulb.off()
                fan.off()

        # Display current action
        cv2.putText(img, text, org, font, fontScale, color, thickness, cv2.LINE_AA)
        cv2.imshow("Gesture Relay Control", img)

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        time.sleep(0.02)

finally:
    # Turn off relays and release resources
    bulb.off()
    fan.off()
    picam2.close()
    cv2.destroyAllWindows()