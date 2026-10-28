# Prompts were sent in Turkish in the original run; translated here.
import json, sys, time, uuid, urllib.request, winreg, os
from concurrent.futures import ThreadPoolExecutor
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'planted-errors')
k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment'); KEY = winreg.QueryValueEx(k, 'OPENCODE_GO_API_KEY')[0]
code = open(os.path.join(D, 'code_round1.py'), encoding='utf-8').read(); facts = open(os.path.join(D, 'facts_round1.md'), encoding='utf-8').read()
P = {
 'CODE': 'Review this Python module for bugs. For each function, say either OK or BUG. For each BUG give the function name, the concrete failing input, and the fix. Do not report style issues.\n\n```python\n' + code + '```',
 'FACTS': 'Which of the numbered statements below are factually WRONG? For each wrong statement, write its number and the correct version. Do not list the correct ones.\n\n' + facts,
}
def ask(job):
    pid, eff, rep = job
    body = json.dumps({'model': 'deepseek-v4.1-flash', 'reasoning_effort': eff, 'max_tokens': 64000, 'messages': [{'role': 'user', 'content': P[pid]}]}).encode()
    req = urllib.request.Request('https://opencode.ai/inference/go/openai/v1/chat/completions', body, {'authorization': 'Bearer ' + KEY, 'content-type': 'application/json', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) WindowsPowerShell/5.1', 'x-opencode-session': str(uuid.uuid4())})
    t = time.time()
    try:
        r = json.load(urllib.request.urlopen(req, timeout=1500)); u = r['usage']
        res = dict(p=pid, effort=eff, rep=rep, sec=round(time.time()-t), out=u.get('completion_tokens'), reasoning=(u.get('completion_tokens_details') or {}).get('reasoning_tokens'), text=r['choices'][0]['message'].get('content'))
    except Exception as e:
        res = dict(p=pid, effort=eff, rep=rep, sec=round(time.time()-t), error=str(e)[:300])
    print(json.dumps(res, ensure_ascii=False), flush=True)
jobs = [(p, e, r) for p in P for e in ('high', 'max') for r in (1, 2)]
with ThreadPoolExecutor(8) as ex: list(ex.map(ask, jobs))
