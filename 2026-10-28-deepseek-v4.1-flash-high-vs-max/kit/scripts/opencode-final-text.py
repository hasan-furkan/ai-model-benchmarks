# Usage: py -3 opencode-final-text.py <session-jsonl> <output.txt>
# Writes the last two text parts of the session; the file was written as UTF-16.
import json, sys
text = open(sys.argv[1], 'rb').read().decode('utf-16')
parts = []
for l in text.splitlines():
    try: r = json.loads(l)
    except Exception: continue
    p = r.get('part', {})
    if p.get('type') == 'text': parts.append(p.get('text', ''))
open(sys.argv[2], 'w', encoding='utf-8').write('\n\n-----\n\n'.join(parts[-2:]))
