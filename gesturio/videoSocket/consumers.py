import base64
import cv2
import numpy as np
from channels.generic.websocket import AsyncWebsocketConsumer
import json

# Load the Haar Cascade classifier for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

class VideoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            # Decode JPEG bytes into image
            np_arr = np.frombuffer(bytes_data, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            # Convert to grayscale and detect faces
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            # Draw bounding boxes
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)

            # Encode processed image to JPEG
            _, processed_buffer = cv2.imencode('.jpg', img)
            processed_bytes = processed_buffer.tobytes()

            # Send the processed image as binary frame (Blob compatible)
            await self.send(bytes_data=processed_bytes)
