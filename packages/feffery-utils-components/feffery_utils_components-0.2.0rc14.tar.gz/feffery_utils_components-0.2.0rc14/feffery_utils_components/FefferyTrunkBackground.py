# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class FefferyTrunkBackground(Component):
    """A FefferyTrunkBackground component.


Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    设置内嵌元素内容.

- id (string; optional):
    组件id.

- backgroundColor (string; default '#222426'):
    设置背景颜色，默认为'#222426'.

- chaos (number; default 1):
    设置trunk混乱程度，范围0到10，默认为1.

- className (string | dict; optional):
    css类名.

- color (string; default '#98465f'):
    设置trunk颜色，默认为'#98465f'.

- gyroControls (boolean; default False):
    设置是否开启陀螺仪控制，默认为False.

- key (string; optional):
    辅助刷新用唯一标识key值.

- loading_state (dict; optional)

    `loading_state` is a dict with keys:

    - component_name (string; optional):
        Holds the name of the component that is loading.

    - is_loading (boolean; optional):
        Determines if the component is loading or not.

    - prop_name (string; optional):
        Holds which property is loading.

- minHeight (number; default 200.00):
    设置最小高度，默认为200.00.

- minWidth (number; default 200.00):
    设置最小宽度，默认为200.00.

- mouseControls (boolean; default True):
    设置是否开启鼠标控制，默认为True.

- scale (number; default 1.00):
    设置比例，默认为1.00.

- scaleMobile (number; default 1.00):
    设置移动端比例，默认为1.00.

- spacing (number; default 0):
    设置trunk间距，范围0到10，默认为0.

- style (dict; optional):
    自定义css字典.

- touchControls (boolean; default True):
    设置是否开启触摸控制，默认为True."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'feffery_utils_components'
    _type = 'FefferyTrunkBackground'
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, key=Component.UNDEFINED, mouseControls=Component.UNDEFINED, touchControls=Component.UNDEFINED, gyroControls=Component.UNDEFINED, minHeight=Component.UNDEFINED, minWidth=Component.UNDEFINED, scale=Component.UNDEFINED, scaleMobile=Component.UNDEFINED, backgroundColor=Component.UNDEFINED, color=Component.UNDEFINED, spacing=Component.UNDEFINED, chaos=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'backgroundColor', 'chaos', 'className', 'color', 'gyroControls', 'key', 'loading_state', 'minHeight', 'minWidth', 'mouseControls', 'scale', 'scaleMobile', 'spacing', 'style', 'touchControls']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'backgroundColor', 'chaos', 'className', 'color', 'gyroControls', 'key', 'loading_state', 'minHeight', 'minWidth', 'mouseControls', 'scale', 'scaleMobile', 'spacing', 'style', 'touchControls']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(FefferyTrunkBackground, self).__init__(children=children, **args)
