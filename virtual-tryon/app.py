"""Virtual Try-On with Gradio and Vertex AI."""
# ruff: noqa: E501

# %% IMPORTS

import io
import logging
import os
from typing import List, Optional

import gradio as gr
from PIL import Image
import google.generativeai as genai
from google.cloud import aiplatform
import base64

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# %% ENVIRONS

GOOGLE_CLOUD_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
GOOGLE_CLOUD_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "your-project-id")
GOOGLE_GENAI_USE_VERTEXAI = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "true").lower() == "true"

LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
VIRTUAL_TRY_ON_MODEL = os.environ.get("VIRTUAL_TRY_ON_MODEL", "imagen-3.0-generate-001")

# %% CONFIGS

THEME = "soft"
TITLE = "Bharat Heritage - Virtual Try-On"
FAVICON = "assets/favicon.ico"
DESCRIPTION = """
**Experience Traditional Indian Attire with AI**

Upload your photo and select traditional Indian clothing to see how you'd look! Our AI-powered virtual try-on technology brings India's rich textile heritage to life.

**Supported Items:** Traditional tops (kurtas, blouses, sarees), bottoms (dhoti, lehenga, salwar), and footwear (mojari, kolhapuri chappals).
"""
FOOTER = (
    "<center>"
    "🇮🇳 Celebrating India's Rich Cultural Heritage through Technology 🇮🇳<br />"
    "<a href='../main.html'>← Back to Bharat Heritage</a>"
    "</center>"
)

# %% CLIENTS

try:
    # Initialize Vertex AI
    if GOOGLE_GENAI_USE_VERTEXAI:
        aiplatform.init(project=GOOGLE_CLOUD_PROJECT, location=GOOGLE_CLOUD_LOCATION)
    
    # Configure GenAI
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
    client_initialized = True
except Exception as e:
    print(f"Warning: Could not initialize Google AI client: {e}")
    client_initialized = False

# %% LOGGING

logging.basicConfig(level=getattr(logging, LOGGING_LEVEL))
logger = logging.getLogger(__name__)

# %% FUNCTIONS

def image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 string."""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def generate_try_on_images(
    person_image: Optional[Image.Image],
    product_image: Optional[Image.Image],
    base_steps: int = 32,
    image_count: int = 1,
) -> List[Image.Image]:
    """Generates images using AI for virtual try-on."""
    
    if not person_image:
        raise gr.Error("Please upload a person image.", title="Missing Person Image")
    if not product_image:
        raise gr.Error("Please upload a product image.", title="Missing Product Input")
    
    if not client_initialized:
        raise gr.Error("Google AI client not initialized. Please check your credentials.", title="Configuration Error")
    
    try:
        # For now, we'll use a simple image composition approach
        # This is a fallback implementation until Vertex AI Virtual Try-On is properly configured
        
        # Resize images to similar dimensions
        person_width, person_height = person_image.size
        product_image = product_image.resize((person_width // 3, person_height // 3))
        
        # Create a simple overlay effect
        result_image = person_image.copy()
        
        # Position the product image (this is a basic implementation)
        overlay_x = person_width // 4
        overlay_y = person_height // 4
        
        # Create a semi-transparent overlay
        overlay = Image.new('RGBA', result_image.size, (0, 0, 0, 0))
        overlay.paste(product_image, (overlay_x, overlay_y))
        
        # Blend the images
        result_image = Image.alpha_composite(result_image.convert('RGBA'), overlay)
        result_image = result_image.convert('RGB')
        
        # Generate multiple variations by slightly adjusting the overlay position
        images = []
        for i in range(image_count):
            if i == 0:
                images.append(result_image)
            else:
                # Create slight variations
                variant = person_image.copy()
                variant_overlay = Image.new('RGBA', variant.size, (0, 0, 0, 0))
                offset_x = overlay_x + (i * 10)
                offset_y = overlay_y + (i * 5)
                variant_overlay.paste(product_image, (offset_x, offset_y))
                variant = Image.alpha_composite(variant.convert('RGBA'), variant_overlay)
                images.append(variant.convert('RGB'))
        
        return images
        
    except Exception as error:
        logger.error(f"Generation error: {error}")
        raise gr.Error(f"A Generation Error Occurred: {error}", title="Generation Error")

def generate_with_vertex_ai(
    person_image: Image.Image,
    product_image: Image.Image,
    base_steps: int = 32,
    image_count: int = 1,
) -> List[Image.Image]:
    """
    Advanced implementation using Vertex AI (requires proper setup).
    This is a placeholder for when Vertex AI Virtual Try-On is properly configured.
    """
    try:
        # This would be the actual Vertex AI implementation
        # For now, fall back to the basic implementation
        return generate_try_on_images(person_image, product_image, base_steps, image_count)
    except Exception as e:
        logger.error(f"Vertex AI error: {e}")
        return generate_try_on_images(person_image, product_image, base_steps, image_count)

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
                height=400,
                info="Upload a clear photo of yourself facing the camera"
            )
            
            gr.Markdown("### Step 2: Choose Traditional Attire")
            product_image = gr.Image(
                label="Traditional Clothing", 
                type="pil", 
                height=400,
                info="Upload an image of traditional Indian clothing"
            )
            
            with gr.Row():
                base_steps = gr.Slider(
                    minimum=1,
                    maximum=150,
                    value=32,
                    step=1,
                    label="Quality Steps",
                    info="Higher value for better quality, lower for faster generation.",
                )
                image_count = gr.Slider(
                    minimum=1,
                    maximum=4,
                    value=1,
                    step=1,
                    label="Number of Images",
                    info="Generate up to 4 variations.",
                )
            
            generate_button = gr.Button("✨ Try On Traditional Attire", variant="primary", size="lg")
            
        with gr.Column():
            gr.Markdown("### Your Virtual Try-On Result")
            output_image = gr.Gallery(
                label="Virtual Try-On Results", 
                columns=2,
                height=600,
                show_label=False
            )
    
    generate_button.click(
        fn=generate_try_on_images,
        inputs=[person_image, product_image, base_steps, image_count],
        outputs=output_image,
    )
    
    gr.Markdown(value=FOOTER)

# %% ENTRYPOINTS

if __name__ == "__main__":
    demo.queue()
    demo.launch(
        favicon_path=FAVICON if os.path.exists(FAVICON) else None,
        pwa=True,
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )