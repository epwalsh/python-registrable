from collections import defaultdict
import importlib
from warnings import warn
from typing import TypeVar, Type, Dict, List, Optional, Iterable, Tuple

from registrable.exceptions import RegistrationError


T = TypeVar("T")


class Registrable:
    """
    Adapted from https://github.com/allenai/allennlp/blob/master/allennlp/common/registrable.py.

    Any class that inherits from ``Registrable`` gains access to a named registry for its
    subclasses. To register them, just decorate them with the classmethod
    ``@BaseClass.register(name)``.

    After which you can call ``BaseClass.list_available()`` to get the keys for the
    registered subclasses, and ``BaseClass.by_name(name)`` to get the corresponding subclass.
    Note that the registry stores the subclasses themselves; not class instances.

    You can specify a default by setting ``BaseClass.default_implementation``.
    If it is set, it will be the first element of ``list_available()``.

    Note that if you use this class to implement a new ``Registrable`` abstract class,
    you must ensure that all subclasses of the abstract class are loaded when the module is
    loaded, because the subclasses register themselves in their respective files. You can
    achieve this by having the abstract class and all subclasses in the __init__.py of the
    module in which they reside (as this causes any import of either the abstract class or
    a subclass to load all other subclasses and the abstract class).
    """

    _registry: Dict[Type, Dict[str, Type]] = defaultdict(dict)
    default_implementation: Optional[str] = None

    @classmethod
    def register(cls: Type[T], name: str, override: bool = False):
        registry = Registrable._registry[cls]

        def add_subclass_to_registry(subclass: Type[T]):
            # Add to registry.
            # If name already registered, warn if overriding or raise an error if override not allowed.
            if name in registry:
                if not override:
                    raise RegistrationError(
                        f"Cannot register {name} as {cls.__name__}; "
                        f"name already in use for {registry[name].__name__}"
                    )
                else:
                    warn(f"Overriding {name} in {cls.__name__} registry")
            registry[name] = subclass
            return subclass

        return add_subclass_to_registry

    @classmethod
    def by_name(cls: Type[T], name: str) -> Type[T]:
        if name in Registrable._registry[cls]:
            return Registrable._registry[cls][name]
        elif "." in name:
            # This might be a fully qualified class name, so we'll try importing its "module"
            # and finding it there.
            parts = name.split(".")
            submodule = ".".join(parts[:-1])
            class_name = parts[-1]

            try:
                module = importlib.import_module(submodule)
            except ModuleNotFoundError:
                raise RegistrationError(
                    f"tried to interpret {name} as a path to a class "
                    f"but unable to import module {submodule}"
                )

            try:
                return getattr(module, class_name)
            except AttributeError:
                raise RegistrationError(
                    f"tried to interpret {name} as a path to a class "
                    f"but unable to find class {class_name} in {submodule}"
                )
        else:
            # is not a qualified class name
            raise RegistrationError(
                f"{name} is not a registered name for {cls.__name__}."
            )

    @classmethod
    def list_available(cls: Type[T]) -> List[str]:
        """List default first if it exists"""
        keys = list(Registrable._registry[cls].keys())
        default = cls.default_implementation  # type: ignore

        if default is None:
            return keys
        if default not in keys:
            raise RegistrationError(
                f"Default implementation {default} is not registered"
            )
        return [default] + [k for k in keys if k != default]

    @classmethod
    def is_registered(cls: Type[T], name: str) -> bool:
        return name in Registrable._registry[cls]

    @classmethod
    def iter_registered(cls: Type[T]) -> Iterable[Tuple[str, Type[T]]]:
        return Registrable._registry[cls].items()
