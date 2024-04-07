# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DataFlow(Component):
    """A DataFlow component.
ExampleComponent is an example component.
It takes a property, `label`, and
displays it.
It renders an input with the property `value`
which is editable by the user.

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- edges (list; optional):
    Array of edges connecting the nodes.

- graphType (string; default "multiPlot"):
    Type of the graph structure [singleOutput, multiPlot].

- meta (dict; required):
    Metadata dictionary of the available databases.

- nodeTypes (list of strings; default ["db", "merge", "filter", "trafo", "plot"]):
    Metadata dictionary of the available databases.

- nodes (list; optional):
    Array of nodes."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_dataflow_components'
    _type = 'DataFlow'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, meta=Component.REQUIRED, nodes=Component.UNDEFINED, edges=Component.UNDEFINED, nodeTypes=Component.UNDEFINED, graphType=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'edges', 'graphType', 'meta', 'nodeTypes', 'nodes']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'edges', 'graphType', 'meta', 'nodeTypes', 'nodes']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        for k in ['meta']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(DataFlow, self).__init__(**args)
