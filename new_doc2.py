import json
from components.vocab import Vocab, VocabEntry
from datasets.conala.util import tokenize_intent

import subprocess
import pickle

data = pickle.load(open('data/conala_new/test-types_for_mypy.bin', 'rb'))

filtered_data = []

intro = """
from typing import *

"""

all_exs = []
myf = open("complete_local_vars.py", "r")
lines = myf.readlines()[:317]
crt_line_idx = 2

for i, e in enumerate(data):
    if crt_line_idx >= len(lines) or not lines[crt_line_idx][0] == '#':
        break
    assert lines[crt_line_idx+1][0] == '#'
    ok = True

    last_line_idx = crt_line_idx + 2
    while lines[last_line_idx][0] != '#':
        if 'DELETED' in lines[last_line_idx]:
            ok = False
        last_line_idx += 1
        if last_line_idx >= len(lines):
            ok = False
            break

    if ok:
        added_lines = lines[crt_line_idx:last_line_idx]
        e.local_vars = '\n'.join(added_lines)
        filtered_data.append(e)

        f = open("my_py_tst.py", "w")
        f.write(intro + e.local_vars + e.tgt_code)
        f.close()
        output = subprocess.check_output(['mypy', '--py2', 'my_py_tst.py'])
        assert output[:7] == b'Success'

    crt_line_idx = last_line_idx

pickle.dump(filtered_data, open('data/conala_new/filtered_test.bin', 'wb'))
print('done')
# json.dump(filtered_data, open('data/conala_new/test-types_for_mypy.json', 'w'))

