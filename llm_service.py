
"""
P36 - Script2Video AI
U2: LLM-based Six Scene Script Generator

Uses Google's Gemini API to generate structured
video scripts from user-provided topics.
"""

import os
import json

from dotenv import load_dotenv
from google import genai
from google.genai import types

from prompts import get_script_prompt

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


def get_gemini_client():
    """Initialize Gemini API client."""

    if not API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is missing. Check your .env file."
        )

    return genai.Client(api_key=API_KEY)


SCRIPT_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "video_title": {
            "type": "STRING"
        },
        "topic": {
            "type": "STRING"
        },
        "total_duration": {
            "type": "INTEGER"
        },
        "scenes": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "scene_number": {
                        "type": "INTEGER"
                    },
                    "scene_title": {
                        "type": "STRING"
                    },
                    "narration": {
                        "type": "STRING"
                    },
                    "visual_description": {
                        "type": "STRING"
                    },
                    "image_prompt": {
                        "type": "STRING"
                    },
                    "duration_seconds": {
                        "type": "INTEGER"
                    }
                },
                "required": [
                    "scene_number",
                    "scene_title",
                    "narration",
                    "visual_description",
                    "image_prompt",
                    "duration_seconds"
                ]
            }
        }
    },
    "required": [
        "video_title",
        "topic",
        "total_duration",
        "scenes"
    ]
}


def generate_video_script(topic, technique="zero-shot"):
    """
    Generate a structured six-scene video script.

    Args:
        topic: User's video topic.
        technique: zero-shot or few-shot.

    Returns:
        Dictionary containing six video scenes.
    """

    if not topic or not topic.strip():
        raise ValueError("Please enter a valid topic.")

    client = get_gemini_client()

    base_prompt = get_script_prompt(topic, technique)

    instructions = """
    Return a complete six-scene video script.

    Requirements:
    1. Generate exactly six scenes.
    2. Total video duration must be 30-60 seconds.
    3. Use durations of 7 or 8 seconds per scene.
    4. Total duration should be approximately 45 seconds.
    5. Narration should sound natural when spoken aloud.
    6. Each scene must have a detailed visual description.
    7. Each image prompt must describe a cinematic image.
    8. Scenes must follow a logical sequence.
    9. Do not include markdown formatting.
    """

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=base_prompt + "\n\n" + instructions,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_json_schema=SCRIPT_SCHEMA,
            temperature=0.7,
            max_output_tokens=5000
        )
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    script = json.loads(response.text)

    # Validate the generated script.
    scenes = script.get("scenes", [])

    if len(scenes) != 6:
        raise ValueError(
            f"Expected 6 scenes, but received {len(scenes)}."
        )

    for index, scene in enumerate(scenes, start=1):
        if scene["scene_number"] != index:
            raise ValueError("Scene numbering is incorrect.")

        if not all([
            scene["scene_title"].strip(),
            scene["narration"].strip(),
            scene["visual_description"].strip(),
            scene["image_prompt"].strip()
        ]):
            raise ValueError(
                f"Scene {index} contains missing information."
            )

    total_duration = sum(
        scene["duration_seconds"] for scene in scenes
    )

    if not 30 <= total_duration <= 60:
        raise ValueError(
            f"Invalid video duration: {total_duration} seconds."
        )

    script["total_duration"] = total_duration

    return script
