"""Opt-in Windows test fix for PySpark's zipped JSON-resource path lookup.

Load the already-installed, unpacked package. No library or Spark engine is mocked.
"""
import os
import sys

unpacked = os.environ.get('SPARK_PYTHON_UNPACKED')
if unpacked:
    sys.path.insert(0, unpacked)
