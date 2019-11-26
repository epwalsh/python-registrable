import pytest

from registrable import Registrable, RegistrationError


@pytest.fixture(scope="module")
def BaseClass():
    class SomeRegistrableBaseClass(Registrable):
        def do_something(self) -> int:
            raise NotImplementedError

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


def test_register_duplicate_fails(BaseClass):
    with pytest.raises(RegistrationError):

        @BaseClass.register(BaseClass.default_implementation)
        class AnotherImplementation(BaseClass):
            def do_something(self) -> int:
                return 2


def test_override_registered(BaseClass):
    with pytest.warns(UserWarning):

        @BaseClass.register(BaseClass.default_implementation, override=True)
        class AnotherImplementation(BaseClass):
            def do_something(self) -> int:
                return 2

    assert BaseClass.by_name("default_implementation")().do_something() == 2
