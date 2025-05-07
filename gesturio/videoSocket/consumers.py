import cv2
import numpy as np
from channels.generic.websocket import AsyncWebsocketConsumer
import torch
from yolov5 import YOLOv5
import os
from gesturio.settings import BASE_DIR

# device = '0' if torch.cuda.is_available() else 'cpu'
# print(f"Using device: {device}")

# model = YOLOv5(os.path.join(BASE_DIR, 'models/yolov5_alphabet_best.pt'), device=device)  # Replace with your model path

class VideoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            np_arr = np.frombuffer(bytes_data, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            # results = model.predict(img)
            
            # annotated_img = results.render()[0]
            
            # annotated_img = cv2.cvtColor(annotated_img, cv2.COLOR_RGB2BGR)
            _, processed_buffer = cv2.imencode('.jpg',img)
            processed_bytes = processed_buffer.tobytes()
            await self.send(bytes_data=processed_bytes)
