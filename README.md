# 🚀 DSMAC-Based Navigation System

A Windows application suite designed to simulate and evaluate aircraft or missile navigation in GPS-denied environments using vision-based techniques.

## 🛰️ Overview

In long-range navigation, traditional **Inertial Navigation Systems (INS)** tend to drift, and **GPS** signals are prone to spoofing or jamming. This project implements a **DSMAC (Digital Scene-Matching Area Correlation)** approach to enable robust and accurate navigation without relying on GPS.

The project consists of two core applications:

- **DCAS (Data Creation and Stitching App)**  
  Automates the collection of aerial image data from **Google Earth Pro** using `.kml` input files, and saves images with associated latitude-longitude coordinates for training.

- **Flight Test Simulator**  
  Simulates an aircraft flight over an input aerial map. Allows setting of **waypoints**, **altitude**, and **speed**, captures real-time images during flight, and tests image-matching models to evaluate navigation accuracy.

## 🔍 Features

- Simulated aircraft navigation with image capturing
- Aerial data scraping using Google Earth Pro and KML files
- Image matching using:
  - **ORB (Oriented FAST and Rotated BRIEF)**
  - **FAISS with ResNet-50 feature extraction**
- Error analysis with visualization of predicted vs actual coordinates

## 🛠️ Tech Stack

- Python (PyQt5 for GUI)
- OpenCV (for ORB)
- FAISS + PyTorch (ResNet-50)
- Google Earth Pro (for image collection)
- Matplotlib / Plotly (for visualizations)

## 🖥️ How to Run

1. **DCAS App**  
   - Open the app  
   - Load your `.kml` file  
   - Start the image scraping process  
   - Output: Aerial images + metadata (lat-long)

2. **Flight Test Simulator**  
   - Load an aerial map  
   - Set waypoints, speed, and altitude  
   - Start the navigation simulation  
   - Captured images will be saved automatically  
   - Load a trained model (ORB or FAISS)  
   - Run test and view accuracy results (min, max, avg error in meters)

## 📊 Sample Output

#### 1. DCAS Application
   --- 
   <img width="398" height="320" alt="1DCAS" src="https://github.com/user-attachments/assets/eea4accb-1d2a-46d2-b0f0-eee78976ec16" />
  
   <img width="397" height="319" alt="2DCAS" src="https://github.com/user-attachments/assets/fc6a5fae-9259-439d-9314-b4272a815963" />
  
   <img width="398" height="320" alt="3DCAS" src="https://github.com/user-attachments/assets/4e19e861-979d-4a24-9bea-2a3735d48a45" />
   
#### 2. Flight Test Simulator Application
  ---
   <img width="1920" height="1080" alt="Framework" src="https://github.com/user-attachments/assets/7c0eb7f9-e1c6-4c13-8e9c-148e59fac940" />

#### Results
<img width="1200" height="800" alt="graphFoggy" src="https://github.com/user-attachments/assets/6fa61a6a-ccd2-4193-845e-c79c66d254ea" />
<img width="1200" height="800" alt="graphLowLight" src="https://github.com/user-attachments/assets/87415ada-ede6-4649-8c5c-54be1b26e52f" />
<img width="1200" height="800" alt="graphRainy" src="https://github.com/user-attachments/assets/ac184772-8f9f-40f5-91aa-4ca47e96876c" />
<img width="1200" height="800" alt="graphSunny" src="https://github.com/user-attachments/assets/38fca936-070e-4d07-a5b0-33630c17f0de" />

## 📌 Future Enhancements

- Integration with real-time drone camera feed
- Support for additional matching models (e.g., Siamese Network)
- Dynamic weather and terrain simulation

