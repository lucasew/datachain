#!/usr/bin/env python3

import tempfile
import json
from pathlib import Path

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
        json.dump(j, f)
        f.write("\n")
        f.write((this_dir / "example.body.json").read_text())

    db = Database(concatenated_file)
    print(db._header)

if __name__ == '__main__':
    test_basic()
