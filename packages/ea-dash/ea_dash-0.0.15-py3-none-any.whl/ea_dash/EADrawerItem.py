# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class EADrawerItem(Component):
    """An EADrawerItem component.
EADrawerItem is a component that renders a non-collapsible drawer item. It is typically used
within a navigation drawer to represent a single navigational link or action. It supports
a disabled state, which can be used to indicate that the item is not currently available
for interaction. A lock icon is displayed when the item is disabled.

Keyword arguments:

- disabled (boolean; default False):
    A boolean that determines whether the drawer item is disabled.
    When set to True, the item will typically be non-interactive and
    may be styled differently to indicate its disabled state to the
    user.

- href (string; optional):
    A string specifying the URL that the drawer item links to. When
    provided, the item will function as a hyperlink, navigating the
    user to the specified destination when clicked. This is typically
    used to create navigational links in the drawer that take the user
    to different parts of the application or website.

- label (string; optional):
    The text label for the drawer item. This label will be displayed
    as the primary content of the item and is typically the name or
    title of the section that can be expanded or collapsed."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'ea_dash'
    _type = 'EADrawerItem'
    @_explicitize_args
    def __init__(self, disabled=Component.UNDEFINED, label=Component.UNDEFINED, href=Component.UNDEFINED, **kwargs):
        self._prop_names = ['disabled', 'href', 'label']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['disabled', 'href', 'label']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(EADrawerItem, self).__init__(**args)
