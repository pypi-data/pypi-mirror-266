import collections.abc as collections
import sys
import warnings

from . import Pipeline, Modifier, ModifierInterface, ModificationNode
from ..modifiers import PythonModifier
from ..nonpublic import PipelineStatus

# Implementation of the Pipeline.modifiers collection.
def _Pipeline_modifiers(self):
    """ The sequence of modifiers in the pipeline.

        This list contains any modifiers that are applied to the input data provided by the pipeline's data :py:attr:`source`. You
        can add and remove modifiers as needed using standard Python ``append()`` and ``del`` operations. The
        head of the list represents the beginning of the pipeline, i.e. the first modifier receives the data from the
        data :py:attr:`source`, manipulates it and passes the results on to the second modifier in the list and so forth.

        Example: Adding a new modifier to the end of a data pipeline::

           pipeline.modifiers.append(WrapPeriodicImagesModifier())
    """

    class PipelineModifierList(collections.MutableSequence):
        """ This is a helper class is used for the implementation of the Pipeline.modifiers field. It emulates a
            mutable list of modifiers. The array is generated from the chain (linked list) of ModificationNodes
            that make up the pipeline.
        """

        def __init__(self, pipeline):
            """ The constructor stores away a back-pointer to the owning Pipeline. """
            self.pipeline = pipeline

        def _modifiers(self):
            """ Builds a list of all modifiers in the pipeline by traversing the chain of ModificationNodes. """
            mods = []
            obj = self.pipeline.head
            while isinstance(obj, ModificationNode):
                mods.insert(0, obj.modifier)
                obj = obj.input
            return mods

        def _mod_nodes(self):
            """ Builds a lost containing all ModificationNodes in the pipeline. """
            nodes = []
            node = self.pipeline.head
            while isinstance(node, ModificationNode):
                nodes.insert(0, node)
                node = node.input
            return nodes

        def __len__(self):
            """ Determines the total number of modifiers in the pipeline. """
            count = 0
            node = self.pipeline.head
            while isinstance(node, ModificationNode):
                count += 1
                node = node.input
            return count

        def __iter__(self):
            """ Returns an iterator that visits all modifiers in the pipeline. """
            return self._modifiers().__iter__()

        def __getitem__(self, index):
            """ Return a modifier from the pipeline by index. """
            return self._modifiers()[index]

        @staticmethod
        def _create_modification_node(mod):
            # Check if the argument is a valid modifier instance.
            # If it is a Python function, automatically wrap it in a PythonModifier.
            # If it is a Python object implementing the abstract ModifierInterface, automatically wrap it in a PythonModifier.
            # If the caller accidentally passed a Modifier derived class type instead of an instance, automatically instantiate the type.
            # Finally, create and return a ModificationNode for the modifier.
            if isinstance(mod, type) and issubclass(mod, Modifier):
                warnings.warn(f"Method expects a modifier instance, not a modifier class type. Did you forget to write parentheses () after {mod.__name__}?", stacklevel=3)
                mod = mod()
            if not isinstance(mod, Modifier):
                if isinstance(mod, ModifierInterface):
                    mod = PythonModifier(delegate=mod)
                elif callable(mod) and not isinstance(mod, type):
                    mod = PythonModifier(function=mod)
                else:
                    raise TypeError("Expected a modifier instance or user-defined modifier function.")
            node = mod.create_modification_node()
            assert isinstance(node, ModificationNode)
            node.modifier = mod
            return node

        def __setitem__(self, index, modifier):
            """ Replaces an existing modifier in the pipeline with a new one. """
            node = self._create_modification_node(modifier)
            if isinstance(index, slice):
                raise TypeError("This sequence type does not support slicing.")
            if not isinstance(index, int):
                raise TypeError("Expected integer index")
            if index < 0:
                index += len(self)
            mod_nodes = self._mod_nodes()
            if index == len(mod_nodes) - 1 and index >= 0:
                assert self.pipeline.head == mod_nodes[-1]
                self.pipeline.head = node
                node.input = mod_nodes[-1].input
            elif 0 <= index < len(mod_nodes) - 1:
                node.input = mod_nodes[index].input
                mod_nodes[index + 1].input = node
            else:
                raise IndexError("List index is out of range.")
            node.modifier.initialize_modifier(node, None)

        def __delitem__(self, index):
            """ Removes a modifier from the pipeline by index. """
            if isinstance(index, slice):
                raise TypeError("This sequence type does not support slicing.")
            if not isinstance(index, int):
                raise TypeError("Expected integer index")
            if index < 0:
                index += len(self)
            mod_nodes = self._mod_nodes()
            if index >= 0 and index == len(mod_nodes) - 1:
                assert self.pipeline.head == mod_nodes[-1]
                self.pipeline.head = mod_nodes[-1].input
            elif 0 <= index < len(mod_nodes) - 1:
                mod_nodes[index + 1].input = mod_nodes[index].input
            else:
                raise IndexError("List index is out of range.")

        def insert(self, index, mod):
            """ Inserts a new modifier into the pipeline at a given position. """
            if not isinstance(index, int):
                raise TypeError("Expected integer index")
            if index < 0:
                index += len(self)
            mod_nodes = self._mod_nodes()
            node = self._create_modification_node(mod)
            if index == len(mod_nodes) and index >= 0:
                assert self.pipeline.head == mod_nodes[-1]
                self.pipeline.head = node
                node.input = mod_nodes[-1]
            elif 0 <= index <= len(mod_nodes) - 1:
                node.input = mod_nodes[index].input
                mod_nodes[index].input = node
            else:
                raise IndexError("List index is out of range.")
            node.modifier.initialize_modifier(node, None)

        def append(self, modifier):
            """ Inserts a new modifier at the end of the pipeline. """
            # Automatically wrap Python methods in a PythonModifier object.
            node = self._create_modification_node(modifier)
            node.input = self.pipeline.head
            self.pipeline.head = node
            node.modifier.initialize_modifier(node, None)

        def clear(self):
            """ Removes all modifiers from the pipeline. """
            self.pipeline.head = self.pipeline.source

        def __str__(self):
            return str(self._modifiers())

    return PipelineModifierList(self)
Pipeline.modifiers = property(_Pipeline_modifiers)

def _Pipeline_compute(self, frame = None):
    """ Computes and returns the output of this data pipeline (for one trajectory frame).

        This method requests an evaluation of the pipeline and blocks until the input data has been obtained from the
        data :py:attr:`source`, e.g. a simulation file, and all modifiers have been applied to the data. If you invoke the :py:meth:`!compute` method repeatedly
        without changing the modifiers in the pipeline between calls, the pipeline may serve subsequent requests by returning cached output data.

        The optional *frame* parameter specifies the animation frame at which the pipeline should be evaluated. Frames are always consecutively numbered (0, 1, 2, ...).
        If you don't specify any frame number, the current time slider position is used -- or frame 0 if not running in the context of an interactive OVITO Pro session.

        The :py:meth:`!compute` method raises a ``RuntimeError`` if the pipeline could not be successfully evaluated for some reason.
        This may happen due to invalid modifier settings or file I/O errors, for example.

        :param int frame: The animation frame number at which the pipeline should be evaluated.
        :returns: A :py:class:`~ovito.data.DataCollection` produced by the data pipeline.

        .. attention::

            This method returns a snapshot of the results of the current pipeline, representing an independent data copy.
            That means snapshot will *not* reflect changes you subsequently make to the pipeline or the modifiers within the pipeline.
            After changing the pipeline, you have to invoke :py:meth:`!compute` again to let the pipeline produce a new updated snapshot.

        .. attention::

            The returned :py:class:`~ovito.data.DataCollection` represents a copy of the pipeline's internal data, which means,
            if you subsequently make any changes to the objects in the :py:class:`~ovito.data.DataCollection`, those changes will *not*
            be visible to the modifiers *within* the pipeline -- even if you add those modifiers to the pipeline after the :py:meth:`compute`
            call as in this example::

                data = pipeline.compute()
                data.particles_.create_property('Foo', data=...)

                pipeline.modifiers.append(ExpressionSelectionModifier(expression='Foo > 0'))
                new_data = pipeline.compute() # ERROR

            The second call to :py:meth:`compute` will raise an error, because the :py:class:`~ovito.modifiers.ExpressionSelectionModifier`
            references the new particle property ``Foo``, which does not exist in the original data seen by the pipeline.
            That' because we've added the property ``Foo`` only to the :py:class:`~ovito.data.Particles` object that is stored
            in our snapshot ``data``. This :py:class:`~ovito.data.DataCollection` is independent from the transient data the pipeline operates on.

            To make the property ``Foo`` available to modifiers in the pipeline, we thus need to create the property *within*
            the pipeline. This can be accomplished by performing the modification step as a :ref:`Python modifier function <writing_custom_modifiers>`
            that is inserted into the pipeline::

                def add_foo(frame, data):
                    data.particles_.create_property('Foo', data=...)
                pipeline.modifiers.append(add_foo)
                pipeline.modifiers.append(ExpressionSelectionModifier(expression='Foo > 0'))

            Downstream modifiers now see the new particle property created by our user-defined modifier function ``add_foo``,
            which operates on a transient data collection managed by the pipeline system.

    """
    state = self.evaluate_pipeline(frame)
    if state.status.type == PipelineStatus.Type.Error:
        raise RuntimeError(f"Data pipeline failure: {state.status.text}")
    if not state.data:
        raise RuntimeError("Data pipeline did not yield any output DataCollection.")

    return state.mutable_data
Pipeline.compute = _Pipeline_compute
