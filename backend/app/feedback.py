import os,json

def feedback(report):
    """API receives ONLY pose-derived structured features, not identifiable video images."""
    key=os.getenv('OPENAI_API_KEY','').strip()
    if not key:return {'source':'local rules','text':'Review the observations and suggestions below. Record with a fixed side-view camera. These are screening indicators rather than a definitive technique or safety assessment.'}
    try:
        from openai import OpenAI
        client=OpenAI(api_key=key,timeout=25,max_retries=1)
        safe={k:report[k] for k in ('sport','metrics','issues','limitations')}
        resp=client.responses.create(model=os.getenv('OPENAI_MODEL','gpt-4.1-mini'),
            instructions='You are a cautious sports coaching assistant. Use only supplied measurements. Do not invent observed faults, medical diagnoses, injury risk, certainty or unseen movements. Keep under 150 words. Explain 1-3 practical technique checks and limitations.',
            input=json.dumps(safe),store=False)
        return {'source':'openai','text':resp.output_text}
    except Exception as e:
        return {'source':'local rules (API unavailable)','text':'AI explanation unavailable; see the rule-based findings.', 'warning':str(e)[:160]}
