"""
P36 - Script2Video AI
Main Streamlit Application

Implemented Units:
U1 - Prompt Engineering (Zero-shot & Few-shot)
U2 - Gemini LLM Six-Scene Script Generation
U3 - AI Image Generation (Stable Diffusion 1.5 via Colab) & BLIP Semantic Verification
"""

import os
import json
from pathlib import Path
import streamlit as st

from llm_service import generate_video_script
from image_service import (
    extract_and_validate_u3_zip,
    inspect_zip_contents,
    load_generation_results,
    get_scene_image_path,
    package_u3_output,
    validate_image_file
)
from blip_service import (
    load_verification_results,
    load_caption_results,
    apply_heuristic_threshold,
    update_manual_review,
    generate_verification_summary,
    export_verification_report_markdown,
    export_verification_report_json,
    DEFAULT_HEURISTIC_THRESHOLD
)

# Ensure required local directories exist
os.makedirs("generated/images", exist_ok=True)
os.makedirs("generated/audio", exist_ok=True)
os.makedirs("generated/videos", exist_ok=True)


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="Script2Video AI",
    page_icon="🎬",
    layout="wide"
)


# ---------------- CUSTOM HEADER ----------------

st.title("🎬 Script2Video AI")

st.markdown(
    """
    ### Turn your ideas into narrated AI videos
    Generate a cinematic six-scene video script, generate photorealistic visuals with 
    **Stable Diffusion 1.5**, and verify image relevance using **BLIP** captioning and **Sentence Transformers**.
    """
)

st.divider()


# ---------------- SIDEBAR ----------------

st.sidebar.title("Project Information")

st.sidebar.markdown(
    """
    **Project:** P36 - Script-to-Narrated Video Maker
    
    **Generative AI Units:**
    - ✅ **U1:** Prompt Engineering (Zero-shot & Few-shot)
    - ✅ **U2:** LLM Script Generation (Gemini 3.8 Flash)
    - 🚀 **U3:** Image Generation (SD 1.5) & BLIP Verification
    - ⏳ **U4:** Audio & Video Composition
    - ⏳ **U5:** Responsible AI & Watermarking
    """
)

st.sidebar.info(
    "Units 1, 2, and 3 are active. Local environment uses PyCharm on Windows; "
    "GPU image generation is executed via Google Colab."
)

with st.sidebar.expander("ℹ️ Model Attribution & Licenses", expanded=False):
    st.markdown(
        """
        - **Google Gemini 3.8 Flash:** LLM script generation.
        - **Stable Diffusion 1.5:** `stable-diffusion-v1-5/stable-diffusion-v1-5` (CreativeML OpenRAIL-M license).
        - **BLIP Captioning:** `Salesforce/blip-image-captioning-base` (BSD-3-Clause license).
        - **Sentence Transformers:** `sentence-transformers/all-MiniLM-L6-v2` (Apache 2.0 license).
        """
    )


# ---------------- AUTO-LOAD EXISTING SCRIPT ----------------

LOCAL_SCRIPT_FILE = Path("generated/video_script.json")

if "generated_script" not in st.session_state and LOCAL_SCRIPT_FILE.exists():
    try:
        with open(LOCAL_SCRIPT_FILE, "r", encoding="utf-8") as f:
            st.session_state["generated_script"] = json.load(f)
            st.session_state["prompt_technique"] = "few-shot"
    except Exception:
        pass


# ---------------- USER INPUT (U1 & U2) ----------------

st.subheader("1. Create Your Video Script (U1 & U2)")

topic = st.text_area(
    "Enter your video topic",
    placeholder="Example: The Future of Artificial Intelligence",
    height=90
)

col1, col2 = st.columns(2)

with col1:
    technique = st.selectbox(
        "Select Prompt Engineering Technique",
        ["zero-shot", "few-shot"]
    )

with col2:
    st.text_input(
        "Number of Scenes",
        value="6 Scenes (Standard)",
        disabled=True
    )

generate_button = st.button(
    "✨ Generate Six-Scene Script",
    type="primary",
    use_container_width=True
)


# ---------------- SCRIPT GENERATION ----------------

if generate_button:
    if not topic.strip():
        st.warning("Please enter a topic first.")
    else:
        try:
            with st.spinner("Gemini is creating your video script..."):
                script = generate_video_script(
                    topic=topic,
                    technique=technique
                )

            st.session_state["generated_script"] = script
            st.session_state["prompt_technique"] = technique

            # Save local copy
            with open(LOCAL_SCRIPT_FILE, "w", encoding="utf-8") as file:
                json.dump(script, file, indent=4, ensure_ascii=False)

            st.success("Your six-scene script was generated and saved!")
        except Exception as error:
            st.error(f"Script generation failed: {error}")


# ---------------- DISPLAY GENERATED SCRIPT ----------------

if "generated_script" in st.session_state:
    script = st.session_state["generated_script"]

    st.divider()
    st.subheader("2. Generated Video Script")

    st.markdown(f"### {script.get('video_title', 'Video Script')}")
    st.write(f"**Topic:** {script.get('topic', 'N/A')}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Scenes", len(script.get("scenes", [])))
    col2.metric("Video Duration", f"{script.get('total_duration', 45)} seconds")
    col3.metric(
        "Prompt Technique",
        st.session_state.get("prompt_technique", "Few-shot").title()
    )

    st.divider()

    for scene in script.get("scenes", []):
        with st.expander(
            f"🎞️ Scene {scene['scene_number']}: {scene['scene_title']}",
            expanded=False
        ):
            st.markdown("**Narration**")
            st.write(scene["narration"])

            st.markdown("**Visual Description**")
            st.write(scene["visual_description"])

            st.markdown("**Image Generation Prompt**")
            st.code(scene["image_prompt"])

            st.caption(f"Duration: {scene['duration_seconds']} seconds")

    # ---------------- DOWNLOAD SCRIPT ----------------
    st.divider()
    st.subheader("3. Script Actions")

    script_json = json.dumps(script, indent=4, ensure_ascii=False)

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.download_button(
            label="📥 Download Script as JSON",
            data=script_json,
            file_name="video_script.json",
            mime="application/json",
            use_container_width=True
        )
    with col_d2:
        if st.button("🔄 Reload Local video_script.json", use_container_width=True):
            if LOCAL_SCRIPT_FILE.exists():
                with open(LOCAL_SCRIPT_FILE, "r", encoding="utf-8") as f:
                    st.session_state["generated_script"] = json.load(f)
                st.success("Reloaded video_script.json from disk.")
                st.rerun()


# ---------------- U3: AI IMAGE GENERATION & BLIP VERIFICATION ----------------

st.divider()
st.subheader("4. U3 — AI Image Generation & BLIP Verification Pipeline")

st.markdown(
    """
    **End-to-End Visual Pipeline:**
    1. **GPU Generation (Google Colab):** Generate 6 scene images using **Stable Diffusion 1.5** in FP16.
    2. **Image Captioning (Salesforce BLIP):** Generate neutral objective descriptions of each generated image.
    3. **Semantic Verification (Sentence Transformers):** Compute raw cosine similarity between intended scene descriptions and BLIP captions.
    4. **Local Integration:** Import `P36_U3_Output.zip` into PyCharm/Streamlit to review scenes, inspect similarity, apply manual review, and export reports.
    """
)

# Colab Instructions Accordion
with st.expander("📖 Step-by-Step Instructions: Run Google Colab Generator", expanded=False):
    st.markdown(
        """
        1. Open the included notebook: [`notebooks/P36_U3_Image_Generation_BLIP.ipynb`](file:///c:/PyCharm/PS36_PratikGholap/notebooks/P36_U3_Image_Generation_BLIP.ipynb).
        2. Upload it to [Google Colab](https://colab.research.google.com/) and connect to a free GPU runtime (**Runtime > Change runtime type > T4 GPU**).
        3. Upload your `video_script.json` (downloadable above) in **Cell 3**.
        4. Run all cells. The notebook will:
           - Verify CUDA and GPU memory.
           - Generate `scene_01.png` through `scene_06.png` with deterministic seeds.
           - Generate captions via `Salesforce/blip-image-captioning-base`.
           - Calculate raw cosine similarities via `sentence-transformers/all-MiniLM-L6-v2`.
           - Package everything into `P36_U3_Output.zip` and auto-download.
        5. Upload `P36_U3_Output.zip` below to view the results in Streamlit.
        """
    )

# Colab ZIP Upload & Import Section
st.markdown("#### Import Colab Generation Output (`P36_U3_Output.zip`)")

tab_upload, tab_local = st.tabs(["📤 Upload Colab ZIP Archive", "📂 Import Existing Local Output"])

with tab_upload:
    uploaded_zip = st.file_uploader(
        "Upload P36_U3_Output.zip",
        type=["zip"],
        help="Select the P36_U3_Output.zip downloaded from Google Colab."
    )

    if uploaded_zip is not None:
        if st.button("🚀 Process & Extract Uploaded ZIP", type="primary", use_container_width=True):
            with st.spinner("Extracting and validating archive..."):
                extraction_res = extract_and_validate_u3_zip(uploaded_zip, "generated")

            if extraction_res["success"]:
                st.success(
                    f"Successfully extracted {len(extraction_res['extracted_files'])} assets into generated/."
                )
                # Load metadata into session state
                st.session_state["verification_results"] = load_verification_results("generated")
                st.session_state["caption_results"] = load_caption_results("generated")
                st.session_state["generation_results"] = load_generation_results("generated")
                st.session_state["u3_extraction_report"] = extraction_res
                st.rerun()
            else:
                st.error("ZIP extraction failed:")
                for err in extraction_res["errors"]:
                    st.write(f"- ❌ {err}")

with tab_local:
    local_zip_path = Path("generated/P36_U3_Output.zip")
    local_verif_file = Path("generated/verification_results.json")

    st.write(
        f"**Local Archive Status:** "
        f"{'Available (' + str(round(local_zip_path.stat().st_size / 1024, 1)) + ' KB)' if local_zip_path.exists() else 'Not found yet.'}"
    )

    col_loc1, col_loc2 = st.columns(2)
    with col_loc1:
        if st.button("📂 Load from Local generated/ Directory", use_container_width=True):
            if local_verif_file.exists():
                st.session_state["verification_results"] = load_verification_results("generated")
                st.session_state["caption_results"] = load_caption_results("generated")
                st.session_state["generation_results"] = load_generation_results("generated")
                st.success("Loaded local verification data and images.")
                st.rerun()
            else:
                st.warning("No local verification_results.json found in generated/.")

    with col_loc2:
        if local_zip_path.exists():
            if st.button("📦 Unpack generated/P36_U3_Output.zip", use_container_width=True):
                with st.spinner("Unpacking local ZIP..."):
                    extraction_res = extract_and_validate_u3_zip(local_zip_path, "generated")
                if extraction_res["success"]:
                    st.session_state["verification_results"] = load_verification_results("generated")
                    st.session_state["caption_results"] = load_caption_results("generated")
                    st.session_state["generation_results"] = load_generation_results("generated")
                    st.session_state["u3_extraction_report"] = extraction_res
                    st.success("Local ZIP unpacked successfully.")
                    st.rerun()
                else:
                    st.error("Failed to unpack local ZIP.")


# ---------------- VERIFICATION CONTROLS & THRESHOLD ----------------

# Auto-initialize verification results from disk if available
if "verification_results" not in st.session_state and Path("generated/verification_results.json").exists():
    st.session_state["verification_results"] = load_verification_results("generated")
    st.session_state["caption_results"] = load_caption_results("generated")
    st.session_state["generation_results"] = load_generation_results("generated")

if "verification_results" in st.session_state and st.session_state["verification_results"]:
    v_results = st.session_state["verification_results"]

    st.divider()
    st.subheader("5. Semantic Verification & Heuristic Evaluation")

    st.markdown(
        """
        > **⚠️ Metric Definition & Heuristic Threshold Notice:**  
        > Cosine similarity evaluates the geometric angular alignment between embeddings in multidimensional vector space. 
        > Scores range from **-1.0 to +1.0**. Negative scores are valid and preserved. Cosine similarity is **not** classification accuracy.
        > The slider below adjusts an exploratory **heuristic review threshold** to highlight scenes that may benefit from manual review.
        """
    )

    # Configurable Heuristic Threshold Slider
    current_thresh = st.slider(
        "Configurable Review Threshold (Exploratory Heuristic)",
        min_value=0.00,
        max_value=1.00,
        value=float(st.session_state.get("heuristic_threshold", DEFAULT_HEURISTIC_THRESHOLD)),
        step=0.05,
        help="Scenes with cosine similarity >= threshold are flagged as 'Relevant'. Others are marked 'Needs Review (Heuristic)'."
    )
    st.session_state["heuristic_threshold"] = current_thresh

    # Apply threshold across records
    updated_records = apply_heuristic_threshold(v_results, current_thresh)
    st.session_state["verification_results"] = updated_records
    summary = generate_verification_summary(updated_records, current_thresh)

    # High-level Summary Metrics
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Scenes", summary["total_scenes"])
    m2.metric("Relevant (Heuristic)", summary["relevant_scenes"])
    m3.metric("Needs Review", summary["needs_review_scenes"])
    m4.metric(
        "Avg Cosine Sim",
        f"{summary['average_cosine_similarity']:+.4f}" if summary["average_cosine_similarity"] is not None else "N/A"
    )
    m5.metric(
        "Manual Reviews",
        f"{summary['manual_approved']} Approved / {summary['manual_flagged']} Flagged"
    )

    # ---------------- 6-SCENE VISUAL GALLERY & VERIFICATION ----------------

    st.divider()
    st.subheader("6. Generated Scene Visuals & Caption Verification")

    for idx, record in enumerate(updated_records):
        s_num = record["scene_number"]
        s_title = record["scene_title"]
        cos_sim = record.get("cosine_similarity")
        h_status = record.get("verification_status", "Needs Review")
        m_status = record.get("manual_review_status", "Pending")

        status_icon = "🟢" if h_status == "Relevant" else "🟠"

        with st.expander(
            f"{status_icon} Scene {s_num}: {s_title} | Cosine Sim: {f'{cos_sim:+.4f}' if cos_sim is not None else 'N/A'} | Status: {h_status}",
            expanded=(idx < 2)  # Expand first 2 scenes by default
        ):
            col_img, col_data = st.columns([1.2, 1.0])

            with col_img:
                img_path = get_scene_image_path(s_num, "generated/images")
                if img_path and img_path.exists():
                    st.image(
                        str(img_path),
                        caption=f"Scene {s_num:02d}: {s_title} ({record.get('image_filename', '')})",
                        use_container_width=True
                    )
                else:
                    st.warning(f"⚠️ Image not found: `{record.get('image_filename', f'scene_{s_num:02d}.png')}`")
                    st.caption("Ensure P36_U3_Output.zip has been extracted or image generated.")

            with col_data:
                st.markdown("**Expected Visual Description (Script):**")
                st.write(record.get("original_visual_description", "N/A"))

                st.markdown("**BLIP Generated Caption:**")
                blip_cap = record.get("blip_caption")
                if blip_cap:
                    st.info(f"💬 *\"{blip_cap}\"*")
                else:
                    st.error(f"BLIP Error: {record.get('error') or 'Caption not available'}")

                st.markdown("**Semantic Alignment Evaluation:**")
                c_sim1, c_sim2 = st.columns(2)
                with c_sim1:
                    sim_display = f"{cos_sim:+.4f}" if cos_sim is not None else "N/A"
                    st.metric("Cosine Similarity", sim_display)
                with c_sim2:
                    if h_status == "Relevant":
                        st.success(f"Status: **{h_status}**\n(>= {current_thresh:.2f})")
                    else:
                        st.warning(f"Status: **{h_status}**\n(< {current_thresh:.2f})")

                st.caption(
                    "Metric: Raw cosine similarity from `sentence-transformers/all-MiniLM-L6-v2`. "
                    "Threshold is heuristic."
                )

                st.markdown("---")
                st.markdown("**👤 Human-in-the-Loop Manual Review:**")

                review_options = ["Pending", "Approved (Manual)", "Flagged for Revision", "Rejected"]
                curr_review_idx = 0
                if m_status in review_options:
                    curr_review_idx = review_options.index(m_status)

                sel_col, note_col = st.columns([1, 1])
                with sel_col:
                    new_m_status = st.selectbox(
                        f"Review Decision (Scene {s_num})",
                        review_options,
                        index=curr_review_idx,
                        key=f"manual_status_{s_num}"
                    )
                with note_col:
                    new_notes = st.text_input(
                        f"Review Notes (Scene {s_num})",
                        value=record.get("manual_notes", ""),
                        placeholder="Optional curator feedback...",
                        key=f"manual_notes_{s_num}"
                    )

                if (new_m_status != m_status) or (new_notes != record.get("manual_notes", "")):
                    st.session_state["verification_results"] = update_manual_review(
                        st.session_state["verification_results"],
                        s_num,
                        new_m_status,
                        new_notes
                    )
                    export_verification_report_json(
                        st.session_state["verification_results"],
                        "generated/verification_results.json"
                    )

    # ---------------- VERIFICATION REPORT EXPORTS ----------------

    st.divider()
    st.subheader("7. Download Verification Reports & Output Package")

    report_md = export_verification_report_markdown(
        st.session_state["verification_results"],
        summary,
        project_title=f"P36 Script2Video AI - Verification Report ({script.get('video_title', 'Video')})"
    )

    report_json_str = json.dumps(st.session_state["verification_results"], indent=4, ensure_ascii=False)

    col_exp1, col_exp2, col_exp3 = st.columns(3)

    with col_exp1:
        st.download_button(
            label="📄 Download Report (Markdown)",
            data=report_md,
            file_name="verification_report.md",
            mime="text/markdown",
            use_container_width=True
        )

    with col_exp2:
        st.download_button(
            label="📥 Download Report (JSON)",
            data=report_json_str,
            file_name="verification_results.json",
            mime="application/json",
            use_container_width=True
        )

    with col_exp3:
        local_zip = Path("generated/P36_U3_Output.zip")
        if local_zip.exists():
            with open(local_zip, "rb") as zf:
                st.download_button(
                    label="📦 Download Output Archive (ZIP)",
                    data=zf.read(),
                    file_name="P36_U3_Output.zip",
                    mime="application/zip",
                    use_container_width=True
                )
        else:
            if st.button("📦 Package generated/ as ZIP", use_container_width=True):
                packaged_zip = package_u3_output("generated", "generated/P36_U3_Output.zip")
                st.success(f"Packaged to {packaged_zip.name}")
                st.rerun()

else:
    st.info("ℹ️ No image generation or verification results loaded yet. Generate your script in U2, then run the Colab notebook or import an existing P36_U3_Output.zip archive above.")


# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "P36 | Script2Video AI | Generative AI Mini Project | Unit 3 Implemented & Tested"
)
