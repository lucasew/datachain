import sqlite3
from pathlib import Path
import json
import sys

from .evaluator import evaluator_item, Evaluator, _eval, truep

class Database():
    """
    Materializes a JSON-line chainfile into an in-memory SQLite database.

    The chainfile serves as the source of truth, where the first line defines
    the header (schema, custom types, ops, and allowed signers), and subsequent
    lines represent individual data transactions. Transactions are validated
    cryptographically (if `allowed_keys` are configured) and evaluated using a
    custom JSON-based Lisp evaluator to mutate the SQLite state.
    """
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
        """
        Cryptographically verifies the authenticity of a transaction block.

        If the database header defines `allowed_keys`, every transaction must
        carry a valid `_sign` signature matching at least one of the known
        Ed25519 public keys. If no keys are configured, all transactions are
        accepted by default.
        """
        if len(self.verifiers) == 0:
            return True
        for verifier in self.verifiers:
            if verifier.is_valid(data):
                return True
        return False
        
    def _handle_body_item(self, item):
        """
        Processes a single transaction line from the chainfile.

        This includes parsing the JSON payload, verifying cryptographic
        signatures, and passing the transaction body into the Lisp evaluator
        to apply the operation to the SQLite state. Failing verification
        silently drops the transaction.
        """
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
        """
        Generates a validation function for a custom type parameter.

        The returned checker evaluates custom logic (like `int_min`,
        `int_max`, or arbitrary Lisp `check` expressions) against incoming
        data during operation dispatch. It acts as the gatekeeper for strongly
        typed transaction arguments.
        """
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
        """
        Bootstraps the evaluator environment based on the chainfile header.

        Extracts allowed public keys for transaction validation and registers
        custom user-defined types and operations as callable Lisp forms within
        the evaluator's namespace. This allows transactions to trigger domain-
        specific logic defined entirely in the schema.
        """
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
        """
        Executes a raw SQL query against the materialized in-memory SQLite database.

        Unwraps single-column results into a flat list, and single-row results
        into singular scalar values. This method is exposed to the evaluator as
        the primitive `sql` function, allowing transactions to modify state.
        """
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
