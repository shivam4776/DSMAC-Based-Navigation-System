# DSMAC-Based-Navigation-System

Absolutely! Here's a clean and professional README template you can use for your GitHub repository. It includes sections for project overview, features, how to run the apps, and more:

---

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

- [ ] Add screenshots or videos of both apps here
- [ ] Include example plots of error analysis

## 📌 Future Enhancements

- Integration with real-time drone camera feed
- Support for additional matching models (e.g., Siamese Network)
- Dynamic weather and terrain simulation

