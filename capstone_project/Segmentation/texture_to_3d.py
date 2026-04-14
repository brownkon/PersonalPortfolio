

#!/usr/bin/env python3
"""
Texture to 3D - Convert texture patterns into tactile 3D height variations
"""

import numpy as np
import cv2
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for threading compatibility
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import os
import struct
default_base_height = 0.05


def calculate_intensity_based_params(rgb_color, texture_type):
    """Calculate texture parameters based on color intensity for more nuanced textures"""
    r, g, b = rgb_color
    brightness = (r + g + b) / 3.0  # 0-255 range
    intensity = brightness / 255.0  # Normalize to 0-1
    
    params = {}
    
    if texture_type == 'vertical_lines':
        # Darker = closer lines (more intense texture) - much wider spacing for smaller files
        params['spacing'] = max(12, int(20 - intensity * 8))  # 12-20 range (much wider)
        params['thickness'] = max(2, int(2 + intensity * 2))  # 2-4 range (thicker lines)
        
    elif texture_type == 'horizontal_waves':
        # Darker = tighter waves
        params['frequency'] = 0.05 + intensity * 0.1  # 0.05-0.15 range
        params['amplitude'] = int(8 + intensity * 8)  # 8-16 range
        params['wave_spacing'] = max(4, int(10 - intensity * 6))  # 4-10 range
        params['line_thickness'] = max(1, int(1 + intensity * 2))  # 1-3 range
        
    elif texture_type == 'vertical_waves':
        # Darker = more intense waves, constant line thickness - much wider spacing for smaller files
        params['frequency'] = 0.02 + (1 - intensity) * 0.06  # 0.02-0.08 range (much wider waves)
        params['amplitude'] = int(8 + (1 - intensity) * 12)  # 8-20 range (higher for darker)
        params['wave_spacing'] = max(16, int(16 + intensity * 8))  # 16-24 range (much wider spacing)
        params['line_thickness'] = 2  # Thicker lines for better visibility
        
    elif texture_type == 'dots':
        # Darker = more dots, smaller spacing
        params['dot_size'] = max(1, int(2 + intensity * 3))  # 2-5 range
        params['dot_spacing'] = max(6, int(15 - intensity * 8))  # 6-15 range
        

    elif texture_type == 'broken_horizontal_lines':
        # Darker = more broken lines, closer spacing, smaller gaps - much wider spacing for smaller files
        # Lighter = fewer lines, wider spacing, larger gaps (less texture)
        params['spacing'] = max(12, int(12 + intensity * 12))  # 12-24 range (much wider)
        params['gap_size'] = max(6, int(6 + intensity * 8))  # 6-14 range (larger gaps)
        params['line_thickness'] = max(2, int(2 + intensity * 2))  # 2-4 range (thicker lines)
        
    elif texture_type == 'broken_vertical_lines':
        # Darker = more broken lines, closer spacing
        params['spacing'] = max(3, int(8 - intensity * 5))  # 3-8 range
        params['gap_size'] = max(2, int(6 - intensity * 3))  # 2-6 range
        params['thickness'] = max(1, int(1 + intensity * 2))  # 1-3 range
        
    elif texture_type == 'slanted_lines':
        # Darker = closer slanted lines
        params['spacing'] = max(4, int(12 - intensity * 6))  # 4-12 range
        params['thickness'] = max(1, int(2 + intensity * 2))  # 2-4 range
        
    elif texture_type == 'inverted_slanted_lines':
        # Darker = closer slanted lines
        params['spacing'] = max(4, int(12 - intensity * 6))  # 4-12 range
        params['thickness'] = max(1, int(2 + intensity * 2))  # 2-4 range
        
    elif texture_type == 'offset_dots':
        # Darker = more offset dots
        params['dot_size'] = max(1, int(2 + intensity * 3))  # 2-5 range
        params['dot_spacing'] = max(6, int(18 - intensity * 8))  # 6-18 range
        
    elif texture_type == 'noisy':
        # Darker = more noise
        params['noise_level'] = 0.2 + intensity * 0.8  # 0.2-1.0 range
        
    elif texture_type == 'flat':
        # Flat texture - no variation needed
        params = {}
        
    else:  # Default smooth
        params = {}
    
    return params

def generate_texture_pattern(texture_type, height, width, **params):
    """Generate texture pattern as height map for 3D printing"""
    texture = np.zeros((height, width), dtype=np.float32)
    
    # Define default height_boost
    height_boost = params.get('height_boost', 1.0)  # Will be scaled by 2% later
    
    if texture_type == 'vertical_lines':
        spacing = params.get('spacing', 5)  # Reduced from 8 to 6
        thickness = params.get('thickness', 1)
        for x in range(0, width, spacing):
            texture[:, x:x+thickness] = height_boost
            
    elif texture_type == 'horizontal_waves':
        # Create continuous horizontal wave lines
        frequency = params.get('frequency', 0.08)  # Higher frequency for sharper waves
        amplitude = params.get('amplitude', 12)  # Reduced amplitude for tighter waves
        line_thickness = params.get('line_thickness', 1)  # Thinner lines for sharper edges
        wave_spacing = params.get('wave_spacing', 7)  # Reduced from 10 to 8 for closer spacing
        
        for base_y in range(0, height, wave_spacing):
            for x in range(width):
                # Calculate wave offset using sine function
                wave_offset = int(amplitude * np.sin(frequency * x))
                wave_y = base_y + wave_offset
                
                # Draw thick wave line
                for thickness in range(-line_thickness, line_thickness + 1):
                    y_pos = wave_y + thickness
                    if 0 <= y_pos < height:
                        texture[y_pos, x] = height_boost
                    
    elif texture_type == 'vertical_waves':
        # Create continuous vertical wave lines
        frequency = params.get('frequency', 0.08)  # Higher frequency for sharper waves
        amplitude = params.get('amplitude', 12)  # Reduced amplitude for tighter waves
        line_thickness = params.get('line_thickness', 1)  # Thinner lines for sharper edges
        wave_spacing = params.get('wave_spacing', 7)  # Reduced from 10 to 8 for closer spacing
        
        for base_x in range(0, width, wave_spacing):
            for y in range(height):
                # Calculate wave offset using sine function
                wave_offset = int(amplitude * np.sin(frequency * y))
                wave_x = base_x + wave_offset
                
                # Draw thick wave line
                for thickness in range(-line_thickness, line_thickness + 1):
                    x_pos = wave_x + thickness
                    if 0 <= x_pos < width:
                        texture[y, x_pos] = height_boost
                    
    elif texture_type == 'dots':
        dot_size = params.get('dot_size', 3)
        dot_spacing = params.get('dot_spacing', 10)  # Reduced from 16 to 12
        print(f"  Generating sharp dots: size={dot_size}, spacing={dot_spacing}, height={height_boost}")
        dots_created = 0
        for y in range(dot_size, height - dot_size, dot_spacing):
            for x in range(dot_size, width - dot_size, dot_spacing):
                # Create sharp circular dots
                for dy in range(-dot_size, dot_size + 1):
                    for dx in range(-dot_size, dot_size + 1):
                        if dy*dy + dx*dx <= dot_size*dot_size:
                            ny, nx = y + dy, x + dx
                            if 0 <= ny < height and 0 <= nx < width:
                                texture[ny, nx] = height_boost
                dots_created += 1
        print(f"  Created {dots_created} sharp dots")
                
    elif texture_type == 'broken_horizontal_lines':
        spacing = params.get('spacing', 6)  # Reduced from 12 to 10
        gap_size = params.get('gap_size', 4)
        line_thickness = params.get('line_thickness', 1)
        for y in range(0, height, spacing):
            for x in range(0, width, gap_size * 3):
                end_x = min(x + gap_size, width)
                # Create sharp horizontal lines
                for ty in range(max(0, y - line_thickness//2), min(height, y + line_thickness//2 + 1)):
                    for tx in range(x, end_x):
                        texture[ty, tx] = height_boost
                
    elif texture_type == 'broken_vertical_lines':
        spacing = params.get('spacing', 6)  # Reduced from 12 to 10
        gap_size = params.get('gap_size', 4)
        thickness = params.get('thickness', 1)
        for x in range(0, width, spacing):
            for y in range(0, height, gap_size * 2):
                end_y = min(y + gap_size, height)
                # Create sharp vertical lines
                for tx in range(max(0, x - thickness//2), min(width, x + thickness//2 + 1)):
                    for ty in range(y, end_y):
                        texture[ty, tx] = height_boost
                
    elif texture_type == 'slanted_lines':
        spacing = params.get('spacing', 8)  # Reduced from 18 to 14
        thickness = params.get('thickness', 3)
        for i in range(0, height + width, spacing):
            for j in range(max(0, i-height), min(width, i)):
                y = i - j
                if 0 <= y < height:
                    # Create sharp slanted lines
                    for ty in range(max(0, y - thickness//2), min(height, y + thickness//2 + 1)):
                        for tx in range(max(0, j - thickness//2), min(width, j + thickness//2 + 1)):
                            texture[ty, tx] = height_boost
                    
    elif texture_type == 'inverted_slanted_lines':
        spacing = params.get('spacing', 8)  # Reduced from 18 to 14
        thickness = params.get('thickness', 3)
        for i in range(-width, height, spacing):
            for j in range(max(0, -i), min(width, height - i)):
                y = i + j
                if 0 <= y < height:
                    # Create sharp inverted slanted lines
                    for ty in range(max(0, y - thickness//2), min(height, y + thickness//2 + 1)):
                        for tx in range(max(0, j - thickness//2), min(width, j + thickness//2 + 1)):
                            texture[ty, tx] = height_boost
                    
    elif texture_type == 'offset_dots':
        dot_size = params.get('dot_size', 3)
        dot_spacing = params.get('dot_spacing', 10)  # Reduced from 20 to 16
        for y in range(dot_size, height - dot_size, dot_spacing):
            for x in range(dot_size, width - dot_size, dot_spacing):
                # Offset every other row
                offset = dot_spacing // 2 if (y // dot_spacing) % 2 == 1 else 0
                x_offset = x + offset
                if dot_size <= x_offset < width - dot_size:
                    # Create sharp offset dots
                    for dy in range(-dot_size, dot_size + 1):
                        for dx in range(-dot_size, dot_size + 1):
                            if dy*dy + dx*dx <= dot_size*dot_size:
                                ny, nx = y + dy, x_offset + dx
                                if 0 <= ny < height and 0 <= nx < width:
                                    texture[ny, nx] = height_boost
                    
    elif texture_type == 'noisy':
        # Generate a noisy texture
        noise_level = params.get('noise_level', 0.5)
        texture = np.random.normal(0, noise_level, (height, width))
        texture = texture.astype(np.float32)
        
    elif texture_type == 'flat':
        # Generate a flat texture (no texture)
        texture = np.zeros((height, width), dtype=np.float32)
        
    else:  # Default smooth
        texture[:, :] = 0.0
        
    return texture



def get_texture_for_color(rgb_color):
    """Map RGB color to texture type based on ColorTextureKey.png specifications"""
    r, g, b = rgb_color
    
    # Calculate color characteristics for better classification
    total = r + g + b
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    brightness = total / 3
    saturation = (max_val - min_val) / max(max_val, 1)
    
    print(f"   Color RGB({r:.0f},{g:.0f},{b:.0f}) - Brightness: {brightness:.1f}, Saturation: {saturation:.2f}")
    
    # ===== COLOR-TO-TEXTURE MAPPING BASED ON ColorTextureKey.png =====
    # Updated based on user specifications
    
    # BLACK - Noisy texture
    if brightness < 50:
        return 'noisy'
    
    # WHITE - Flat (no texture) - Very high threshold for only pure whites
    elif brightness > 240:
        return 'flat'
    
    # NEAR-WHITE - Very light texture (reduced intensity)
    elif brightness > 220:
        return 'flat'  # Will be handled with reduced intensity in texture generation
    
    # BEIGE/LIGHT NEUTRAL COLORS - Flat texture (no texture) - More restrictive
    elif brightness > 160 and saturation < 0.15:  # Only very light colors with very low saturation
        return 'flat'
    
    # PINK FAMILY (High Red, Medium Blue) - Broken Vertical Lines
    elif r > 150 and 100 < b < 180 and g < 120:
        return 'broken_vertical_lines'
    
    # PURPLE FAMILY (High Red + Blue) - Slanted Lines
    elif r > 120 and b > 120 and g < 100:
        return 'slanted_lines'
    
    # RED FAMILY - Vertical Lines (very restrictive to only catch true reds)
    elif r > g + 60 and r > b + 60 and r > 150 and g < 80 and b < 80:
        return 'vertical_lines'
    
    # GREEN FAMILY - Inverted Slanted Lines  
    elif g > r + 30 and g > b + 30 and g > 100:
        return 'inverted_slanted_lines'
        
    # BLUE FAMILY - Horizontal Waves
    elif b > r + 30 and b > g + 30 and b > 100:
        return 'horizontal_waves'
        
    # YELLOW FAMILY (High Red + Green) - Offset Dots
    elif r > 150 and g > 150 and b < 100:
        return 'offset_dots'
        
    # CYAN FAMILY (High Green + Blue) - Vertical Waves
    elif g > 120 and b > 120 and r < 100:
        return 'vertical_waves'
        
    # ORANGE FAMILY (High Red, Medium Green) - Broken Horizontal Lines
    elif r > 150 and 80 < g < 150 and b < 80:
        return 'broken_horizontal_lines'
        
    # BROWN/TAN/BEIGE FAMILY (Expanded to include all warm neutral colors) - Broken Horizontal Lines
    elif ((100 < r < 220 and 50 < g < 200 and b < 150 and 
           r > g - 20 and r > b + 20 and g > b - 10) or
          # Dark browns that were falling through
          (r > 60 and g > 40 and b > 20 and r > g + 10 and r > b + 20 and 
           g > b + 5 and r < 150 and g < 100)):
        return 'broken_horizontal_lines'
        
    # GRAY FAMILY (Low saturation) - Vertical Waves
    elif saturation < 0.35:
        return 'vertical_waves'
        
    # MEDIUM SATURATION COLORS - Assign based on dominant color
    else:
        if r > g and r > b:  # Red dominant
            return 'vertical_lines'
        elif g > r and g > b:  # Green dominant
            return 'inverted_slanted_lines'
        elif b > r and b > g:  # Blue dominant
            return 'horizontal_waves'
        else:  # Balanced colors
            return 'dots'

def find_custom_texture_for_color(rgb_color, color_mappings):
    """Find the best matching custom texture for a given RGB color"""
    if not color_mappings:
        return None
    
    r, g, b = rgb_color
    best_match = None
    best_distance = float('inf')
    
    for mapping in color_mappings:
        # Calculate Euclidean distance in RGB space
        distance = np.sqrt(
            (r - mapping['r'])**2 + 
            (g - mapping['g'])**2 + 
            (b - mapping['b'])**2
        )
        
        # Check if within tolerance and is the best match so far
        if distance <= mapping['tolerance'] and distance < best_distance:
            best_distance = distance
            best_match = mapping['texture']
    
    return best_match

def reduce_image_resolution(image, target_width=800, target_height=600):
    """Reduce image resolution to target dimensions while maintaining aspect ratio"""
    height, width = image.shape[:2]
    
    # Calculate aspect ratio
    aspect_ratio = width / height
    target_aspect = target_width / target_height
    
    # Determine final dimensions maintaining aspect ratio
    if aspect_ratio > target_aspect:
        # Image is wider than target
        final_width = target_width
        final_height = int(target_width / aspect_ratio)
    else:
        # Image is taller than target
        final_height = target_height
        final_width = int(target_height * aspect_ratio)
    
    # Resize image
    resized_image = cv2.resize(image, (final_width, final_height), interpolation=cv2.INTER_AREA)
    
    print(f"✓ Reduced image resolution: {width}x{height} -> {final_width}x{final_height}")
    print(f"✓ Resolution reduction factor: {width * height / (final_width * final_height):.1f}x")
    
    return resized_image

def create_tactile_heightmap(image_path, num_segments=8, color_tolerance=1.0, color_mappings=None, depth_map_path=None):
    """Create a heightmap with tactile textures based on color segmentation
    
    Args:
        image_path: Path to input image
        num_segments: Number of color segments for K-means clustering
        color_tolerance: Tolerance for color boundaries (affects cluster initialization)
        color_mappings: List of custom RGB color to texture mappings
        depth_map_path: Path to an optional depth map image for 3D mode
    """
    
    # Load image
    rgb_image = cv2.imread(image_path)
    if rgb_image is None:
        raise ValueError(f"Could not load image: {image_path}")
    rgb_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2RGB)
    
    # Reduce image resolution to reduce STL file size
    rgb_image = reduce_image_resolution(rgb_image, target_width=800, target_height=600)
    
    height, width = rgb_image.shape[:2]
    
    # Segment the image
    pixels = rgb_image.reshape(-1, 3)
    # Use color_tolerance to adjust clustering sensitivity
    kmeans = KMeans(n_clusters=num_segments, random_state=42, tol=color_tolerance)
    labels = kmeans.fit_predict(pixels)
    
    # Get the segmented image
    segmented = kmeans.cluster_centers_[labels].reshape(rgb_image.shape)
    segmented = segmented.astype(np.uint8)
    
    # Load the depth map from height_maps directory
    # Convert .jpg to .png for depth map filename
    depth_filename = os.path.splitext(os.path.basename(image_path))[0] + "_heightmap.png"
    depth_image_path = f"../3dOutputs/height_maps/{depth_filename}"
    
    # Start with the depth map as the base
    if depth_map_path and os.path.exists(depth_map_path):
        depth_image = cv2.imread(depth_map_path, cv2.IMREAD_GRAYSCALE)
        if depth_image is not None:
            # Resize depth map to match RGB image dimensions
            depth_image_resized = cv2.resize(depth_image, (width, height))
            combined_heightmap = depth_image_resized.astype(np.float32) / 255.0  # Normalize to 0-1
            print(f"✓ Loaded depth map from: {depth_map_path} and resized to {width}x{height}")
        else:
            print(f"⚠️  Could not load depth map, falling back to grayscale")
            gray_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
            combined_heightmap = gray_image.astype(np.float32) / 255.0
    else:
        print(f"⚠️  Depth map not found at: {depth_map_path}, falling back to grayscale")
        gray_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
        combined_heightmap = gray_image.astype(np.float32) / 255.0
    
    # Apply textures directly on top of the depth map
    for i, center in enumerate(kmeans.cluster_centers_):
        # Check for custom color mapping first
        custom_texture = find_custom_texture_for_color(center, color_mappings)
        if custom_texture:
            texture_type = custom_texture
            print(f"🎨 Using custom texture '{texture_type}' for RGB{tuple(center.astype(int))}")
        else:
            texture_type = get_texture_for_color(center)
        
        # Calculate intensity-based parameters for this color segment
        intensity_params = calculate_intensity_based_params(center, texture_type)
        
        # Debug: show intensity-based parameters
        if intensity_params:
            param_str = ", ".join([f"{k}={v}" for k, v in intensity_params.items()])
            print(f"   Intensity params for {texture_type}: {param_str}")
        
        # Generate texture pattern with intensity-based parameters
        texture = generate_texture_pattern(texture_type, height, width, **intensity_params)
        
        # Apply texture directly to this segment on the combined heightmap
        mask = (labels.reshape(height, width) == i)
        # Add texture height (2% of the overall height) on top of existing depth
        texture_height = texture[mask] * 0.02
        combined_heightmap[mask] += texture_height
        
        # Debug: show how many pixels in this segment have texture
        segment_pixels = np.sum(mask)
        textured_pixels = np.sum(texture[mask] > 0)
        print(f"Segment {i}: RGB{tuple(center.astype(int))} -> {texture_type} ({textured_pixels}/{segment_pixels} pixels textured)")
    
    return combined_heightmap, segmented, kmeans, labels

def create_texture_only_heightmap(image_path, num_segments=8, color_tolerance=1.0, color_mappings=None, depth_map_path=None):
    """Create a heightmap with only tactile textures (no depth map) for 2D mode
    
    Args:
        image_path: Path to input image
        num_segments: Number of color segments for K-means clustering
        color_tolerance: Tolerance for color boundaries (affects cluster initialization)
        color_mappings: List of custom RGB color to texture mappings
    """
    
    # Load image
    rgb_image = cv2.imread(image_path)
    if rgb_image is None:
        raise ValueError(f"Could not load image: {image_path}")
    rgb_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2RGB)
    
    # Reduce image resolution to reduce STL file size (optimized for 2D mode)
    rgb_image = reduce_image_resolution(rgb_image, target_width=550, target_height=550)
    
    height, width = rgb_image.shape[:2]
    
    # Segment the image
    pixels = rgb_image.reshape(-1, 3)
    # Use color_tolerance to adjust clustering sensitivity
    kmeans = KMeans(n_clusters=num_segments, random_state=42, tol=color_tolerance)
    labels = kmeans.fit_predict(pixels)
    
    # Get the segmented image
    segmented = kmeans.cluster_centers_[labels].reshape(rgb_image.shape)
    segmented = segmented.astype(np.uint8)
    
    # Start with a flat base (no depth map) - just a minimal base height
    texture_only_heightmap = np.full((height, width), 0.1, dtype=np.float32)  # Flat 0.1 base
    print(f"✓ Created flat base heightmap for texture-only mode")
    
    # Apply textures on top of the flat base
    for i, center in enumerate(kmeans.cluster_centers_):
        # Check for custom color mapping first
        custom_texture = find_custom_texture_for_color(center, color_mappings)
        if custom_texture:
            texture_type = custom_texture
            print(f"🎨 Using custom texture '{texture_type}' for RGB{tuple(center.astype(int))}")
        else:
            texture_type = get_texture_for_color(center)
        
        # Calculate intensity-based parameters for this color segment
        intensity_params = calculate_intensity_based_params(center, texture_type)
        
        # Generate texture pattern with intensity-based parameters
        texture = generate_texture_pattern(texture_type, height, width, **intensity_params)
        
        # Apply texture directly to this segment on the flat heightmap
        mask = (labels.reshape(height, width) == i)
        # Add texture height (20% of the overall height) on top of flat base - very pronounced for 2D mode
        texture_height = texture[mask] * 0.20
        texture_only_heightmap[mask] += texture_height
        
        # Debug: show how many pixels in this segment have texture
        segment_pixels = np.sum(mask)
        textured_pixels = np.sum(texture[mask] > 0)
        print(f"Segment {i}: RGB{tuple(center.astype(int))} -> {texture_type} ({textured_pixels}/{segment_pixels} pixels textured)")
    
    return texture_only_heightmap, segmented, kmeans, labels

def heightmap_to_stl(heightmap, output_path, scale_factor=1.0, base_height=default_base_height):
    """Convert heightmap to STL file for 3D printing with simple base"""
    heightmap = np.fliplr(heightmap)
    height, width = heightmap.shape
    
    # Scale the heightmap
    scaled_heightmap = heightmap * scale_factor + base_height
    
    # Calculate aspect ratio to preserve original image dimensions
    aspect_ratio = width / height
    
    # Create vertices for the top surface (heightmap)
    vertices = []
    for y in range(height):
        for x in range(width):
            # Preserve aspect ratio: normalize x by width, y by height
            x_norm = x / (width - 1) * aspect_ratio
            y_norm = y / (height - 1)
            z = scaled_heightmap[y, x]
            vertices.append([x_norm, y_norm, z])
    
    # Add just 4 corner vertices for a simple base (much more efficient)
    base_vertices_start = len(vertices)
    vertices.extend([
        [0.0, 0.0, 0.0],  # Bottom-left
        [aspect_ratio, 0.0, 0.0],  # Bottom-right
        [aspect_ratio, 1.0, 0.0],  # Top-right
        [0.0, 1.0, 0.0]   # Top-left
    ])
    
    vertices = np.array(vertices)
    
    # Create faces (triangles)
    faces = []
    
    # Top surface (heightmap)
    for y in range(height - 1):
        for x in range(width - 1):
            # Calculate vertex indices for top surface
            v1 = y * width + x
            v2 = y * width + (x + 1)
            v3 = (y + 1) * width + x
            v4 = (y + 1) * width + (x + 1)
            
            # Create two triangles for each square
            faces.append([v1, v2, v3])
            faces.append([v2, v4, v3])
    
    # Simple bottom surface (just 2 triangles using 4 corner vertices)
    faces.extend([
        [base_vertices_start, base_vertices_start + 2, base_vertices_start + 1],  # Bottom triangle
        [base_vertices_start, base_vertices_start + 3, base_vertices_start + 2]   # Top triangle
    ])
    
    # Simple side walls (only 8 triangles total instead of hundreds)
    # Front wall (y=0)
    for x in range(width - 1):
        top1 = x
        top2 = x + 1
        bottom1 = base_vertices_start if x == 0 else base_vertices_start + 1
        bottom2 = base_vertices_start + 1 if x == width - 2 else base_vertices_start + 1
        
        faces.append([top1, bottom1, top2])
        faces.append([top2, bottom1, bottom2])
    
    # Back wall (y=1)
    for x in range(width - 1):
        top1 = (height - 1) * width + x
        top2 = (height - 1) * width + x + 1
        bottom1 = base_vertices_start + 3 if x == 0 else base_vertices_start + 2
        bottom2 = base_vertices_start + 2 if x == width - 2 else base_vertices_start + 2
        
        faces.append([top2, bottom2, top1])
        faces.append([top1, bottom2, bottom1])
    
    # Left wall (x=0)
    for y in range(height - 1):
        top1 = y * width
        top2 = (y + 1) * width
        bottom1 = base_vertices_start if y == 0 else base_vertices_start + 3
        bottom2 = base_vertices_start + 3 if y == height - 2 else base_vertices_start + 3
        
        faces.append([top1, top2, bottom1])
        faces.append([top2, bottom2, bottom1])
    
    # Right wall (x=1)
    for y in range(height - 1):
        top1 = y * width + (width - 1)
        top2 = (y + 1) * width + (width - 1)
        bottom1 = base_vertices_start + 1 if y == 0 else base_vertices_start + 2
        bottom2 = base_vertices_start + 2 if y == height - 2 else base_vertices_start + 2
        
        faces.append([top2, top1, bottom2])
        faces.append([top1, bottom1, bottom2])
    
    # Write STL file
    with open(output_path, 'wb') as f:
        # Write STL header
        f.write(b'\x00' * 80)
        
        # Write number of triangles
        f.write(struct.pack('<I', len(faces)))
        
        # Write each triangle
        for face in faces:
            # Calculate normal for each triangle
            v1 = vertices[face[0]]
            v2 = vertices[face[1]]
            v3 = vertices[face[2]]
            
            # Calculate normal vector
            edge1 = v2 - v1
            edge2 = v3 - v1
            normal = np.cross(edge1, edge2)
            normal = normal / np.linalg.norm(normal)  # Normalize
            
            # Write normal
            for component in normal:
                f.write(struct.pack('<f', component))
            
            # Write vertices
            for vertex_idx in face:
                vertex = vertices[vertex_idx]
                for component in vertex:
                    f.write(struct.pack('<f', component))
            
            # Write attribute byte count
            f.write(struct.pack('<H', 0))
    
    print(f"✓ Saved optimized STL file: {output_path}")

def generate_preview_images(combined_heightmap, segmented, labels, kmeans, output_folder, color_mappings=None):
    """Generate preview images: segmentation map and texture overlay"""
    try:
        # 1. Generate segmentation map (colored segments)
        segmentation_path = os.path.join(output_folder, 'segmentation_map.png')
        plt.figure(figsize=(10, 8))
        plt.imshow(segmented)
        plt.title('Color Segmentation Map')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(segmentation_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"✓ Saved segmentation map: {segmentation_path}")
        
        # 2. Generate texture overlay showing actual texture patterns
        texture_overlay_path = os.path.join(output_folder, 'texture_overlay.png')
        
        # Create a visual representation of textures overlaid on the original image
        height, width = combined_heightmap.shape
        
        # Start with the segmented image as base
        texture_visualization = segmented.copy()
        
        # Create a texture pattern overlay
        texture_overlay = np.zeros((height, width), dtype=np.float32)
        
        # Recreate the texture patterns for visualization
        for i, center in enumerate(kmeans.cluster_centers_):
            # Check for custom color mapping first
            custom_texture = find_custom_texture_for_color(center, color_mappings)
            if custom_texture:
                texture_type = custom_texture
            else:
                texture_type = get_texture_for_color(center)
            
            # Generate texture pattern for this segment with intensity-based parameters
            intensity_params = calculate_intensity_based_params(center, texture_type)
            segment_texture = generate_texture_pattern(texture_type, height, width, **intensity_params)
            mask = (labels.reshape(height, width) == i)
            
            # Add texture pattern to overlay where this segment exists
            texture_overlay[mask] += segment_texture[mask]
        
        # Create a pure texture pattern visualization
        plt.figure(figsize=(12, 8))
        
        # Create a high-contrast texture visualization
        texture_display = np.zeros((height, width, 3))  # RGB
        
        # Color each segment's background and overlay its texture patterns
        for i, center in enumerate(kmeans.cluster_centers_):
            mask = (labels.reshape(height, width) == i)
            
            # Use the segment color as background
            segment_color = center.astype(int) / 255.0
            texture_display[mask] = segment_color
            
            # Get texture pattern for this segment
            custom_texture = find_custom_texture_for_color(center, color_mappings)
            if custom_texture:
                texture_type = custom_texture
            else:
                texture_type = get_texture_for_color(center)
            
            # Generate texture pattern with intensity-based parameters
            intensity_params = calculate_intensity_based_params(center, texture_type)
            segment_texture = generate_texture_pattern(texture_type, height, width, **intensity_params)
            texture_mask = (segment_texture > 0) & mask
            
            # Make texture lines bright red for maximum visibility
            texture_display[texture_mask] = [1.0, 0.0, 0.0]  # Bright red
        
        plt.imshow(texture_display)
        plt.title('Tactile Texture Patterns (Red Lines = Raised Textures)')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(texture_overlay_path, dpi=200, bbox_inches='tight')
        plt.close()
        print(f"✓ Saved texture overlay: {texture_overlay_path}")
        

        
    except Exception as e:
        print(f"⚠️ Error generating preview images: {e}")

def generate_textured_stl(image_path, heightmap_path, output_stl_path, num_segments=14, color_tolerance=1.0, generate_3d=True, output_folder=None, color_mappings=None):
    """
    Generate textured STL files from an image and heightmap.
    
    Args:
        image_path: Path to input image
        heightmap_path: Path to heightmap image
        output_stl_path: Path for output textured STL file
        num_segments: Number of color segments (2-20)
        color_tolerance: Color boundary sensitivity (0.5-2.0)
        generate_3d: Whether to generate 3D STL (True) or just 2D heightmap (False)
        output_folder: Folder to save preview images and additional STL files
    """
    try:
        print(f"🎨 Generating textured model for: {os.path.basename(image_path)}")
        print(f"   - Segments: {num_segments}")
        print(f"   - Color tolerance: {color_tolerance}")
        print(f"   - Generate 3D: {generate_3d}")
        
        # Create heightmap based on mode
        if generate_3d:
            # 3D mode: Create combined heightmap (painting depth + textures)
            combined_heightmap, segmented, kmeans, labels = create_tactile_heightmap(
                image_path, 
                num_segments=num_segments,
                color_tolerance=color_tolerance,
                color_mappings=color_mappings,
                depth_map_path=heightmap_path  # Pass the depth map path from backend
            )
            print(f"ℹ️ Created 3D heightmap with depth + textures")
        else:
            # 2D mode: Create texture-only heightmap (no depth)
            combined_heightmap, segmented, kmeans, labels = create_texture_only_heightmap(
                image_path, 
                num_segments=num_segments,
                color_tolerance=color_tolerance,
                color_mappings=color_mappings,
                depth_map_path=None  # 2D mode ignores heightmap completely
            )
            print(f"ℹ️ Created 2D texture-only heightmap")
        
        # Generate preview images if output folder is provided
        if output_folder:
            generate_preview_images(combined_heightmap, segmented, labels, kmeans, output_folder, color_mappings)
        
        # Generate the main textured STL file
        
        heightmap_to_stl(combined_heightmap, output_stl_path, scale_factor=0.3, base_height=default_base_height)
        print(f"✓ Generated textured STL: {output_stl_path}")
        
        # Generate additional STL files if output folder is provided
        if output_folder:
            # 1. Heightmap only (depth without textures)
            if generate_3d and heightmap_path and os.path.exists(heightmap_path):
                depth_only_stl = os.path.join(output_folder, 'heightmap_only.stl')
                depth_image = cv2.imread(heightmap_path, cv2.IMREAD_GRAYSCALE)
                if depth_image is not None:
                    # Resize to match the working dimensions
                    height, width = combined_heightmap.shape
                    depth_resized = cv2.resize(depth_image, (width, height))
                    depth_normalized = depth_resized.astype(np.float32) / 255.0
                    heightmap_to_stl(depth_normalized, depth_only_stl, scale_factor=0.3, base_height=default_base_height)
                    print(f"✓ Generated heightmap-only STL: {depth_only_stl}")
            
            # 2. Texture only (textures without depth)
            texture_only_stl = os.path.join(output_folder, 'texture_only.stl')
            if generate_3d:
                # Extract just the texture component (remove depth base)
                texture_component = combined_heightmap.copy()
                if heightmap_path and os.path.exists(heightmap_path):
                    depth_image = cv2.imread(heightmap_path, cv2.IMREAD_GRAYSCALE)
                    if depth_image is not None:
                        height, width = combined_heightmap.shape
                        depth_resized = cv2.resize(depth_image, (width, height))
                        depth_normalized = depth_resized.astype(np.float32) / 255.0
                        # Subtract depth to get only textures
                        texture_component = combined_heightmap - depth_normalized
                        # Ensure non-negative values
                        texture_component = np.maximum(texture_component, 0)
                
                # Add minimal base height for texture-only STL
                texture_component += 0.1
                heightmap_to_stl(texture_component, texture_only_stl, scale_factor=0.3, base_height=default_base_height)
                print(f"✓ Generated texture-only STL: {texture_only_stl}")
            else:
                # Already texture-only mode
                heightmap_to_stl(combined_heightmap, texture_only_stl, scale_factor=0.3, base_height=default_base_height)
                print(f"✓ Generated texture-only STL: {texture_only_stl}")
        
        if generate_3d:
            print(f"ℹ️ STL generated for 3D mode (depth + textures)")
        else:
            print(f"ℹ️ STL generated for 2D mode (textures only)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating textured model: {e}")
        return False

def main():
    """Main function to create tactile 3D model for testing"""
    
    # Use the 2021.17.10_1k_1 painting for testing
    image_path = "../test-pics/2021.17.10_1k_1.jpg"
    
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        return
    
    print("🎨 Creating Tactile 3D Model for Testing (2021 Painting)")
    print("=" * 60)
    
    # Create combined heightmap (painting depth + textures)
    combined_heightmap, segmented, kmeans, labels = create_tactile_heightmap(image_path, num_segments=14)
    
    # Get dimensions
    height, width = combined_heightmap.shape
    
    # Save preview
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    
    # Create visualization - just the combined heightmap
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    
    # Combined heightmap - show full image and enhance contrast
    print(f"Full heightmap stats: min={combined_heightmap.min():.4f}, max={combined_heightmap.max():.4f}, mean={combined_heightmap.mean():.4f}")
    # Enhance contrast by squaring the values to make differences more visible
    enhanced_heightmap = combined_heightmap ** 2
    normalized_heightmap = (enhanced_heightmap - enhanced_heightmap.min()) / (enhanced_heightmap.max() - enhanced_heightmap.min())
    ax.imshow(normalized_heightmap, cmap='gray')
    ax.set_title(f'{base_name} - Combined Heightmap (Painting Depth + Textures)', fontsize=16)
    ax.axis('off')
    
    plt.tight_layout()
    
    # Save preview
    preview_path = f"../3dOutputs/{base_name}_tactile_preview.png"
    plt.savefig(preview_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved preview: {preview_path}")
    
    # Generate STL file - use full image and increase height
    stl_path = f"../3dOutputs/{base_name}_tactile_textures.stl"
    heightmap_to_stl(combined_heightmap, stl_path, scale_factor=0.3, base_height=default_base_height
                     )
    
    print("\n🎨 Tactile 3D Model Complete!")
    print("The STL file contains tactile textures that can be felt:")
    print("- Red areas: Vertical lines (raised ridges)")
    print("- Blue areas: Horizontal lines (raised ridges)")
    print("- Brown areas: Broken horizontal lines (gapped ridges)")
    print("- Dark areas: Dots (raised bumps)")
    print("- Gray areas: Vertical waves (wavy surface)")

if __name__ == "__main__":
    main() 
