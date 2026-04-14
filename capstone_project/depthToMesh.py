import numpy as np
import cv2
import open3d as o3d

# === Load images ===
depth = cv2.imread('Depth-Anything-V2/depth_vis/iu.png', cv2.IMREAD_GRAYSCALE).astype(np.float32)
color = cv2.cvtColor(cv2.imread('test-pics/iu.png'), cv2.COLOR_BGR2RGB)
h, w = depth.shape

# === Normalize depth map to [0, 1] range ===
depth /= 255.0  # Assuming 8-bit depth map

# === Create 3D point cloud ===
fx = fy = 1  # Arbitrary focal lengths for now
cx, cy = w / 2, h / 2

points = []
colors = []

for y in range(h):
    for x in range(w):
        z = depth[y, x]
        X = (x - cx) * z / fx
        Y = (y - cy) * z / fy
        points.append([X, -Y, -z])  # Flip Y and Z for upright orientation
        colors.append(color[y, x] / 255.0)

points = np.array(points)
colors = np.array(colors)

# === Convert to Open3D PointCloud ===
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points)
pcd.colors = o3d.utility.Vector3dVector(colors)
pcd.estimate_normals()

# === Poisson surface reconstruction ===
mesh, _ = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=9)

# === Crop to the point cloud's bounding box to remove artifacts ===
bbox = pcd.get_axis_aligned_bounding_box()
mesh = mesh.crop(bbox)

# === Export mesh ===
o3d.io.write_triangle_mesh("textured_mesh.ply", mesh)

# === Preview ===
o3d.visualization.draw_geometries([mesh])