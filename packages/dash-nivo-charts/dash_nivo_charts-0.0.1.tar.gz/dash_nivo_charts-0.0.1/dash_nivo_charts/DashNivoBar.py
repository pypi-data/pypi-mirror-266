# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DashNivoBar(Component):
    """A DashNivoBar component.
ExampleComponent is an example component.
It takes a property, `label`, and
displays it.
It renders an input with the property `value`
which is editable by the user.

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- data (list; optional):
    The value displayed in the input.

- eventData (dict; optional):
    The value displayed in the input."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_nivo_charts'
    _type = 'DashNivoBar'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, eventData=Component.UNDEFINED, data=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'data', 'eventData']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'data', 'eventData']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DashNivoBar, self).__init__(**args)
