import pytest

from registrable import Registrable, RegistrationError


@pytest.fixture(scope="module")
def BaseClass():
    class SomeRegistrableBaseClass(Registrable):
        def do_something(self) -> int:
            raise NotImplementedError

    @SomeRegistrableBaseClass.hook
    def add_registered_name_hook(subclass, name):
        subclass.registered_name = name

    return SomeRegistrableBaseClass


def test_list_available_none_available(BaseClass):
    assert BaseClass.list_available() == []


def test_add_default(BaseClass):
    BaseClass.default_implementation = "default_implementation"
    # Since we haven't registered the default yet, calling `list_available` should
    # raise a `RegistrationError` exception.
    with pytest.raises(RegistrationError):
        BaseClass.list_available()


def test_register_default(BaseClass):
    @BaseClass.register(BaseClass.default_implementation)
    class FirstImplementation(BaseClass):
        def do_something(self) -> int:
            return 1

    assert BaseClass.is_registered(BaseClass.default_implementation)
    assert BaseClass.list_available() == ["default_implementation"]


def test_by_name(BaseClass):
    assert BaseClass.by_name("default_implementation")().do_something() == 1


def test_registered_name_hook_worked(BaseClass):
    subclass = BaseClass.by_name("default_implementation")
    assert subclass.registered_name == "default_implementation"


def test_iter_registered(BaseClass):
    registered = list(BaseClass.iter_registered())
    assert len(registered) == 1
    assert isinstance(registered[0], tuple)
    name, subclass = registered[0]
    assert name == "default_implementation"
    assert subclass().do_something() == 1


def test_register_duplicate_fails(BaseClass):
    with pytest.raises(RegistrationError):

        @BaseClass.register(BaseClass.default_implementation)
        class AnotherImplementation(BaseClass):
            def do_something(self) -> int:
                return 2


def test_override_registered(BaseClass):
    with pytest.warns(UserWarning) as records:

        @BaseClass.register(BaseClass.default_implementation, override=True)
        class AnotherImplementation(BaseClass):
            def do_something(self) -> int:
                return 2

    assert len(records) == 1
    assert (
        records[0].message.args[0]
        == "Overriding default_implementation in SomeRegistrableBaseClass registry"
    )
    assert BaseClass.by_name("default_implementation")().do_something() == 2


def test_hooks_parameter(BaseClass):
    @BaseClass.register(
        "another",
        hooks=[lambda subclass, name: setattr(subclass, "alternate_name", "blah")],
    )
    class AnotherImplementation(BaseClass):
        def do_something(self) -> int:
            return 2

    assert AnotherImplementation.registered_name == "another"
    assert AnotherImplementation.alternate_name == "blah"


def test_register_non_subclass_fails(BaseClass):
    with pytest.raises(RegistrationError) as excinfo:

        @BaseClass.register("another")
        class AnotherClass:
            pass

    assert str(excinfo.value) == (
        "Cannot register AnotherClass as another; "
        "AnotherClass must be a subclass of SomeRegistrableBaseClass"
    )


def test_register_non_class_fails(BaseClass):
    with pytest.raises(RegistrationError) as excinfo:

        @BaseClass.register("another")
        def function_not_class():
            return 1

    assert str(excinfo.value) == (
        "Cannot register function_not_class as another; "
        "function_not_class must be a subclass of SomeRegistrableBaseClass"
    )
