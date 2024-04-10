PYPROJECT_TEXT = '''[project]
name = ""
version = "0.0.0"
authors = [
  { name="", email="" },
]
description = ""
readme = "README.md"
requires-python = ">=3.11"
classifiers = [
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
]

[project.urls]
Homepage = ""
Issues = ""
'''

MAIN__TEXT = '''if __name__ == '__main__':
    print('Hello world!')
'''

PYPIRC = '''[distutils]
index-servers =
  pypi

[pypi]
username = __token__
password = 
'''


__all__ = (
    'PYPROJECT_TEXT',
    'MAIN__TEXT',
    'PYPIRC',
)
