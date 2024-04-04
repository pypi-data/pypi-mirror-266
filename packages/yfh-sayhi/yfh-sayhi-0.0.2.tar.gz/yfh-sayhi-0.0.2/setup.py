import setuptools
import say_hiaaaaaaa221
with open("README.md", "r",encoding='utf8') as fh:
  long_description = fh.read()

setuptools.setup(
  name="yfh-sayhi",
  version="0.0.2",
  author="Example Author",
  author_email="author@example.com",
  description="A small example package",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/pypa/sampleproject",
  packages=setuptools.find_packages(),
  classifiers=[
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
  ],
)