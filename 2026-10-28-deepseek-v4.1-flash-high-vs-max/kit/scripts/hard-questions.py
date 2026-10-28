import json, sys, time, uuid, urllib.request, winreg
from concurrent.futures import ThreadPoolExecutor
k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment'); KEY = winreg.QueryValueEx(k, 'OPENCODE_GO_API_KEY')[0]
Q = {
 'S1': ('How many positive integers n <= 10000 have the property that n and n+1 both have exactly 4 positive divisors? Think carefully, then give only the number.', '460'),
 'S2': ('How many permutations p of {1,...,8} satisfy both: p(i) != i for every i, and |p(i) - p(i+1)| != 1 for every i from 1 to 7? Give only the number.', '1695'),
 'S3': ('Find the sum of all primes p < 1000 such that p+2 and p+6 are also prime. Give only the number.', '5019'),
}
def ask(job):
    qid, eff = job; q, ans = Q[qid]
    body = json.dumps({'model': 'deepseek-v4.1-flash', 'reasoning_effort': eff, 'max_tokens': 64000, 'messages': [{'role': 'user', 'content': q}]}).encode()
    req = urllib.request.Request('https://opencode.ai/inference/go/openai/v1/chat/completions', body, {'authorization': 'Bearer ' + KEY, 'content-type': 'application/json', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) WindowsPowerShell/5.1', 'x-opencode-session': str(uuid.uuid4())})
    t = time.time()
    try:
        r = json.load(urllib.request.urlopen(req, timeout=1500))
        u = r['usage']; txt = (r['choices'][0]['message'].get('content') or '').strip()
        res = dict(q=qid, effort=eff, sec=round(time.time()-t), out=u.get('completion_tokens'), reasoning=(u.get('completion_tokens_details') or {}).get('reasoning_tokens'), answer=txt[-40:], correct=ans in txt.split()[-1:] or txt.strip().endswith(ans))
    except Exception as e:
        res = dict(q=qid, effort=eff, sec=round(time.time()-t), error=str(e)[:200])
    print(json.dumps(res), flush=True); return res
jobs = [(q, e) for q in Q for e in ('high', 'max')]
with ThreadPoolExecutor(6) as ex: list(ex.map(ask, jobs))
