#!/usr/bin/env python3
"""Push files to xizhina9/slova in one commit. Usage: GH_TOKEN=... python3 push.py "message" file1 [file2 ...]"""
import os, sys, json, base64, urllib.request, urllib.error
OWNER, REPO, BRANCH = 'xizhina9', 'slova', 'main'
T = os.environ['GH_TOKEN']
def api(path, method='GET', data=None):
    req = urllib.request.Request('https://api.github.com' + path, method=method,
        headers={'Authorization': 'Bearer ' + T, 'Accept': 'application/vnd.github+json',
                 'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'slova-bot'},
        data=json.dumps(data).encode() if data is not None else None)
    try:
        with urllib.request.urlopen(req) as r: return r.status, json.loads(r.read() or b'{}')
    except urllib.error.HTTPError as e: return e.code, json.loads(e.read() or b'{}')
def must(res, what):
    s, r = res
    if s >= 300: sys.exit(f'{what}: {s} {r.get("message")}')
    return r
msg, files = sys.argv[1], sys.argv[2:]
base = f'/repos/{OWNER}/{REPO}'
ref = must(api(f'{base}/git/ref/heads/{BRANCH}'), 'ref')
head = ref['object']['sha']
commit = must(api(f'{base}/git/commits/{head}'), 'commit')
tree_items = []
for f in files:
    raw = open(f, 'rb').read()
    blob = must(api(f'{base}/git/blobs', 'POST', {'content': base64.b64encode(raw).decode(), 'encoding': 'base64'}), f'blob {f}')
    tree_items.append({'path': os.path.basename(f), 'mode': '100644', 'type': 'blob', 'sha': blob['sha']})
tree = must(api(f'{base}/git/trees', 'POST', {'base_tree': commit['tree']['sha'], 'tree': tree_items}), 'tree')
new = must(api(f'{base}/git/commits', 'POST', {'message': msg, 'tree': tree['sha'], 'parents': [head]}), 'new commit')
must(api(f'{base}/git/refs/heads/{BRANCH}', 'PATCH', {'sha': new['sha']}), 'update ref')
print('pushed', new['sha'][:7], [t['path'] for t in tree_items])
