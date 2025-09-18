// DOM Elements
const upload = document.getElementById('uploadImage');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const tryOnButton = document.getElementById('tryOnButton');
const resetButton = document.getElementById('resetButton');
const loadingOverlay = document.getElementById('loadingOverlay');
const loadingText = document.getElementById('loadingText');
const statusMessage = document.getElementById('statusMessage');

// State variables
let uploadedImage = new Image();
let dressImage = new Image();
let detector = null;
let isModelLoading = true;
let isImageUploaded = false;

// Load the dress image
dressImage.src = 'image.png';

// Utility functions
function updateStatus(message, type = 'info') {
    statusMessage.className = `status-message ${type}`;
    statusMessage.innerHTML = `<p>${message}</p>`;
}

function updateLoadingText(text) {
    loadingText.textContent = text;
}

function hideLoading() {
    loadingOverlay.classList.add('hidden');
}

function showLoading() {
    loadingOverlay.classList.remove('hidden');
}

function updateButtonState() {
    if (isModelLoading) {
        tryOnButton.disabled = true;
        tryOnButton.innerHTML = '<span class="btn-icon">⏳</span>Loading AI...';
    } else if (!isImageUploaded) {
        tryOnButton.disabled = true;
        tryOnButton.innerHTML = '<span class="btn-icon">📸</span>Upload Photo First';
    } else {
        tryOnButton.disabled = false;
        tryOnButton.innerHTML = '<span class="btn-icon">✨</span>Try On Dress';
    }
}

// Initialize pose detection
async function initializePoseDetection() {
    try {
        updateLoadingText('Initializing AI Models...');
        updateStatus('Loading AI models for pose detection...', 'info');
        
        // Wait for TensorFlow to be ready
        await tf.ready();
        updateLoadingText('TensorFlow.js Ready...');
        
        // Create pose detector
        detector = await poseDetection.createDetector(
            poseDetection.SupportedModels.MoveNet, 
            { 
                modelType: poseDetection.movenet.modelType.SINGLEPOSE_LIGHTNING,
                enableSmoothing: true
            }
        );
        
        updateLoadingText('Pose Detection Ready!');
        console.log('✅ Pose detector initialized successfully');
        
        isModelLoading = false;
        updateButtonState();
        updateStatus('AI models loaded successfully! Upload a photo to begin.', 'success');
        
        // Hide loading after a brief success message
        setTimeout(() => {
            if (!isImageUploaded) {
                hideLoading();
            }
        }, 1000);
        
    } catch (error) {
        console.error('❌ Failed to initialize pose detector:', error);
        updateStatus('Failed to load AI models. Please refresh the page and try again.', 'error');
        updateLoadingText('Failed to load models');
        isModelLoading = false;
        updateButtonState();
    }
}

// Handle dress image loading
dressImage.onload = () => {
    console.log('✅ Dress image loaded successfully');
};

dressImage.onerror = () => {
    console.error('❌ Failed to load dress image');
    updateStatus('Failed to load dress image. Please check if image.png exists.', 'error');
};

// Handle file upload
upload.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        // Validate file type
        if (!file.type.startsWith('image/')) {
            updateStatus('Please select a valid image file.', 'error');
            return;
        }
        
        // Validate file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            updateStatus('Image file is too large. Please select an image under 10MB.', 'error');
            return;
        }
        
        showLoading();
        updateLoadingText('Processing your photo...');
        updateStatus('Processing uploaded photo...', 'info');
        
        const reader = new FileReader();
        reader.onload = () => {
            uploadedImage = new Image();
            uploadedImage.src = reader.result;
            uploadedImage.onload = () => {
                // Set canvas dimensions to match image
                const maxWidth = 600;
                const maxHeight = 800;
                let { width, height } = uploadedImage;
                
                // Scale down if too large
                if (width > maxWidth || height > maxHeight) {
                    const scale = Math.min(maxWidth / width, maxHeight / height);
                    width *= scale;
                    height *= scale;
                }
                
                canvas.width = width;
                canvas.height = height;
                
                // Draw the uploaded image
                ctx.drawImage(uploadedImage, 0, 0, width, height);
                
                isImageUploaded = true;
                updateButtonState();
                updateStatus('Photo uploaded successfully! Click "Try On Dress" to see the magic ✨', 'success');
                
                resetButton.style.display = 'inline-flex';
                hideLoading();
                
                console.log('✅ Image uploaded and displayed');
            };
            
            uploadedImage.onerror = () => {
                updateStatus('Failed to process the uploaded image. Please try another image.', 'error');
                hideLoading();
            };
        };
        
        reader.onerror = () => {
            updateStatus('Failed to read the uploaded file. Please try again.', 'error');
            hideLoading();
        };
        
        reader.readAsDataURL(file);
    }
});

// Handle try-on button click
tryOnButton.addEventListener('click', async () => {
    if (!uploadedImage.src || !detector || isModelLoading) {
        updateStatus('Please wait for the AI models to load completely.', 'error');
        return;
    }

    if (!dressImage.complete) {
        updateStatus('Dress image is still loading. Please wait...', 'error');
        return;
    }

    showLoading();
    updateLoadingText('Analyzing pose...');
    updateStatus('Analyzing your pose for dress fitting...', 'info');

    try {
        // Redraw original image
        ctx.drawImage(uploadedImage, 0, 0, canvas.width, canvas.height);

        // Create a temporary canvas for pose detection
        const tempCanvas = document.createElement('canvas');
        const tempCtx = tempCanvas.getContext('2d');
        tempCanvas.width = uploadedImage.width;
        tempCanvas.height = uploadedImage.height;
        tempCtx.drawImage(uploadedImage, 0, 0);

        updateLoadingText('Detecting pose...');
        
        // Estimate poses on the original size image
        const poses = await detector.estimatePoses(tempCanvas);

        if (poses.length > 0) {
            const keypoints = poses[0].keypoints;
            const leftShoulder = keypoints.find(k => k.name === 'left_shoulder');
            const rightShoulder = keypoints.find(k => k.name === 'right_shoulder');
            const leftHip = keypoints.find(k => k.name === 'left_hip');
            const rightHip = keypoints.find(k => k.name === 'right_hip');

            // Check confidence scores
            const minConfidence = 0.3;
            if (leftShoulder?.score > minConfidence && 
                rightShoulder?.score > minConfidence && 
                leftHip?.score > minConfidence && 
                rightHip?.score > minConfidence) {
                
                updateLoadingText('Fitting dress...');
                
                // Calculate scaling factors
                const scaleX = canvas.width / uploadedImage.width;
                const scaleY = canvas.height / uploadedImage.height;
                
                // Scale keypoints to canvas size
                const scaledKeypoints = {
                    leftShoulder: { x: leftShoulder.x * scaleX, y: leftShoulder.y * scaleY },
                    rightShoulder: { x: rightShoulder.x * scaleX, y: rightShoulder.y * scaleY },
                    leftHip: { x: leftHip.x * scaleX, y: leftHip.y * scaleY },
                    rightHip: { x: rightHip.x * scaleX, y: rightHip.y * scaleY }
                };

                // Calculate dress position and size
                const centerX = (scaledKeypoints.leftShoulder.x + scaledKeypoints.rightShoulder.x) / 2;
                const torsoY = (scaledKeypoints.leftShoulder.y + scaledKeypoints.leftHip.y) / 2;
                const shoulderWidth = Math.abs(scaledKeypoints.rightShoulder.x - scaledKeypoints.leftShoulder.x);
                const torsoHeight = Math.abs(scaledKeypoints.leftHip.y - scaledKeypoints.leftShoulder.y);
                
                // Make dress slightly wider and longer for better coverage
                const dressWidth = shoulderWidth * 1.5;
                const dressHeight = torsoHeight * 1.8;
                
                // Position dress
                const dressX = centerX - dressWidth / 2;
                const dressY = scaledKeypoints.leftShoulder.y - dressHeight * 0.1; // Start slightly above shoulders

                // Set blend mode for better overlay effect
                ctx.globalAlpha = 0.8;
                ctx.globalCompositeOperation = 'multiply';
                
                // Draw the dress
                ctx.drawImage(dressImage, dressX, dressY, dressWidth, dressHeight);
                
                // Reset canvas properties
                ctx.globalAlpha = 1.0;
                ctx.globalCompositeOperation = 'source-over';

                updateStatus('🎉 Dress fitted successfully! How do you look?', 'success');
                console.log('✅ Dress overlay applied successfully');
                
            } else {
                updateStatus('Could not detect clear body pose. Please use a clearer photo with better lighting.', 'error');
                console.log('❌ Insufficient confidence in keypoint detection');
            }
        } else {
            updateStatus('No person detected in the image. Please upload a photo with a clear view of yourself.', 'error');
            console.log('❌ No poses detected');
        }
    } catch (error) {
        console.error('❌ Error during pose estimation:', error);
        updateStatus('An error occurred while processing your photo. Please try again.', 'error');
    } finally {
        hideLoading();
    }
});

// Handle reset button
resetButton.addEventListener('click', () => {
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Reset file input
    upload.value = '';
    
    // Reset state
    isImageUploaded = false;
    uploadedImage = new Image();
    
    // Update UI
    updateButtonState();
    resetButton.style.display = 'none';
    updateStatus('Ready for a new photo! Please upload an image to begin.', 'info');
    
    console.log('✅ Reset completed');
});

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 WebAR Virtual Dress Try-On starting...');
    
    // Check browser support
    if (typeof tf === 'undefined') {
        updateStatus('Your browser does not support the required AI features. Please try a modern browser.', 'error');
        return;
    }
    
    updateButtonState();
    initializePoseDetection();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        console.log('🔇 Page hidden - pausing operations');
    } else {
        console.log('🔊 Page visible - resuming operations');
    }
});