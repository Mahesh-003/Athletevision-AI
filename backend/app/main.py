# import os,uuid,json
# from pathlib import Path
# from contextlib import asynccontextmanager
# from concurrent.futures import ThreadPoolExecutor
# from fastapi import FastAPI,UploadFile,File,Form,HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import FileResponse
# from dotenv import load_dotenv
# from .pipeline import analyze
# from .feedback import feedback

# ROOT=Path(__file__).resolve().parents[1];load_dotenv(ROOT/'.env')
# DATA=ROOT/'data';DATA.mkdir(exist_ok=True)
# POOL=ThreadPoolExecutor(max_workers=2)
# JOBS={}
# @asynccontextmanager
# async def lifespan(app):
#     yield
#     POOL.shutdown(wait=False,cancel_futures=True)
# app=FastAPI(title='AthleteVision AI API',version='0.3.0',lifespan=lifespan)
# app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:5173','http://127.0.0.1:5173','http://localhost:5174','http://127.0.0.1:5174'],
#                    allow_methods=['GET','POST'],allow_headers=['*'])

# @app.get('/')
# def home(): return {'message':'AthleteVision AI Backend Running','status':'success','version':'0.3.0','docs':'/docs'}

# @app.get('/api/health')
# def health():return {'status':'ok','sports':['squat','running'],'yolo_optional':True}

# def worker(job_id,sport,source,out,use_yolo):
#     try:
#         result=analyze(source,out,sport,use_yolo)
#         result['ai_feedback']=feedback(result)
#         result['video_url']=f'/api/jobs/{job_id}/video'
#         result['report_url']=f'/api/jobs/{job_id}/report'
#         (DATA/job_id/'report.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
#         JOBS[job_id]={'status':'completed','report':result}
#     except Exception as e:
#         JOBS[job_id]={'status':'failed','error':str(e)[:350]}

# @app.post('/api/analyze',status_code=202)
# async def submit(file:UploadFile=File(...),sport:str=Form('squat'),use_yolo:bool=Form(False)):
#     if sport not in ('squat','running'):raise HTTPException(400,'Choose squat or running')
#     if not file.filename or Path(file.filename).suffix.lower() not in ('.mp4','.mov','.avi','.mkv','.webm'):
#         raise HTTPException(400,'Upload MP4, MOV, AVI, MKV or WEBM video')
#     max_bytes=int(os.getenv('MAX_UPLOAD_MB','150'))*1024*1024
#     job_id=uuid.uuid4().hex;folder=DATA/job_id;folder.mkdir()
#     source=folder/('source'+Path(file.filename).suffix.lower());total=0
#     try:
#         with source.open('wb') as out:
#             while chunk:=await file.read(1024*1024):
#                 total+=len(chunk)
#                 if total>max_bytes:raise HTTPException(413,'Video exceeds configured upload limit')
#                 out.write(chunk)
#         if total==0:raise HTTPException(400,'Empty video')
#     except Exception:
#         source.unlink(missing_ok=True)
#         folder.rmdir()
#         raise
#     JOBS[job_id]={'status':'processing'}
#     POOL.submit(worker,job_id,sport,source,folder/'annotated.mp4',use_yolo)
#     return {'job_id':job_id,'status':'processing'}

# @app.get('/api/jobs/{job_id}')
# def get_job(job_id:str):
#     if job_id not in JOBS:raise HTTPException(404,'Unknown or expired job')
#     return JOBS[job_id]

# @app.get('/api/jobs/{job_id}/video')
# def video(job_id:str):
#     p=DATA/job_id/'annotated.mp4'
#     if job_id not in JOBS or JOBS[job_id]['status']!='completed' or not p.exists():raise HTTPException(404,'Video not ready')
#     return FileResponse(p,media_type='video/mp4',filename='athletevision_annotated.mp4')

# @app.get('/api/jobs/{job_id}/report')
# def report(job_id:str):
#     p=DATA/job_id/'report.json'
#     if job_id not in JOBS or not p.exists():raise HTTPException(404,'Report not ready')
#     return FileResponse(p,media_type='application/json',filename='athletevision_report.json')

import os
import uuid
import json

from pathlib import Path
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    HTTPException,
)

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv

from .pipeline import analyze
from .feedback import feedback
from .pdf_report import generate_pdf


ROOT = Path(__file__).resolve().parents[1]

load_dotenv(ROOT / ".env")

DATA = ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)

POOL = ThreadPoolExecutor(max_workers=2)

JOBS = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    POOL.shutdown(wait=False, cancel_futures=True)


app = FastAPI(
    title="AthleteVision AI API",
    version="0.4.0",
    description="AI-Based Sports Performance Analysis System",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "AthleteVision AI Backend Running",
        "status": "success",
        "version": "0.4.0",
        "docs": "/docs",
    }


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "sports": ["squat", "running"],
        "pdf_reports": True,
        "yolo_optional": True,
    }


def worker(job_id, sport, source, output, use_yolo):
    folder = DATA / job_id

    try:
        result = analyze(
            source,
            output,
            sport,
            use_yolo,
        )

        try:
            result["ai_feedback"] = feedback(result)
        except Exception as error:
            result["ai_feedback"] = {
                "error": str(error)[:200]
            }

        result["video_url"] = (
            f"/api/jobs/{job_id}/video"
        )

        result["report_url"] = (
            f"/api/jobs/{job_id}/report"
        )

        result["pdf_url"] = (
            f"/api/jobs/{job_id}/pdf"
        )

        report_path = folder / "report.json"

        report_path.write_text(
            json.dumps(result, indent=2),
            encoding="utf-8",
        )

        # PDF generation is independent of video analysis.
        # A PDF failure should not erase successful results.
        pdf_error = None

        try:
            generate_pdf(
                result,
                folder / "performance_report.pdf",
            )
        except Exception as error:
            pdf_error = str(error)[:200]

        JOBS[job_id] = {
            "status": "completed",
            "report": result,
            "pdf_error": pdf_error,
        }

    except Exception as error:
        JOBS[job_id] = {
            "status": "failed",
            "error": str(error)[:350],
        }


@app.post("/api/analyze", status_code=202)
async def submit(
    file: UploadFile = File(...),
    sport: str = Form("squat"),
    use_yolo: bool = Form(False),
):
    if sport not in ("squat", "running"):
        raise HTTPException(
            status_code=400,
            detail="Choose squat or running",
        )

    allowed_extensions = {
        ".mp4", ".mov", ".avi", ".mkv", ".webm"
    }

    extension = (
        Path(file.filename).suffix.lower()
        if file.filename else ""
    )

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported video format",
        )

    max_bytes = (
        int(os.getenv("MAX_UPLOAD_MB", "150"))
        * 1024 * 1024
    )

    job_id = uuid.uuid4().hex

    folder = DATA / job_id
    folder.mkdir(parents=True, exist_ok=True)

    source = folder / f"source{extension}"
    total = 0

    try:
        with source.open("wb") as output_file:
            while chunk := await file.read(1024 * 1024):
                total += len(chunk)

                if total > max_bytes:
                    raise HTTPException(
                        status_code=413,
                        detail="Video exceeds upload limit",
                    )

                output_file.write(chunk)

        if total == 0:
            raise HTTPException(
                status_code=400,
                detail="Empty video",
            )

    except Exception:
        source.unlink(missing_ok=True)
        folder.rmdir()
        raise

    finally:
        await file.close()

    JOBS[job_id] = {
        "status": "processing",
    }

    POOL.submit(
        worker,
        job_id,
        sport,
        source,
        folder / "annotated.mp4",
        use_yolo,
    )

    return {
        "job_id": job_id,
        "status": "processing",
    }


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    if job_id not in JOBS:
        raise HTTPException(
            status_code=404,
            detail="Unknown or expired job",
        )

    return JOBS[job_id]


@app.get("/api/jobs/{job_id}/video")
def video(job_id: str):
    path = DATA / job_id / "annotated.mp4"

    if (
        job_id not in JOBS
        or JOBS[job_id]["status"] != "completed"
        or not path.exists()
    ):
        raise HTTPException(
            status_code=404,
            detail="Video not ready",
        )

    return FileResponse(
        path,
        media_type="video/mp4",
        filename="athletevision_annotated.mp4",
    )


@app.get("/api/jobs/{job_id}/report")
def report(job_id: str):
    path = DATA / job_id / "report.json"

    if (
        job_id not in JOBS
        or JOBS[job_id]["status"] != "completed"
        or not path.exists()
    ):
        raise HTTPException(
            status_code=404,
            detail="Report not ready",
        )

    return FileResponse(
        path,
        media_type="application/json",
        filename="athletevision_report.json",
    )


@app.get("/api/jobs/{job_id}/pdf")
def pdf_report(job_id: str):
    path = DATA / job_id / "performance_report.pdf"

    if (
        job_id not in JOBS
        or JOBS[job_id]["status"] != "completed"
        or not path.exists()
    ):
        raise HTTPException(
            status_code=404,
            detail="PDF report not ready",
        )

    return FileResponse(
        path,
        media_type="application/pdf",
        filename="athletevision_performance_report.pdf",
    )
