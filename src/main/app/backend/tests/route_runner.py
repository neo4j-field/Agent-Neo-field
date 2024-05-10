import unittest


mods = ["test_llm_route", "test_rating_route"]
# initialize the test suite
loader = unittest.TestLoader()
suite = unittest.TestSuite()

# add tests to the test suite
for mod in mods:
    suite.addTests(loader.loadTestsFromName(f"tests.{mod}"))

# initialize a runner, pass it your suite and run it
runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)