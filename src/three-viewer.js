import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader';

export class ThreeViewer {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.init();
  }

  init() {
    // Scene setup
    this.scene = new THREE.Scene();
    // Light neutral background for better visibility of emerald colors and shadows
    this.scene.background = new THREE.Color(0xe2e8f0); 
    
    this.camera = new THREE.PerspectiveCamera(75, this.container.clientWidth / this.container.clientHeight, 0.1, 1000);
    this.camera.position.set(0, 0, 3); 

    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    
    const width = this.container.clientWidth || 800;
    const height = this.container.clientHeight || 600;
    
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(window.devicePixelRatio);
    this.container.appendChild(this.renderer.domElement);

    // High-Intensity Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.9);
    this.scene.add(ambientLight);

    const mainLight = new THREE.DirectionalLight(0xffffff, 1.5);
    mainLight.position.set(10, 10, 10);
    mainLight.castShadow = true;
    this.scene.add(mainLight);

    const fillLight = new THREE.DirectionalLight(0xffffff, 0.8);
    fillLight.position.set(-10, -10, 5);
    this.scene.add(fillLight);

    // Controls
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.05;

    this.placeholderGroup = new THREE.Group();
    this.scene.add(this.placeholderGroup);

    this.animate();
    window.addEventListener('resize', () => this.onResize());
  }

  onResize() {
    if (!this.container) return;
    this.camera.aspect = this.container.clientWidth / this.container.clientHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
  }

  animate() {
    requestAnimationFrame(() => this.animate());
    this.controls.update();
    this.placeholderGroup.rotation.y += 0.002; // Slower, more professional rotation
    this.renderer.render(this.scene, this.camera);
  }

  generateModelFromImage() {
    this.loadSTLFromURL('/models/kolobs_finger.stl');
  }

  loadSTLFromURL(url) {
    // Clear previous
    while(this.placeholderGroup.children.length > 0){ 
        this.placeholderGroup.remove(this.placeholderGroup.children[0]); 
    }

    const loader = new STLLoader();
    loader.load(url, (geometry) => {
        // Material from Capstone: bright green/emerald with high specularity
        const material = new THREE.MeshPhongMaterial({
            color: 0x10b981, // Emerald Green
            specular: 0x111111,
            shininess: 200,
            flatShading: true
        });

        const mesh = new THREE.Mesh(geometry, material);
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        
        geometry.computeBoundingBox();
        const center = new THREE.Vector3();
        geometry.boundingBox.getCenter(center);
        mesh.position.sub(center);

        const size = new THREE.Vector3();
        geometry.boundingBox.getSize(size);
        const maxDim = Math.max(size.x, size.y, size.z);
        const scale = 4 / maxDim; // Zoomed in focus
        mesh.scale.set(scale, scale, scale);

        // Vertical flip as used in original capstone
        mesh.scale.y *= -1;

        this.placeholderGroup.add(mesh);
    });
  }
}
