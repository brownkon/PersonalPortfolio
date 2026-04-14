# Height Map Generator

A React web application that generates height maps and 3D STL files from images using the Depth-Anything-V2 AI model. Perfect for creating 3D printable terrain models from photographs.

## Features

- 🖼️ **Image Upload**: Drag & drop or click to upload images
- 🗺️ **Height Map Generation**: AI-powered depth estimation using Depth-Anything-V2
- 🎯 **3D STL Export**: Convert height maps to 3D printable STL files
- 👁️ **3D Preview**: Interactive 3D preview using Three.js
- 📥 **Download**: Download both height maps and STL files
- 🎨 **Modern UI**: Beautiful, responsive interface with real-time processing status

## Project Structure

```
Capstone/
├── react-app/                 # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── App.js           # Main app component
│   │   └── index.js         # App entry point
│   └── package.json
├── backend/                  # Flask API backend
│   ├── app.py               # Main Flask application
│   └── requirements.txt     # Python dependencies
├── Depth-Anything-V2/       # AI model (existing)
└── test-pics/               # Test images (existing)
```

## Prerequisites

- Python 3.8+
- Node.js 16+
- Depth-Anything-V2 model checkpoint (already in your project)
- CUDA/MPS support (optional, for GPU acceleration)

## Installation

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Frontend Setup

```bash
# Navigate to React app directory
cd react-app

# Install dependencies
npm install
```

## Usage

### 1. Start the Backend

```bash
# From the backend directory
cd backend
source venv/bin/activate  # or activate on Windows
python app.py
```

The Flask API will start on `http://localhost:5000`

### 2. Start the Frontend

```bash
# From the react-app directory
cd react-app
npm start
```

The React app will open in your browser at `http://localhost:3000`

### 3. Generate Height Maps and STLs

1. **Upload Image**: Drag and drop an image or click to select one
2. **Process**: Click "Generate Height Map & STL" to start processing
3. **Preview**: View the generated height map and 3D STL preview
4. **Download**: Download the height map (PNG) and STL file

## API Endpoints

- `POST /api/generate-heightmap` - Generate height map from image
- `POST /api/generate-stl` - Generate STL file from image
- `GET /api/health` - Health check endpoint

## Technical Details

### Frontend
- **React 18** with modern hooks
- **Three.js** for 3D STL preview
- **Axios** for API communication
- **Responsive design** with CSS Grid and Flexbox

### Backend
- **Flask** web framework
- **Depth-Anything-V2** AI model for depth estimation
- **PIL/Pillow** for image processing
- **NumPy** for numerical operations
- **CORS** enabled for frontend communication

### 3D Preview Features
- Interactive camera controls (orbit, zoom, pan)
- Proper lighting and materials
- Automatic model centering and scaling
- Responsive canvas sizing

## Customization

### Adjusting STL Parameters

In `backend/app.py`, you can modify the STL generation parameters:

```python
heightmap_to_stl(depth_normalized, tmp_file.name, 
                 scale_factor=0.5,    # Height intensity
                 base_height=1.0)     # Base thickness
```

### Model Configuration

The Depth-Anything-V2 model uses the 'vitl' (Vision Transformer Large) configuration by default. You can modify this in the `setup_model()` function.

## Troubleshooting

### Common Issues

1. **Model Loading Error**: Ensure the Depth-Anything-V2 checkpoint is in the correct location
2. **CUDA/MPS Issues**: The app will fall back to CPU if GPU acceleration fails
3. **Memory Issues**: Large images may require more RAM/VRAM

### Performance Tips

- Use GPU acceleration when available (CUDA/MPS)
- Process images at reasonable resolutions (1024x1024 or smaller)
- Close other applications to free up memory

### Testing

```bash
# Frontend tests
cd react-app
npm test

# Backend tests (if you add them)
cd backend
python -m pytest
```

## License

This project uses the existing Depth-Anything-V2 model and your existing scripts. The web interface is built on top of these existing tools.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application.

---

**Note**: This application requires the Depth-Anything-V2 model checkpoint to function. Ensure the model is properly set up before running the application.
