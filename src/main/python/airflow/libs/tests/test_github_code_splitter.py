import unittest
from ..splitter import PythonCodeSplitter



class TestGithubCodeSplitter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sample_python_file = '/Users/alexanderfournier/Downloads/Agent-Neo-field/src/main/python/airflow/libs/fetcher/gcp_fetcher.py'

        with open(sample_python_file, 'r') as f:
            python_string = f.readlines()

        cls.python_string = python_string




    def test_splitting_code(self):

        code_splitter = PythonCodeSplitter(code=self.python_string)

        code_splitter.split_code()










if __name__ == '__main__':
    unittest.main()
