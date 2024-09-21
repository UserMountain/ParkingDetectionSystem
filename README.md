In this project, I developed a website using the Flask framework to integrate a machine learning model with a drone camera. The primary goal is to create a system where drones automatically detect whether parked cars are correctly aligned. This technology can assist in efficient parking management.

The current system utilizes the YOLOv8 model for object detection and OCR Tesseract for reading text, such as vehicle license plates. While functional, there are several planned improvements, such as upgrading to more advanced drones and deploying a live server using a Raspberry Pi for real-time processing.

The images below showcase several pages of the system's interface:

### Dashboard Page
Provides an overview of the system’s performance and key metrics.

![Screenshot 2024-09-20 211811](https://github.com/user-attachments/assets/76899192-fa36-4380-92aa-7d1b57e9fb30)

![Screenshot 2024-09-20 211838](https://github.com/user-attachments/assets/17b87cbf-9892-4d47-a37d-794ff072ad7b)

### Live Stream Page
Displays the real-time video feed from the drone's camera.
![Screenshot 2024-09-20 211923](https://github.com/user-attachments/assets/b92acc65-9cbb-4857-a4e9-d665e7c71e64)

### Upload Page
Allows users to upload images or videos for analysis by the model.
![Screenshot 2024-09-20 212002](https://github.com/user-attachments/assets/74da81a5-4c77-4afc-afcd-ec26b6c002e1)

### Management Page
Enables users to manage the drone’s settings and review detection history.
![Screenshot 2024-09-20 212026](https://github.com/user-attachments/assets/baf4a6b3-7f1f-4e44-a2b0-115bdde74aa7)
