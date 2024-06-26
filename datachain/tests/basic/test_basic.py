#!/usr/bin/env python3

import tempfile
import json
from pathlib import Path
import sys

from datachain import Database, Evaluator

this_dir = Path(__file__).parent

def test_basic_chain():
    tmpd = Path(tempfile.mkdtemp())
    tmpd.mkdir(parents=True, exist_ok=True)
    if __name__ == '__main__':
        print(tmpd, file=sys.stderr)
    concatenated_file = tmpd / "concatenated.json"
    with concatenated_file.open('w') as f:
        j = json.loads((this_dir / "example.header.json").read_text())
        print(json.dumps(j), file=f)
        print((this_dir / "example.body.json").read_text(), file=f)

    handle_test_with_concatenated_file(concatenated_file)

def test_signed_chain():
    tmpd = Path(tempfile.mkdtemp())
    tmpd.mkdir(parents=True, exist_ok=True)
    if __name__ == '__main__':
        print(tmpd, file=sys.stderr)
    signed_concatenated_file = tmpd / "signed_concatenated.json"
    with signed_concatenated_file.open('w') as out:
        from datachain.crypto import Signer
        signer = Signer()
        
        header = json.loads((this_dir / "example.header.json").read_text())
        header['allowed_keys'] = [ str(signer.verifier) ]

        print(json.dumps(header), file=out)

        with (this_dir / "example.body.json").open('r') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    if '_sign' not in data:
                        data = signer.sign(data)
                    print(json.dumps(data), file=out)
                except json.JSONDecodeError:
                    print(line, file=out)
    handle_test_with_concatenated_file(signed_concatenated_file, is_the_signed_test=True)
    

def handle_test_with_concatenated_file(concatenated_file, is_the_signed_test=False):

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

    print(db.sql('select * from idx'), file=sys.stderr)
    if is_the_signed_test:
        assert db.sql('select value from idx where name = ?', "aaa") == 2
    else:
        assert db.sql('select value from idx where name = ?', "aaa") == 3
    assert db.sql('select value from idx where name = ?', "test") == 4

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
