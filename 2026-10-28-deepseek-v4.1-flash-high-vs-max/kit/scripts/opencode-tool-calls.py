# Usage: py -3 opencode-tool-calls.py <session-jsonl> [text]
# The original runner wrote the file as UTF-16 through a PowerShell redirect.
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
text = open(sys.argv[1], 'rb').read().decode('utf-16')
for l in text.splitlines():
    try: r = json.loads(l)
    except Exception: continue
    p = r.get('part', {})
    if p.get('type') == 'tool':
        st = p.get('state', {}); out = str(st.get('output', ''))
        flag = ' <ERR ' + str(out.count('error[')) + '>' if 'error[' in out else ''
        print(p.get('tool'), json.dumps(st.get('input', {}), ensure_ascii=False)[:150], flag)
    elif p.get('type') == 'text' and len(sys.argv) > 2:
        print('TEXT:', p.get('text', '')[:1500])
