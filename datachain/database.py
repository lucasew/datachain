import sqlite3
from pathlib import Path

class Database():
    def __init__(self, chainfile):
        self.chainfile = Path(chainfile)
        assert self.chainfile.exists()

    @property
    def _header(self):
        with self.chainfile.open('r') as f:
            return next(f)
        
