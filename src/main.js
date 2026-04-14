import './style.css';
import { ThreeViewer } from './three-viewer.js';

// Initialize Three.js Viewer
let viewer;

document.addEventListener('DOMContentLoaded', () => {
    initModal();
    initProjectEffects();
});

function initModal() {
    const trigger = document.querySelector('.demo-trigger');
    const overlay = document.getElementById('gui-overlay');
    const closeBtn = document.querySelector('.close-gui');
    const generateBtn = document.getElementById('generate-btn');
    const fileInput = document.getElementById('file-input');
    const stats = document.getElementById('stats');
    const loadSampleBtn = document.getElementById('load-sample');
    const preview = document.getElementById('image-preview');

    if (!trigger) return; // Guard against missing elements

    trigger.addEventListener('click', () => {
        overlay.classList.remove('modal-hidden');
        if (!viewer) {
            viewer = new ThreeViewer('three-canvas-container');
        }
        // Small timeout to ensure the DOM has updated its dimensions
        setTimeout(() => {
            viewer.onResize();
        }, 100);
    });

    closeBtn.addEventListener('click', () => {
        overlay.classList.add('modal-hidden');
    });

    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) overlay.classList.add('modal-hidden');
    });

    // Handle Sample Loading
    loadSampleBtn.addEventListener('click', () => {
        preview.style.backgroundImage = `url('/models/ref_image.png')`;
        preview.classList.remove('hidden');
        generateBtn.disabled = false;
        generateBtn.textContent = 'Process Sample Image';
    });

    // Handle Upload
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            const file = e.target.files[0];
            const reader = new FileReader();
            reader.onload = (event) => {
                preview.style.backgroundImage = `url(${event.target.result})`;
                preview.classList.remove('hidden');
            };
            reader.readAsDataURL(file);
            generateBtn.disabled = false;
            generateBtn.textContent = 'Ready to Process';
        }
    });

    // Handle Generation Simulation / Real API
    generateBtn.addEventListener('click', async () => {
        generateBtn.disabled = true;
        
        // Hide placeholder
        const placeholder = document.querySelector('.viewer-placeholder');
        if (placeholder) placeholder.style.display = 'none';

        const isSample = preview.style.backgroundImage.includes('ref_image.png');
        
        if (isSample) {
            // Static Demo Flow
            generateBtn.textContent = 'Analyzing Sample Features...';
            setTimeout(() => {
                generateBtn.textContent = 'Synthesizing Geometry...';
                setTimeout(() => {
                    viewer.generateModelFromImage(); // Loads kolobs_finger.stl
                    generateBtn.textContent = 'Generation Complete';
                    stats.classList.remove('hidden');
                    setTimeout(() => {
                        generateBtn.disabled = false;
                        generateBtn.textContent = 'Regenerate Sample';
                    }, 3000);
                }, 1500);
            }, 1000);
        } else {
            // Real API Flow
            generateBtn.textContent = 'Connecting to AI Engine...';
            try {
                const formData = new FormData();
                // Get the file from hidden input
                if (fileInput.files.length > 0) {
                    formData.append('image', fileInput.files[0]);
                } else {
                    throw new Error("No image selected");
                }

                generateBtn.textContent = 'Processing Image (Real-time AI)...';
                const response = await fetch('http://localhost:5001/api/generate', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) throw new Error("Server Error");

                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                
                generateBtn.textContent = 'Reconstructing Mesh...';
                viewer.loadSTLFromURL(url); // We need this new method
                
                generateBtn.textContent = 'Generation Complete';
                stats.classList.remove('hidden');
                document.getElementById('extra-controls').classList.remove('hidden');
            } catch (err) {
                console.error(err);
                generateBtn.textContent = 'AI Server Offline - Using Mock Engine';
                setTimeout(() => {
                    viewer.generateModelFromImage();
                    document.getElementById('extra-controls').classList.remove('hidden');
                }, 1000);
            } finally {
                setTimeout(() => {
                    generateBtn.disabled = false;
                    generateBtn.textContent = 'Generate Again';
                }, 3000);
            }
        }
    });

    // Extra Model Controls from Capstone
    document.getElementById('flip-h').addEventListener('click', () => {
        if (viewer.placeholderGroup) viewer.placeholderGroup.scale.x *= -1;
    });

    document.getElementById('flip-v').addEventListener('click', () => {
        if (viewer.placeholderGroup) viewer.placeholderGroup.scale.y *= -1;
    });

    document.getElementById('reset-view').addEventListener('click', () => {
        if (viewer.placeholderGroup) {
            viewer.placeholderGroup.scale.setScalar(1);
            viewer.placeholderGroup.rotation.set(0, 0, 0);
        }
        if (viewer.controls) viewer.controls.reset();
    });
}

function initProjectEffects() {
    // Reveal project cards on scroll
    const cards = document.querySelectorAll('.project-card');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(40px)';
        card.style.transition = 'all 0.8s cubic-bezier(0.2, 0.8, 0.2, 1)';
        observer.observe(card);
    });
}
