import pytest

from registrable.exceptions import RegistrationError
from example_module.foo_class import Foo


def test_registered_on_import():
    import example_module.foo_subclasses

    assert Foo.list_available() == ["foo_a"]


def test_by_fully_qualified_name():
    assert not Foo.is_registered(
        "example_module.unregistered_foo_subclasses.FooUnregistered"
    )
    subclass = Foo.by_name("example_module.unregistered_foo_subclasses.FooUnregistered")
    assert Foo.is_registered(
        "example_module.unregistered_foo_subclasses.FooUnregistered"
    )
    assert issubclass(subclass, Foo)
    assert subclass().do_something() == "Am I registered?"


def test_by_fully_qualified_name_fail_not_a_module():
    with pytest.raises(RegistrationError) as excinfo:
        Foo.by_name("example_module.not_a_module.foo")
    assert str(excinfo.value) == (
        "tried to interpret example_module.not_a_module.foo as a path to a class "
        "but unable to import module example_module.not_a_module"
    )


def test_by_fully_qualified_name_fail_class_not_exist():
    with pytest.raises(RegistrationError) as excinfo:
        Foo.by_name("example_module.unregistered_foo_subclasses.NotASubclass")
    assert str(excinfo.value) == (
        "tried to interpret example_module.unregistered_foo_subclasses.NotASubclass "
        "as a path to a class but unable to find class "
        "NotASubclass in example_module.unregistered_foo_subclasses"
    )


def test_by_fully_qualified_name_fail_not_a_subclass():
    with pytest.raises(RegistrationError) as excinfo:
        Foo.by_name("example_module.bar_class.Bar")
    assert str(excinfo.value) == (
        "tried to interpret example_module.bar_class.Bar as a path to a class "
        "but Bar is not a subclass of Foo"
    )
