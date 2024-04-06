# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DashSpreadGrid(Component):
    """A DashSpreadGrid component.


Keyword arguments:

- id (string; optional)

- borderWidth (number; default 1)

- clicked_cell (dict; optional)

- clicked_custom_cell (dict; optional)

- columnWidths (list; optional)

- columns (list; default [{ "type": "DATA-BLOCK" }])

- data (boolean | number | string | dict | list; optional)

- dataSelector (string; default "data[row.id][column.id]")

- editedCells (list; optional)

- filtering (list; optional)

- filters (list; optional)

- focusedCell (dict; optional)

- formatting (list; optional)

- highlightedCells (list; optional)

- pinnedBottom (number; default 0)

- pinnedLeft (number; default 0)

- pinnedRight (number; default 0)

- pinnedTop (number; default 0)

- rowHeights (list; optional)

- rows (list; default [{ "type": "HEADER" }, { "type": "DATA-BLOCK" }])

- selectedCells (list; optional)

- sortBy (list; optional)

- sorting (list; optional)"""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_spread_grid'
    _type = 'DashSpreadGrid'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, data=Component.UNDEFINED, columns=Component.UNDEFINED, rows=Component.UNDEFINED, formatting=Component.UNDEFINED, filtering=Component.UNDEFINED, sorting=Component.UNDEFINED, dataSelector=Component.UNDEFINED, pinnedTop=Component.UNDEFINED, pinnedBottom=Component.UNDEFINED, pinnedLeft=Component.UNDEFINED, pinnedRight=Component.UNDEFINED, borderWidth=Component.UNDEFINED, focusedCell=Component.UNDEFINED, selectedCells=Component.UNDEFINED, highlightedCells=Component.UNDEFINED, editedCells=Component.UNDEFINED, filters=Component.UNDEFINED, sortBy=Component.UNDEFINED, columnWidths=Component.UNDEFINED, rowHeights=Component.UNDEFINED, clicked_cell=Component.UNDEFINED, clicked_custom_cell=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'borderWidth', 'clicked_cell', 'clicked_custom_cell', 'columnWidths', 'columns', 'data', 'dataSelector', 'editedCells', 'filtering', 'filters', 'focusedCell', 'formatting', 'highlightedCells', 'pinnedBottom', 'pinnedLeft', 'pinnedRight', 'pinnedTop', 'rowHeights', 'rows', 'selectedCells', 'sortBy', 'sorting']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'borderWidth', 'clicked_cell', 'clicked_custom_cell', 'columnWidths', 'columns', 'data', 'dataSelector', 'editedCells', 'filtering', 'filters', 'focusedCell', 'formatting', 'highlightedCells', 'pinnedBottom', 'pinnedLeft', 'pinnedRight', 'pinnedTop', 'rowHeights', 'rows', 'selectedCells', 'sortBy', 'sorting']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DashSpreadGrid, self).__init__(**args)
