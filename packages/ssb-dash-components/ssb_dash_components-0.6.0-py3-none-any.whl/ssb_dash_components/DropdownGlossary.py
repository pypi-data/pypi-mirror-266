# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DropdownGlossary(Component):
    """A DropdownGlossary component.
SSB styled Dropdown list

Keyword arguments:

- id (string; optional)

- ariaLabel (string; optional)

- className (string; optional)

- error (boolean; optional)

- errorMessage (string; optional)

- glossary (dash component; optional)

- header (string; optional)

- icon (dict; optional)

- items (list of dicts; optional)

    `items` is a list of dicts with keys:

    - disabled (boolean; optional)

    - id (string; optional)

    - title (string; optional)

- largeSize (boolean; optional)

- open (boolean; optional)

- placeholder (string; optional)

- searchable (boolean; optional)

- showGlossary (boolean; optional)

- tabIndex (number; optional)

- value (string; optional)"""
    _children_props = ['glossary']
    _base_nodes = ['glossary', 'children']
    _namespace = 'ssb_dash_components'
    _type = 'DropdownGlossary'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, ariaLabel=Component.UNDEFINED, className=Component.UNDEFINED, error=Component.UNDEFINED, errorMessage=Component.UNDEFINED, header=Component.UNDEFINED, icon=Component.UNDEFINED, items=Component.UNDEFINED, open=Component.UNDEFINED, placeholder=Component.UNDEFINED, searchable=Component.UNDEFINED, value=Component.UNDEFINED, tabIndex=Component.UNDEFINED, largeSize=Component.UNDEFINED, showGlossary=Component.UNDEFINED, glossary=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'ariaLabel', 'className', 'error', 'errorMessage', 'glossary', 'header', 'icon', 'items', 'largeSize', 'open', 'placeholder', 'searchable', 'showGlossary', 'tabIndex', 'value']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'ariaLabel', 'className', 'error', 'errorMessage', 'glossary', 'header', 'icon', 'items', 'largeSize', 'open', 'placeholder', 'searchable', 'showGlossary', 'tabIndex', 'value']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DropdownGlossary, self).__init__(**args)
