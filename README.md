# datachain

PoC of a small-data database that is based on text files that uses a JSON-based Lisp to setup stuff 

## Design

The database text file is a file that each line is an indepentent JSON object. The first line
is the database schema and the rest of the lines are data transactions.

This database text file is materialized into a in-memory SQLite database that can be queried at will.
