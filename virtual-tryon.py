"""Virtual Try-On with Gradio and Vertex AI."""
# ruff: noqa: E501

# %% IMPORTS

import io
import logging
import os

import gradio as gr
from PIL import Image

try:
    import google.cloud.logging as gcl
    from google.cloud import aiplatform
    from vertexai.preview.vision_models import ImageGenerationModel
    VERTEX_AI_AVAILABLE = True
except ImportError:
    print("Warning: Google Cloud AI Platform not available. Using fallback mode.")
    VERTEX_AI_AVAILABLE = False

# %% ENVIRONS

GOOGLE_CLOUD_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
GOOGLE_CLOUD_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "your-project-id")

LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")

# %% CONFIGS

THEME = "soft"
TITLE = "Bharat Heritage - Virtual Try-On"
FAVICON = "assets/favicon.ico"
DESCRIPTION = """
**Experience Traditional Indian Attire with AI-Powered Virtual Try-On**

Discover the beauty of Indian heritage clothing through our advanced virtual try-on technology. Upload your photo and select from traditional Indian garments like sarees, lehengas, kurtas, and more to see how they look on you.

**Supported Traditional Wear:** Sarees, Lehengas, Kurtas, Sherwanis, Anarkalis, Dhoti-Kurta sets, Traditional Blouses, and Ethnic Accessories.

**Note:** This is a demonstration interface. For full functionality, Google Cloud Vertex AI configuration is required.
"""
FOOTER = (
    "<center>"
    "<a href='main.html'>← Back to Bharat Heritage</a> | "
    "Powered by Google Vertex AI Technology"
    "</center>"
)

# %% CLIENTS

client = None
if VERTEX_AI_AVAILABLE and GOOGLE_CLOUD_PROJECT != "your-project-id":
    try:
        aiplatform.init(project=GOOGLE_CLOUD_PROJECT, location=GOOGLE_CLOUD_LOCATION)
        client = ImageGenerationModel.from_pretrained("imagegeneration@006")
    except Exception as e:
        print(f"Warning: Could not initialize Vertex AI client: {e}")
        client = None

# %% LOGGING

try:
    if VERTEX_AI_AVAILABLE:
        logging_client = gcl.Client()
        logging_client.setup_logging(log_level=getattr(logging, LOGGING_LEVEL))
except Exception as e:
    print(f"Warning: Could not setup cloud logging: {e}")
    logging.basicConfig(level=getattr(logging, LOGGING_LEVEL))

# %% FUNCTIONS

def create_demo_image(person_image: Image.Image, product_image: Image.Image) -> Image.Image:
    """Creates a demo composite image when AI service is not available."""
    # Create a simple side-by-side composite for demonstration
    width = max(person_image.width, product_image.width) * 2
    height = max(person_image.height, product_image.height)
    
    composite = Image.new('RGB', (width, height), (255, 255, 255))
    
    # Resize images to fit
    person_resized = person_image.resize((width//2, height))
    product_resized = product_image.resize((width//2, height))
    
    composite.paste(person_resized, (0, 0))
    composite.paste(product_resized, (width//2, 0))
    
    return composite

def generate_try_on_images(
    person_image: Image.Image,
    product_image: Image.Image,
    base_steps: int = 32,
    image_count: int = 1,
) -> list[Image.Image]:
    """Generates images using the Virtual Try-On API or demo mode."""
    if not person_image:
        raise gr.Error("Please upload a person image.", title="Missing Person Image")
    if not product_image:
        raise gr.Error("Please upload a traditional wear image.", title="Missing Product Input")
    
    if not client or not VERTEX_AI_AVAILABLE:
        # Demo mode - create a simple composite
        gr.Info("Demo mode: Creating composite image. For AI-powered try-on, configure Google Cloud Vertex AI.")
        demo_image = create_demo_image(person_image, product_image)
        return [demo_image]
    
    try:
        # This is a simplified approach - you may need to adjust based on your specific Vertex AI setup
        prompt = f"A person wearing traditional Indian clothing, high quality, realistic, {base_steps} steps"
        
        response = client.generate_images(
            prompt=prompt,
            number_of_images=image_count,
        )
        
        images = []
        for generated_image in response.images:
            # Convert the generated image to PIL Image
            image_bytes = generated_image._image_bytes
            pil_image = Image.open(io.BytesIO(image_bytes))
            images.append(pil_image)
        
        return images
        
    except Exception as error:
        gr.Warning(f"AI generation failed: {error}. Showing demo composite instead.")
        demo_image = create_demo_image(person_image, product_image)
        return [demo_image]

# %% SAMPLE IMAGES

def get_sample_traditional_wear():
    """Returns sample traditional wear images for demonstration."""
    return [
        "https://images.pexels.com/photos/8442493/pexels-photo-8442493.jpeg",
        "https://images.pexels.com/photos/8442492/pexels-photo-8442492.jpeg",
        "https://images.pexels.com/photos/8442491/pexels-photo-8442491.jpeg"
    ]

# %% INTERFACES

with gr.Blocks(title=TITLE, theme=THEME, fill_width=True, css="""
    .gradio-container {
        background: linear-gradient(120deg, #eecda3 0%, #ef629f 100%);
        min-height: 100vh;
    }
    .main-container {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem;
        box-shadow: 0 6px 48px rgba(0,0,0,.10);
    }
    .heritage-header {
        background: linear-gradient(90deg, orange, white, green);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .status-info {
        background: #e8f4fd;
        border: 1px solid #bee5eb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        text-align: center;
    }
""") as demo:
    with gr.Column(elem_classes="main-container"):
        gr.Markdown(f"# {TITLE}", elem_classes="heritage-header")
        gr.Markdown(DESCRIPTION)
        
        # Status information
        if not VERTEX_AI_AVAILABLE or GOOGLE_CLOUD_PROJECT == "your-project-id":
            gr.Markdown("""
            <div class="status-info">
            <strong>🔧 Configuration Required</strong><br>
            This demo runs in fallback mode. For AI-powered virtual try-on:<br>
            1. Install: <code>pip install google-cloud-aiplatform vertexai</code><br>
            2. Set up Google Cloud authentication<br>
            3. Configure GOOGLE_CLOUD_PROJECT in your .env file
            </div>
            """)
        else:
            gr.Markdown("""
            <div class="status-info">
            <strong>✅ AI Service Ready</strong><br>
            Google Cloud Vertex AI is configured and ready for virtual try-on generation.
            </div>
            """)
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Upload Your Photo")
                person_image = gr.Image(
                    label="Your Photo", 
                    type="pil", 
                    height=400,
                    info="Upload a clear photo of yourself for the best results"
                )
                
                gr.Markdown("### Select Traditional Wear")
                product_image = gr.Image(
                    label="Traditional Wear", 
                    type="pil", 
                    height=400,
                    info="Upload an image of the traditional Indian garment you want to try on"
                )
                
                with gr.Row():
                    base_steps = gr.Slider(
                        minimum=1,
                        maximum=150,
                        value=32,
                        step=1,
                        label="Quality Steps",
                        info="Higher value for better quality (when AI is enabled).",
                    )
                    image_count = gr.Slider(
                        minimum=1,
                        maximum=4,
                        value=1,
                        step=1,
                        label="Number of Images",
                        info="Generate up to 4 variations (when AI is enabled).",
                    )
                
                generate_button = gr.Button(
                    "✨ Try On Traditional Wear", 
                    variant="primary", 
                    size="lg"
                )
                
            with gr.Column():
                gr.Markdown("### Virtual Try-On Results")
                output_image = gr.Gallery(
                    label="Your Virtual Try-On", 
                    columns=2,
                    height=600,
                    show_label=True
                )
                
                gr.Markdown("### Sample Traditional Wear")
                gr.Markdown("*You can download these sample images and upload them as traditional wear*")
                
                sample_gallery = gr.Gallery(
                    value=get_sample_traditional_wear(),
                    label="Sample Traditional Wear",
                    columns=3,
                    height=200,
                    allow_preview=True
                )
        
        generate_button.click(
            fn=generate_try_on_images,
            inputs=[person_image, product_image, base_steps, image_count],
            outputs=output_image,
        )
        
        gr.Markdown(value=FOOTER)

# %% ENTRYPOINTS

if __name__ == "__main__":
    print("🎭 Starting Bharat Heritage Virtual Try-On Service")
    print("=" * 50)
    
    if not VERTEX_AI_AVAILABLE:
        print("⚠️  Running in demo mode - install google-cloud-aiplatform for full AI features")
    elif GOOGLE_CLOUD_PROJECT == "your-project-id":
        print("⚠️  Please configure GOOGLE_CLOUD_PROJECT in your .env file")
    else:
        print("✅ AI service configured and ready")
    
    demo.queue()
    demo.launch(
        favicon_path=FAVICON if os.path.exists(FAVICON) else None, 
        pwa=True,
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )