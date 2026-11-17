# Script2Video AI - Unit 3 Verification Report
## Generative AI Verification Report (BLIP + Sentence Transformers)

> **Important Methodology Note:**
> Similarity scores report raw **Cosine Similarity** between sentence embeddings (`sentence-transformers/all-MiniLM-L6-v2`) of the intended visual description and the BLIP-generated caption. Cosine similarity measures angle in vector space (range: -1.0 to +1.0) and is **not** classification accuracy. The review threshold (0.40) is an exploratory **heuristic** indicator to assist human curation, not an absolute automated guarantee.

### 1. Executive Summary

- **Total Scenes Evaluated:** 6
- **Relevant (Heuristic):** 6
- **Needs Review (Heuristic):** 0
- **Configurable Heuristic Threshold:** 0.40
- **Average Cosine Similarity:** +0.6685
- **Min / Max Similarity:** +0.5934 / +0.7410
- **Manual Review Status:** 0 Approved, 0 Flagged, 6 Pending

### 2. Scene-by-Scene Verification Table

| Scene | Title | Image File | BLIP Caption | Cosine Sim | Heuristic Status | Manual Review |
| :---: | :--- | :--- | :--- | :---: | :---: | :---: |
| 1 | The Dawn of a New Era | `scene_01.png` | a glowing digital neural network sky... | `+0.6842` | Relevant | Pending |
| 2 | Revolutionizing Medicine | `scene_02.png` | a healthcare scientist looking at a... | `+0.7125` | Relevant | Pending |
| 3 | Autonomous and Sustainable Living | `scene_03.png` | a futuristic city with vertical gard... | `+0.6518` | Relevant | Pending |
| 4 | The Evolution of Creativity | `scene_04.png` | an artist using glowing light brushe... | `+0.5934` | Relevant | Pending |
| 5 | The Ethical Frontier | `scene_05.png` | a robotic hand and a human hand touc... | `+0.6279` | Relevant | Pending |
| 6 | The Symbiotic Horizon | `scene_06.png` | astronauts and robots gazing out of ... | `+0.7410` | Relevant | Pending |

### 3. Detailed Scene Findings

#### Scene 1: The Dawn of a New Era
- **Original Visual Description:** A close-up of a human eye reflecting glowing, intricate neural network pathways that branch into a panoramic view of an advanced metropolis at sunrise.
- **BLIP Caption:** a glowing digital neural network skyline with sunrise in the background
- **Raw Cosine Similarity:** `+0.6842`
- **Heuristic Evaluation:** `Relevant`
- **Manual Review:** `Pending`

#### Scene 2: Revolutionizing Medicine
- **Original Visual Description:** A compassionate doctor wearing holographic glasses interacts with a floating three-dimensional digital DNA strand inside a modern hospital laboratory.
- **BLIP Caption:** a healthcare scientist looking at a three dimensional holographic dna strand in a laboratory
- **Raw Cosine Similarity:** `+0.7125`
- **Heuristic Evaluation:** `Relevant`
- **Manual Review:** `Pending`

#### Scene 3: Autonomous and Sustainable Living
- **Original Visual Description:** Sleek magnetic levitation transit glides silently through a lush, solarpunk city filled with vertical forest skyscrapers and solar crystal bridges.
- **BLIP Caption:** a futuristic city with vertical gardens and monorail transit system under a blue sky
- **Raw Cosine Similarity:** `+0.6518`
- **Heuristic Evaluation:** `Relevant`
- **Manual Review:** `Pending`

#### Scene 4: The Evolution of Creativity
- **Original Visual Description:** An artist in a futuristic studio gestures into the air, synthesizing surreal kaleidoscopic visual landscapes composed of light and sound.
- **BLIP Caption:** an artist using glowing light brushes and geometric patterns in a dark digital studio
- **Raw Cosine Similarity:** `+0.5934`
- **Heuristic Evaluation:** `Relevant`
- **Manual Review:** `Pending`

#### Scene 5: The Ethical Frontier
- **Original Visual Description:** Two translucent glowing hands, one mechanical and one biological, gently converge over a core of radiant blue light symbolizing balance and ethics.
- **BLIP Caption:** a robotic hand and a human hand touching with blue light between their fingers
- **Raw Cosine Similarity:** `+0.6279`
- **Heuristic Evaluation:** `Relevant`
- **Manual Review:** `Pending`

#### Scene 6: The Symbiotic Horizon
- **Original Visual Description:** A diverse group of explorers look outward from an orbital station viewing deck toward deep space, alongside friendly glowing robotic companions.
- **BLIP Caption:** astronauts and robots gazing out of a spaceship window toward a colorful nebula
- **Raw Cosine Similarity:** `+0.7410`
- **Heuristic Evaluation:** `Relevant`
- **Manual Review:** `Pending`
