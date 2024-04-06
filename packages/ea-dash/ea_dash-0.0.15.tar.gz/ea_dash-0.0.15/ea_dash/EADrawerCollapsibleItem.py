# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class EADrawerCollapsibleItem(Component):
    """An EADrawerCollapsibleItem component.
EADrawerCollapsibleItem is a component that renders a collapsible drawer item. It can be used
within a navigation drawer to group related items that can be expanded or collapsed by the user.
It supports a disabled state, which can be used to indicate that the item is not currently
available for interaction. A lock icon is displayed when the item is disabled.

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children nodes to be rendered inside the collapsible drawer
    item. This can include any valid React components or elements that
    you want to display when the item is expanded.

- className (string; optional):
    An optional string that specifies custom CSS class names to be
    added to the drawer item's class attribute. This allows for
    additional styling to be applied to the drawer item for
    customization or theming purposes. The class names provided here
    will be merged with any other existing classes on the drawer item.

- disabled (boolean; default False):
    A boolean that determines whether the drawer item is disabled.
    When set to True, the item will typically be non-interactive and
    may be styled differently to indicate its disabled state to the
    user.

- label (string; optional):
    The text label for the drawer item. This label will be displayed
    as the primary content of the item and is typically the name or
    title of the section that can be expanded or collapsed."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'ea_dash'
    _type = 'EADrawerCollapsibleItem'
    @_explicitize_args
    def __init__(self, children=None, disabled=Component.UNDEFINED, label=Component.UNDEFINED, className=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'className', 'disabled', 'label']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'className', 'disabled', 'label']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(EADrawerCollapsibleItem, self).__init__(children=children, **args)
