### **Step 1: Create a project directory**

The first step to creating a Python package is to create a new project directory. This will contain all the files and directories necessary for the package.

To create a new project directory, open a terminal or command prompt and run the following command:

```
mkdir mypackage
cd mypackage
```

Replace "mypackage" with the name of your package.

### **Step 2: Create a package directory**

The next step is to create a new directory inside the project directory to hold the package code. It should have the same name as your package.

To create a new package directory, run the following command:

```
mkdir mypackage
```

Replace "mypackage" with the name of your package.

### **Step 3: Create a module file**

Inside the package directory, create a new Python file to hold the package code. The file should have the same name as your package with a .py extension.

For example, if your package is named "mypackage", create a file named "mypackage.py".

In case of wrapping multiple modules with different names then create an “__**init__.py”** hosting all the modules which needs to be utilized

### **Step 4: Write the package code**

Write your package code in the module file you just created. It can include any Python code you want to have in the package, such as functions, classes, and variables.

### **Step 5: Create a setup.py file**

To publish your Python package to PyPI, you need to create a setup.py file. It contains metadata about your package like its name, version, author, and dependencies.

Create a new file named "setup.py" in the project directory and add the following code:

```
from setuptools import setup, find_packages
setup(
name='mypackage',
version='0.1.0',
author='Your Name',
author_email='your.email@example.com',
description='A short description of your package',
packages=find_packages(),
classifiers=[
'Programming Language :: Python :: 3',
'License :: OSI Approved :: MIT License',
'Operating System :: OS Independent',
],
python_requires='>=3.6',
)
```

### **Step 6: Build the package**

To build the package, run the following command in the project directory:

```
python setup.py sdist

python setup.py sdist bdist_wheel
```

This will create a source distribution of your package in a new directory named "dist".

### **Step 7: Upload the package to PyPI**

To upload your package to PyPI, you first need to create an account on the [PyPI](https://pypi.org/account/register/) / [TestPyPI · The Python Package Index](https://test.pypi.org/) website

Once done, run the following command in the project directory:

```
twine upload dist/*
```

This will upload your package to PyPI.

# **Step 8: PyPi .pypirc location on windows**

Your .pypirc file on windows should be in your `$HOME` directory.

On windows this is typically your user folder under `C:\Users\`. For example my current home folder for the user `hiro` is `C:\Users\hiro\`

This means that my `.pypirc` file should live at `C:\Users\hiro\.pypirc`.

If .pypirc file is not existing for the user then create it with the help of below template. on pypi/testpypi, generate your respective API token and use it as your password below.

# **Typical PyPi .pypirc file contents**

Typically the PyPi file will include information for the pypi and testpypi server. If you have a token for each of these your file will look something like this

Here the settings for pypi and testpypi

```python
[distutils]
index-servers =
    pypi
    testpypi
 
[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = <PyPI token>
 
[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = <PyPI token>
```

### **Step 9: Install the package**

To install your package from PyPI, run the following command:

```
pip install mypackage
```

Replace "mypackage" with the name of your package.