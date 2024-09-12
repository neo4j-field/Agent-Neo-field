# tests/runner.py
import os
import unittest

mods = [x[:-3] for x in os.listdir("tests/") if x.startswith("test_")]
loader = unittest.TestLoader()
suite = unittest.TestSuite()

for mod in mods:
    suite.addTests(loader.loadTestsFromName(f"tests.{mod}"))

runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)
