# Usage: py -3 opencode-session-stats.py <session-id> [session-id ...]
# The database path can be overridden with the OPENCODE_DB environment variable;
# by default it is the OpenCode data directory of the current user.
import os, sqlite3, sys

db_path = os.environ.get('OPENCODE_DB') or os.path.join(
    os.environ.get('USERPROFILE') or os.path.expanduser('~'),
    '.local', 'share', 'opencode', 'opencode.db')
c = sqlite3.connect('file:' + db_path.replace('\\', '/') + '?mode=ro', uri=True)
for sid in sys.argv[1:]:
    r = c.execute("select title, cost, tokens_input, tokens_output, tokens_reasoning, tokens_cache_read, (time_updated-time_created)/1000 from session_v2 where id=?", (sid,)).fetchone()
    print(sid, r)
