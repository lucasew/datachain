#!/usr/bin/env python3

import tempfile
import json
from pathlib import Path
import sys

from datachain import Database

this_dir = Path(__file__).parent

def test_basic():
    tmpd = Path(tempfile.mkdtemp())
    tmpd.mkdir(parents=True, exist_ok=True)
    if __name__ == '__main__':
        print(tmpd)
    concatenated_file = tmpd / "concatenated.json"
    with concatenated_file.open('w') as f:
        j = json.loads((this_dir / "example.header.json").read_text())
        print(json.dumps(j), file=f)
        print((this_dir / "example.body.json").read_text(), file=f)

    with concatenated_file.open('r') as f:
        for i, line in enumerate(f):
            line = line.strip()
            if line == '':
                continue
            try:
                json.loads(line)
            except Exception as e:
                print('while parsing line', i + 1, line, file=sys.stderr)
                raise e

    db = Database(concatenated_file)
    print(db._header, file=sys.stderr)
    print(db.db_id, file=sys.stderr)
    print(db.sql("create table teste (eoq, trabson)"))
    print(db.sql("select name from sqlite_schema"))

if __name__ == '__main__':
    test_basic()
