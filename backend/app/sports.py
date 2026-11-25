# """Educational single-camera screening; not a clinical or coach-certified classifier."""
# import statistics
# import math
# from .geometry import get_point


# def _round(value):
#     return round(value, 2)


# def _rep_review(number, samples):
#     """One complete down/up interval; only 2D observations are scored."""
#     start_t = samples[0][0]
#     end_t = samples[-1][0]
#     # The deepest observed pose is approximated by the smallest knee angle;
#     # camera angle still limits absolute depth judgment.
#     bottom_t, bottom = min(samples, key=lambda item: item[1]['knee_angle'])
#     min_knee = bottom['knee_angle']
#     max_lean = max(f['torso_lean'] for _, f in samples)
#     hip_minus_knee = bottom['hip_y'] - bottom['knee_y']
#     # y increases downwards in video coordinates. 0.025 is a normalized margin.
#     depth_review = hip_minus_knee < -0.025
#     lean_review = max_lean > 48
#     findings = []
#     checks = [
#         {'name': 'Apparent depth', 'points_possible': 50,
#          'points_awarded': 0 if depth_review else 50, 'flagged': depth_review},
#         {'name': 'Torso inclination', 'points_possible': 30,
#          'points_awarded': 0 if lean_review else 30, 'flagged': lean_review},
#         {'name': 'Observable complete cycle', 'points_possible': 20,
#          'points_awarded': 20, 'flagged': False},
#     ]
#     if depth_review:
#         findings.append({'code': 'depth', 'title': 'Apparent squat depth may be limited',
#             'detail': 'At the most bent-knee frame, the visible hip landmark is above the knee landmark in this 2D view.',
#             'correction': 'Film from a stationary side view at roughly hip height. With a coach, compare the bottom position with the intended squat variation; do not force a painful depth.',
#             'time_s': _round(bottom_t)})
#     if lean_review:
#         lean_t = max(samples, key=lambda item: item[1]['torso_lean'])[0]
#         findings.append({'code': 'torso', 'title': 'Large apparent torso inclination',
#             'detail': 'At least one sampled frame exceeds the configurable 48° screen threshold; this can be normal for some squat styles.',
#             'correction': 'Check camera alignment and have a coach review bracing, stance and bar position. Torso inclination alone is not a fault or evidence of spinal rounding.',
#             'time_s': _round(lean_t)})
#     score = sum(c['points_awarded'] for c in checks)
#     return {'rep': number, 'start_s': _round(start_t), 'bottom_s': _round(bottom_t),
#             'end_s': _round(end_t), 'duration_s': _round(end_t-start_t),
#             'min_knee_angle_deg': round(min_knee, 1),
#             'max_torso_inclination_deg': round(max_lean, 1),
#             'hip_minus_knee_normalized': round(hip_minus_knee, 3),
#             'depth_review': depth_review, 'torso_review': lean_review,
#             'technique_score': score, 'checks': checks, 'findings': findings,
#             'assessment': 'Review suggested' if findings else 'No screened issue detected'}


# def squat(frames):
#     valid = [(t, f) for t, f in frames if f and f.get('knee_angle') is not None]
#     if len(valid) < 5:
#         return empty('squat')
#     phase = 'up'
#     active = []
#     events = []
#     last_upright = None
#     for t, f in valid:
#         knee = f['knee_angle']
#         if phase == 'up' and knee < 115:
#             phase = 'down'
#             # Include preceding upright frame when present for a more useful start.
#             active = [last_upright] if last_upright else []
#             active.append((t, f))
#         elif phase == 'down':
#             active.append((t, f))
#             if knee > 155:
#                 if len(active) >= 3 and t-active[0][0] >= .25:
#                     events.append(_rep_review(len(events)+1, active))
#                 phase = 'up'
#                 active = []
#         if phase == 'up' and knee >= 155:
#             last_upright = (t, f)
#     n = len(valid)
#     issues = []
#     shallow = sum(bool(e['depth_review']) for e in events)
#     leaned = sum(bool(e['torso_review']) for e in events)
#     if shallow:
#         issues.append({'severity':'review', 'title':'Depth may be limited',
#             'detail':f'{shallow} of {len(events)} completed repetitions have apparent hip-above-knee geometry at the bent-knee frame.',
#             'tip':'Use a fixed side-view camera and review the bottom position with a qualified coach.'})
#     if leaned:
#         issues.append({'severity':'review', 'title':'Torso inclination deserves review',
#             'detail':f'{leaned} of {len(events)} repetitions cross the 48° 2D screen threshold.',
#             'tip':'Compare with squat style, camera position, balance and bracing; forward lean is not automatically wrong.'})
#     if not events:
#         issues.append({'severity':'info', 'title':'No complete repetitions confirmed',
#             'detail':'No complete down-up cycle crossed both knee-angle thresholds.',
#             'tip':'Include standing positions before and after each squat in a clear side-view clip.'})
#     scores = [e['technique_score'] for e in events]
#     return {'sport':'squat', 'reps':len(events),
#         'metrics':{'average_knee_angle_deg':round(statistics.mean(f['knee_angle'] for _,f in valid),1),
#             'min_knee_angle_deg':round(min(f['knee_angle'] for _,f in valid),1),
#             'average_torso_inclination_deg':round(statistics.mean(f['torso_lean'] for _,f in valid),1),
#             'frames_with_pose':n,
#             'average_technique_score':round(statistics.mean(scores),1) if scores else None},
#         'events':events, 'rep_details':events, 'issues':issues,
#         'score_method':{'name':'Experimental visual screening score (not a safety or correctness rating)',
#            'criteria':'Each complete rep begins at 100: -50 if hip appears above knee by >0.025 normalized image height at the most bent-knee sampled frame; -30 if 2D torso lean exceeds 48°; 20 points are for observing a complete motion cycle. Missing/partial reps are excluded.',
#            'camera':'For stationary, unobstructed side-view footage only. Thresholds are not validated for all squat styles, camera positions or body types.'},
#         'assessment':'Review suggested' if issues else 'No screened issue detected',
#         'limitations':['Rep times are approximate sampled-frame timestamps.',
#                        '2D depth and torso screens depend on camera viewpoint; scores are not validated technique grades.',
#                        'Bar path, spinal posture and injury risk are not verified.']}


# def _percentile(values, pct):
#     values = sorted(values)
#     if not values:
#         return None
#     position = (len(values) - 1) * pct / 100
#     low = int(position)
#     high = min(low + 1, len(values) - 1)
#     return values[low] + (values[high] - values[low]) * (position - low)


# def _joint_angle(raw, a, b, c, width, height):
#     """Landmark visibility screened, pixel-aspect-corrected 2D joint angle."""
#     if len(raw) <= max(a, b, c):
#         return None
#     pts = [raw[i] for i in (a, b, c)]
#     if any(p.get('visibility', 0) < .6 for p in pts):
#         return None
#     ax, ay = pts[0]['x'] * width, pts[0]['y'] * height
#     bx, by = pts[1]['x'] * width, pts[1]['y'] * height
#     cx, cy = pts[2]['x'] * width, pts[2]['y'] * height
#     u, v = (ax - bx, ay - by), (cx - bx, cy - by)
#     den = math.hypot(*u) * math.hypot(*v)
#     if den < 1e-8:
#         return None
#     cosine = max(-1, min(1, (u[0] * v[0] + u[1] * v[1]) / den))
#     return math.degrees(math.acos(cosine))


# def running(frames, width, height):
#     """Running observations: not a validated gait or injury classifier."""
#     valid = [(t, f, raw) for t, f, raw in frames if f and raw]
#     if len(valid) < 12:
#         return empty('running')

#     left, right, torso, ankles = [], [], [], []
#     for t, f, raw in valid:
#         la = _joint_angle(raw, 23, 25, 27, width, height)
#         ra = _joint_angle(raw, 24, 26, 28, width, height)
#         if la is not None:
#             left.append((t, la))
#         if ra is not None:
#             right.append((t, ra))
#         if f.get('torso_lean') is not None:
#             torso.append((t, f['torso_lean']))
#         if len(raw) > 28 and all(raw[i].get('visibility', 0) >= .6 for i in (27, 28)):
#             ankles.append((t, (raw[27]['x'] - raw[28]['x']) * width))

#     duration = valid[-1][0] - valid[0][0]
#     lv = [x for _, x in left]
#     rv = [x for _, x in right]
#     tv = [x for _, x in torso]
#     quality_l, quality_r = len(left) / len(valid), len(right) / len(valid)
#     left_range = _percentile(lv, 95) - _percentile(lv, 5) if len(lv) >= 12 else None
#     right_range = _percentile(rv, 95) - _percentile(rv, 5) if len(rv) >= 12 else None
#     lean_avg = statistics.mean(tv) if tv else None
#     lean_max = max(tv) if tv else None
#     lean_sd = statistics.pstdev(tv) if len(tv) >= 2 else None
#     knee = [f['knee_angle'] for _, f, _ in valid if f.get('knee_angle') is not None]

#     issues = []
#     events = []

#     def finding(severity, code, title, detail, tip, timestamp=None):
#         obj = dict(severity=severity, code=code, title=title, detail=detail, tip=tip)
#         if timestamp is not None:
#             obj['time_s'] = round(timestamp, 2)
#         issues.append(obj)

#     insufficient = duration < 3 or min(quality_l, quality_r) < .5
#     if insufficient:
#         finding('info', 'limited_evidence', 'Limited gait-analysis evidence',
#                 'The clip is too short or one leg is not clearly visible for much of the recording.',
#                 'Use a fixed side-view camera with both legs visible for at least 5–10 seconds.')

#     if lean_avg is not None and lean_avg > 30:
#         finding('review', 'torso_angle', 'Large observed torso inclination',
#                 f'The mean 2D torso inclination was {lean_avg:.1f}°. This is not automatically a technique error.',
#                 'Compare camera angle and running style with a coach.',
#                 max(torso, key=lambda x: x[1])[0])
#     if lean_sd is not None and lean_sd > 10 and duration >= 3:
#         finding('info', 'torso_variation', 'Variation in torso orientation',
#                 f'Observed 2D torso-angle standard deviation: {lean_sd:.1f}°.',
#                 'Review the annotated footage for camera movement and repeated torso motion.')
#     if left_range is not None and right_range is not None and min(quality_l, quality_r) >= .7 and duration >= 3:
#         if abs(left_range - right_range) > 25:
#             finding('info', 'knee_range_difference', 'Different visible left/right knee ranges',
#                     f'Left: {left_range:.1f}°; right: {right_range:.1f}°. Camera perspective can create apparent differences.',
#                     'Compare complete gait cycles under consistent lighting and a side-view camera.')

#     last_cross = -10.
#     for (ta, xa), (tb, xb) in zip(ankles, ankles[1:]):
#         if (tb - ta <= .3 and xa * xb < 0 and abs(xa - xb) > width * .025
#                 and tb - last_cross >= .25):
#             events.append({'type': 'ankle_crossing', 'time_s': round(tb, 2),
#                            'description': 'Approximate horizontal ankle crossing (not a foot strike)'})
#             last_cross = tb
#     ankle_duration = ankles[-1][0] - ankles[0][0] if len(ankles) > 1 else 0
#     crossing_proxy = (len(events) * 60 / ankle_duration) if ankle_duration >= 3 else None
#     if crossing_proxy is None:
#         finding('info', 'ankle_visibility', 'Ankle-cycle estimate unavailable',
#                 'There are insufficient continuous observations of both ankles.',
#                 'Record a stable side view with both feet visible.')

#     # Descriptive insights are included even if no provisional threshold is crossed.
#     if lean_avg is not None:
#         finding('info', 'torso_summary', 'Observed torso orientation',
#                 f'Mean: {lean_avg:.1f}°; maximum: {lean_max:.1f}°; '
#                 f'variation: {lean_sd:.1f}°.' if lean_sd is not None else f'Mean: {lean_avg:.1f}°.',
#                 'Compare sessions filmed from the same camera position.')
#     if left_range is not None and right_range is not None:
#         finding('info', 'knee_summary', 'Observed left/right knee motion',
#                 f'Left knee 5th–95th percentile range: {left_range:.1f}°; right: {right_range:.1f}°.',
#                 'These are image-plane measurements, not a diagnosis of gait asymmetry.')

#     metrics = {
#         'average_knee_angle_deg': round(statistics.mean(knee), 1) if knee else None,
#         'average_torso_inclination_deg': round(lean_avg, 1) if lean_avg is not None else None,
#         'max_torso_inclination_deg': round(lean_max, 1) if lean_max is not None else None,
#         'torso_variability_deg': round(lean_sd, 1) if lean_sd is not None else None,
#         'left_knee_range_deg': round(left_range, 1) if left_range is not None else None,
#         'right_knee_range_deg': round(right_range, 1) if right_range is not None else None,
#         'left_knee_visibility_ratio': round(quality_l, 2),
#         'right_knee_visibility_ratio': round(quality_r, 2),
#         'ankle_crossings_per_min_proxy': round(crossing_proxy, 1) if crossing_proxy is not None else None,
#         'frames_with_pose': len(valid),
#     }
#     assessment = ('Insufficient evidence' if insufficient else
#                   'Review suggested' if any(i['severity'] == 'review' for i in issues) else
#                   'No screened issue detected')
#     return {'sport': 'running', 'reps': None, 'metrics': metrics, 'events': events,
#             'issues': issues, 'assessment': assessment,
#             'limitations': ['2D knee angles and torso orientation depend on viewpoint and landmark visibility.',
#                             'Ankle-crossing frequency is not validated running cadence or foot strike timing.',
#                             'Speed, stride length, impact force and injury risk are not measured.']}


# def empty(sport):
#     return {'sport':sport,'reps':0 if sport=='squat' else None,'metrics':{'frames_with_pose':0},'events':[],
#             'rep_details':[] if sport=='squat' else None,
#             'issues':[{'severity':'review','title':'Pose not detected','detail':'Could not see a complete visible body.',
#                        'tip':'Record a brighter video, with the full person visible and minimal occlusion.'}],
#             'assessment':'Insufficient evidence','limitations':['No technique classification possible without landmarks.']}

"""
AthleteVision AI - Sports Analysis Engine

Supported Sports:
1. Weightlifting (Squat)
2. Running

Educational single-camera movement screening.
Results are not validated technique or safety ratings.
"""

import math
import statistics


# =====================================================
# COMMON HELPER FUNCTIONS
# =====================================================

def _round(value):
    return round(value, 2)


def _percentile(values, pct):
    """Calculate percentile from numerical observations."""

    values = sorted(values)

    if not values:
        return None

    position = (len(values) - 1) * pct / 100

    low = int(position)
    high = min(low + 1, len(values) - 1)

    return (
        values[low]
        + (values[high] - values[low]) * (position - low)
    )


def _joint_angle(raw, a, b, c, width, height):
    """
    Calculate 2D joint angle from three MediaPipe landmarks.
    Returns None when landmark visibility is insufficient.
    """

    if len(raw) <= max(a, b, c):
        return None

    points = [raw[i] for i in (a, b, c)]

    if any(
        p.get("visibility", 0) < 0.6
        for p in points
    ):
        return None

    ax = points[0]["x"] * width
    ay = points[0]["y"] * height

    bx = points[1]["x"] * width
    by = points[1]["y"] * height

    cx = points[2]["x"] * width
    cy = points[2]["y"] * height

    u = (ax - bx, ay - by)
    v = (cx - bx, cy - by)

    denominator = (
        math.hypot(*u) * math.hypot(*v)
    )

    if denominator < 1e-8:
        return None

    cosine = (
        u[0] * v[0] + u[1] * v[1]
    ) / denominator

    cosine = max(-1.0, min(1.0, cosine))

    return math.degrees(math.acos(cosine))


# =====================================================
# WEIGHTLIFTING - INDIVIDUAL REP ANALYSIS
# =====================================================

def _rep_review(number, samples):
    """
    Analyze one completed squat repetition.

    Uses:
    - Knee flexion
    - Apparent hip-to-knee depth
    - Sustained torso inclination
    """

    start_t = samples[0][0]
    end_t = samples[-1][0]

    # Approximate bottom by smallest observed knee angle.
    bottom_t, bottom = min(
        samples,
        key=lambda item: item[1]["knee_angle"]
    )

    min_knee = bottom["knee_angle"]

    # Collect all torso measurements.
    lean_samples = [
        f["torso_lean"]
        for _, f in samples
        if f.get("torso_lean") is not None
    ]

    max_lean = (
        max(lean_samples)
        if lean_samples else None
    )

    # Use an upper percentile instead of one noisy frame.
    sustained_lean = (
        _percentile(lean_samples, 85)
        if len(lean_samples) >= 3
        else max_lean
    )

    hip_minus_knee = (
        bottom["hip_y"] - bottom["knee_y"]
    )

    # Normalized image coordinates:
    # larger y means lower in the video.
    depth_review = hip_minus_knee < -0.025

    # Provisional torso-angle screening.
    lean_review = (
        sustained_lean is not None
        and sustained_lean > 48
    )

    findings = []

    # Experimental screening score.
    checks = [
        {
            "name": "Apparent depth",
            "points_possible": 50,
            "points_awarded": (
                0 if depth_review else 50
            ),
            "flagged": depth_review,
        },
        {
            "name": "Torso inclination",
            "points_possible": 30,
            "points_awarded": (
                0 if lean_review else 30
            ),
            "flagged": lean_review,
        },
        {
            "name": "Observable complete cycle",
            "points_possible": 20,
            "points_awarded": 20,
            "flagged": False,
        },
    ]

    if depth_review:
        findings.append({
            "code": "depth",
            "title": "Apparent squat depth may be limited",
            "detail": (
                "At the most bent-knee frame, "
                "the hip landmark appears above "
                "the knee landmark in the 2D view."
            ),
            "correction": (
                "Record a stationary side-view video "
                "at approximately hip height. "
                "Review depth with a qualified coach "
                "according to the squat variation. "
                "Do not force painful depth."
            ),
            "time_s": _round(bottom_t),
        })

    if lean_review:

        valid_lean_samples = [
            (t, f["torso_lean"])
            for t, f in samples
            if f.get("torso_lean") is not None
        ]

        lean_t = max(
            valid_lean_samples,
            key=lambda item: item[1]
        )[0]

        findings.append({
            "code": "torso",
            "title": "Large apparent torso inclination",
            "detail": (
                "The upper-range torso inclination "
                "exceeds the provisional 48-degree "
                "screening threshold."
            ),
            "correction": (
                "Review bracing, stance, bar position "
                "and camera alignment with a coach. "
                "Forward torso lean alone does not "
                "prove incorrect lifting technique."
            ),
            "time_s": _round(lean_t),
        })

    score = sum(
        check["points_awarded"]
        for check in checks
    )

    return {
        "rep": number,

        "start_s": _round(start_t),
        "bottom_s": _round(bottom_t),
        "end_s": _round(end_t),

        "duration_s": _round(end_t - start_t),

        "min_knee_angle_deg": round(min_knee, 1),

        "max_torso_inclination_deg": (
            round(max_lean, 1)
            if max_lean is not None else None
        ),

        "sustained_torso_inclination_deg": (
            round(sustained_lean, 1)
            if sustained_lean is not None else None
        ),

        "hip_minus_knee_normalized": round(
            hip_minus_knee, 3
        ),

        "depth_review": depth_review,
        "torso_review": lean_review,

        "technique_score": score,
        "checks": checks,
        "findings": findings,

        "assessment": (
            "Review suggested"
            if findings
            else "No screened issue detected"
        ),
    }


# =====================================================
# WEIGHTLIFTING - COMPLETE VIDEO ANALYSIS
# =====================================================

def squat(frames):
    """
    Detect squat repetitions from knee-angle transitions.

    Down threshold: knee angle < 115 degrees
    Up threshold: knee angle > 155 degrees
    """

    valid = [
        (t, f)
        for t, f in frames
        if (
            f
            and f.get("knee_angle") is not None
            and f.get("torso_lean") is not None
            and f.get("hip_y") is not None
            and f.get("knee_y") is not None
        )
    ]

    if len(valid) < 5:
        return empty("squat")

    phase = "up"
    active = []
    events = []
    last_upright = None

    for t, f in valid:

        knee = f["knee_angle"]

        if phase == "up" and knee < 115:

            phase = "down"

            active = (
                [last_upright]
                if last_upright else []
            )

            active.append((t, f))

        elif phase == "down":

            active.append((t, f))

            if knee > 155:

                if (
                    len(active) >= 3
                    and t - active[0][0] >= 0.25
                ):
                    events.append(
                        _rep_review(
                            len(events) + 1,
                            active
                        )
                    )

                phase = "up"
                active = []

        if phase == "up" and knee >= 155:
            last_upright = (t, f)

    issues = []

    shallow = sum(
        bool(e["depth_review"])
        for e in events
    )

    leaned = sum(
        bool(e["torso_review"])
        for e in events
    )

    if shallow:
        issues.append({
            "severity": "review",
            "title": "Depth may be limited",
            "detail": (
                f"{shallow} of {len(events)} completed "
                "repetitions showed apparent "
                "hip-above-knee geometry."
            ),
            "tip": (
                "Record from a fixed side-view camera "
                "and review squat depth with a coach."
            ),
        })

    if leaned:
        issues.append({
            "severity": "review",
            "title": "Torso inclination deserves review",
            "detail": (
                f"{leaned} of {len(events)} repetitions "
                "exceeded the provisional sustained "
                "48-degree torso screen."
            ),
            "tip": (
                "Review stance, balance, camera position "
                "and bracing. Forward lean is not "
                "automatically incorrect."
            ),
        })

    if not events:
        issues.append({
            "severity": "info",
            "title": "No complete repetitions confirmed",
            "detail": (
                "No complete down-up squat cycle "
                "crossed both knee-angle thresholds."
            ),
            "tip": (
                "Include standing positions before "
                "and after each repetition."
            ),
        })

    scores = [
        e["technique_score"]
        for e in events
    ]

    metrics = {
        "average_knee_angle_deg": round(
            statistics.mean(
                f["knee_angle"]
                for _, f in valid
            ),
            1
        ),

        "min_knee_angle_deg": round(
            min(
                f["knee_angle"]
                for _, f in valid
            ),
            1
        ),

        "average_torso_inclination_deg": round(
            statistics.mean(
                f["torso_lean"]
                for _, f in valid
            ),
            1
        ),

        "frames_with_pose": len(valid),

        "average_technique_score": (
            round(statistics.mean(scores), 1)
            if scores else None
        ),
    }

    has_review = any(
        issue["severity"] == "review"
        for issue in issues
    )

    assessment = (
        "Insufficient evidence"
        if not events
        else "Review suggested"
        if has_review
        else "No screened issue detected"
    )

    return {
        "sport": "squat",
        "reps": len(events),

        "metrics": metrics,

        "events": events,
        "rep_details": events,

        "issues": issues,

        "score_method": {
            "name": (
                "Experimental visual screening score"
            ),
            "criteria": (
                "Each completed repetition starts at 100. "
                "50 points relate to apparent depth, "
                "30 to the 85th-percentile torso angle, "
                "and 20 to the observed completed cycle. "
                "These criteria have not been validated."
            ),
            "camera": (
                "Designed for stable side-view footage."
            ),
        },

        "assessment": assessment,

        "limitations": [
            "Repetition timestamps are approximate.",
            "2D depth depends on camera perspective.",
            "The score is not a validated technique grade.",
            "Spinal alignment and injury risk are not verified.",
        ],
    }


# =====================================================
# RUNNING - COMPLETE MOVEMENT ANALYSIS
# =====================================================

def running(frames, width, height):
    """
    Analyze running movement using MediaPipe landmarks.

    Measures:
    - Left and right knee movement
    - Torso angle
    - Torso variability
    - Approximate ankle crossing events
    - Landmark visibility
    """

    valid = [
        (t, f, raw)
        for t, f, raw in frames
        if f and raw
    ]

    if len(valid) < 12:
        return empty("running")

    left = []
    right = []
    torso = []
    ankles = []

    # Extract measurements for each sampled frame.
    for t, f, raw in valid:

        left_angle = _joint_angle(
            raw, 23, 25, 27, width, height
        )

        right_angle = _joint_angle(
            raw, 24, 26, 28, width, height
        )

        if left_angle is not None:
            left.append((t, left_angle))

        if right_angle is not None:
            right.append((t, right_angle))

        if f.get("torso_lean") is not None:
            torso.append(
                (t, f["torso_lean"])
            )

        if len(raw) > 28 and all(
            raw[i].get("visibility", 0) >= 0.6
            for i in (27, 28)
        ):
            separation = (
                raw[27]["x"] - raw[28]["x"]
            ) * width

            ankles.append(
                (t, separation)
            )

    duration = (
        valid[-1][0] - valid[0][0]
    )

    left_values = [
        value for _, value in left
    ]

    right_values = [
        value for _, value in right
    ]

    torso_values = [
        value for _, value in torso
    ]

    quality_left = (
        len(left) / len(valid)
    )

    quality_right = (
        len(right) / len(valid)
    )

    # Robust knee motion range (P95 - P5).
    left_range = (
        _percentile(left_values, 95)
        - _percentile(left_values, 5)
        if len(left_values) >= 12
        else None
    )

    right_range = (
        _percentile(right_values, 95)
        - _percentile(right_values, 5)
        if len(right_values) >= 12
        else None
    )

    average_lean = (
        statistics.mean(torso_values)
        if torso_values else None
    )

    maximum_lean = (
        max(torso_values)
        if torso_values else None
    )

    lean_variability = (
        statistics.pstdev(torso_values)
        if len(torso_values) >= 2
        else None
    )

    knee_values = [
        f["knee_angle"]
        for _, f, _ in valid
        if f.get("knee_angle") is not None
    ]

    issues = []
    events = []

    # Helper for observation messages.
    def add_finding(
        severity,
        code,
        title,
        detail,
        tip,
        timestamp=None
    ):
        finding = {
            "severity": severity,
            "code": code,
            "title": title,
            "detail": detail,
            "tip": tip,
        }

        if timestamp is not None:
            finding["time_s"] = round(
                timestamp, 2
            )

        issues.append(finding)

    # -------------------------------------------------
    # CHECK 1 - Video / landmark quality
    # -------------------------------------------------

    insufficient = (
        duration < 3
        or min(quality_left, quality_right) < 0.5
    )

    if insufficient:
        add_finding(
            "info",
            "limited_evidence",
            "Limited running-analysis evidence",
            (
                "The clip is too short or one leg "
                "is insufficiently visible."
            ),
            (
                "Use a stationary side-view camera "
                "with the full body visible for "
                "at least 5-10 seconds."
            ),
        )

    # -------------------------------------------------
    # CHECK 2 - Torso orientation
    # -------------------------------------------------

    if (
        average_lean is not None
        and average_lean > 30
    ):
        lean_time = max(
            torso,
            key=lambda item: item[1]
        )[0]

        add_finding(
            "review",
            "torso_angle",
            "Large observed torso inclination",
            (
                f"Mean apparent torso inclination "
                f"is {average_lean:.1f} degrees."
            ),
            (
                "Check camera orientation and review "
                "running posture with a coach. "
                "Forward lean is not necessarily incorrect."
            ),
            lean_time,
        )

    # -------------------------------------------------
    # CHECK 3 - Torso movement variation
    # -------------------------------------------------

    if (
        lean_variability is not None
        and lean_variability > 10
        and duration >= 3
    ):
        add_finding(
            "info",
            "torso_variation",
            "Variation in torso orientation",
            (
                f"Observed torso-angle standard deviation "
                f"is {lean_variability:.1f} degrees."
            ),
            (
                "Review camera movement and repeated "
                "torso motion in the annotated video."
            ),
        )

    # -------------------------------------------------
    # CHECK 4 - Left and right knee motion
    # -------------------------------------------------

    if (
        left_range is not None
        and right_range is not None
        and min(quality_left, quality_right) >= 0.7
        and duration >= 3
    ):

        difference = abs(
            left_range - right_range
        )

        if difference > 25:
            add_finding(
                "info",
                "knee_range_difference",
                "Different visible knee movement ranges",
                (
                    f"Left knee range: {left_range:.1f}°. "
                    f"Right knee range: {right_range:.1f}°."
                ),
                (
                    "Review complete running cycles. "
                    "Camera viewpoint and landmark occlusion "
                    "can cause apparent left/right differences."
                ),
            )

    # -------------------------------------------------
    # CHECK 5 - Approximate ankle crossing events
    # -------------------------------------------------

    last_cross = -10.0

    for (ta, xa), (tb, xb) in zip(
        ankles,
        ankles[1:]
    ):

        if (
            tb - ta <= 0.3
            and xa * xb < 0
            and abs(xa - xb) > width * 0.025
            and tb - last_cross >= 0.25
        ):
            events.append({
                "type": "ankle_crossing",
                "time_s": round(tb, 2),
                "description": (
                    "Approximate horizontal ankle crossing"
                ),
            })

            last_cross = tb

    ankle_duration = (
        ankles[-1][0] - ankles[0][0]
        if len(ankles) > 1
        else 0
    )

    crossing_proxy = (
        len(events) * 60 / ankle_duration
        if ankle_duration >= 3
        else None
    )

    if crossing_proxy is None:
        add_finding(
            "info",
            "ankle_visibility",
            "Ankle-crossing estimate unavailable",
            (
                "Insufficient continuous observations "
                "of both ankles."
            ),
            (
                "Record a clear side-view video "
                "with both feet visible."
            ),
        )

    # -------------------------------------------------
    # DESCRIPTIVE FEEDBACK
    # -------------------------------------------------

    # Provide useful measurement feedback
    # even when no review threshold is crossed.

    if average_lean is not None:
        detail = (
            f"Average torso inclination: "
            f"{average_lean:.1f} degrees."
        )

        if maximum_lean is not None:
            detail += (
                f" Maximum: {maximum_lean:.1f} degrees."
            )

        if lean_variability is not None:
            detail += (
                f" Variability: {lean_variability:.1f} degrees."
            )

        add_finding(
            "info",
            "torso_summary",
            "Observed torso movement",
            detail,
            (
                "Compare videos captured from "
                "the same camera position."
            ),
        )

    if (
        left_range is not None
        and right_range is not None
    ):
        add_finding(
            "info",
            "knee_summary",
            "Observed left/right knee movement",
            (
                f"Left knee movement range: "
                f"{left_range:.1f} degrees. "
                f"Right knee movement range: "
                f"{right_range:.1f} degrees."
            ),
            (
                "These measurements describe visible "
                "movement and do not independently "
                "establish a gait problem."
            ),
        )

    # -------------------------------------------------
    # FINAL METRICS
    # -------------------------------------------------

    metrics = {
        "average_knee_angle_deg": (
            round(statistics.mean(knee_values), 1)
            if knee_values else None
        ),

        "average_torso_inclination_deg": (
            round(average_lean, 1)
            if average_lean is not None else None
        ),

        "max_torso_inclination_deg": (
            round(maximum_lean, 1)
            if maximum_lean is not None else None
        ),

        "torso_variability_deg": (
            round(lean_variability, 1)
            if lean_variability is not None else None
        ),

        "left_knee_range_deg": (
            round(left_range, 1)
            if left_range is not None else None
        ),

        "right_knee_range_deg": (
            round(right_range, 1)
            if right_range is not None else None
        ),

        "left_knee_visibility_ratio": round(
            quality_left, 2
        ),

        "right_knee_visibility_ratio": round(
            quality_right, 2
        ),

        "ankle_crossings_per_min_proxy": (
            round(crossing_proxy, 1)
            if crossing_proxy is not None else None
        ),

        "frames_with_pose": len(valid),
    }

    has_review = any(
        issue["severity"] == "review"
        for issue in issues
    )

    assessment = (
        "Insufficient evidence"
        if insufficient
        else "Review suggested"
        if has_review
        else "No screened issue detected"
    )

    return {
        "sport": "running",
        "reps": None,

        "metrics": metrics,

        "events": events,
        "issues": issues,

        "assessment": assessment,

        "limitations": [
            "2D joint angles depend on camera viewpoint.",
            "Ankle crossings are not validated running cadence.",
            "Different knee-angle ranges do not prove a gait disorder.",
            "Speed, impact forces and injury risk are not measured.",
        ],
    }


# =====================================================
# INSUFFICIENT LANDMARK DATA
# =====================================================

def empty(sport):
    return {
        "sport": sport,

        "reps": (
            0 if sport == "squat"
            else None
        ),

        "metrics": {
            "frames_with_pose": 0
        },

        "events": [],

        "rep_details": (
            [] if sport == "squat"
            else None
        ),

        "issues": [
            {
                "severity": "review",
                "title": "Pose not detected",
                "detail": (
                    "Not enough reliable body landmarks "
                    "were available for analysis."
                ),
                "tip": (
                    "Record a brighter video with "
                    "the whole athlete visible."
                ),
            }
        ],

        "assessment": "Insufficient evidence",

        "limitations": [
            "No technique classification is possible "
            "without sufficient landmark data."
        ],
    }
