from typing import Any, Literal, NotRequired, TypeAlias, Required, TypedDict, Union, Self
from uuid import UUID

code_map: dict[int, str] = {
    1_200: "成功请求代码",
    1_404: "请求的内容或流程不存在",
    1_500: "流程内部错误或流程错误",
    1_503: "服务器宕机，主机强迫断开连接"
}

class MessageInit:

    class nodoc_int4(int):
        "4位整型数据，范围：[-8, 7]"

        def __init__(self, value: int) -> None:
            super().__init__()
            if not (isinstance(value, int) or (-8 < value < 7)):
                raise ValueError(f"{value} 超出范围。")

    class nodoc_int8(int):
        "8位整型数据，范围：[-128, 127]"

        def __init__(self, value: int) -> None:
            super().__init__()
            if not (isinstance(value, int) or (-128 < value < 127)):
                raise ValueError(f"{value} 超出范围。")

    class fontStylePropertyInit:

        class Color:
            ...

        class Rotation(TypedDict):
            value: float
            """
            double, 字块旋转角度 （角度值）
            """
            center: list[float]
            """
            nodoc_vec<double>[2] 二维向量, 定义字块旋转中心（相对坐标）
            """

        class Spin(TypedDict):
            value: float
            """
            double, 单个字符旋转角度 （角度值）
            """
            center: list[float]
            """
            nodoc_vec<double>[2] 二维向量，定义单个字旋转中心（相对坐标）
            """

        class Hyperlink(TypedDict):
            inherited: Union[str, "MessageInit.fontStyleProperty"]
            url: str
   


    class fontStyleProperty(TypedDict):
        color: "MessageInit.fontStylePropertyInit.Color"
        """
        字体颜色
        """
        font_size: "MessageInit.nodoc_int8"
        """
        字体尺寸
        """
        font_family: str
        """
        字体族
        """
        bold: "MessageInit.nodoc_int4"
        """
        粗体程度
        """
        underlined: bool
        """
        下划线
        """
        italic: bool
        """
        斜体
        """
        rotation: Union[float, "MessageInit.fontStylePropertyInit.Rotation"]
        """
        double | compound, 字体块旋转角度（角度值），仅是double时旋转中心默认为字块中心。
        """
        spin: Union[float, "MessageInit.fontStylePropertyInit.Spin"]
        """
        double | compound, 单个字符旋转角度（角度值），仅是double时旋转中心默认为字符中心。
        """
        hyperlink: Union[str, "MessageInit.fontStylePropertyInit.Hyperlink"]
        """
        string | compound, 该字体的超链接，当仅为字符串类型时，以url跳转到字符串中的位置。
        """
        width: float
        """
        double, bbox宽度
        """
        height: float
        """
        double, bbox高度
        """
        position: list[float]
        """
        nodoc_vec<double> ...[2] 二维向量，bbox位置（绝对坐标）
        """
        line_distance: float
        """
        double, 自动排版时正文的行间距。
        """
        font_distance: float
        """
        各个字符之间的间距。
        """
        align: Literal['left', 'right', 'center', 'justify', 'middle', 'vertical', 'horizontal', 'top', 'bottom', 'top-left', 'top-right', 'bottom-left', 'bottom-right']
        """
        string, 对齐类型
        """



    class generalProperty(TypedDict):
        inherited: Union[str, "MessageInit.fontStyleProperty"]
        """
        - Union
          - str: 继承自来自另一段指定hash消息的属性
          - fontStyleProperty: 同fontStyle的property字段一致
        """

    class titleProperty(generalProperty):
        level: "MessageInit.nodoc_int4"
        """
        unsigned nodoc_int4
        范围[0, 15]，决定标题的层级
        """

    class headerProperty(generalProperty):
        underlined: Required[bool]
        """
        不同于fontStyle的下划线，这将决定整个页眉的bbox底部是否加下划线。
        """

    class footerProperty(generalProperty):
        # Required
        overlined: Required[bool]
        """
        这将决定整个页脚的bbox顶部是否加上划线。
        """

    class textProperty(generalProperty):
        indent: float
        """
        double, 该段正文的缩进像素
        """

    class latexProperty(TypedDict):
        index: int
        """
        该段公式在父节点中的位置，用于插入公式调整排版。
        """

    class imageProperty(TypedDict):
        size: list[float]
        """
        nodoc_vec<double>[2] 二维向量，图像尺寸
        """
        position: list[float]
        """
        nodoc_vec<double>[2] 二维向量，图像位置
        """

class Checker:
    # 看到之后觉得很迷茫？
    """
    例如当type为title时，我们仅仅只有inherited和level两个property，但是由于许多type继承了generalProperty，而python无法确定类型为title时会采用哪个property字典类型，python认为以下字典中的level是不必要的，因为在其他property中没有该字段，而当我们在索引字典不存在的下标时会报错，故而python给出了警告，为了消除这个警告同时为了简化语法，故而将其封装为了一个类
    {
        "type": "title",
        "property": {
            "inherited": "...",
            "level": 3
        }
    }
    示例：
    ``` py
    import Checker
    def randomDict(x):
        if x == 0:
            return {"foo": 0}
        else:
            return {"bar": 1}
    out1 = Checker("foo", None) >> randomDict(0)
    out2 = Checker("foo", None) >> randomDict(1)
    print(out1)
    print(out2)
    ```
    输出：
    ``` py
    >> 0
       None
    ```
    """

    def __init__(self, content: str, default: Any = None) -> None:
        """
        用于解决类型提示报错。
        - content: str, 绝对存在当前type的字段
        - default: Any, 特殊情况下，该字段可能不存在值，返回某个默认值。
        """
        self.content = content
        self.default = default
        pass

    def __rshift__(self, other):
        if self.content in other:
            try:
                return other[self.content]
            except:
                return self.default
        else:
            return self.default

class MetaData(TypedDict):
    filename: str
    "文件名称"
    create: str
    "文件被创建的时间"
    access: str
    "文件最近一次被访问的时间"
    modify: str
    "文件最近一次被修改的时间"
    change: str
    "元数据最近一次被修改的时间"
    custom: dict
    "其它元数据"

class MessageUnit(TypedDict):
    type: Required[
        Literal[
            "fontStyle",
            "header",
            "footer",
            "title",
            "image",
            "latex",
            "text"
        ]
    ]
    content: NotRequired[str]
    uuid: NotRequired[UUID]
    index: NotRequired[int]
    parent: NotRequired[
        Union[
            UUID,
            list[UUID]
        ]
    ]
    property: Required[
        Union[
            MessageInit.fontStyleProperty,
            MessageInit.headerProperty,
            MessageInit.footerProperty,
            MessageInit.titleProperty,
            MessageInit.imageProperty,
            MessageInit.latexProperty,
            MessageInit.textProperty
        ]
    ]

class Message(TypedDict):
    metadata: MetaData | None
    pipeline: list[MessageUnit]
    code: int

class Data:

    def __init__(self, content: str = "") -> None:
        if not isinstance(content, str):
            raise ValueError(f"期望：str，实际：{type(content)}")
        self.__content: str = content

    @property
    def content(self) -> str:
        return self.__content

    def __lshift__(self, other: str):
        if isinstance(other, str):
            self.__content += other

        return self

    def __str__(self) -> str:
        return self.__content


document_type: TypeAlias = Literal[
    'markdown',
    'html',
    'pdf',
    'word',
    'ppt',
    'excel'
]