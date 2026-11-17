"""
Unit & Integration Test Suite for P36 Script2Video AI - Unit 3 Pipeline

Test Areas Covered:
1. JSON script import and validation.
2. Single-image import and validation.
3. Six-image complete import and validation.
4. BLIP caption loading and parsing.
5. Cosine similarity calculation and heuristic thresholding.
6. Missing and corrupted image error handling.
7. ZIP archive extraction and structural validation.
8. Existing U1 and U2 regression validation.
"""

import os
import json
import shutil
import tempfile
import unittest
import zipfile
from io import BytesIO
from pathlib import Path
from PIL import Image

import prompts
import llm_service
from image_service import (
    validate_image_file,
    inspect_zip_contents,
    extract_and_validate_u3_zip,
    get_scene_image_path,
    load_generation_results,
    package_u3_output
)
from blip_service import (
    load_verification_results,
    load_caption_results,
    calculate_cosine_similarity_tokens,
    evaluate_heuristic_status,
    apply_heuristic_threshold,
    update_manual_review,
    generate_verification_summary,
    export_verification_report_markdown,
    DEFAULT_HEURISTIC_THRESHOLD
)


class TestU3Pipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.script_path = Path("generated/video_script.json")
        cls.zip_path = Path("generated/P36_U3_Output.zip")
        cls.images_dir = Path("generated/images")

    # ---------------- 1. JSON IMPORT ----------------
    def test_01_json_script_import_and_structure(self):
        """Test reading and schema compliance of generated/video_script.json."""
        self.assertTrue(self.script_path.exists(), "video_script.json must exist")
        with open(self.script_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("video_title", data)
        self.assertIn("topic", data)
        self.assertIn("total_duration", data)
        self.assertIn("scenes", data)

        scenes = data["scenes"]
        self.assertEqual(len(scenes), 6, "Expected exactly 6 scenes in script")

        for idx, scene in enumerate(scenes, start=1):
            self.assertEqual(scene["scene_number"], idx)
            self.assertTrue(len(scene["scene_title"].strip()) > 0)
            self.assertTrue(len(scene["narration"].strip()) > 0)
            self.assertTrue(len(scene["visual_description"].strip()) > 0)
            self.assertTrue(len(scene["image_prompt"].strip()) > 0)
            self.assertGreater(scene["duration_seconds"], 0)

    # ---------------- 2. ONE-IMAGE IMPORT ----------------
    def test_02_single_image_import_and_validation(self):
        """Test single scene image validation (scene_01.png)."""
        scene_1_img = self.images_dir / "scene_01.png"
        self.assertTrue(scene_1_img.exists(), "scene_01.png must exist for test")

        is_valid, err_msg = validate_image_file(scene_1_img)
        self.assertTrue(is_valid, f"scene_01.png validation failed: {err_msg}")
        self.assertEqual(err_msg, "")

        resolved_path = get_scene_image_path(1, self.images_dir)
        self.assertIsNotNone(resolved_path)
        self.assertTrue(resolved_path.exists())

    # ---------------- 3. SIX-IMAGE IMPORT ----------------
    def test_03_six_images_import_and_validation(self):
        """Test validation of all 6 scene images."""
        for scene_idx in range(1, 7):
            img_path = self.images_dir / f"scene_{scene_idx:02d}.png"
            self.assertTrue(img_path.exists(), f"scene_{scene_idx:02d}.png should exist")
            is_valid, err = validate_image_file(img_path)
            self.assertTrue(is_valid, f"Scene {scene_idx} image invalid: {err}")

            with Image.open(img_path) as img:
                width, height = img.size
                self.assertGreater(width, 100)
                self.assertGreater(height, 100)

    # ---------------- 4. BLIP CAPTION DISPLAY ----------------
    def test_04_blip_caption_loading_and_parsing(self):
        """Test loading and validating BLIP captions for all scenes."""
        captions = load_caption_results("generated")
        self.assertEqual(len(captions), 6, "Expected 6 caption results")

        for cap in captions:
            self.assertIn("scene_number", cap)
            self.assertIn("image_filename", cap)
            self.assertIn("blip_caption", cap)
            self.assertIn(cap["status"], ["Success", "Generated", "Failed"])
            self.assertTrue(len(cap["blip_caption"].strip()) > 0)

    # ---------------- 5. SIMILARITY CALCULATION & HEURISTIC THRESHOLD ----------------
    def test_05_similarity_calculation_and_heuristic_evaluation(self):
        """Test cosine similarity calculation, direct score handling, and thresholding."""
        # Test token-based cosine similarity calculation
        text_a = "futuristic city skyline at dawn with glowing neural networks"
        text_b = "a futuristic city skyline with glowing digital networks in morning light"
        text_c = "completely unrelated cooking recipe with tomatoes and pasta"

        sim_high = calculate_cosine_similarity_tokens(text_a, text_b)
        sim_low = calculate_cosine_similarity_tokens(text_a, text_c)

        # Ensure raw cosine similarity properties
        self.assertIsInstance(sim_high, float)
        self.assertGreater(sim_high, sim_low)
        self.assertGreaterEqual(sim_high, -1.0)
        self.assertLessEqual(sim_high, 1.0)

        # Test evaluation with heuristic threshold
        status_high = evaluate_heuristic_status(sim_high, threshold=0.40)
        status_low = evaluate_heuristic_status(sim_low, threshold=0.40)
        status_none = evaluate_heuristic_status(None, threshold=0.40)

        self.assertEqual(status_high, "Relevant")
        self.assertEqual(status_low, "Needs Review (Heuristic)")
        self.assertEqual(status_none, "Needs Review (Missing/Error)")

        # Verify negative score is NOT clamped to positive
        neg_val = -0.25
        status_neg = evaluate_heuristic_status(neg_val, threshold=0.0)
        self.assertEqual(status_neg, "Needs Review (Heuristic)")

    # ---------------- 6. MISSING-IMAGE & CORRUPTED HANDLING ----------------
    def test_06_missing_and_corrupted_image_handling(self):
        """Test resilience against missing images, 0-byte files, and corrupted headers."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            temp_images = temp_path / "images"
            temp_images.mkdir()

            # Create only scene 1 and scene 2; scene 3 is missing; scene 4 is 0-byte; scene 5 is bad header
            shutil.copy(self.images_dir / "scene_01.png", temp_images / "scene_01.png")
            shutil.copy(self.images_dir / "scene_02.png", temp_images / "scene_02.png")

            # 0-byte file
            (temp_images / "scene_04.png").touch()

            # Corrupted bytes file
            with open(temp_images / "scene_05.png", "wb") as bf:
                bf.write(b"NOT_A_VALID_PNG_HEADER_DATA")

            # Validate individual files
            v1, _ = validate_image_file(temp_images / "scene_01.png")
            self.assertTrue(v1)

            v4, err4 = validate_image_file(temp_images / "scene_04.png")
            self.assertFalse(v4)
            self.assertIn("empty", err4.lower())

            v5, err5 = validate_image_file(temp_images / "scene_05.png")
            self.assertFalse(v5)
            self.assertIn("corrupted", err5.lower())

            # Package into test zip
            test_zip = temp_path / "test_partial.zip"
            with zipfile.ZipFile(test_zip, "w") as zf:
                zf.write(temp_images / "scene_01.png", "P36_U3_Output/images/scene_01.png")
                zf.write(temp_images / "scene_04.png", "P36_U3_Output/images/scene_04.png")

            # Test extraction of partial zip into new target
            target_dest = temp_path / "extracted_partial"
            res = extract_and_validate_u3_zip(test_zip, target_dest)

            # Scene 1 should be valid; Scene 3 missing; Scene 4 invalid
            self.assertTrue(res["images"][1]["is_valid"])
            self.assertFalse(res["images"][3]["exists"])
            self.assertFalse(res["images"][4]["is_valid"])
            self.assertGreater(len(res["warnings"]), 0)

    # ---------------- 7. ZIP EXTRACTION ----------------
    def test_07_zip_archive_extraction_and_reporting(self):
        """Test inspecting and extracting the full P36_U3_Output.zip archive."""
        self.assertTrue(self.zip_path.exists(), "P36_U3_Output.zip must exist")

        # Test inspection
        inspection = inspect_zip_contents(self.zip_path)
        self.assertTrue(inspection["is_valid"])
        self.assertEqual(inspection["image_count"], 6)
        self.assertEqual(len(inspection["missing_metadata"]), 0)

        # Test extraction into temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            dest = Path(temp_dir) / "output"
            extract_res = extract_and_validate_u3_zip(self.zip_path, dest)

            self.assertTrue(extract_res["success"])
            self.assertEqual(len(extract_res["errors"]), 0)

            # Verify extracted files exist and are valid
            for s_idx in range(1, 7):
                img_path = dest / "images" / f"scene_{s_idx:02d}.png"
                self.assertTrue(img_path.exists())
                is_valid, _ = validate_image_file(img_path)
                self.assertTrue(is_valid)

            # Verify metadata
            self.assertIn("verification_results.json", extract_res["metadata_loaded"])
            verif_data = extract_res["metadata_loaded"]["verification_results.json"]
            self.assertEqual(len(verif_data), 6)

    # ---------------- 8. EXISTING U1 & U2 FUNCTIONALITY ----------------
    def test_08_existing_u1_and_u2_functionality(self):
        """Verify U1 prompt engineering and U2 LLM schemas are preserved."""
        # U1: Zero-shot prompt generation
        prompt_zero = prompts.get_script_prompt("Space Exploration", "zero-shot")
        self.assertIn("Space Exploration", prompt_zero)
        self.assertIn("six-scene", prompt_zero.lower())

        # U1: Few-shot prompt generation
        prompt_few = prompts.get_script_prompt("Space Exploration", "few-shot")
        self.assertIn("Space Exploration", prompt_few)
        self.assertIn("EXAMPLE", prompt_few)

        # U1: Scene prompt template
        scene_dummy = {
            "scene_number": 1,
            "scene_title": "Launch",
            "visual_description": "Rocket launching into space."
        }
        scene_prompt = prompts.create_scene_image_prompt("Space Exploration", scene_dummy)
        self.assertIn("Space Exploration", scene_prompt)
        self.assertIn("Rocket launching into space.", scene_prompt)

        # U2: Script schema integrity
        schema = llm_service.SCRIPT_SCHEMA
        self.assertEqual(schema["type"], "OBJECT")
        self.assertIn("scenes", schema["properties"])
        scene_props = schema["properties"]["scenes"]["items"]["properties"]
        for required_prop in ["scene_number", "scene_title", "narration", "visual_description", "image_prompt", "duration_seconds"]:
            self.assertIn(required_prop, scene_props)


if __name__ == "__main__":
    unittest.main()
