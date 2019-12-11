# python-registrable

[![CircleCI](https://circleci.com/gh/epwalsh/python-registrable.svg?style=svg)](https://circleci.com/gh/epwalsh/python-registrable)
[![License](https://img.shields.io/github/license/epwalsh/python-registrable)](https://github.com/epwalsh/python-registrable/blob/master/LICENSE)
[![PyPI version](https://badge.fury.io/py/registrable.svg)](https://pypi.org/project/registrable/)
[![Documentation Status](https://readthedocs.org/projects/python-registrable/badge/?version=latest)](https://python-registrable.readthedocs.io/en/latest/?badge=latest)

Python module that provides a `Registrable` base class. Based on the implementation from [AllenNLP](https://github.com/allenai/allennlp).

This is useful in scenarios where each particular subclass implementation of some base class has a natural association with a unique string, or where you'd prefer to create such an association, like when you need to specify which subclasses to use in a human-readable configuration file.

## Installing

The quickest way to install is through PyPI.

```
pip install registrable
```

## Usage

The basic way to use `registrable` is to create a `Registrable` base class and then
"register" subclass implementations under sensible names:

```python
>>> from registrable import Registrable
>>> class MyBaseClass(Registrable):
...    def do_something(self):
...        raise NotImplementedError

```

To register subclass implementations of your base class:

```python
>>> @MyBaseClass.register("first_implementation")
... class SubclassA(MyBaseClass):
...     def do_something(self):
...         return 1

```

Then access an implementation by calling `.by_name()` on the base class:

```python
>>> subclass = MyBaseClass.by_name("first_implementation")
>>> instance = subclass()
>>> instance.do_something()
1

```

You can easily check if a given name is registered:

```python
>>> MyBaseClass.is_registered("first_implementation")
True
>>> MyBaseClass.is_registered("anything else?")
False

```

And you can list all registered names or iterate through tuples of registered names and their corresponding subclasses:

```python
>>> MyBaseClass.list_available()
['first_implementation']
>>> list(MyBaseClass.iter_registered())
[('first_implementation', <class '__main__.SubclassA'>)]

```
