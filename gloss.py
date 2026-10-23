#!/usr/bin/env python3
"""Build books/<book>.gloss.json from books/gloss/<book>/NN.txt (one file per chapter, NN = chapter number from 01).

Line format (one word or expression per line, # starts a comment):
  forms|lemma|pos|ru|level|mark|note
  forms - as written in the chapter, lowercase; alternatives separated by "/"
  lemma - dictionary form if it differs from the first form
  pos   - n, v, adj, adv, prep, pv (phrasal verb), id (idiom), ph (phrase)
  mark  - "+" worth learning, "-" can be skipped (archaic, rare, nautical); add "*" when
          the meaning holds only in this chapter, so other chapters do not reuse it
Usage: python3 gloss.py mysterious-island
"""
import glob, json, os, re, sys

book = sys.argv[1]
B = json.load(open(f'books/{book}.json', encoding='utf-8'))


def text_of(ch):
    return ' '.join(x if isinstance(x, str) else x['h'] for x in ch['b']).replace('’', "'").lower()


out, problems = {}, []
for path in sorted(glob.glob(f'books/gloss/{book}/*.txt')):
    ci = int(os.path.basename(path).split('.')[0]) - 1
    t = text_of(B['chapters'][ci])
    rows = []
    for ln, line in enumerate(open(path, encoding='utf-8'), 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        f = (line.split('|') + [''] * 7)[:7]
        forms = [x.strip().lower().replace('’', "'") for x in f[0].split('/') if x.strip()]
        if not forms or not f[3].strip():
            problems.append(f'{path}:{ln} empty')
            continue
        for fm in forms:
            if not re.search(r'(?<![a-z])' + re.escape(fm) + r'(?![a-z])', t):
                problems.append(f'{path}:{ln} not in text: {fm}')
        rows.append(['/'.join(forms)] + [x.strip() for x in f[1:]])
    out[str(ci)] = rows
json.dump({'v': 1, 'ch': out}, open(f'books/{book}.gloss.json', 'w', encoding='utf-8'),
          ensure_ascii=False, separators=(',', ':'))
print(sum(len(v) for v in out.values()), 'entries in', len(out), 'chapters')
print('\n'.join(problems) or 'all forms found in the text')
