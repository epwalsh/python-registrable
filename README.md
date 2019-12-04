# python-registrable

[![CircleCI](https://circleci.com/gh/epwalsh/python-registrable.svg?style=svg)](https://circleci.com/gh/epwalsh/python-registrable)
[![License](https://img.shields.io/github/license/epwalsh/python-registrable)](https://github.com/epwalsh/python-registrable/blob/master/LICENSE)
[![PyPI version](https://badge.fury.io/py/registrable.svg)](https://pypi.org/project/registrable/)
[![Documentation Status](https://readthedocs.org/projects/python-registrable/badge/?version=latest)](https://python-registrable.readthedocs.io/en/latest/?badge=latest)

Python module for registering and instantiating classes by name. Based on the implementation from [AllenNLP](https://github.com/allenai/allennlp).


## Installing

The quickest way to install is through PyPI.

```
pip install registrable
```

## Usage

```python
from registrable import Registrable

# Create a base class that inherits from `Registrable`.
class MyBaseClass(Registrable):
    def do_something(self):
        raise NotImplementedError


# Now register subclass implementations of your base class.
@MyBaseClass.register("first_implementation")
class FirstImplementation(MyBaseClass):
    def do_something(self):
        return 1


# You can access an implementation by calling `.by_name()` on the base class.
subclass = MyBaseClass.by_name("first_implementation")
instance = subclass()
assert instance.do_something() == 1
```
