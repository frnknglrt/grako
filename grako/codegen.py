# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from grako.model import Node
from grako.rendering import render, Renderer, RenderingFormatter


class DelegatingRenderingFormatter(RenderingFormatter):
    def __init__(self, delegate):
        assert hasattr(delegate, 'render')
        super(DelegatingRenderingFormatter, self).__init__()
        self.delegate = delegate

    #override
    def render(self, item, join='', **fields):
        result = self.delegate.render(item, join=join, **fields)
        if result is None:
            result = super(DelegatingRenderingFormatter).render(item, join=join, **fields)
        return result

    def convert_field(self, value, conversion):
        if isinstance(value, Node):
            return self.render(value)
        else:
            return super(RenderingFormatter, self).convert_field(value, conversion)


class ModelRenderer(Renderer):
    def __init__(self, codegen, node, template=None):
        super(ModelRenderer, self).__init__(template=template)
        self._codegen = codegen
        self._node = node

        self.formatter = codegen.formatter

        # FIXME: What if the node is not an AST or object?
        # if isinstance(node, Node):
        #    for name, value in vars(node).items():
        #        if not name.startswith('_'):
        #            setattr(self, name, value)
        #else:
        #    self.value = node

        self.__postinit__()

    def __postinit__(self):
        pass


    @property
    def node(self):
        return self._node

    def get_renderer(self, item):
        return self._codegen.get_renderer(item)

    def render(self, template=None, **fields):
        # FIXME: Not needed if Node copies AST entries to attributes
        fields.update({k: v for k, v in vars(self.node).items() if not k.startswith('_')})
        return super(ModelRenderer, self).render(template=template, **fields)


class NullModelRenderer(ModelRenderer):
    """A `ModelRenderer` that generates nothing.
    """
    template = ''


class CodeGenerator(object):
    """
    A **CodeGenerator** is an abstract class that finds a
    ``ModelRenderer`` class with the same name as each model's node and
    uses it to render the node.
    """
    def __init__(self):
        self.formatter = DelegatingRenderingFormatter(self)

    def _find_renderer_class(self, item):
        """
        This method is used to find a ``ModelRenderer`` for the given
        item. It must be overriden in concrete classes.
        """
        pass

    def get_renderer(self, item):
        rendererClass = self._find_renderer_class(item)
        if rendererClass is None:
            return None
        try:
            assert issubclass(rendererClass, ModelRenderer)
            return rendererClass(self, item)
        except Exception as e:
            raise type(e)(str(e), rendererClass.__name__)

    def render(self, item, join='', **fields):
        renderer = self.get_renderer(item)
        if renderer is None:
            return render(item, join=join, **fields)
        return renderer.render(**fields)
