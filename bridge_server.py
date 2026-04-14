import os
import sys
import torch
import numpy as np
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from PIL import Image
import cv2
import open3d as o3d
import tempfile
import uuid

# Add capstone to path
sys.path.append(os.path.join(os.getcwd(), 'capstone_project/Depth-Anything-V2'))
sys.path.append(os.path.join(os.getcwd(), 'capstone_project/Segmentation'))
from depth_anything_v2.dpt import DepthAnythingV2
from texture_to_3d import create_tactile_heightmap, heightmap_to_stl

app = Flask(__name__)
CORS(app)

# --- Configuration ---
DEVICE = 'cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu'
# Using 'vitl' as it is the checkpoint found in your capstone folder
ENCODER = 'vitl' 
MODEL_CONFIG = {'encoder': ENCODER, 'features': 256, 'out_channels': [256, 512, 1024, 1024]}
CHECKPOINT_PATH = f'capstone_project/Depth-Anything-V2/checkpoints/depth_anything_v2_{ENCODER}.pth'

model = None

def load_model():
    global model
    if model is None:
        model = DepthAnythingV2(**MODEL_CONFIG)
        if os.path.exists(CHECKPOINT_PATH):
            model.load_state_dict(torch.load(CHECKPOINT_PATH, map_location='cpu'))
            model = model.to(DEVICE).eval()

@app.route('/api/generate', methods=['POST'])
def generate():
    load_model()
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    file = request.files['image']
    
    # Save temp input for segmentation script
    temp_dir = tempfile.gettempdir()
    input_path = os.path.join(temp_dir, f"in_{uuid.uuid4().hex}.png")
    file.save(input_path)
    
    # 1. Infer Depth (we use the model to create a heightmap first, as their script expects it)
    img = Image.open(input_path).convert('RGB')
    depth = model.infer_image(np.array(img))
    
    # Save depth map for the segmentation script to use
    depth_path = os.path.join(temp_dir, f"depth_{uuid.uuid4().hex}.png")
    cv2.imwrite(depth_path, (depth / depth.max() * 255).astype(np.uint8))
    
    # 2. Run the Real Capstone Segmentation Logic
    print("🎨 Applying Color Segmentation & Tactile Textures...")
    combined_heightmap, segmented, kmeans, labels = create_tactile_heightmap(
        input_path,
        num_segments=10,
        depth_map_path=depth_path
    )
    
    # 3. Convert to STL using their optimized exporter
    output_filename = f"gen_{uuid.uuid4().hex}.stl"
    output_path = os.path.join(temp_dir, output_filename)
    
    # Using their heightmap_to_stl function
    heightmap_to_stl(combined_heightmap, output_path, scale_factor=0.3, base_height=0.05)
    
    print(f"✅ Real Textured Mesh Generated: {output_path}")
    return send_file(output_path, as_attachment=True, download_name="textured_model.stl")

if __name__ == '__main__':
    app.run(port=5001, debug=True)
