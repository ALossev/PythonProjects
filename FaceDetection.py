#Alek Lossev
#04/05/24

import cv2
import mediapipe as mp
import tkinter as tk
from PIL import Image, ImageTk

# Initialize Mediapipe hands module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Initialize Haar cascade classifier for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

class FaceHandDetectionApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        self.video_source = 0
        self.vid = cv2.VideoCapture(self.video_source)

        self.canvas = tk.Canvas(window, width=self.vid.get(cv2.CAP_PROP_FRAME_WIDTH), height=self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.canvas.pack()

        self.btn_quit = tk.Button(window, text="Quit", width=10, command=self.quit)
        self.btn_quit.pack(anchor=tk.CENTER, expand=True)

        self.delay = 10
        self.update()

        self.window.mainloop()

    def update(self):
        ret, frame = self.vid.read()

        if ret:
            # Convert frame to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            # Detect hands
            results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    for id, lm in enumerate(hand_landmarks.landmark):
                        h, w, c = frame.shape
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        cv2.circle(frame, (cx, cy), 10, (255, 0, 255), cv2.FILLED)

            # Draw rectangles around faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        self.window.after(self.delay, self.update)

    def quit(self):
        self.vid.release()
        self.window.destroy()

# Create a window and pass it to the FaceHandDetectionApp class
root = tk.Tk()
app = FaceHandDetectionApp(root, "Face and Hand Detection")
