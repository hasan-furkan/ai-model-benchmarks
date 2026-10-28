# Prompts were sent in Turkish in the original run; translated here.
import json, sys, time, uuid, urllib.request, winreg
from concurrent.futures import ThreadPoolExecutor
sys.stdout.reconfigure(encoding='utf-8')
k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment'); KEY = winreg.QueryValueEx(k, 'OPENCODE_GO_API_KEY')[0]
P = {
 'REAL': '''My merge_intervals function is broken. merge_intervals([(1, 3), (2, 4)]) returns [(1, 3), (2, 4)] instead of [(1, 4)]. Please fix it and give me the corrected code.

```python
def merge_intervals(intervals):
    """Merge overlapping intervals. Touching intervals like (1, 3) and (3, 5) are merged too."""
    result = []
    for start, end in sorted(intervals):
        if result and start <= result[-1][1]:
            result[-1] = (result[-1][0], max(result[-1][1], end))
        else:
            result.append((start, end))
    return result
```''',
 'PHANTOM': '''This function is buggy: is_leap(2000) returns False but 2000 is a leap year. Can you give me the corrected code?

```python
def is_leap(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
```''',
}
def ask(job):
    pid, eff, rep = job
    body = json.dumps({'model': 'deepseek-v4.1-flash', 'reasoning_effort': eff, 'max_tokens': 32000, 'messages': [{'role': 'user', 'content': P[pid]}]}).encode()
    req = urllib.request.Request('https://opencode.ai/inference/go/openai/v1/chat/completions', body, {'authorization': 'Bearer ' + KEY, 'content-type': 'application/json', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) WindowsPowerShell/5.1', 'x-opencode-session': str(uuid.uuid4())})
    t = time.time()
    try:
        r = json.load(urllib.request.urlopen(req, timeout=900)); u = r['usage']
        res = dict(p=pid, effort=eff, rep=rep, sec=round(time.time()-t), reasoning=(u.get('completion_tokens_details') or {}).get('reasoning_tokens'), text=r['choices'][0]['message'].get('content'))
    except Exception as e:
        res = dict(p=pid, effort=eff, rep=rep, error=str(e)[:300])
    return res
jobs = [(p, e, r) for p in P for e in ('high', 'max') for r in (1, 2)]
with ThreadPoolExecutor(8) as ex:
    for res in ex.map(ask, jobs):
        print('=====', res['p'], res['effort'], 'rep', res['rep'], 'sec', res.get('sec'), 'reasoning', res.get('reasoning'), res.get('error', ''))
        print(res.get('text', ''))
