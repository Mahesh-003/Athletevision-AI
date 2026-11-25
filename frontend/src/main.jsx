// import React,{useEffect,useState,useRef} from 'react';import{createRoot}from'react-dom/client';
// import {Activity,UploadCloud,PlayCircle,ScanLine,ChartNoAxesCombined,CheckCircle2,AlertTriangle,Clock,Download,BrainCircuit,Footprints,Dumbbell,ArrowRight,Info,RefreshCw,Video,Menu,X,ShieldCheck} from 'lucide-react';
// import {LineChart,Line,XAxis,YAxis,Tooltip,CartesianGrid,ResponsiveContainer} from 'recharts';import './styles.css';
// const METRIC_NAMES={average_knee_angle_deg:'Average knee angle',min_knee_angle_deg:'Minimum knee angle',average_torso_inclination_deg:'Average torso inclination',max_torso_inclination_deg:'Maximum torso inclination',torso_variability_deg:'Torso angle variability',left_knee_range_deg:'Left knee movement range',right_knee_range_deg:'Right knee movement range',left_knee_visibility_ratio:'Left knee visibility',right_knee_visibility_ratio:'Right knee visibility',ankle_crossings_per_min_proxy:'Ankle crossing proxy / min',frames_with_pose:'Frames with detected pose',average_technique_score:'Mean experimental squat score'};
// const SPORTS=[{id:'squat',name:'Weightlifting',subtitle:'Barbell squat analysis',icon:Dumbbell},{id:'running',name:'Running',subtitle:'Gait & posture screening',icon:Footprints}];
// function App(){const[sport,setSport]=useState('squat'),[file,setFile]=useState(null),[preview,setPreview]=useState(''),[job,setJob]=useState(null),[status,setStatus]=useState('idle'),[report,setReport]=useState(null),[error,setError]=useState(''),[yolo,setYolo]=useState(false),[menu,setMenu]=useState(false);const input=useRef(null),videoRef=useRef(null);const [activeRep,setActiveRep]=useState(null);const selected=SPORTS.find(s=>s.id===sport);
// useEffect(()=>{if(!file)return;const url=URL.createObjectURL(file);setPreview(url);return()=>URL.revokeObjectURL(url)},[file]);
// useEffect(()=>{if(!job||status!=='processing')return;let alive=true;const interval=setInterval(async()=>{try{const res=await fetch(`/api/jobs/${job}`);if(!res.ok)throw Error('Could not check analysis status');const body=await res.json();if(!alive)return;if(body.status==='completed'){setReport(body.report);setStatus('completed')}else if(body.status==='failed'){setStatus('failed');setError(body.error||'Analysis failed')}}catch(e){if(alive){setStatus('failed');setError(e.message)}}},1700);return()=>{alive=false;clearInterval(interval)}},[job,status]);
// function changeFile(f){if(!f)return;if(!/\.(mp4|mov|avi|mkv|webm)$/i.test(f.name)){setError('Please choose a supported video file.');return;}setFile(f);setActiveRep(null);setReport(null);setJob(null);setStatus('idle');setError('')}
// async function submit(){if(!file)return;setStatus('uploading');setError('');setReport(null);setActiveRep(null);try{const fd=new FormData();fd.append('file',file);fd.append('sport',sport);fd.append('use_yolo',String(yolo));const res=await fetch('/api/analyze',{method:'POST',body:fd});let data=await res.json();if(!res.ok)throw Error(typeof data.detail==='string'?data.detail:'Upload failed');setJob(data.job_id);setStatus('processing')}catch(e){setError(e.message);setStatus('failed')}}
// const download=(url)=>{window.open(url,'_blank','noopener,noreferrer')};return <div className="shell"><aside className={'sidebar '+(menu?'show':'')}><div className="brand"><div className="brandlogo"><Activity size={24}/></div><div><strong>ATHLETE<span>VISION</span></strong><small>AI PERFORMANCE LAB</small></div></div><div className="sidecaption">WORKSPACE</div><a className="nav active" href="#overview"><ChartNoAxesCombined size={18}/> Overview</a><a className="nav" href="#analyzer"><ScanLine size={18}/> Video analyzer</a><a className="nav" href="#report"><BrainCircuit size={18}/> AI insights</a><div className="sidecaption space">SUPPORTED SPORTS</div>{SPORTS.map(({id,name,icon:Icon})=><button className={'nav sportnav '+(sport===id?'selected':'')} onClick={()=>{setSport(id);setReport(null);setJob(null);setStatus('idle');setMenu(false)}} key={id}><Icon size={18}/>{name}<span className="dot"/></button>)}<div className="sidebarfooter"><ShieldCheck size={17}/> Training research prototype<div className="tiny">No medical or injury-risk diagnosis.</div></div></aside><main className="main" id="overview"><div className="topbar"><button className="menubtn" onClick={()=>setMenu(!menu)}>{menu?<X/>:<Menu/>}</button><span className="breadcrumb">WORKSPACE <span>/</span> ANALYTICS</span><div className="topright"><span className="live"><span/> System ready</span><div className="avatar">AV</div></div></div><div className="content"><div className="hero"><div><div className="eyebrow"><span/> NEXT-GEN SPORTS INTELLIGENCE</div><h1>Precision in every <em>movement.</em></h1><p>Turn training footage into measurable insights. Analyze your movement, review flagged technique patterns, and improve with informed feedback.</p><a href="#analyzer" className="textlink">Analyze your first video <ArrowRight size={16}/></a></div><div className="hero-art"><div className="hero-orbit orbit1"/><div className="hero-orbit orbit2"/><Activity size={74} strokeWidth={1.1}/><div className="hero-tag">MOTION TRACKING <span>● LIVE READY</span></div></div></div><div className="stats"><div className="stat"><span className="stathead"><ScanLine size={17}/> ANALYSIS ENGINE</span><strong>2 <small>sports</small></strong><span className="muted">Weightlifting & running</span></div><div className="stat"><span className="stathead"><Activity size={17}/> BODY LANDMARKS</span><strong>33 <small>keypoints</small></strong><span className="muted">MediaPipe Pose Landmarker</span></div><div className="stat"><span className="stathead"><Video size={17}/> PROCESSING</span><strong>12 <small>FPS target</small></strong><span className="muted">Sampled frame analysis</span></div></div><div className="sectionhead" id="analyzer"><div><div className="eyebrow mutedeye">THE STUDIO</div><h2>Movement Analyzer</h2><p>Choose a sport and upload a training clip to begin.</p></div><div className="stepbadge">01 / UPLOAD & ANALYZE</div></div><div className="workgrid"><div className="panel"><h3>1. Select movement</h3><div className="sportcards">{SPORTS.map(({id,name,subtitle,icon:Icon})=><button className={'sportcard '+(sport===id?'chosen':'')} key={id} onClick={()=>{setSport(id);setReport(null);setJob(null);setStatus('idle')}}><Icon size={22}/><b>{name}</b><small>{subtitle}</small>{sport===id&&<CheckCircle2 className="tick" size={17}/>}</button>)}</div><h3 className="mt">2. Upload footage</h3><div className="dropzone" onDragOver={e=>e.preventDefault()} onDrop={e=>{e.preventDefault();changeFile(e.dataTransfer.files[0])}} onClick={()=>input.current?.click()}><input type="file" accept="video/*,.mkv" ref={input} hidden onChange={e=>changeFile(e.target.files[0])}/>{file?<><PlayCircle size={30}/><strong>{file.name}</strong><span>{(file.size/1024/1024).toFixed(1)} MB · Click to replace</span></>:<><UploadCloud size={34}/><strong>Drop your video here</strong><span>or click to browse your files</span><small>MP4, MOV, AVI, MKV, WEBM · max 150 MB</small></>}</div><label className="toggle"><input type="checkbox" checked={yolo} onChange={e=>setYolo(e.target.checked)}/><span className="switch"/><span><b>Enable YOLO person tracking</b><small>Optional; requires Ultralytics and extra processing</small></span></label><button className="analyze" disabled={!file||status==='uploading'||status==='processing'} onClick={submit}>{status==='uploading'||status==='processing'?<><RefreshCw className="spin" size={18}/> {status==='uploading'?'Uploading…':'Analyzing video…'}</>:<><ScanLine size={19}/> Start analysis <ArrowRight size={18}/></>}</button>{error&&<div className="error"><AlertTriangle size={17}/>{error}</div>}</div><div className="panel previewpanel"><div className="panelheading"><h3>Video preview</h3><span className="previewbadge">{status==='completed'?'ANALYZED':'PREVIEW'}</span></div><div className="videoarea">{file?<video ref={videoRef} key={status==='completed'?'annotated':preview} controls playsInline src={status==='completed'?report?.video_url:preview}/>:<div className="placeholder"><div className="playicon"><PlayCircle size={45}/></div><strong>Your footage appears here</strong><span>Select a video to see a preview</span></div>}</div><div className="previewbottom"><div><div className="previewtitle"><span className="greendot"/>{selected.name} session</div><small>{status==='processing'?'Processing frames and measuring landmarks…':status==='completed'?'Analysis completed. Review findings below.':'Awaiting video'}</small></div><span className="quality"><Clock size={14}/> {status==='completed'?`${report.elapsed_seconds}s compute`:'Not started'}</span></div>{status==='completed'&&<div className="downloads"><button onClick={()=>download(report.video_url)}><Download size={16}/> Annotated video</button><button onClick={()=>download(report.report_url)}><Download size={16}/> JSON report</button></div>}</div></div>{report&&<section className="results" id="report"><div className="sectionhead"><div><div className="eyebrow mutedeye">ANALYSIS COMPLETE</div><h2>Your performance insights</h2><p>Heuristic findings from visible 2D body landmarks.</p></div><span className={'resultstatus '+(report.assessment==='Review suggested'||report.assessment==='Insufficient evidence'?'caution':'good')}>{report.assessment}</span></div><div className="metricrow">{Object.entries(report.metrics).filter(([k,v])=>typeof v==='number').map(([k,v])=><div className="metric" key={k}><span>{METRIC_NAMES[k]||k.replaceAll('_',' ')}</span><strong>{v}</strong></div>)}</div>{report.sport==='running'&&<div className="panel reps-panel"><div className="reps-head"><div><h3>Running movement observations</h3><p>Measurements from sampled 2D body landmarks; descriptions are not diagnoses.</p></div><span className="rep-summary">{report.events?.length||0} ankle events</span></div><div className="running-detail"><h4>Measurement interpretation</h4><p>Left/right knee range and torso variability may reveal patterns worth reviewing, but camera position and occlusion can change the readings. Ankle crossing counts are not validated cadence.</p></div>{report.events?.length>0&&<><h4>Approximate movement timestamps</h4><div className="event-list">{report.events.slice(0,24).map((e,i)=><button key={i} className="event-pill" onClick={()=>{if(videoRef.current){videoRef.current.currentTime=e.time_s;videoRef.current.play().catch(()=>{});document.querySelector('.previewpanel')?.scrollIntoView({behavior:'smooth',block:'center'})}}}>{e.time_s.toFixed(2)}s</button>)}</div><p className="rep-note">Click a timestamp to seek the annotated video. These events indicate horizontal ankle crossings, not foot strikes.</p></>}</div>}{report.sport==='squat'&&<div className="panel reps-panel"><div className="reps-head"><div><h3>Repetition-by-repetition review</h3><p>Click a repetition to seek the annotated video to its most bent-knee frame. Video timestamps are approximate.</p></div><span className="rep-summary">{report.reps} complete reps</span></div>{report.events?.length?<><div className="rep-list">{report.events.map(e=><button key={e.rep} className={'rep-card '+(activeRep===e.rep?'rep-active':'')} onClick={()=>{setActiveRep(e.rep);if(videoRef.current){videoRef.current.currentTime=e.bottom_s;videoRef.current.play().catch(()=>{});document.querySelector('.previewpanel')?.scrollIntoView({behavior:'smooth',block:'center'})}}}><span className="rep-number">REP {e.rep}</span><strong>{e.technique_score}/100</strong><span className={e.findings.length?'rep-review':'rep-clear'}>{e.findings.length?'Review suggested':'No flags'}</span><small>{e.start_s.toFixed(1)}s — {e.end_s.toFixed(1)}s</small></button>)}</div>{(()=>{const e=report.events.find(e=>e.rep===activeRep)||report.events[0];return <div className="rep-detail"><div className="rep-detail-title"><strong>Rep {e.rep} · Analysis at {e.bottom_s.toFixed(2)}s</strong><span>{e.assessment}</span></div><div className="rep-measures"><div><small>Min knee angle</small><b>{e.min_knee_angle_deg}°</b></div><div><small>Max torso inclination</small><b>{e.max_torso_inclination_deg}°</b></div><div><small>Duration</small><b>{e.duration_s}s</b></div><div><small>Screening score</small><b>{e.technique_score}/100</b></div></div><div className="rep-checks">{e.checks.map(c=><div key={c.name}><span>{c.name}</span><b>{c.points_awarded}/{c.points_possible}</b></div>)}</div>{e.findings.length?e.findings.map(f=><div className="rep-finding" key={f.code}><b><AlertTriangle size={15}/> {f.title}</b><p>{f.detail}</p><small>{f.correction}</small></div>):<p className="rep-note">No issue flagged by these two screening rules. This does not confirm safe or correct squat technique.</p>}</div>})()}</>:<p className="rep-note">No completed repetitions detected. Ensure the athlete stands upright before and after squatting.</p>}<p className="rep-method">{report.score_method?.name}: {report.score_method?.criteria} {report.score_method?.camera}</p></div>}<div className="resultgrid"><div className="panel chartpanel"><h3>Joint movement over time</h3><div className="chartwrap"><ResponsiveContainer width="100%" height={245}><LineChart data={report.series}><CartesianGrid stroke="#232d40" strokeDasharray="3 6"/><XAxis dataKey="time_s" stroke="#8390a6" tick={{fontSize:11}}/><YAxis stroke="#8390a6" tick={{fontSize:11}}/><Tooltip contentStyle={{background:'#131c2c',border:'1px solid #334057',color:'#fff',borderRadius:9}}/><Line type="monotone" dataKey="knee_angle" stroke="#58e6bb" strokeWidth={2} dot={false} name="Knee angle"/><Line type="monotone" dataKey="torso_lean" stroke="#8c96ff" strokeWidth={2} dot={false} name="Torso lean"/></LineChart></ResponsiveContainer></div><div className="legend"><span className="mint"/> Knee angle <span className="violet"/> Torso inclination</div></div><div className="panel"><h3><BrainCircuit size={19}/> Coaching insights</h3><div className="aiblock"><span className="source">{report.ai_feedback?.source||'local rules'}</span><p>{report.ai_feedback?.text||'Review the measured observations below.'}</p></div><h4>Technique review</h4>{report.issues.length?report.issues.map((issue,i)=><div className="issue" key={i}>{issue.severity==='review'?<AlertTriangle size={17}/>:<Info size={17}/>}<div><b>{issue.title}</b><p>{issue.detail}</p><small>{issue.tip}</small></div></div>):<div className="issue success"><CheckCircle2 size={18}/><div><b>No screened issue detected</b><p>This does not guarantee correct or safe technique.</p></div></div>}</div></div><div className="disclaimer"><Info size={17}/><span>{report.limitations.join(' ')}</span></div></section>}<footer>ATHLETEVISION AI <span>·</span> Computer vision research prototype <span>·</span> Results are not a medical or coaching certification</footer></div></main></div>}
// createRoot(document.getElementById('root')).render(<App/>);

import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";

import {
  Activity,
  UploadCloud,
  PlayCircle,
  ScanLine,
  ChartNoAxesCombined,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Download,
  BrainCircuit,
  Footprints,
  Dumbbell,
  ArrowRight,
  Info,
  RefreshCw,
  Video,
  Menu,
  X,
  ShieldCheck,
} from "lucide-react";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

import "./styles.css";

// =====================================================
// METRIC DISPLAY NAMES
// =====================================================

const METRIC_NAMES = {
  average_knee_angle_deg: "Average knee angle",
  min_knee_angle_deg: "Minimum knee angle",
  average_torso_inclination_deg: "Average torso inclination",
  max_torso_inclination_deg: "Maximum torso inclination",
  torso_variability_deg: "Torso angle variability",
  left_knee_range_deg: "Left knee movement range",
  right_knee_range_deg: "Right knee movement range",
  left_knee_visibility_ratio: "Left knee visibility",
  right_knee_visibility_ratio: "Right knee visibility",
  ankle_crossings_per_min_proxy: "Ankle crossing proxy / min",
  frames_with_pose: "Frames with detected pose",
  average_technique_score: "Mean experimental squat score",
};

const SPORTS = [
  {
    id: "squat",
    name: "Weightlifting",
    subtitle: "Barbell squat analysis",
    icon: Dumbbell,
  },
  {
    id: "running",
    name: "Running",
    subtitle: "Gait & posture screening",
    icon: Footprints,
  },
];

// =====================================================
// MAIN APPLICATION
// =====================================================

function App() {
  const [sport, setSport] = useState("squat");
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [job, setJob] = useState(null);
  const [status, setStatus] = useState("idle");
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");
  const [yolo, setYolo] = useState(false);
  const [menu, setMenu] = useState(false);
  const [activeRep, setActiveRep] = useState(null);

  // PDF report state
  const [pdfAvailable, setPdfAvailable] = useState(false);
  const [pdfError, setPdfError] = useState("");

  const input = useRef(null);
  const videoRef = useRef(null);

  const selected = SPORTS.find((s) => s.id === sport);

  // ===================================================
  // LOCAL VIDEO PREVIEW
  // ===================================================

  useEffect(() => {
    if (!file) {
      setPreview("");
      return;
    }

    const url = URL.createObjectURL(file);
    setPreview(url);

    return () => URL.revokeObjectURL(url);
  }, [file]);

  // ===================================================
  // ANALYSIS STATUS POLLING
  // ===================================================

  useEffect(() => {
    if (!job || status !== "processing") return;

    let alive = true;

    const interval = setInterval(async () => {
      try {
        const response = await fetch(
          `/api/jobs/${job}`
        );

        if (!response.ok) {
          throw new Error(
            "Could not check analysis status."
          );
        }

        const body = await response.json();

        if (!alive) return;

        if (body.status === "completed") {
          setReport(body.report);
          setStatus("completed");

          const available =
            !body.pdf_error &&
            Boolean(body.report?.pdf_url);

          setPdfAvailable(available);
          setPdfError(
            body.pdf_error || ""
          );
        } else if (body.status === "failed") {
          setStatus("failed");
          setError(
            body.error || "Analysis failed."
          );
        }
      } catch (err) {
        if (alive) {
          setStatus("failed");
          setError(err.message);
        }
      }
    }, 1700);

    return () => {
      alive = false;
      clearInterval(interval);
    };
  }, [job, status]);

  // ===================================================
  // RESET ANALYSIS
  // ===================================================

  function resetAnalysis() {
    setJob(null);
    setReport(null);
    setStatus("idle");
    setError("");
    setActiveRep(null);
    setPdfAvailable(false);
    setPdfError("");
  }

  function changeSport(newSport) {
    setSport(newSport);
    resetAnalysis();
    setMenu(false);
  }

  // ===================================================
  // VIDEO FILE VALIDATION
  // ===================================================

  function changeFile(selectedFile) {
    if (!selectedFile) return;

    if (!/\.(mp4|mov|avi|mkv|webm)$/i.test(selectedFile.name)) {
      setError(
        "Please choose a supported video file."
      );
      return;
    }

    setFile(selectedFile);
    resetAnalysis();
  }

  // ===================================================
  // SUBMIT VIDEO TO FASTAPI
  // ===================================================

  async function submit() {
    if (!file) return;

    setStatus("uploading");
    setError("");
    setReport(null);
    setActiveRep(null);
    setPdfAvailable(false);
    setPdfError("");

    try {
      const formData = new FormData();

      formData.append("file", file);
      formData.append("sport", sport);
      formData.append(
        "use_yolo",
        String(yolo)
      );

      const response = await fetch(
        "/api/analyze",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Upload failed."
        );
      }

      setJob(data.job_id);
      setStatus("processing");
    } catch (err) {
      setError(err.message);
      setStatus("failed");
    }
  }

  // ===================================================
  // DOWNLOAD HANDLERS
  // ===================================================

  function download(url) {
    if (!url) {
      setError("Download URL unavailable.");
      return;
    }

    window.open(
      url,
      "_blank",
      "noopener,noreferrer"
    );
  }

  async function downloadPdf() {
    if (!job || !pdfAvailable) {
      setPdfError(
        "PDF report is not available for this analysis."
      );
      return;
    }

    const url =
      report?.pdf_url ||
      `/api/jobs/${job}/pdf`;

    try {
      const response = await fetch(url);

      if (!response.ok) {
        let message = "Unable to download PDF report.";

        if (response.status === 404) {
          message =
            "PDF file not found. Analyze the video again and check backend PDF generation.";
        }

        throw new Error(message);
      }

      const blob = await response.blob();

      const objectUrl =
        URL.createObjectURL(blob);

      const link =
        document.createElement("a");

      link.href = objectUrl;
      link.download =
        `AthleteVision_${sport}_report.pdf`;

      document.body.appendChild(link);
      link.click();
      link.remove();

      setTimeout(() => {
        URL.revokeObjectURL(objectUrl);
      }, 1000);

      setPdfError("");
    } catch (err) {
      setPdfError(err.message);
    }
  }

  // ===================================================
  // SEEK ANNOTATED VIDEO
  // ===================================================

  function seekVideo(timestamp) {
    if (!videoRef.current) return;

    videoRef.current.currentTime = timestamp;

    videoRef.current
      .play()
      .catch(() => {});

    document
      .querySelector(".previewpanel")
      ?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
  }

  // ===================================================
  // FRONTEND RENDER
  // ===================================================

  return (
    <div className="shell">
      {/* SIDEBAR */}
      <aside
        className={
          "sidebar " +
          (menu ? "show" : "")
        }
      >
        <div className="brand">
          <div className="brandlogo">
            <Activity size={24} />
          </div>

          <div>
            <strong>
              ATHLETE<span>VISION</span>
            </strong>
            <small>AI PERFORMANCE LAB</small>
          </div>
        </div>

        <div className="sidecaption">
          WORKSPACE
        </div>

        <a
          className="nav active"
          href="#overview"
        >
          <ChartNoAxesCombined size={18} />
          Overview
        </a>

        <a className="nav" href="#analyzer">
          <ScanLine size={18} />
          Video analyzer
        </a>

        <a className="nav" href="#report">
          <BrainCircuit size={18} />
          AI insights
        </a>

        <div className="sidecaption space">
          SUPPORTED SPORTS
        </div>

        {SPORTS.map(
          ({ id, name, icon: Icon }) => (
            <button
              key={id}
              className={
                "nav sportnav " +
                (sport === id
                  ? "selected"
                  : "")
              }
              onClick={() => changeSport(id)}
            >
              <Icon size={18} />
              {name}
              <span className="dot" />
            </button>
          )
        )}

        <div className="sidebarfooter">
          <ShieldCheck size={17} />
          Training research prototype

          <div className="tiny">
            No medical or injury-risk diagnosis.
          </div>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <main
        className="main"
        id="overview"
      >
        {/* TOP BAR */}
        <div className="topbar">
          <button
            className="menubtn"
            onClick={() => setMenu(!menu)}
          >
            {menu ? <X /> : <Menu />}
          </button>

          <span className="breadcrumb">
            WORKSPACE <span>/</span> ANALYTICS
          </span>

          <div className="topright">
            <span className="live">
              <span />
              System ready
            </span>

            <div className="avatar">
              AV
            </div>
          </div>
        </div>

        <div className="content">
          {/* HERO */}
          <div className="hero">
            <div>
              <div className="eyebrow">
                <span />
                NEXT-GEN SPORTS INTELLIGENCE
              </div>

              <h1>
                Precision in every{" "}
                <em>movement.</em>
              </h1>

              <p>
                Turn training footage into
                measurable insights. Analyze your
                movement, review flagged technique
                patterns, and improve with
                informed feedback.
              </p>

              <a
                href="#analyzer"
                className="textlink"
              >
                Analyze your first video
                <ArrowRight size={16} />
              </a>
            </div>

            <div className="hero-art">
              <div className="hero-orbit orbit1" />
              <div className="hero-orbit orbit2" />

              <Activity
                size={74}
                strokeWidth={1.1}
              />

              <div className="hero-tag">
                MOTION TRACKING
                <span>● LIVE READY</span>
              </div>
            </div>
          </div>

          {/* STATS */}
          <div className="stats">
            <div className="stat">
              <span className="stathead">
                <ScanLine size={17} />
                ANALYSIS ENGINE
              </span>

              <strong>
                2 <small>sports</small>
              </strong>

              <span className="muted">
                Weightlifting & running
              </span>
            </div>

            <div className="stat">
              <span className="stathead">
                <Activity size={17} />
                BODY LANDMARKS
              </span>

              <strong>
                33 <small>keypoints</small>
              </strong>

              <span className="muted">
                MediaPipe Pose Landmarker
              </span>
            </div>

            <div className="stat">
              <span className="stathead">
                <Video size={17} />
                PROCESSING
              </span>

              <strong>
                12 <small>FPS target</small>
              </strong>

              <span className="muted">
                Sampled frame analysis
              </span>
            </div>
          </div>

          {/* ANALYZER HEADER */}
          <div
            className="sectionhead"
            id="analyzer"
          >
            <div>
              <div className="eyebrow mutedeye">
                THE STUDIO
              </div>

              <h2>Movement Analyzer</h2>

              <p>
                Choose a sport and upload a
                training clip to begin.
              </p>
            </div>

            <div className="stepbadge">
              01 / UPLOAD & ANALYZE
            </div>
          </div>

          {/* UPLOAD AND VIDEO PREVIEW */}
          <div className="workgrid">
            <div className="panel">
              <h3>1. Select movement</h3>

              <div className="sportcards">
                {SPORTS.map(
                  ({
                    id,
                    name,
                    subtitle,
                    icon: Icon,
                  }) => (
                    <button
                      key={id}
                      className={
                        "sportcard " +
                        (sport === id
                          ? "chosen"
                          : "")
                      }
                      onClick={() =>
                        changeSport(id)
                      }
                    >
                      <Icon size={22} />

                      <b>{name}</b>
                      <small>{subtitle}</small>

                      {sport === id && (
                        <CheckCircle2
                          className="tick"
                          size={17}
                        />
                      )}
                    </button>
                  )
                )}
              </div>

              <h3 className="mt">
                2. Upload footage
              </h3>

              <div
                className="dropzone"
                onDragOver={(e) =>
                  e.preventDefault()
                }
                onDrop={(e) => {
                  e.preventDefault();
                  changeFile(
                    e.dataTransfer.files[0]
                  );
                }}
                onClick={() =>
                  input.current?.click()
                }
              >
                <input
                  type="file"
                  accept="video/*,.mkv"
                  ref={input}
                  hidden
                  onChange={(e) =>
                    changeFile(e.target.files[0])
                  }
                />

                {file ? (
                  <>
                    <PlayCircle size={30} />

                    <strong>
                      {file.name}
                    </strong>

                    <span>
                      {(
                        file.size /
                        1024 /
                        1024
                      ).toFixed(1)}{" "}
                      MB · Click to replace
                    </span>
                  </>
                ) : (
                  <>
                    <UploadCloud size={34} />

                    <strong>
                      Drop your video here
                    </strong>

                    <span>
                      or click to browse your files
                    </span>

                    <small>
                      MP4, MOV, AVI, MKV, WEBM ·
                      max 150 MB
                    </small>
                  </>
                )}
              </div>

              {/* YOLO TRACKING */}
              <label className="toggle">
                <input
                  type="checkbox"
                  checked={yolo}
                  onChange={(e) =>
                    setYolo(e.target.checked)
                  }
                />

                <span className="switch" />

                <span>
                  <b>
                    Enable YOLO person tracking
                  </b>

                  <small>
                    Optional; requires Ultralytics
                    and extra processing
                  </small>
                </span>
              </label>

              {/* ANALYZE BUTTON */}
              <button
                className="analyze"
                disabled={
                  !file ||
                  status === "uploading" ||
                  status === "processing"
                }
                onClick={submit}
              >
                {status === "uploading" ||
                status === "processing" ? (
                  <>
                    <RefreshCw
                      className="spin"
                      size={18}
                    />

                    {status === "uploading"
                      ? "Uploading…"
                      : "Analyzing video…"}
                  </>
                ) : (
                  <>
                    <ScanLine size={19} />

                    Start analysis

                    <ArrowRight size={18} />
                  </>
                )}
              </button>

              {error && (
                <div className="error">
                  <AlertTriangle size={17} />
                  {error}
                </div>
              )}
            </div>

            {/* VIDEO PREVIEW */}
            <div className="panel previewpanel">
              <div className="panelheading">
                <h3>Video preview</h3>

                <span className="previewbadge">
                  {status === "completed"
                    ? "ANALYZED"
                    : "PREVIEW"}
                </span>
              </div>

              <div className="videoarea">
                {file ? (
                  <video
                    ref={videoRef}
                    key={
                      status === "completed"
                        ? "annotated"
                        : preview
                    }
                    controls
                    playsInline
                    src={
                      status === "completed"
                        ? report?.video_url
                        : preview
                    }
                  />
                ) : (
                  <div className="placeholder">
                    <div className="playicon">
                      <PlayCircle size={45} />
                    </div>

                    <strong>
                      Your footage appears here
                    </strong>

                    <span>
                      Select a video to see a preview
                    </span>
                  </div>
                )}
              </div>

              <div className="previewbottom">
                <div>
                  <div className="previewtitle">
                    <span className="greendot" />
                    {selected.name} session
                  </div>

                  <small>
                    {status === "processing"
                      ? "Processing frames and measuring landmarks…"
                      : status === "completed"
                      ? "Analysis completed. Review findings below."
                      : "Awaiting video"}
                  </small>
                </div>

                <span className="quality">
                  <Clock size={14} />

                  {status === "completed"
                    ? `${report.elapsed_seconds}s compute`
                    : "Not started"}
                </span>
              </div>

              {/* DOWNLOAD SECTION */}
              {status === "completed" && (
                <>
                  <div className="downloads">
                    <button
                      onClick={() =>
                        download(report.video_url)
                      }
                    >
                      <Download size={16} />
                      Annotated video
                    </button>

                    <button
                      onClick={() =>
                        download(report.report_url)
                      }
                    >
                      <Download size={16} />
                      JSON report
                    </button>

                    {/* NEW PDF BUTTON */}
                    <button
                      disabled={!pdfAvailable}
                      onClick={downloadPdf}
                      title={
                        pdfAvailable
                          ? "Download performance report as PDF"
                          : "PDF report unavailable"
                      }
                    >
                      <Download size={16} />
                      PDF Report
                    </button>
                  </div>

                  {pdfError && (
                    <div
                      className="error"
                      role="alert"
                      style={{ marginTop: 12 }}
                    >
                      <AlertTriangle size={17} />
                      {pdfError}
                    </div>
                  )}

                  {!pdfAvailable &&
                    !pdfError && (
                      <p className="rep-note">
                        PDF report is not yet
                        available for this analysis.
                      </p>
                    )}
                </>
              )}
            </div>
          </div>

          {/* RESULTS */}
          {report && (
            <section
              className="results"
              id="report"
            >
              <div className="sectionhead">
                <div>
                  <div className="eyebrow mutedeye">
                    ANALYSIS COMPLETE
                  </div>

                  <h2>
                    Your performance insights
                  </h2>

                  <p>
                    Heuristic findings from
                    visible 2D body landmarks.
                  </p>
                </div>

                <span
                  className={
                    "resultstatus " +
                    (report.assessment ===
                      "Review suggested" ||
                    report.assessment ===
                      "Insufficient evidence"
                      ? "caution"
                      : "good")
                  }
                >
                  {report.assessment}
                </span>
              </div>

              {/* METRIC CARDS */}
              <div className="metricrow">
                {Object.entries(
                  report.metrics || {}
                )
                  .filter(
                    ([key, value]) =>
                      typeof value === "number"
                  )
                  .map(([key, value]) => (
                    <div
                      className="metric"
                      key={key}
                    >
                      <span>
                        {METRIC_NAMES[key] ||
                          key.replaceAll(
                            "_",
                            " "
                          )}
                      </span>

                      <strong>
                        {value}
                      </strong>
                    </div>
                  ))}
              </div>

              {/* RUNNING REVIEW */}
              {report.sport === "running" && (
                <div className="panel reps-panel">
                  <div className="reps-head">
                    <div>
                      <h3>
                        Running movement observations
                      </h3>

                      <p>
                        Measurements from sampled 2D
                        body landmarks; descriptions
                        are not diagnoses.
                      </p>
                    </div>

                    <span className="rep-summary">
                      {report.events?.length || 0}{" "}
                      ankle events
                    </span>
                  </div>

                  <div className="running-detail">
                    <h4>
                      Measurement interpretation
                    </h4>

                    <p>
                      Left/right knee range and
                      torso variability may reveal
                      patterns worth reviewing,
                      but camera position and
                      occlusion can change the
                      readings. Ankle crossing
                      counts are not validated
                      cadence.
                    </p>
                  </div>

                  {report.events?.length > 0 && (
                    <>
                      <h4>
                        Approximate movement
                        timestamps
                      </h4>

                      <div className="event-list">
                        {report.events
                          .slice(0, 24)
                          .map((event, index) => (
                            <button
                              key={index}
                              className="event-pill"
                              onClick={() =>
                                seekVideo(
                                  event.time_s
                                )
                              }
                            >
                              {Number(
                                event.time_s
                              ).toFixed(2)}
                              s
                            </button>
                          ))}
                      </div>

                      <p className="rep-note">
                        Click a timestamp to seek
                        the annotated video.
                        These events indicate
                        horizontal ankle crossings,
                        not foot strikes.
                      </p>
                    </>
                  )}
                </div>
              )}

              {/* SQUAT REP REVIEW */}
              {report.sport === "squat" && (
                <div className="panel reps-panel">
                  <div className="reps-head">
                    <div>
                      <h3>
                        Repetition-by-repetition
                        review
                      </h3>

                      <p>
                        Click a repetition to seek
                        the annotated video to its
                        most bent-knee frame.
                        Video timestamps are approximate.
                      </p>
                    </div>

                    <span className="rep-summary">
                      {report.reps} complete reps
                    </span>
                  </div>

                  {report.events?.length ? (
                    <>
                      <div className="rep-list">
                        {report.events.map(
                          (event) => (
                            <button
                              key={event.rep}
                              className={
                                "rep-card " +
                                (activeRep ===
                                event.rep
                                  ? "rep-active"
                                  : "")
                              }
                              onClick={() => {
                                setActiveRep(
                                  event.rep
                                );
                                seekVideo(
                                  event.bottom_s
                                );
                              }}
                            >
                              <span className="rep-number">
                                REP {event.rep}
                              </span>

                              <strong>
                                {
                                  event.technique_score
                                }
                                /100
                              </strong>

                              <span
                                className={
                                  event.findings
                                    ?.length
                                    ? "rep-review"
                                    : "rep-clear"
                                }
                              >
                                {event.findings
                                  ?.length
                                  ? "Review suggested"
                                  : "No flags"}
                              </span>

                              <small>
                                {Number(
                                  event.start_s
                                ).toFixed(1)}
                                s —{" "}
                                {Number(
                                  event.end_s
                                ).toFixed(1)}
                                s
                              </small>
                            </button>
                          )
                        )}
                      </div>

                      {(() => {
                        const event =
                          report.events.find(
                            (item) =>
                              item.rep ===
                              activeRep
                          ) ||
                          report.events[0];

                        return (
                          <div className="rep-detail">
                            <div className="rep-detail-title">
                              <strong>
                                Rep {event.rep} ·
                                Analysis at{" "}
                                {Number(
                                  event.bottom_s
                                ).toFixed(2)}
                                s
                              </strong>

                              <span>
                                {event.assessment}
                              </span>
                            </div>

                            <div className="rep-measures">
                              <div>
                                <small>
                                  Min knee angle
                                </small>
                                <b>
                                  {
                                    event.min_knee_angle_deg
                                  }
                                  °
                                </b>
                              </div>

                              <div>
                                <small>
                                  Max torso inclination
                                </small>
                                <b>
                                  {
                                    event.max_torso_inclination_deg
                                  }
                                  °
                                </b>
                              </div>

                              <div>
                                <small>
                                  Duration
                                </small>
                                <b>
                                  {
                                    event.duration_s
                                  }
                                  s
                                </b>
                              </div>

                              <div>
                                <small>
                                  Screening score
                                </small>
                                <b>
                                  {
                                    event.technique_score
                                  }
                                  /100
                                </b>
                              </div>
                            </div>

                            <div className="rep-checks">
                              {(
                                event.checks || []
                              ).map((check) => (
                                <div
                                  key={
                                    check.name
                                  }
                                >
                                  <span>
                                    {check.name}
                                  </span>

                                  <b>
                                    {
                                      check.points_awarded
                                    }
                                    /
                                    {
                                      check.points_possible
                                    }
                                  </b>
                                </div>
                              ))}
                            </div>

                            {event.findings
                              ?.length ? (
                              event.findings.map(
                                (finding) => (
                                  <div
                                    className="rep-finding"
                                    key={
                                      finding.code
                                    }
                                  >
                                    <b>
                                      <AlertTriangle
                                        size={15}
                                      />
                                      {
                                        finding.title
                                      }
                                    </b>

                                    <p>
                                      {
                                        finding.detail
                                      }
                                    </p>

                                    <small>
                                      {
                                        finding.correction
                                      }
                                    </small>
                                  </div>
                                )
                              )
                            ) : (
                              <p className="rep-note">
                                No issue flagged by
                                these screening rules.
                                This does not confirm
                                safe or correct squat
                                technique.
                              </p>
                            )}
                          </div>
                        );
                      })()}
                    </>
                  ) : (
                    <p className="rep-note">
                      No completed repetitions
                      detected. Ensure the athlete
                      stands upright before and
                      after squatting.
                    </p>
                  )}

                  <p className="rep-method">
                    {report.score_method?.name}
                    :{" "}
                    {report.score_method?.criteria}{" "}
                    {report.score_method?.camera}
                  </p>
                </div>
              )}

              {/* MOVEMENT CHART AND INSIGHTS */}
              <div className="resultgrid">
                <div className="panel chartpanel">
                  <h3>
                    Joint movement over time
                  </h3>

                  <div className="chartwrap">
                    <ResponsiveContainer
                      width="100%"
                      height={245}
                    >
                      <LineChart
                        data={
                          report.series || []
                        }
                      >
                        <CartesianGrid
                          stroke="#232d40"
                          strokeDasharray="3 6"
                        />

                        <XAxis
                          dataKey="time_s"
                          stroke="#8390a6"
                          tick={{
                            fontSize: 11,
                          }}
                        />

                        <YAxis
                          stroke="#8390a6"
                          tick={{
                            fontSize: 11,
                          }}
                        />

                        <Tooltip
                          contentStyle={{
                            background:
                              "#131c2c",
                            border:
                              "1px solid #334057",
                            color: "#fff",
                            borderRadius: 9,
                          }}
                        />

                        <Line
                          type="monotone"
                          dataKey="knee_angle"
                          stroke="#58e6bb"
                          strokeWidth={2}
                          dot={false}
                          name="Knee angle"
                        />

                        <Line
                          type="monotone"
                          dataKey="torso_lean"
                          stroke="#8c96ff"
                          strokeWidth={2}
                          dot={false}
                          name="Torso lean"
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="legend">
                    <span className="mint" />
                    Knee angle
                    <span className="violet" />
                    Torso inclination
                  </div>
                </div>

                {/* COACHING INSIGHTS */}
                <div className="panel">
                  <h3>
                    <BrainCircuit size={19} />
                    Coaching insights
                  </h3>

                  <div className="aiblock">
                    <span className="source">
                      {report.ai_feedback
                        ?.source ||
                        "local rules"}
                    </span>

                    <p>
                      {report.ai_feedback
                        ?.text ||
                        "Review the measured observations below."}
                    </p>
                  </div>

                  <h4>
                    Technique review
                  </h4>

                  {(report.issues || [])
                    .length ? (
                    report.issues.map(
                      (issue, index) => (
                        <div
                          className="issue"
                          key={index}
                        >
                          {issue.severity ===
                          "review" ? (
                            <AlertTriangle
                              size={17}
                            />
                          ) : (
                            <Info size={17} />
                          )}

                          <div>
                            <b>
                              {issue.title}
                            </b>

                            <p>
                              {issue.detail}
                            </p>

                            <small>
                              {issue.tip}
                            </small>
                          </div>
                        </div>
                      )
                    )
                  ) : (
                    <div className="issue success">
                      <CheckCircle2
                        size={18}
                      />

                      <div>
                        <b>
                          No screened issue
                          detected
                        </b>

                        <p>
                          This does not guarantee
                          correct or safe technique.
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* LIMITATIONS */}
              <div className="disclaimer">
                <Info size={17} />

                <span>
                  {(report.limitations || [])
                    .join(" ")}
                </span>
              </div>
            </section>
          )}

          {/* FOOTER */}
          <footer>
            ATHLETEVISION AI
            <span> · </span>
            Computer vision research prototype
            <span> · </span>
            Results are not a medical or
            coaching certification
          </footer>
        </div>
      </main>
    </div>
  );
}

createRoot(
  document.getElementById("root")
).render(<App />);
