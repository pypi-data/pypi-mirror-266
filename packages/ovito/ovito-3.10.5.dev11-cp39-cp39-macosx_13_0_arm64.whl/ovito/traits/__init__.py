"""
.. versionadded:: 3.8.0

This module provides specific `trait types <https://docs.enthought.com/traits/traits_user_manual/intro.html>`__ which
are used in the context of :ref:`custom modifiers <writing_custom_modifiers>` and other extension classes to
:ref:`define additional object parameters <writing_custom_modifiers.advanced_interface.user_params>`.
They supplement the `generic trait types <https://docs.enthought.com/traits/traits_user_manual/defining.html#predefined-traits>`__
provided by the `Traits <https://docs.enthought.com/traits/index.html>`__ Python package.
"""

import traits.api
from collections.abc import Iterable

__all__ = ['OvitoObject', 'Color', 'Vector2', 'Vector3', 'FilePath', 'OvitoObjectTrait', 'ColorTrait']

class OvitoObject(traits.api.Instance):
    """
    A `trait type <https://docs.enthought.com/traits/traits_user_manual/intro.html>`__ that stores an instance of a class from the :py:mod:`ovito` package,
    e.g. a visual element, modifier, or data object.
    """
    def __init__(self, klass, factory=None, **params):
        """
        :param klass: The object class type to instantiate.
        :param params: All other keyword parameters are forwarded to the constructor of the object class.
        """
        params['_load_user_defaults_in_gui'] = True # Initialize object parameters to user default values when running in the GUI environment.
        super().__init__(klass, factory=factory, kw=params)

class Color(traits.api.BaseTuple):
    """
    A `trait type <https://docs.enthought.com/traits/traits_user_manual/intro.html>`__ that stores a tuple of three floats representing the RGB components of a color parameter.
    The three components must be in the range 0.0 - 1.0.
    """
    def __init__(self, default=(1.0, 1.0, 1.0), **metadata):
        """
        :param default: The initial color value to be assigned to the parameter trait.
        """
        if not isinstance(default, tuple) and isinstance(default, Iterable):
            default = tuple(default)
        if len(default) != 3:
            raise ValueError("Expected tuple of length 3.")
        super().__init__(default, **metadata)

    # Override the validate() method to also accept NumPy arrays.
    # Some OVITO functions return RGB colors as NumPy arrays, not tuples.
    def validate(self, object, name, value):
        if not isinstance(value, tuple) and isinstance(value, Iterable):
            value = tuple(value)
        return super().validate(object, name, value)

class FilePath(traits.api.BaseFile):
    """
    A `trait type <https://docs.enthought.com/traits/traits_user_manual/intro.html>`__ that stores a filesystem path.
    In the GUI, a file selection dialog is displayed for the user to pick the trait value.

    .. versionadded:: 3.10.0
    """
    def __init__(self, default: str = "", **metadata) -> None:
        """:param default: Initial parameter trait value."""
        super().__init__(default, **metadata)

class Vector2(traits.api.BaseTuple):
    """
    A `trait type <https://docs.enthought.com/traits/traits_user_manual/intro.html>`__ that stores a tuple of two floats, which represent a vector or point in 2d space.

    .. versionadded:: 3.10.0
    """
    def __init__(self, default=(0.0, 0.0), **metadata):
        """
        :param default: The initial vector value to be assigned to the parameter trait.
        """
        if len(default) != 2:
            raise ValueError("Expected tuple of length 2.")
        super().__init__(default, **metadata)

    # Override the validate() method to also accept NumPy arrays.
    # Some OVITO functions return Vector2 values as NumPy arrays, not tuples.
    def validate(self, object, name, value):
        if not isinstance(value, tuple) and isinstance(value, Iterable):
            value = tuple(value)
        return super().validate(object, name, value)

class Vector3(traits.api.BaseTuple):
    """
    A `trait type <https://docs.enthought.com/traits/traits_user_manual/intro.html>`__ that stores a tuple of three floats, which represent a vector or point in 3d space.

    .. versionadded:: 3.10.0
    """
    def __init__(self, default=(0.0, 0.0, 0.0), **metadata):
        """
        :param default: The initial vector value to be assigned to the parameter trait.
        """
        if len(default) != 3:
            raise ValueError("Expected tuple of length 3.")
        super().__init__(default, **metadata)

    # Override the validate() method to also accept NumPy arrays.
    # Some OVITO functions return Vector3 values as NumPy arrays, not tuples.
    def validate(self, object, name, value):
        if not isinstance(value, tuple) and isinstance(value, Iterable):
            value = tuple(value)
        return super().validate(object, name, value)

# For backward compatibility with OVITO 3.9.2:
OvitoObjectTrait = OvitoObject
ColorTrait = Color