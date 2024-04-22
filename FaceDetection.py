#Alek Lossev
#04/22/24

import cv2
import mediapipe as mp
import tkinter as tk
import time
from PIL import Image, ImageTk

class WelcomePage:
    def __init__(self, window):
        self.window = window
        self.window.title("Welcome to Face and Hand Detection App")

        self.label = tk.Label(window, text="Welcome to Face and Hand Detection App", font=("Helvetica", 16))
        self.label.pack(pady=20)

        self.start_button = tk.Button(window, text="Start Detection", command=self.start_detection)
        self.start_button.pack(pady=10)

        self.quit_button = tk.Button(window, text="Quit", command=self.quit)
        self.quit_button.pack(pady=10)

    def start_detection(self):
        self.window.destroy()
        root = tk.Tk()
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        app = FaceHandDetectionApp(root, "Face and Hand Detection", face_cascade)

    def quit(self):
        self.window.destroy()

class FaceHandDetectionApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        self.video_source = 0
        self.vid = cv2.VideoCapture(self.video_source)

        self.canvas = tk.Canvas(window, width=self.vid.get(cv2.CAP_PROP_FRAME_WIDTH), height=self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.canvas.pack()
         self.label_face = tk.Label(window, text="Faces Detected: 0")
        self.label_face.pack()

        self.label_hand = tk.Label(window, text="Hands Detected: 0")
        self.label_hand.pack()
        
        self.label_fps = tk.Label(window, text= "FPS: 0")
        self.label_fps.pack()

        self.btn_quit = tk.Button(window, text="Quit", width=10, command=self.quit)
        self.btn_quit.pack(anchor=tk.CENTER, expand=True)

        self.delay = 10
        self.face_count = 0
        self.hand_count = 0
        self.face_cascade = face_cascade
        self.hands = mp.solutions.hands.Hands()
        self.start_time = time.time()
        self.frame_count = 0
        self.update()

        self.window.mainloop()

    def update(self):
        ret, frame = self.vid.read()
        self.frame_count += 1
         if ret:
            # Calculate FPS
            elapsed_time = time.time() - self.start_time
            if elapsed_time > 1:
                fps = self.frame_count / elapsed_time
                self.label_fps.config(text="FPS: {:.2f}".format(fps))
                self.start_time = time.time()
                self.frame_count = 0
       
            # Convert frame to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            self.face_count = len(faces)
            self.label_face.config(text="Faces Detected: {}".format(self.face_count))

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

# Create a window and pass it to the WelcomePage class
root = tk.Tk()
welcome_page = WelcomePage(root)
root.mainloop()
