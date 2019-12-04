from collections import defaultdict
import importlib
import inspect
from warnings import warn
from typing import TypeVar, Type, Dict, List, Optional, Iterable, Tuple, Callable

from registrable.exceptions import RegistrationError


T = TypeVar("T")
"""
Subclass type.
"""

HookType = Callable[[Type[T], str], None]
"""
Hooks are callables that take the subclass and registered name of the subclass.
"""


class Registrable:
    """
    Adapted from `allennlp.common.registrable
    <https://github.com/allenai/allennlp/blob/master/allennlp/common/registrable.py>`_.

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
    achieve this by having the abstract class and all subclasses in the ``__init__.py`` of the
    module in which they reside (as this causes any import of either the abstract class or
    a subclass to load all other subclasses and the abstract class).
    """

    _registry: Dict[Type, Dict[str, Type]] = defaultdict(dict)
    _hooks: Optional[List[HookType]] = None
    default_implementation: Optional[str] = None

    @classmethod
    def register(
        cls: Type[T],
        name: str,
        override: bool = False,
        hooks: Optional[List[HookType]] = None,
    ):
        """
        Class decorator for registering a subclass.

        Parameters
        ----------
        name : ``str``
            The name to register the subclass under.
        override : ``bool``, optional (default = False)
            If ``name`` is already registered a :class:`registrable.exceptions.RegistrationError` will be raised
            unless this is set to ``True``.
        hooks : ``Optional[List[HookType]]``, optional (default = None)
            Hooks to run when the subclass is registered.

        Raises
        ------
        RegistrationError
        """
        registry = Registrable._registry[cls]
        default_hooks = cls._hooks or []  # type: ignore

        def add_subclass_to_registry(subclass: Type[T]):
            if not inspect.isclass(subclass) or not issubclass(subclass, cls):
                raise RegistrationError(
                    f"Cannot register {subclass.__name__} as {name}; "
                    f"{subclass.__name__} must be a subclass of {cls.__name__}"
                )
            # Add to registry.
            # If name already registered, warn if overriding or raise an error if override not allowed.
            if name in registry:
                if not override:
                    raise RegistrationError(
                        f"Cannot register {subclass.__name__} as {name}; "
                        f"name already in use for {registry[name].__name__}"
                    )
                else:
                    warn(f"Overriding {name} in {cls.__name__} registry")
            registry[name] = subclass
            for hook in default_hooks + (hooks or []):
                hook(subclass, name)
            return subclass

        return add_subclass_to_registry

    @classmethod
    def hook(cls, hook: HookType):
        """
        Function decorator for adding a default hook to a registrable base class.
        """
        if not cls._hooks:
            cls._hooks = []
        cls._hooks.append(hook)
        return hook

    @classmethod
    def by_name(cls: Type[T], name: str) -> Type[T]:
        """
        Get a subclass by its registered name, or its fully qualified class name.

        Parameters
        ----------
        name : ``str``

        Returns
        -------
        Type[T]
            The subclass registered under ``name``.

        Raises
        ------
        RegistrationError
            If name is not a registered subclass or valid fully qualified class name.
        """
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
                maybe_subclass = getattr(module, class_name)
            except AttributeError:
                raise RegistrationError(
                    f"tried to interpret {name} as a path to a class "
                    f"but unable to find class {class_name} in {submodule}"
                )

            if not inspect.isclass(maybe_subclass) or not issubclass(
                maybe_subclass, cls
            ):
                raise RegistrationError(
                    f"tried to interpret {name} as a path to a class "
                    f"but {class_name} is not a subclass of {cls.__name__}"
                )

            # Add subclass to registry and return it.
            Registrable._registry[cls][name] = maybe_subclass
            return maybe_subclass
        else:
            # is not a qualified class name
            raise RegistrationError(
                f"{name} is not a registered name for {cls.__name__}."
            )

    @classmethod
    def list_available(cls: Type[T]) -> List[str]:
        """
        List all registered subclasses.
        """
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
        """
        Returns True if ``name`` is a registered name.
        """
        return name in Registrable._registry[cls]

    @classmethod
    def iter_registered(cls: Type[T]) -> Iterable[Tuple[str, Type[T]]]:
        """
        Iterate through the registered names and subclasses.
        """
        return Registrable._registry[cls].items()
