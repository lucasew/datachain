import pytest
import json
import tempfile
import os
from datachain.database import Database

def test_int_validation():
    f_name = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            header = {
                "schema": {},
                "types": {},
                "ops": {
                    "set_age": {
                        "params": {
                            "val": {"int_min": 10, "int_max": 100, "default": 0}
                        },
                        "body": "var val"
                    }
                }
            }
            f.write(json.dumps(header) + "\n")

            # Valid age
            f.write(json.dumps({"transaction": ["set_age", {"val": 50}]}) + "\n")
            f_name = f.name

        # Valid input shouldn't crash
        db = Database(f_name)
    finally:
        if f_name and os.path.exists(f_name):
            os.remove(f_name)

def test_int_min_validation_failure():
    f_name = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            header = {
                "schema": {},
                "types": {},
                "ops": {
                    "set_age": {
                        "params": {
                            "val": {"int_min": 10, "int_max": 100, "default": 0}
                        },
                        "body": "var val"
                    }
                }
            }
            f.write(json.dumps(header) + "\n")

            # Invalid age (too low)
            f.write(json.dumps({"transaction": ["set_age", {"val": 5}]}) + "\n")
            f_name = f.name

        with pytest.raises(AssertionError):
            db = Database(f_name)
    finally:
        if f_name and os.path.exists(f_name):
            os.remove(f_name)

def test_int_max_validation_failure():
    f_name = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            header = {
                "schema": {},
                "types": {},
                "ops": {
                    "set_age": {
                        "params": {
                            "val": {"int_min": 10, "int_max": 100, "default": 0}
                        },
                        "body": "var val"
                    }
                }
            }
            f.write(json.dumps(header) + "\n")

            # Invalid age (too high)
            f.write(json.dumps({"transaction": ["set_age", {"val": 150}]}) + "\n")
            f_name = f.name

        with pytest.raises(AssertionError):
            db = Database(f_name)
    finally:
        if f_name and os.path.exists(f_name):
            os.remove(f_name)
