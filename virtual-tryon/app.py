"""Virtual Try-On with Gradio and Google AI."""

import io
import logging
import os
from typing import List, Optional

import gradio as gr
from PIL import Image
import google.generativeai as genai
import base64

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed, using system environment variables")

# %% ENVIRONS

GOOGLE_CLOUD_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
GOOGLE_CLOUD_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "your-project-id")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")

# %% CONFIGS

THEME = "soft"
TITLE = "Bharat Heritage - Virtual Try-On"
FAVICON = "assets/favicon.ico"
DESCRIPTION = """
**Experience Traditional Indian Attire with AI**

Upload your photo and select traditional Indian clothing to see how you'd look! Our AI-powered virtual try-on technology brings India's rich textile heritage to life.

**Supported Items:** Traditional tops (kurtas, blouses, sarees), bottoms (dhoti, lehenga, salwar), and footwear (mojari, kolhapuri chappals).

*Note: This is a demo version using image composition. For best results, use clear photos with good lighting.*
"""
FOOTER = (
    "<center>"
    "🇮🇳 Celebrating India's Rich Cultural Heritage through Technology 🇮🇳<br />"
    "<a href='../main.html'>← Back to Bharat Heritage</a>"
    "</center>"
)

# %% CLIENTS

client_initialized = False
try:
    if GOOGLE_API_KEY:
        genai.configure(api_key=GOOGLE_API_KEY)
        client_initialized = True
        print("Google AI client initialized successfully")
    else:
        print("Warning: GOOGLE_API_KEY not found in environment variables")
except Exception as e:
    print(f"Warning: Could not initialize Google AI client: {e}")

# %% LOGGING

logging.basicConfig(level=getattr(logging, LOGGING_LEVEL))
logger = logging.getLogger(__name__)

# %% FUNCTIONS

def image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 string."""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def create_simple_overlay(person_image: Image.Image, product_image: Image.Image) -> Image.Image:
    """Create a simple overlay effect for virtual try-on."""
    # Convert to RGBA for transparency support
    person_rgba = person_image.convert('RGBA')
    product_rgba = product_image.convert('RGBA')
    
    # Resize product image to fit appropriately on person
    person_width, person_height = person_rgba.size
    
    # Scale product image to be about 1/3 the size of person image
    scale_factor = min(person_width // 3, person_height // 3) / max(product_rgba.size)
    new_size = (int(product_rgba.width * scale_factor), int(product_rgba.height * scale_factor))
    product_resized = product_rgba.resize(new_size, Image.Resampling.LANCZOS)
    
    # Position the product image (center-top area for clothing)
    overlay_x = (person_width - product_resized.width) // 2
    overlay_y = person_height // 4
    
    # Create result image
    result = person_rgba.copy()
    
    # Paste product with some transparency
    product_with_alpha = product_resized.copy()
    # Make it semi-transparent
    alpha = product_with_alpha.split()[-1]
    alpha = alpha.point(lambda p: int(p * 0.8))  # 80% opacity
    product_with_alpha.putalpha(alpha)
    
    # Paste onto result
    result.paste(product_with_alpha, (overlay_x, overlay_y), product_with_alpha)
    
    return result.convert('RGB')

def generate_try_on_images(
    person_image: Optional[Image.Image],
    product_image: Optional[Image.Image],
    base_steps: int = 32,
    image_count: int = 1,
) -> List[Image.Image]:
    """Generates images using simple image composition for virtual try-on."""
    
    if not person_image:
        raise gr.Error("Please upload a person image.", title="Missing Person Image")
    if not product_image:
        raise gr.Error("Please upload a product image.", title="Missing Product Input")
    
    try:
        images = []
        
        for i in range(image_count):
            if i == 0:
                # Main result
                result_image = create_simple_overlay(person_image, product_image)
                images.append(result_image)
            else:
                # Create variations by adjusting position slightly
                person_rgba = person_image.convert('RGBA')
                product_rgba = product_image.convert('RGBA')
                
                person_width, person_height = person_rgba.size
                scale_factor = min(person_width // 3, person_height // 3) / max(product_rgba.size)
                new_size = (int(product_rgba.width * scale_factor), int(product_rgba.height * scale_factor))
                product_resized = product_rgba.resize(new_size, Image.Resampling.LANCZOS)
                
                # Vary position slightly
                overlay_x = (person_width - product_resized.width) // 2 + (i * 10)
                overlay_y = person_height // 4 + (i * 5)
                
                result = person_rgba.copy()
                product_with_alpha = product_resized.copy()
                alpha = product_with_alpha.split()[-1]
                alpha = alpha.point(lambda p: int(p * (0.8 - i * 0.1)))  # Varying opacity
                product_with_alpha.putalpha(alpha)
                
                result.paste(product_with_alpha, (overlay_x, overlay_y), product_with_alpha)
                images.append(result.convert('RGB'))
        
        return images
        
    except Exception as error:
        logger.error(f"Generation error: {error}")
        raise gr.Error(f"A Generation Error Occurred: {error}", title="Generation Error")

# %% SAMPLE IMAGES

def load_sample_images():
    """Load sample images for demonstration."""
    samples = {
        "person": [],
        "clothing": []
    }
    
    # You can add sample images here if needed
    return samples

# %% INTERFACES

with gr.Blocks(title=TITLE, theme=THEME, fill_width=True) as demo:
    gr.Markdown(f"# {TITLE}")
    gr.Markdown(DESCRIPTION)
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Step 1: Upload Your Photo")
            person_image = gr.Image(
                label="Your Photo", 
                type="pil", 
                height=400
            )
            gr.Markdown("*Upload a clear photo of yourself facing the camera*")
            
            gr.Markdown("### Step 2: Choose Traditional Attire")
            product_image = gr.Image(
                label="Traditional Clothing", 
                type="pil", 
                height=400
            )
            gr.Markdown("*Upload an image of traditional Indian clothing*")
            
            with gr.Row():
                base_steps = gr.Slider(
                    minimum=1,
                    maximum=150,
                    value=32,
                    step=1,
                    label="Quality Steps"
                )
                gr.Markdown("*Higher value for better quality (currently for demo purposes)*")
                
                image_count = gr.Slider(
                    minimum=1,
                    maximum=4,
                    value=1,
                    step=1,
                    label="Number of Images"
                )
                gr.Markdown("*Generate up to 4 variations*")
            
            generate_button = gr.Button("✨ Try On Traditional Attire", variant="primary", size="lg")
            
        with gr.Column():
            gr.Markdown("### Your Virtual Try-On Result")
            output_image = gr.Gallery(
                label="Virtual Try-On Results", 
                columns=2,
                height=600,
                show_label=False
            )
    
    # Examples section
    gr.Markdown("### 💡 Tips for Best Results")
    gr.Markdown("""
    - Use clear, well-lit photos
    - Face the camera directly
    - Choose clothing images with transparent or simple backgrounds
    - Traditional Indian attire works best (kurtas, sarees, lehengas, etc.)
    """)
    
    generate_button.click(
        fn=generate_try_on_images,
        inputs=[person_image, product_image, base_steps, image_count],
        outputs=output_image,
    )
    
    gr.Markdown(value=FOOTER)

# %% ENTRYPOINTS

if __name__ == "__main__":
    print("🎨 Starting Bharat Heritage Virtual Try-On...")
    print(f"🌐 Server will be available at: http://localhost:7860")
    
    demo.queue()
    demo.launch(
        favicon_path=FAVICON if os.path.exists(FAVICON) else None,
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )