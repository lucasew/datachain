import sqlite3
from pathlib import Path
import json

class Database():
    def __init__(self, chainfile):
        self.chainfile = Path(chainfile)
        self.db = sqlite3.connect(':memory:') # TODO: persistence cache
        assert self.chainfile.exists()

    @property
    def db_id(self):
        from hashlib import sha256
        hasher = sha256()
        header_sorted = json.dumps(self._header, sort_keys=True)
        hasher.update(header_sorted.encode('utf-8'))
        return hasher.hexdigest()

    @property
    def _header(self):
        with self.chainfile.open('r') as f:
            return json.loads(next(f))

    def sql(self, query, *args):
        cursor = self.db.cursor()
        result = cursor.execute(query, args)
        items = result.fetchall()
        if len(items) > 0 and len(items[0]) == 1:
            items = [v[0] for v in items]
        if len(items) == 1:
            return items[0]
        return items
        
