# Full Stack Portfolio & Capstone Setup

This project now integrates your **Honors Capstone** (AI Model & 3D Reconstruction) directly into your portfolio web app.

## 📂 Project Structure
- `/capstone`: Contains your original capstone files, models, and scripts.
- `/src`: Portfolio frontend (Vite/Vanilla JS).
- `bridge_server.py`: The Python Flask API that connects the portfolio GUI to your AI models.

## 🚀 How to Run the Full System

### 1. Setup the AI Backend
You'll need a Python environment with the required dependencies (torch, open3d, flask, etc.).

```bash
# It's recommended to create a new venv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install flask flask-cors torch torchvision opencv-python open3d Pillow scikit-learn
```

### 2. Start the AI Bridge Server
This server handles the image-to-3D processing using your `Depth-Anything-V2` models.

```bash
python3 bridge_server.py
```
*Note: The server runs on `http://localhost:5001`. Keep this terminal open.*

### 3. Start the Portfolio Frontend
In a new terminal, launch the web interface.

```bash
npm run dev
```
*Open `http://localhost:5173` in your browser.*

## 🧪 Testing the Integration
1.  Navigate to **Project Spotlight** -> **3D Generative Vision**.
2.  Click **Open Live Lab**.
3.  **Real Mode**: Click "Import Reference Image" and select a high-contrast photo. Click "Generate". The system will send the image to the Python backend, run your AI model, and return a real 3D mesh.
4.  **Static Mode**: Click "Load Honors Project Sample" to use the pre-rendered `kolobs_finger.stl` from your capstone results.

## 🛠️ Troubleshooting
- **Model Not Found**: If the server fails to load the model, ensure the checkpoint files are located in `capstone/Depth-Anything-V2/checkpoints/`.
- **Performance**: High-resolution images may take 5–10 seconds to process depending on your GPU/CPU.
- **Port Conflict**: If port 5001 is taken, you can change it at the bottom of `bridge_server.py`.
