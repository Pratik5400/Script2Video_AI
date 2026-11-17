# 🎬 P36 - Script2Video AI

An end-to-end Generative AI application for creating narrated cinematic video scripts, generating AI scene imagery, and automatically verifying visual relevance using multi-modal AI captioning and sentence transformers.

---

## 📌 Project Overview

- **Author / Workspace:** `PS36_PratikGholap`
- **Application Platform:** Streamlit
- **Target OS / Environment:** Windows (Python 3.12, PyCharm)
- **GPU Processing:** Google Colab (Free T4 GPU runtime)

---

## 🚀 Generative AI Units Status

| Unit | Title | Status | Technology Stack |
| :---: | :--- | :---: | :--- |
| **U1** | Prompt Engineering | ✅ Implemented | Zero-shot & Few-shot prompt templates (`prompts.py`) |
| **U2** | LLM Script Generation | ✅ Implemented | Google Gemini API (`gemini-3.8-flash`, `llm_service.py`) |
| **U3** | AI Image Generation & BLIP Verification | ✅ Implemented | Stable Diffusion 1.5, Salesforce BLIP, Sentence Transformers |
| **U4** | Audio & Video Generation | ⏳ Upcoming | Text-to-Speech & Video Synthesis |
| **U5** | Responsible AI | ⏳ Upcoming | Watermarking, Content Safety, Ethics |

---

## 🏗️ Unit 3 Architecture & Workflow

Unit 3 implements a decoupled architecture:
1. **Google Colab (`notebooks/P36_U3_Image_Generation_BLIP.ipynb`):**
   - Connects to a GPU runtime (T4).
   - Generates 6 high-detail 16:9 images with **Stable Diffusion 1.5** (`stable-diffusion-v1-5/stable-diffusion-v1-5`) using FP16 precision, attention slicing, and reproducible seeds.
   - Generates objective captions for each image with **Salesforce BLIP** (`Salesforce/blip-image-captioning-base`).
   - Computes raw semantic **Cosine Similarity** between intended visual descriptions and BLIP captions using **Sentence Transformers** (`sentence-transformers/all-MiniLM-L6-v2`).
   - Packages all outputs into `P36_U3_Output.zip`.
2. **Local Streamlit Application (`app.py`):**
   - Ingests `P36_U3_Output.zip` or existing `generated/` assets.
   - Validates archive structure and image integrity.
   - Displays a 6-scene interactive gallery with images, BLIP captions, and cosine similarity scores.
   - Provides a configurable **Heuristic Threshold** slider.
   - Supports **Human-in-the-Loop Manual Review** (Approved / Flagged / Rejected) and exports comprehensive JSON & Markdown verification reports.

---

## ⚙️ Quick Start Guide (Local PyCharm / Windows)

### 1. Environment Setup
```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install local dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys
Ensure your `.env` contains your Gemini API key:
```ini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.8-flash
```

### 3. Run the Streamlit Application
```powershell
.\.venv\Scripts\streamlit run app.py
```

---

## 📓 Running Unit 3 on Google Colab

1. Open [`notebooks/P36_U3_Image_Generation_BLIP.ipynb`](file:///c:/PyCharm/PS36_PratikGholap/notebooks/P36_U3_Image_Generation_BLIP.ipynb).
2. Upload the notebook to [Google Colab](https://colab.research.google.com/).
3. Change runtime type to GPU (**Runtime > Change runtime type > T4 GPU**).
4. Run Cell 1 to install dependencies.
5. In Cell 3, upload your `video_script.json` (or use the built-in default script).
6. Run all remaining cells. The notebook will generate the images, captions, similarities, and download `P36_U3_Output.zip`.
7. In your Streamlit app, upload `P36_U3_Output.zip` under **Section 4**.

---

## 🧪 Automated Testing

Run the automated test suite covering all 8 unit and integration requirements:
```powershell
.\.venv\Scripts\python -m unittest tests/test_u3_pipeline.py
```

Tests execute:
1. `test_01_json_script_import_and_structure`: Validates 6-scene JSON schema.
2. `test_02_single_image_import_and_validation`: Tests single scene image verification.
3. `test_03_six_images_import_and_validation`: Verifies all 6 scene images.
4. `test_04_blip_caption_loading_and_parsing`: Validates BLIP captions.
5. `test_05_similarity_calculation_and_heuristic_evaluation`: Tests raw cosine similarity preservation and heuristic thresholding.
6. `test_06_missing_and_corrupted_image_handling`: Tests error resilience on missing/corrupted files.
7. `test_07_zip_archive_extraction_and_reporting`: Tests `P36_U3_Output.zip` extraction.
8. `test_08_existing_u1_and_u2_functionality`: Regression testing on U1 prompts and U2 schemas.

---

## ⚖️ Model Attribution & Licenses

- **Stable Diffusion 1.5:** `stable-diffusion-v1-5/stable-diffusion-v1-5` — [CreativeML OpenRAIL-M License](https://huggingface.co/spaces/CompVis/stable-diffusion-license)
- **Salesforce BLIP:** `Salesforce/blip-image-captioning-base` — [BSD-3-Clause License](https://opensource.org/licenses/BSD-3-Clause)
- **Sentence Transformers:** `sentence-transformers/all-MiniLM-L6-v2` — [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0)
- **Gemini 3.8 Flash:** Google Generative AI API
