import td_pyspark
from pyspark.sql import SparkSession
import unittest

class TDPySparkShutdownTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        builder = SparkSession.builder.appName("td-pyspark-test")
        self.td = td_pyspark.TDSparkContextBuilder(builder).build()
        self.td.set_log_level("DEBUG")

    @classmethod
    def tearDownClass(self):
        self.td.spark.stop()

    def test_show(self):
        df = self.td.table("sample_datasets.www_access").df()
        df.show()

if __name__ == "__main__":
    unittest.main()
