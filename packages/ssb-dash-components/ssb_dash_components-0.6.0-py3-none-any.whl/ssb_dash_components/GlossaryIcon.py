# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class GlossaryIcon(Component):
    """A GlossaryIcon component.


Keyword arguments:

- children (a list of or a singular dash component, string or number; optional)

- className (string; optional)

- closeText (string; default 'Lukk')

- explanation (string; required)

- iconType (a value equal to: 'Book', 'Info', 'Help'; default 'Book'):
    Choose either: Book, Info or Help icon."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'ssb_dash_components'
    _type = 'GlossaryIcon'
    @_explicitize_args
    def __init__(self, children=None, className=Component.UNDEFINED, closeText=Component.UNDEFINED, explanation=Component.REQUIRED, iconType=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'className', 'closeText', 'explanation', 'iconType']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'className', 'closeText', 'explanation', 'iconType']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in ['explanation']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(GlossaryIcon, self).__init__(children=children, **args)
