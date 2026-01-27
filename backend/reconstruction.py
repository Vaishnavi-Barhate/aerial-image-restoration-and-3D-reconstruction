import cv2
import numpy as np
import trimesh
from PIL import Image

# ---------- DEBLUR ----------
def deblur_image(input_path, job_id):
    print("DEBLUR START")
    img = cv2.imread(input_path)
    kernel = np.ones((5,5), np.float32) / 25
    restored = cv2.filter2D(img, -1, kernel)
    out_path = f"processed/{job_id}_restored.png"
    cv2.imwrite(out_path, restored)
    return out_path

# ---------- DEPTH ----------
def run_depth(image_path, job_id):
    print("DEPTH START")
    # Read image
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Compute gradients using Sobel
    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)
    
    # Compute magnitude
    magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
    
    # Normalize to 0-255
    depth = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
    
    # Apply Gaussian blur to smooth
    depth = cv2.GaussianBlur(depth, (5,5), 0)
    
    # Save depth map
    depth_path = f"processed/{job_id}_depth.png"
    cv2.imwrite(depth_path, depth)
    
    return depth, depth_path

# ---------- MESH ----------
def pointcloud_to_mesh(depth, job_id):
    h, w = depth.shape
    xs, ys = np.meshgrid(np.arange(w), np.arange(h))
    points = np.stack([xs, ys, depth], axis=-1).reshape(-1, 3)
    
    # Normalize points
    points = points.astype(np.float32)
    points[:, 0] = (points[:, 0] - np.min(points[:, 0])) / (np.max(points[:, 0]) - np.min(points[:, 0]))
    points[:, 1] = (points[:, 1] - np.min(points[:, 1])) / (np.max(points[:, 1]) - np.min(points[:, 1]))
    points[:, 2] = (points[:, 2] - np.min(points[:, 2])) / (np.max(points[:, 2]) - np.min(points[:, 2]))
    
    cloud = trimesh.points.PointCloud(points)
    mesh = cloud.convex_hull
    
    mesh_path = f"processed/{job_id}_mesh.obj"
    mesh.export(mesh_path)
    return mesh_path

# ---------- HALLUCINATION ----------
def hallucinate_mesh(mesh_path, job_id):
    mesh = trimesh.load(mesh_path)
    # Subdivide the mesh
    mesh = mesh.subdivide()
    # Scale a bit
    mesh.vertices *= 1.15
    out_path = f"processed/{job_id}_mesh_full.obj"
    mesh.export(out_path)
    return out_path