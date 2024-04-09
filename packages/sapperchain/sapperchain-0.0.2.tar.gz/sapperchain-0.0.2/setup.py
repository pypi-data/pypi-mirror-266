import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="sapperchain",
  version="0.0.2",
  author="ChengYu && Yishun Wu",
  author_email="author@example.com",
  description="Programming for natural language",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/promptsapper/sapperchain",
  packages=setuptools.find_packages(),
  classifiers=[
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
  ],
)
