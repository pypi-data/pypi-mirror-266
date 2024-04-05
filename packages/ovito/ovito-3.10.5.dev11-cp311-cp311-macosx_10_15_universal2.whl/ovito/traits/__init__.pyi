"""This module provides specific `trait types <https://docs.enthought.com/traits/traits_user_manual/intro.html>`__ which
are used in the context of custom modifiers and other extension classes to
define additional object parameters.
They supplement the `generic trait types <https://docs.enthought.com/traits/traits_user_manual/defining.html#predefined-traits>`__
provided by the `Traits <https://docs.enthought.com/traits/index.html>`__ Python package."""
__all__ = ['OvitoObject', 'Color', 'Vector2', 'Vector3', 'FilePath', 'OvitoObjectTrait', 'ColorTrait']
from __future__ import annotations
from typing import Tuple, Type, Any, Union
import traits.api
import ovito.pipeline
import ovito.data
import ovito.vis

class OvitoObject(traits.api.Instance):
    """A `trait type <https://docs.enthought.com/traits/traits_user_manual/intro.html>`__ that stores an instance of a class from the :py:mod:`ovito` package,
e.g. a visual element, modifier, or data object."""

    def __init__(self, klass: Type[Union[ovito.vis.DataVis, ovito.pipeline.Modifier, ovito.pipeline.FileSource, ovito.pipeline.StaticSource, ovito.data.DataObject]], **params: Any) -> None:
        """:param klass: The object class type to instantiate.
:param params: All other keyword parameters are forwarded to the constructor of the object class."""
        ...

class Color(traits.api.BaseTuple):
    """A `trait type <https://docs.enthought.com/traits/traits_user_manual/intro.html>`__ that stores a tuple of three floats representing the RGB components of a color parameter.
The three components must be in the range 0.0 - 1.0."""

    def __init__(self, default: Tuple[float, float, float]=(1.0, 1.0, 1.0), **metadata: Any) -> None:
        """:param default: The initial color value to be assigned to the parameter trait."""
        ...

class FilePath(traits.api.BaseFile):
    """A `trait type <https://docs.enthought.com/traits/traits_user_manual/intro.html>`__ that stores a filesystem path.
In the GUI, a file selection dialog is displayed for the user to pick the trait value."""

    def __init__(self, default: str='', **metadata: Any) -> None:
        """:param default: Initial parameter trait value."""
        ...

class Vector2(traits.api.BaseTuple):
    """A `trait type <https://docs.enthought.com/traits/traits_user_manual/intro.html>`__ that stores a tuple of two floats, which represent a vector or point in 2d space."""

    def __init__(self, default: Tuple[float, float]=(0.0, 0.0), **metadata: Any) -> None:
        """:param default: The initial vector value to be assigned to the parameter trait."""
        ...

class Vector3(traits.api.BaseTuple):
    """A `trait type <https://docs.enthought.com/traits/traits_user_manual/intro.html>`__ that stores a tuple of three floats, which represent a vector or point in 3d space."""

    def __init__(self, default: Tuple[float, float, float]=(0.0, 0.0, 0.0), **metadata: Any) -> None:
        """:param default: The initial vector value to be assigned to the parameter trait."""
        ...