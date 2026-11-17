"""
P36 - Script2Video AI
U3: Image Asset Management & Colab Integration Service

This service handles:
1. Validation and extraction of Colab-generated assets (P36_U3_Output.zip).
2. Local image management and integrity validation.
3. Fallback and packaging utilities for generated scenes.
"""

import os
import json
import shutil
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Union, Dict, Any, List, Tuple
from PIL import Image

# Default directory paths
BASE_GENERATED_DIR = Path("generated")
IMAGES_DIR = BASE_GENERATED_DIR / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

REQUIRED_METADATA_FILES = [
    "generation_results.json",
    "caption_results.json",
    "verification_results.json"
]


def validate_image_file(image_path: Union[str, Path]) -> Tuple[bool, str]:
    """
    Validate that an image file exists, is non-empty, and can be opened by PIL.

    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    path = Path(image_path)
    if not path.exists():
        return False, f"File does not exist: {path.name}"

    if path.stat().st_size == 0:
        return False, f"File is empty (0 bytes): {path.name}"

    try:
        with Image.open(path) as img:
            img.verify()
        # Verify only checks header; test reopen to confirm readable pixels
        with Image.open(path) as img:
            img.load()
            width, height = img.size
            if width <= 0 or height <= 0:
                return False, f"Invalid dimensions ({width}x{height}) in {path.name}"
        return True, ""
    except Exception as exc:
        return False, f"Invalid or corrupted image ({path.name}): {str(exc)}"


def inspect_zip_contents(zip_source: Union[str, Path, BytesIO]) -> Dict[str, Any]:
    """
    Inspect the contents of a P36_U3_Output.zip without modifying the filesystem.

    Returns:
        Dictionary containing validation findings, file list, and errors.
    """
    report = {
        "is_valid": False,
        "files": [],
        "has_images_dir": False,
        "image_count": 0,
        "image_files": [],
        "found_metadata": [],
        "missing_metadata": [],
        "errors": []
    }

    try:
        with zipfile.ZipFile(zip_source, "r") as zf:
            namelist = zf.namelist()
            report["files"] = namelist

            # Look for metadata files anywhere in the zip
            for meta_name in REQUIRED_METADATA_FILES:
                matched = any(f.endswith(meta_name) for f in namelist)
                if matched:
                    report["found_metadata"].append(meta_name)
                else:
                    report["missing_metadata"].append(meta_name)

            # Look for scene images
            image_extensions = (".png", ".jpg", ".jpeg", ".webp")
            images = [
                f for f in namelist
                if f.lower().endswith(image_extensions) and not f.startswith("__MACOSX")
            ]
            report["image_files"] = images
            report["image_count"] = len(images)
            report["has_images_dir"] = any("images/" in f for f in namelist) or len(images) > 0

            # Determine validity
            if report["image_count"] == 0:
                report["errors"].append("ZIP archive does not contain any image files.")

            if report["missing_metadata"]:
                report["errors"].append(
                    f"Missing required metadata files: {', '.join(report['missing_metadata'])}"
                )

            report["is_valid"] = (len(report["errors"]) == 0)

    except zipfile.BadZipFile:
        report["errors"].append("The uploaded file is not a valid ZIP archive or is corrupted.")
    except Exception as exc:
        report["errors"].append(f"Failed to read ZIP archive: {str(exc)}")

    return report


def extract_and_validate_u3_zip(
    zip_source: Union[str, Path, BytesIO],
    destination_dir: Union[str, Path] = "generated"
) -> Dict[str, Any]:
    """
    Extract P36_U3_Output.zip into the destination directory and validate all extracted files.

    Handles both root-level archive formats and 'P36_U3_Output/' prefix directories.
    Normalizes images into destination_dir/images and JSON files into destination_dir/.

    Returns:
        Dictionary with extraction status, list of extracted files, and scene validation statuses.
    """
    dest_path = Path(destination_dir)
    images_target_dir = dest_path / "images"
    images_target_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "success": False,
        "extracted_files": [],
        "images": {},
        "metadata_loaded": {},
        "errors": [],
        "warnings": []
    }

    try:
        with zipfile.ZipFile(zip_source, "r") as zf:
            namelist = [f for f in zf.namelist() if not f.startswith("__MACOSX")]

            for member in namelist:
                # Skip directory entries
                if member.endswith("/"):
                    continue

                filename = Path(member).name
                lower_name = filename.lower()

                # Case 1: Image files
                if lower_name.endswith((".png", ".jpg", ".jpeg", ".webp")):
                    target_file = images_target_dir / filename
                    with zf.open(member) as src, open(target_file, "wb") as dst:
                        shutil.copyfileobj(src, dst)
                    result["extracted_files"].append(str(target_file))

                # Case 2: Metadata JSON files
                elif lower_name.endswith(".json") and filename in REQUIRED_METADATA_FILES:
                    target_file = dest_path / filename
                    with zf.open(member) as src, open(target_file, "wb") as dst:
                        shutil.copyfileobj(src, dst)
                    result["extracted_files"].append(str(target_file))
                    try:
                        with open(target_file, "r", encoding="utf-8") as jf:
                            result["metadata_loaded"][filename] = json.load(jf)
                    except Exception as jerr:
                        result["warnings"].append(f"Could not parse {filename}: {str(jerr)}")

        # Validate extracted images for 6 scenes
        for scene_idx in range(1, 7):
            scene_filename = f"scene_{scene_idx:02d}.png"
            scene_img_path = images_target_dir / scene_filename

            if scene_img_path.exists():
                is_valid, err_msg = validate_image_file(scene_img_path)
                result["images"][scene_idx] = {
                    "filename": scene_filename,
                    "path": str(scene_img_path),
                    "exists": True,
                    "is_valid": is_valid,
                    "error": err_msg if not is_valid else None
                }
                if not is_valid:
                    result["warnings"].append(err_msg)
            else:
                result["images"][scene_idx] = {
                    "filename": scene_filename,
                    "path": str(scene_img_path),
                    "exists": False,
                    "is_valid": False,
                    "error": f"Image for scene {scene_idx} is missing from the archive."
                }
                result["warnings"].append(f"scene_{scene_idx:02d}.png was not found in archive.")

        # Check critical errors
        valid_count = sum(1 for s in result["images"].values() if s["is_valid"])
        if valid_count == 0:
            result["errors"].append("No valid scene images could be extracted.")
        else:
            result["success"] = True

    except zipfile.BadZipFile:
        result["errors"].append("Provided file is not a valid ZIP archive.")
    except Exception as exc:
        result["errors"].append(f"Extraction failed: {str(exc)}")

    return result


def load_generation_results(directory: Union[str, Path] = "generated") -> List[Dict[str, Any]]:
    """
    Load generation_results.json from the given directory.
    Returns empty list if not found or corrupted.
    """
    gen_file = Path(directory) / "generation_results.json"
    if not gen_file.exists():
        return []

    try:
        with open(gen_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def get_scene_image_path(scene_number: int, directory: Union[str, Path] = "generated/images") -> Union[Path, None]:
    """
    Get the Path to a scene image if it exists and is valid.
    Returns None if missing.
    """
    candidate = Path(directory) / f"scene_{scene_number:02d}.png"
    if candidate.exists():
        is_valid, _ = validate_image_file(candidate)
        if is_valid:
            return candidate
    return None


def package_u3_output(
    source_dir: Union[str, Path] = "generated",
    output_zip_path: Union[str, Path] = "generated/P36_U3_Output.zip"
) -> Path:
    """
    Package images/ and metadata JSON files into a compliant P36_U3_Output.zip.
    """
    src = Path(source_dir)
    images_dir = src / "images"
    out_path = Path(output_zip_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add images
        if images_dir.exists():
            for img in images_dir.glob("scene_*.png"):
                zf.write(img, arcname=f"P36_U3_Output/images/{img.name}")

        # Add metadata JSON files
        for meta_file in REQUIRED_METADATA_FILES:
            target_json = src / meta_file
            if target_json.exists():
                zf.write(target_json, arcname=f"P36_U3_Output/{meta_file}")

    return out_path
