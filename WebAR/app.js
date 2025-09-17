const upload = document.getElementById('uploadImage');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const tryOnButton = document.getElementById('tryOnButton');

let uploadedImage = new Image();
<<<<<<< HEAD
let dressImage = new Image(); // dress overlay image
dressImage.src = 'image.png'; // your dress image path
=======
let dressImage = new Image();
dressImage.src = 'dress.png'; // Make sure dress.png is in your project folder
>>>>>>> 7c3c56977e334a30fc11e0e11892a71b33f1a172

dressImage.onload = () => {
    console.log('Dress image loaded');
};

// Initially disable the try button until model and image are ready
tryOnButton.disabled = true;

upload.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = () => {
            uploadedImage = new Image();
            uploadedImage.src = reader.result;
            uploadedImage.onload = () => {
                canvas.width = uploadedImage.width;
                canvas.height = uploadedImage.height;
                ctx.drawImage(uploadedImage, 0, 0);
                // Enable button only if pose detector is ready
                if (detector) tryOnButton.disabled = false;
            };
        };
        reader.readAsDataURL(file);
    }
});

let detector;

async function init() {
    try {
        detector = await poseDetection.createDetector(
            poseDetection.SupportedModels.MoveNet, 
            { modelType: poseDetection.movenet.modelType.SINGLEPOSE_LIGHTNING }
        );
        console.log('Pose detector initialized');
        // Enable try button if image uploaded before model ready
        if (uploadedImage.src) tryOnButton.disabled = false;
    } catch (err) {
        console.error('Failed to load pose detector', err);
    }
}

init();

tryOnButton.addEventListener('click', async () => {
    if (!uploadedImage.src || !detector) {
        console.log('Image or detector not ready');
        return;
    }

    ctx.drawImage(uploadedImage, 0, 0);

    try {
        const poses = await detector.estimatePoses(uploadedImage);

        if (poses.length > 0) {
            const keypoints = poses[0].keypoints;
            const leftShoulder = keypoints.find(k => k.name === 'left_shoulder');
            const rightShoulder = keypoints.find(k => k.name === 'right_shoulder');
            const leftHip = keypoints.find(k => k.name === 'left_hip');
            const rightHip = keypoints.find(k => k.name === 'right_hip');

            if (leftShoulder && rightShoulder && leftHip && rightHip) {
                const x = (leftShoulder.x + rightShoulder.x) / 2;
                const y = (leftShoulder.y + leftHip.y) / 2;
                const width = Math.abs(rightShoulder.x - leftShoulder.x) * 1.2;
                const height = Math.abs(leftHip.y - leftShoulder.y) * 1.3;

                ctx.drawImage(dressImage, x - width / 2, y, width, height);
                console.log('Dress overlay drawn');
            } else {
                console.log('Required keypoints missing');
            }
        } else {
            console.log('No poses detected');
        }
    } catch (error) {
        console.error('Error during pose estimation:', error);
    }
});
