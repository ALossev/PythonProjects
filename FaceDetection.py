#Alek Lossev
# 4/22/24
import cv2
import mediapipe as mp
import tkinter as tk
import time
from PIL import Image, ImageTk
import random

class WelcomePage:
    def __init__(self, window):
        self.window = window
        self.window.title("Welcome to Face and Hand Detection App")

        self.label = tk.Label(window, text="Welcome to Face and Hand Detection App", font=("Helvetica", 16))
        self.label.pack(pady=20)

        self.btn_face_detection = tk.Button(window, text="Face Detection", width=15, command=self.start_face_detection)
        self.btn_face_detection.pack(pady=5)

        self.btn_hand_detection = tk.Button(window, text="Hand Detection", width=15, command=self.start_hand_detection)
        self.btn_hand_detection.pack(pady=5)

        self.quit_button = tk.Button(window, text="Quit", command=self.quit)
        self.quit_button.pack(pady=10)

        self.silly_filter_active = False

    def start_face_detection(self):
        self.window.destroy()
        root = tk.Tk()
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        app = FaceDetectionApp(root, "Face Detection", face_cascade, self.silly_filter_active)

    def start_hand_detection(self):
        self.window.destroy()
        root = tk.Tk()
        app = HandDetectionApp(root, "Hand Detection")

    def toggle_silly_filter(self):
        self.silly_filter_active = not self.silly_filter_active

    def quit(self):
        self.window.destroy()

class FaceDetectionApp:
    def __init__(self, window, window_title, face_cascade, silly_filter_active):
        self.window = window
        self.window.title(window_title)

        self.video_source = 0
        self.vid = cv2.VideoCapture(self.video_source)

        self.canvas = tk.Canvas(window, width=self.vid.get(cv2.CAP_PROP_FRAME_WIDTH), height=self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.canvas.pack()

        self.label_face = tk.Label(window, text="Faces Detected: 0")
        self.label_face.pack()

        self.btn_toggle = tk.Button(window, text="Toggle Detection", width=15, command=self.toggle_detection)
        self.btn_toggle.pack(pady=10)

        self.btn_return = tk.Button(window, text="Return", width=15, command=self.return_to_menu)
        self.btn_return.pack(pady=5)

        self.btn_quit = tk.Button(window, text="Quit", width=10, command=self.quit)
        self.btn_quit.pack(anchor=tk.CENTER, expand=True)

        self.delay = 10
        self.face_count = 0
        self.detect_faces = True  # Initialize to detect faces by default
        self.face_cascade = face_cascade
        self.silly_filter_active = silly_filter_active
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
                self.start_time = time.time()
                self.frame_count = 0

            # Convert frame to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if self.detect_faces:
                # Detect faces
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                self.face_count = len(faces)
                self.label_face.config(text="Faces Detected: {}".format(self.face_count))

                # Apply silly filter if active
                if self.silly_filter_active:
                    for (x, y, w, h) in faces:
                        self.apply_silly_filter(frame, x, y, w, h)

                # Draw rectangles around faces
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Display frame
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        self.window.after(self.delay, self.update)

    def apply_silly_filter(self, frame, x, y, w, h):
        # Randomly choose a silly accessory to draw
        accessory = random.choice(["hat", "glasses"])

        # Load the accessory image
        accessory_image = cv2.imread(f"{accessory}.png", -1)

        # Resize the accessory to fit the face
        accessory_height = h
        accessory_width = int(accessory_height * accessory_image.shape[1] / accessory_image.shape[0])
        accessory_image = cv2.resize(accessory_image, (accessory_width, accessory_height))

        # Calculate position to place the accessory
        x_offset = x + int(w / 2) - int(accessory_width / 2)
        y_offset = y - accessory_height // 2

        # Apply the accessory to the frame
        for c in range(0, 3):
            frame[y_offset:y_offset+accessory_height, x_offset:x_offset+accessory_width, c] = \
                accessory_image[:,:,c] * (accessory_image[:,:,3] / 255.0) + \
                frame[y_offset:y_offset+accessory_height, x_offset:x_offset+accessory_width, c] * \
                (1.0 - accessory_image[:,:,3] / 255.0)

    def toggle_detection(self):
        self.detect_faces = not self.detect_faces

    def return_to_menu(self):
        self.window.destroy()
        root = tk.Tk()
        welcome_page = WelcomePage(root)

    def quit(self):
        self.vid.release()
        self.window.destroy()

class HandDetectionApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        self.video_source = 0
        self.vid = cv2.VideoCapture(self.video_source)

        self.canvas = tk.Canvas(window, width=self.vid.get(cv2.CAP_PROP_FRAME_WIDTH), height=self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.canvas.pack()

        self.label_hand = tk.Label(window, text="Hands Detected: 0")
        self.label_hand.pack()

        self.btn_toggle = tk.Button(window, text="Toggle Detection", width=15, command=self.toggle_detection)
        self.btn_toggle.pack(pady=10)

        self.btn_return = tk.Button(window, text="Return", width=15, command=self.return_to_menu)
        self.btn_return.pack(pady=5)

        self.btn_quit = tk.Button(window, text="Quit", width=10, command=self.quit)
        self.btn_quit.pack(anchor=tk.CENTER, expand=True)

        self.delay = 10
        self.hand_count = 0
        self.detect_hands = True  # Initialize to detect hands by default
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
                self.start_time = time.time()
                self.frame_count = 0

            if self.detect_hands:
                # Detect hands
                results = self.hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                if results.multi_hand_landmarks:
                    self.hand_count = len(results.multi_hand_landmarks)
                    self.label_hand.config(text="Hands Detected: {}".format(self.hand_count))

                    for hand_landmarks in results.multi_hand_landmarks:
                        for id, lm in enumerate(hand_landmarks.landmark):
                            h, w, c = frame.shape
                            cx, cy = int(lm.x * w), int(lm.y * h)
                            cv2.circle(frame, (cx, cy), 10, (255, 0, 255), cv2.FILLED)

            # Display frame
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        self.window.after(self.delay, self.update)

    def toggle_detection(self):
        self.detect_hands = not self.detect_hands

    def return_to_menu(self):
        self.window.destroy()
        root = tk.Tk()
        welcome_page = WelcomePage(root)

    def quit(self):
        self.vid.release()
        self.window.destroy()

# Create a window and pass it to the WelcomePage class
root = tk.Tk()
welcome_page = WelcomePage(root)
root.mainloop()
