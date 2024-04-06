# DocGen-AI
DocGen-AI is a Python library that automatically generates docstrings for Python functions. It takes a Python file as input, generates docstrings for each function in the file, and outputs a new Python file with the generated docstrings.
# Features
 * Automatically generate docstrings for Python functions
 * Easy to use: just pass the file name to the DocGen instance and call the write_to_file() method
# Installation
You can install DocGen-AI by cloning the repository or using pip:
      git clone [<repository-url>](https://github.com/RijinRaju/DocGen-AI/)
      cd DocGen-AI/src
      pip install DocGen-AI


# Usage
Here’s a simple example of how to use DocGen-AI:
```python 
  from docgen_ai import DocGen
  
  doc_gen = DocGen('./test.py')
  doc_gen.write_to_file()
```
In this example, DocGen is instantiated with the path to a Python file ('./test.py'). The write_to_file() method is then called to generate docstrings for each function in the file and output a new Python file with the generated docstrings.

# License
DocGen-AI is licensed under the MIT License. See the LICENSE file for more information.
