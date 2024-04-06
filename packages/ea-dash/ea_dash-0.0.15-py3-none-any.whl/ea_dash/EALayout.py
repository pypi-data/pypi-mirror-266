# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class EALayout(Component):
    """An EALayout component.
EALayout is a layout component used by Energy Aspects apps. It provides a consistent layout structure
including a header, sidebar, main content area, and an optional footer. It also supports theming and
drawer components for additional navigation.

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The main content to be displayed in the layout. This can include
    any valid React nodes such as elements, strings, numbers, or
    fragments.

- id (string; optional):
    The unique identifier for the component, used by Dash to keep
    track of the component's state and to allow callbacks to target
    this component.

- defaultFooterShow (boolean; default True):
    A boolean that determines whether the footer should be displayed
    by default. When True, the footer with slogans and social links is
    enabled; when False, it is disabled.

- defaultLeftDrawerOpen (boolean; default True):
    A boolean that sets the initial state of the left drawer's
    visibility when the layout is first rendered. When True, the left
    drawer starts open; when False, it starts closed.

- defaultRightDrawerOpen (boolean; optional):
    A boolean that sets the initial state of the right drawer's
    visibility when the layout is first rendered. When True, the right
    drawer starts open; when False, it starts closed.

- firstName (string; default 'Energy'):
    The first name of the user, which may be displayed in the layout
    for personalization or account-related features.

- lastName (string; default 'Aspects'):
    The last name of the user, which may be displayed alongside the
    first name for personalization or account-related features.

- leftDrawerContent (a list of or a singular dash component, string or number; optional):
    The navigation items displayed in the left drawer. This can
    include any valid React nodes such as elements, strings, numbers,
    or fragments or it can be None.

- leftDrawerOpen (boolean; optional):
    A boolean that controls the visibility of the left drawer. When
    True, the left drawer is open; when False, it is closed.

- logoLink (string; optional):
    A string that specifies the URL to which the user will be
    redirected when clicking on the logo. This prop sets the
    destination for the logo link, typically pointing to the home page
    or a landing page.

- rightDrawerOpen (boolean; optional):
    A boolean that controls the visibility of the right drawer. When
    True, the right drawer is open; when False, it is closed."""
    _children_props = ['leftDrawerContent']
    _base_nodes = ['leftDrawerContent', 'children']
    _namespace = 'ea_dash'
    _type = 'EALayout'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, leftDrawerOpen=Component.UNDEFINED, firstName=Component.UNDEFINED, lastName=Component.UNDEFINED, rightDrawerOpen=Component.UNDEFINED, defaultLeftDrawerOpen=Component.UNDEFINED, defaultFooterShow=Component.UNDEFINED, defaultRightDrawerOpen=Component.UNDEFINED, logoLink=Component.UNDEFINED, leftDrawerContent=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'defaultFooterShow', 'defaultLeftDrawerOpen', 'defaultRightDrawerOpen', 'firstName', 'lastName', 'leftDrawerContent', 'leftDrawerOpen', 'logoLink', 'rightDrawerOpen']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'defaultFooterShow', 'defaultLeftDrawerOpen', 'defaultRightDrawerOpen', 'firstName', 'lastName', 'leftDrawerContent', 'leftDrawerOpen', 'logoLink', 'rightDrawerOpen']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(EALayout, self).__init__(children=children, **args)
