from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.1a'
DESCRIPTION = 'Personal repository for SoA Deep Learning building blocks (in PyTorch)'
LONG_DESCRIPTION = 'This package contains "all" the SoA NNs architecture building blocks (inheriting nn.Module) from PyTorch framework'

# Setting up
setup(name="DeepTorchBlocks",
      version=VERSION,
      author="Stefano Giacomelli (Ph.D. student UnivAQ)",
      author_email="<stefano.giacomelli@graduate.univaq.it>",
      description=DESCRIPTION,
      long_description_content_type="text/markdown",
      long_description=long_description,
      packages=find_packages(),
      install_requires=['numpy', 'torch'],
      keywords=['python', 'pytorch', 'deep_learning', 'neural_networks'],
      classifiers=["Development Status :: 1 - Planning",
                   "Intended Audience :: Developers",
                   "Programming Language :: Python :: 3",
                   "Operating System :: Unix",
                   "Operating System :: MacOS :: MacOS X",
                   "Operating System :: Microsoft :: Windows"]
      )
