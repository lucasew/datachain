import sqlite3
from pathlib import Path
import json
import sys

from .evaluator import evaluator_item, Evaluator, _eval, truep

class Database():
    def __init__(self, chainfile):
        self.chainfile = Path(chainfile)
        self.db = sqlite3.connect(':memory:') # TODO: persistence cache
        assert self.chainfile.exists()
        self.evaluator = self._setup()
        self.sql(self._sql_schema)

        with self.chainfile.open('r') as f:
            next(f) # skip header
            for body_item in f:
                result = self._handle_body_item(body_item)
                print('result', result, file=sys.stderr)

    def _verify_signature(self, data):
        if len(self.verifiers) == 0:
            return True
        for verifier in self.verifiers:
            if verifier.is_valid(data):
                return True
        return False
        
    def _handle_body_item(self, item):
        print('body_item', item, file=sys.stderr)
        if isinstance(item, str):
            item = item.strip()
            if item == '':
                return
            item = json.loads(item)
        if not self._verify_signature(item):
            return None
        return self.evaluator.eval(item['transaction'], env=item)

    @property
    def _sql_schema(self):
        sql = ""
        for table_name, table in self._header['schema'].items():
            sql += f'create table {table_name} ('
            column_stmts = []
            for column_name, column in table['columns'].items():
                column_stmt = ""
                column_stmt += f'{column_name} '
                column_stmt += f'{column["type"]} '
                if 'default' in column:
                    default = column['default']
                    if isinstance(default, str):
                        column_stmt += f"default '{default}' "
                    else:
                        column_stmt += f"default {default} "
                if column.get('unique'):
                    column_stmt += ' unique'
                column_stmts.append(column_stmt)
            sql += ",".join(column_stmts)
            sql += ');'
        return sql
                
    @property
    def db_id(self):
        from hashlib import sha256
        hasher = sha256()
        header_sorted = json.dumps(self._header, sort_keys=True)
        hasher.update(header_sorted.encode('utf-8'))
        return hasher.hexdigest()

    def _get_checker(self, param):
        if param.get('int_min'):
            assert isinstance(param['int_min'], int)
        if param.get('int_max'):
            assert isinstance(param['int_max'], int)

        def checker(env, item):
            if param.get('int_min'):
                assert isinstance(item, int)
                assert item >= param['int_min']
            if param.get('int_max'):
                assert isinstance(item, int)
                assert item >= param['int_min']
            if 'validation_type' in param:
                assert _eval({**env, 'item': item}, ['truep', [f'validate_{param["validation_type"]}', ['var', 'item']]])
            if 'check' in param:
                assert item is not None
                assert _eval({**env, 'item': item}, ['truep', param['check']])
            return True
        return checker

    def _setup(self):
        header = self._header
        self.verifiers = []
        if 'allowed_keys' in header:
            from datachain.crypto import Verifier
            print('allowed_keys', header['allowed_keys'], file=sys.stderr)
            self.verifiers = [Verifier(v) for v in header['allowed_keys']]

        base_env = dict(
            db=self
        )

        for type_name, type in header['types'].items():
            base_env[f'validate_{type_name}'] = self._get_checker(type)

        for op_name, op in header['ops'].items():
            def op_payload(env):
                handled_args = dict()
                for param_name, param in op['params'].items():
                    item = env.get(param_name, param['default'])
                    print('param', param_name, item, file=sys.stderr)
                    checker = self._get_checker(param)
                    assert checker(env, item)
                    handled_args[param_name] = item
                env = {**env, **handled_args}
                return env['eval'](env, op['body'])
            register = evaluator_item(name=op_name, register=False)

            base_env[op_name] = register(op_payload)
        return Evaluator(base_env)
       

    @property
    def _header(self):
        with self.chainfile.open('r') as f:
            return json.loads(next(f))

    def sql(self, query, *args):
        print('sql', query, args, file=sys.stderr)
        cursor = self.db.cursor()
        result = cursor.execute(query, args)
        items = result.fetchall()
        if len(items) > 0 and len(items[0]) == 1:
            items = [v[0] for v in items]
        if len(items) == 1:
            return items[0]
        if len(items) == 0:
            return None
        return items
        
@evaluator_item(name='sql')
def _sql(env, query, *args):
    return env['db'].sql(query, *args)
