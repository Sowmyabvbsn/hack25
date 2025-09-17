const upload = document.getElementById('uploadImage');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const tryOnButton = document.getElementById('tryOnButton');

let uploadedImage = new Image();
let dressImage = new Image(); // dress overlay image
dressImage.src = 'dress.png'; // your dress image path

// Load dress image
dressImage.onload = () => {
    console.log('Dress image loaded');
};

// Handle image upload
upload.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = () => {
            uploadedImage.src = reader.result;
            uploadedImage.onload = () => {
                // Resize canvas to image size
                canvas.width = uploadedImage.width;
                canvas.height = uploadedImage.height;
                ctx.drawImage(uploadedImage, 0, 0);
            };
        };
        reader.readAsDataURL(file);
    }
});

// Initialize pose detection model
let detector;

async function init() {
    detector = await poseDetection.createDetector(poseDetection.SupportedModels.MoveNet);
}

init();

tryOnButton.addEventListener('click', async () => {
    if (!uploadedImage.src || !detector) return;
    ctx.drawImage(uploadedImage, 0, 0);
    
    // Detect pose
    const poses = await detector.estimatePoses(uploadedImage);
    if (poses.length > 0) {
        const keypoints = poses[0].keypoints;
        // Example: Find shoulder and waist positions
        const leftShoulder = keypoints.find(k => k.name === 'left_shoulder');
        const rightShoulder = keypoints.find(k => k.name === 'right_shoulder');
        const leftHip = keypoints.find(k => k.name === 'left_hip');
        const rightHip = keypoints.find(k => k.name === 'right_hip');

        if (leftShoulder && rightShoulder && leftHip && rightHip) {
            // Calculate overlay position and size
            const x = (leftShoulder.x + rightShoulder.x) / 2;
            const y = (leftShoulder.y + leftHip.y) / 2;

            const width = Math.abs(rightShoulder.x - leftShoulder.x) * 1.2;
            const height = Math.abs(leftHip.y - leftShoulder.y) * 1.3;

            // Draw dress image (assuming dress.png is transparent PNG)
            ctx.drawImage(dressImage, x - width/2, y, width, height);
        }
    }
});
