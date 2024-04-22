#!/usr/bin/env python3

import tempfile
import json
from pathlib import Path
import sys

from datachain import Database, Evaluator

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

    db.sql("create table teste (eoq, trabson)")
    assert db.sql("select name from sqlite_schema where name like '%teste%'") == 'teste'
    assert db.sql('select ?', 2) == 2

def test_evaluator_basic():
    e = Evaluator(dict(
        a=2,
        b=2
    ))
    print(e.env.keys())
    print(e.env.get('var'))
    print('eval', e.eval(['+', ['var', 'a'], ['var', 'b']]), file=sys.stderr)
    assert e.eval(['+', ['var', 'a'], ['var', 'b']]) == 4
    
def test_evaluator_lazy():
    class CallTrigger():
        def __init__(self):
            self.called = False
        def reset(self):
            self.called = False
        def trigger(self):
            self.called = True
        def trigger_from_eval(self, env):
            self.trigger()

    trigger = CallTrigger()
    assert not trigger.called
    trigger.trigger()
    assert trigger.called
    trigger.reset()
    assert not trigger.called

    e = Evaluator(dict(
        cond=True,
        trigger_call=trigger.trigger_from_eval
    ))
    e.eval(['if', ['var', 'cond'], 2, ['trigger_call']])
    assert not trigger.called

if __name__ == '__main__':
    test_basic()
    test_evaluator_basic()
    test_evaluator_lazy()
