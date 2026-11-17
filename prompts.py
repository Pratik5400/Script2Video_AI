
"""
P36 - Script2Video AI
U1: Scene Prompt Templates

This module provides:
1. Zero-shot prompting
2. Few-shot prompting
3. Reusable scene image prompt templates
"""

SCENE_PROMPT_TEMPLATE = """
Create a cinematic visual for the following video scene.

VIDEO TOPIC: {topic}
SCENE NUMBER: {scene_number}
SCENE TITLE: {scene_title}
SCENE DESCRIPTION: {description}

VISUAL REQUIREMENTS:
- Landscape 16:9 composition
- Cinematic and realistic visual style
- Professional lighting and sharp details
- Strong visual storytelling
- Consistent visual theme
- No text, subtitles, logos or watermarks

The image must clearly represent the scene description.
"""


ZERO_SHOT_TEMPLATE = """
You are a professional video scriptwriter.

Create a six-scene video script about:

TOPIC: {topic}

Generate six connected scenes in chronological order.
Each scene must have narration, a visual description,
an image prompt and a duration.

Make the video engaging, informative and suitable
for a short 30-60 second narrated video.
"""


FEW_SHOT_TEMPLATE = """
You are an expert cinematic video scriptwriter.

Follow this example of a six-scene video structure.

EXAMPLE TOPIC: The Importance of Renewable Energy

EXAMPLE:
1. Introduction - Show the growing energy demand.
2. Problem - Show pollution from fossil fuels.
3. Solution - Introduce solar energy.
4. Innovation - Show wind turbines.
5. Impact - Show a cleaner environment.
6. Conclusion - Show a sustainable future.

Now create a NEW six-scene video script.

TOPIC: {topic}

Use the example only to understand the structure.
Do not copy its content.

Make the scenes logically connected and engaging.
"""


def get_script_prompt(topic, technique="zero-shot"):
    """
    Return a script-generation prompt based on
    the selected prompting technique.
    """

    topic = topic.strip()

    if not topic:
        raise ValueError("Topic cannot be empty.")

    if technique == "zero-shot":
        return ZERO_SHOT_TEMPLATE.format(topic=topic)

    elif technique == "few-shot":
        return FEW_SHOT_TEMPLATE.format(topic=topic)

    else:
        raise ValueError("Unsupported prompting technique.")


def create_scene_image_prompt(topic, scene):
    """
    Generate a reusable image prompt for each scene.
    """

    return SCENE_PROMPT_TEMPLATE.format(
        topic=topic,
        scene_number=scene["scene_number"],
        scene_title=scene["scene_title"],
        description=scene["visual_description"]
    )
