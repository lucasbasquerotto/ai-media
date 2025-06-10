import os
import shutil
import requests
from pathlib import Path

def load_guidelines(project_path: str) -> str:
    """Load project guidelines from YAML file as string."""
    guidelines_path = os.path.join(project_path, "guidelines.yaml")
    if not os.path.exists(guidelines_path):
        return ""

    with open(guidelines_path, 'r', encoding='utf-8') as f:
        return f.read()

def get_previous_chapters(chapter_path: str) -> list:
    """Get content from previous chapters in the same arc for context."""
    chapter_dir = os.path.dirname(chapter_path)
    chapter_file = os.path.basename(chapter_path)

    # Extract chapter number (e.g., "003.txt" -> 3)
    try:
        current_num = int(Path(chapter_file).stem)
    except ValueError:
        return []

    previous_chapters = []
    for i in range(1, current_num):
        prev_file = f"{i:03d}.txt"
        prev_path = os.path.join(chapter_dir, prev_file)
        if os.path.exists(prev_path):
            with open(prev_path, 'r', encoding='utf-8') as f:
                previous_chapters.append(f"Chapter {i}:\n{f.read()}")

    return previous_chapters

def get_previous_chapters_sketches(sketch_path: str) -> list:
    """Get content from previous chapter sketches in the same arc for context."""
    chapter_dir = os.path.dirname(sketch_path)
    chapter_file = os.path.basename(sketch_path)

    # Extract chapter number (e.g., "003.png" -> 3)
    try:
        current_num = int(Path(chapter_file).stem)
    except ValueError:
        return []

    previous_chapters = []
    for i in range(1, current_num):
        prev_file = f"{i:03d}.png"
        prev_path = os.path.join(chapter_dir, prev_file)
        if os.path.exists(prev_path):
            previous_chapters.append(prev_path)

    return previous_chapters

class ContentItem:
    def __init__(self, content_type: str, content: str):
        self.content_type = content_type
        self.content = content

def generate_image_with_openai(content_items: list[ContentItem], tmp_path: str, output_path: str):
    return

def create_comic_sketch_with_openai(project_path: str, chapter_path: str, tmp_path: str, output_path: str) -> None:
    """
    Create a comic chapter sketch using OpenAI's image generation.

    Args:
        project_path (str): Path to the project directory
        chapter_path (str): Path to the chapter text file
        tmp_path (str): Temporary path to store the AI output
        output_path (str): Final path where the sketch image will be saved
    """
    from openai import OpenAI

    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY')) # Load guidelines and chapter content
    guidelines = load_guidelines(project_path)

    with open(chapter_path, 'r', encoding='utf-8') as f:
        chapter_content = f.read()    # Get previous chapters for context
    previous_chapters = get_previous_chapters(chapter_path)

    # Get previous chapter sketches for visual context
    previous_sketches = get_previous_chapters_sketches(output_path)

    # Build context for the AI prompt
    context = f"""
        Project Guidelines:
        {guidelines}

        Previous chapters for context:
        {chr(10).join(previous_chapters[-2:]) if previous_chapters else 'No previous chapters'}

        Current chapter to sketch:
        {chapter_content}
    """

    # Add previous sketches information if available
    if previous_sketches:
        context += "\n\nNote: This is part of a series. Please maintain visual consistency " \
            + "with previous sketches in the same style and composition approach."

    # Create prompt for a simple comic sketch
    prompt = f"""Create a simple comic book sketch/storyboard panel based on this story content:

        {context}

        Requirements:
        - Simple art style (more focused on composition, story and interactions than detail)
        - Webtoon panel layout (long strip format)
        - Basic geometric shapes and simple character silhouettes
        - Focus on the key scene/moment from the chapter
        - Include basic speech bubbles or text if there's dialogue
        - Minimalist sketch style, not detailed artwork
        - Single panel composition
        - Style: Simple sketch, comic book or webtoon storyboard style
    """

    try:
        # Generate image using DALL-E with previous sketches as reference if available
        if previous_sketches:
            # Use vision model to analyze previous sketches for consistency
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]

            # Add previous sketches as image references (limit to last 2 to avoid token limits)
            for sketch_path in previous_sketches[-2:]:
                import base64
                with open(sketch_path, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                messages[0]["content"].append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}"
                    }
                })

            response = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=messages,
                max_tokens=300
            )

            # Extract image generation prompt from the response
            vision_prompt = response.choices[0].message.content

            # Generate image using DALL-E with the refined prompt
            response = client.images.generate(
                model="dall-e-3",
                prompt=vision_prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
        else:
            # Generate image using DALL-E without previous sketch context
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )

        # Download and save the image to temporary path first
        image_url = response.data[0].url
        image_response = requests.get(image_url, timeout=30)
        image_response.raise_for_status()

        # Ensure temporary directory exists
        os.makedirs(os.path.dirname(tmp_path), exist_ok=True)

        # Save to temporary path first
        with open(tmp_path, 'wb') as f:
            f.write(image_response.content)

        print(f"✅ Sketch downloaded to temporary path: {tmp_path}")

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Move from temporary to final output path
        shutil.move(tmp_path, output_path)

        print(f"✅ Sketch moved to final destination: {output_path}")
    except Exception as e:
        print(f"❌ Error creating sketch: {str(e)}")
        raise

def create_blank_sketch(output_path: str) -> None:
    """
    Create a blank sketch image with a white background.

    Args:
        output_path (str): Path where the blank sketch image will be saved
    """
    from PIL import Image

    # Create a blank white image
    img = Image.new('RGB', (1024, 1024), color='white')
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    img.save(output_path)
    print(f"✅ Blank sketch created at: {output_path}")

def create_sketch(
    project: str,
    project_path: str,
    chapter_path: str,
    tmp_path: str,
    output_path: str,
) -> None:
    """
    Create a simple sketch for a chapter using AI.

    Args:
        project (str): Project name
        project_path (str): Path to the project directory
        chapter_path (str): Path to the chapter text file
        tmp_path (str): Temporary path for processing
        output_path (str): Path where the sketch image will be saved
    """
    print('-'*80)
    print(f"Project: {project}")
    print(f"Project path: {project_path}")
    print(f"Creating sketch for: {chapter_path}")
    print(f"Temporary path: {tmp_path}")
    print(f"Output: {output_path}")

    try:
        SKETCH_AI = os.getenv('SKETCH_AI', '').lower()
        if SKETCH_AI == 'void':
            create_blank_sketch(output_path)
        elif SKETCH_AI == 'openai':
            create_comic_sketch_with_openai(project_path, chapter_path, tmp_path, output_path)
        else:
            raise ValueError(f"Unknown SKETCH_AI value: {SKETCH_AI}. Expected 'void' or 'openai'.")
    except Exception as e:
        print(f"❌ Failed to create sketch: {str(e)}")
        raise

    print('-'*80)
