# AthleteVision AI — Squat + Running MVP

A React/Vite + FastAPI computer-vision application for **video upload, annotated body landmarks, joint-angle timelines, squat repetition screening and exploratory running posture/gait measures**, plus optional YOLO person tracking and optional OpenAI feedback.

> This is **research/demo software**. It does not certify technique, diagnose injuries, or provide validated running cadence or squat safety judgments. Use coach-labelled footage to evaluate and refine thresholds.

## Prerequisites

- Windows 10/11 (or Linux/macOS), **Python 3.11**, Node.js **20+**, npm
- Internet on first analysis to download official MediaPipe Pose Landmarker model (~5 MB).
- Fixed-camera side-view video, full body visible, 5–30 seconds recommended.

## 1. Backend (Terminal 1, PowerShell)

```powershell
cd AthleteVision-AI\backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8000
```

Backend status: http://127.0.0.1:8000/api/health
API docs: http://127.0.0.1:8000/docs

If you need YOLO: `pip install ultralytics`, then tick **Enable YOLO** in frontend. It detects/tracks people with a COCO-trained model, **not exercise equipment mechanics**. Check Ultralytics license before commercial deployment.

To enable optional API coaching, add `OPENAI_API_KEY=...` to `backend/.env` (never the frontend). API coaching otherwise falls back to local instructions. Paid API use is optional.

## 2. Frontend (Terminal 2, PowerShell)

```powershell
cd AthleteVision-AI\frontend
npm install
npm run dev
```

Open http://localhost:5173, choose **Weightlifting (Squat)** or **Running**, upload your video and click **Start analysis**. Polling tracks the backend processing job. Video and JSON report download buttons appear after completion.

## 3. Tests

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pip install pytest
pytest -q
```

## Architecture

```
frontend React/Vite -> POST /api/analyze -> FastAPI background executor
                         -> OpenCV sampled decoding (~12 FPS)
                         -> MediaPipe Pose Landmarker VIDEO task
                         -> sport-specific heuristic analysis
                         -> optional YOLO person tracker
                         -> optional OpenAI coaching summary (structured metrics only)
                         -> /api/jobs/{id} -> report.json / annotated.mp4
```

## Supported techniques and honest boundaries

- **Squat**: knee flexion threshold-based rep counting, hip-vs-knee image-height depth *screen*, torso inclination *screen*. Side-view camera is essential; none are definitive form assessments.
- **Running**: average observed 2D knee angle, torso inclination, ankle crossover proxy. The ankle-crossing proxy is **not validated running cadence** and can be highly incorrect for camera or stride configurations.
- If insufficient landmarks are detected, results say **insufficient evidence**.
- No assessment of spinal rounding, load, forces, foot pressure, bar path, or injury risk.
- Video overlay is encoded as OpenCV `mp4v`. Some browsers cannot play it without transcoding. Try downloading and playing in VLC, or use ffmpeg to convert: `ffmpeg -i annotated.mp4 -c:v libx264 -pix_fmt yuv420p annotated_h264.mp4`.

## Endpoints

- `GET /api/health`
- `POST /api/analyze` multipart fields: `file`, `sport` (`squat` / `running`), `use_yolo` (boolean); returns `job_id`.
- `GET /api/jobs/{job_id}` status and finished report.
- `GET /api/jobs/{job_id}/video`
- `GET /api/jobs/{job_id}/report`

## Known limitations and next steps

- Research prototype, **not production-ready**. Jobs are in-memory; restarting the server clears status, while files remain under `backend/data/`.
- Uploaded video is stored on disk without authentication or automatic expiry. **Do not deploy publicly** until adding user authentication, video retention/deletion, quotas and background worker infrastructure.
- For high load, move analysis to a proper job queue (Celery/RQ), add secure storage, retry handling and database persistence.
- Provide videos with known coach labels; calculate precision/recall for technique flags and MAE for angle estimates; refine per-sport rules.
- Basic checks exist for geometry and repetition logic. No end-to-end tested real video benchmark is included.
- Video export doesn't contain audio.

## Upgrade: rep-by-rep squat review

After re-analyzing a squat video, the result includes an `events`/`rep_details` array containing each detected completed repetition's start/bottom/end timestamps, duration, minimum knee angle, maximum torso inclination, visible hip-vs-knee displacement, screening checks, findings and correction suggestions. Click a rep in the React review panel to seek the annotated video to the sampled bottom timestamp.

The **experimental screening score** is intentionally simple and auditable: 100 for a detected completed cycle, minus 50 for an apparent hip-above-knee depth flag at the most bent-knee sample, and minus 30 for 2D torso inclination above 48°. The score is **not** a probability, professional technique grade or a measure of safety. These unvalidated reference thresholds require coach-led benchmarking and camera calibration before any high-stakes use. No rep-specific score is produced when no complete cycle is observed.

Restart backend and frontend after replacing the project files; run `pytest -q` from `backend` to check the included unit tests. Old analysis reports will not gain the new fields until video is re-analyzed.


## V3: running analysis and dashboard update

This release keeps squat repetitions and adds bilateral knee ranges, torso variability, data-quality checks, descriptive observations, and clickable approximate ankle-crossing timestamps for running. **These are experimental image-plane measurements, not validated technique faults or injury predictions.**

### Updating a previous installation

Back up your current `backend/app`, `frontend/src`, and `.env`. Extract this package, copy `backend/app/` and `frontend/src/` into your existing project, replacing their old contents (don't append code). Existing `.venv`, `node_modules`, `backend/data`, and `backend/.env` can stay. Restart both servers and **reanalyze** the video: older saved results do not gain new metrics.

Backend (PowerShell):
```powershell
cd "C:\Users\MAHESH\OneDrive\Desktop\AthleteVision-AI\backend"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir . --reload --port 8000
```
Frontend (separate terminal):
```powershell
cd "C:\Users\MAHESH\OneDrive\Desktop\AthleteVision-AI\frontend"
npm install
npm run dev
```
Open the localhost URL printed by Vite; the backend API docs are at http://127.0.0.1:8000/docs. JSON reports are saved under `backend/data/<job_id>/report.json`.
