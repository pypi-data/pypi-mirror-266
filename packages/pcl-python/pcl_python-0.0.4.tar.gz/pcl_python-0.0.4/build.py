from setuptools import setup
from setuptools.dist import Distribution

class BinaryDistribution(Distribution):
    def is_pure(self):
        return False

setup(
    name="pcl-python",
    version="0.3",
    distclass=BinaryDistribution,
)
