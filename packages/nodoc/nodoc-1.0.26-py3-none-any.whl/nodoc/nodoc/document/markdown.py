import os
import re
from time import strftime
from typing import Self, Union, Unpack
from uuid import uuid4

def __import():
    from nodoc import docTree


from .base import Data, Document, Message, Checker
from .base import generalProperty, fontStyleProperty
from .base import MetaData, time
# Use a pipeline as a high-level helper
INDENT = '\t'
END = '\n'
SPACE = '\x20'
TITLE_SIGN = '#'
REPLACE_FORMATTER = (
    (r'(\\)',  r'\\\1'),     # 转义\号
    (r'(\*)',  r'\\\1'),     # 转义*号
    (r'(\_)',  r'\\\1'),     # 转义_号
    (r'(\`)',  r'\\\1'),     # 转义`号
    (r'(\|)',  r'\\\1'),     # 转义|号
    (r'(!)',  r'\\\1'),      # 转义!号
    (r'(\[|\])',  r'\\\1'),  # 转义[]
    (r'(\(|\))',  r'\\\1'),  # 转义()
    (r'^(\x20*[0-9]+)(\.)(\x20)',  r'\1\\\2\3'),   # 有序列表
    (r'^(\x20*)(-|\*|\+)(\x20)',  r'\1\\\2\3'),    # 无序列表
    (r'^(\x20*)(#{1,6})(\x20)',  r'\1\\\2\3'),     # 标题
    (r'^(\x20*)(>)(.*)',  r'\1\\\2\3'),            # 引用
    (r'^(\x20*)(\*{3,}|-{3,}|_{3,})(\x20*)$',  r'\1\\\2\3'),    # 分隔线
    (r'^\s*$',  ''),
)

RECOGNIZE_FORMATTER = ()

def __import():
    global docTree
    from nodoc import docTree

class Markdown(Document):
    
    def __init__(self, data: str = "", metadata: MetaData = None) -> None:
        super().__init__(data, metadata)

    @staticmethod
    def escape(text: Union['Markdown', str]):
        """
        转义文本
        - text: str, 待转义文本
        """
        if isinstance(text, Markdown):
            text = text.content
        for pattern, repl in REPLACE_FORMATTER:
            text = re.sub(pattern, repl, text, flags=re.M)
        return text

    def next_line(self):
        "切换到下一行"
        _ = self.data << END

    def add_title(self, text: str, level: int):
        _ = self.data << TITLE_SIGN * level << SPACE << text << END * 2

    def add_text(self, text: str):
        text = self.escape(text)
        _ = self.data << text << END

    def add_comment(self, text):
        _ = self.data << f'<!-- {text} -->'
        if text == 'title':
            _ = self.data << END
        return text
    
    def add_fontStyle(self, style: fontStyleProperty, hash: str | None = None):
        bold_number = Checker("bold", "initial") >> style
        if not isinstance(bold_number, str):
            bold_number *= 100
        strList = str(""
                + f'text-align: {Checker("align", "initial") >> style};'
                + f'font-weight: {bold_number};'
                + f'color: {Checker("color", "initial") >> style};'
                + f'word-spacing: {Checker("font_distance", "initial") >> style};'
                + f'font-family: {Checker("font_family", "initial") >> style};'
                + f'font-size: {Checker("font_size", "initial") >> style};'
                + f'height: {Checker("height", "initial") >> style};'
                + f'width: {Checker("width", "initial") >> style};'
                + f'font-style: {"italic" if Checker("italic") >> style else "initial"};'
                + f'line_distance: {Checker("line-height", "5px") >> style};'
                + f'text-decoration: {"underline" if Checker("underline") >> style else "initial"};'
            ).split(';')
        if hash is None:
            for i in range(len(strList)):
                if not (strList[i].endswith('px') or strList[i].endswith('initial')):
                    if  not (strList[i].startswith('text-align')
                        or strList[i].startswith('font-family')
                        or strList[i].startswith('font-style')
                        or strList[i].startswith('text-decoration')
                        or strList[i] == ''):
                        strList[i] += 'px'
            return 'style="' + ";".join([x for x in strList if not x.endswith('initial')]) + ''
        _ = (self.data 
            << '<style>' << END
            << f".{hash} " 
            << '{' << END << INDENT
            << ";\n\t".join([x for x in strList if not x.endswith('initial')])[:-1]
            << '}' << END
            << '</style>' << END
            )

    def add_footer(self, text):
        _ = self.data << f'<!-- {text} -->' << END
        return text

    def normalize(self) -> Message:
        ...

    def export(self, name: str, directory: str = './'):
        directory = os.path.abspath(directory)
        with open(directory + '/' + name + '.md', 'w+', encoding='utf-8') as file:
            file.write(self.__str__())

    def treeify(self) -> 'docTree':
        from nodoc import docNode
        from nodoc import docTree
        node = docNode(kind = 'title', content = '')
        node.level = -1
        uuid = uuid4()
        message = self.message
        tree = docTree(node, message, metadata=message['metadata'])
        node @ tree
        pipeline = message['pipeline']
        for order, unit in enumerate(pipeline):
            last_node: docNode = node
            node.order = order
            node: docNode = docNode(kind = unit['type'], content = unit['content'])
            match unit['type']:
                case 'text':
                    if last_node.isText:
                        self.message['pipeline'][node.order]['parent'] = uuid
                        (node & last_node) @ last_node.parent
                    elif last_node.isTitle:
                        node @ last_node

                case 'title':
                    node.level = unit['property']['level']
                    def bind_parent(nodeA: docNode, nodeB: docNode):
                        if nodeA.level == nodeB.level - 1:
                            self.message['pipeline'][nodeA.order]['parent'] = uuid
                            nodeA @ nodeB
                        elif nodeA.level == nodeB.level:
                            self.message['pipeline'][nodeA.order]['parent'] = uuid
                            nodeA @ nodeB.parent
                        elif nodeB.level == -1:
                            self.message['pipeline'][nodeA.order]['parent'] = uuid
                            nodeA @ nodeB
                        else:
                            bind_parent(nodeA, nodeB.parent)
                    if last_node.isText:
                        self.message['pipeline'][order]['parent'] = uuid
                        (node & last_node) @ last_node.parent
                    elif last_node.isTitle:
                        bind_parent(node, last_node)
            uuid = uuid4()
            self.message['pipeline'][order]['uuid'] = uuid
        return tree


    @staticmethod
    def transform(source: Document) -> 'Markdown':
        """
        静态方法，将任意受支持的文档类型转换为Markdown文档。
        - source: Document, 传入的文档。
        """
        document = Markdown.load_from_message(source.message)
        return document

    @staticmethod
    def load_from_message(message: Message) -> 'Markdown':
        """
        从消息中加载markdown。
        - message: Message, 传入的消息。
        """
        document: Markdown = Markdown(metadata=message['metadata'])
        document.message = message
        for unit in message['pipeline']:
            match unit['type']:
                case 'title':
                    if 'inherited' in unit['property']:
                        if isinstance(unit['property']['inherited'], str):
                            document.data << f'<span class="{unit["property"]["inherited"]}" style="'
                        else:
                            document.data << f'<span {document.add_fontStyle(unit["property"]["inherited"])}>'
                    else:
                        document.data << f'<span style="'
                    if True:
                        document.data << '">' << END
                    document.data << END
                    document.add_comment('title')
                    document.add_title(
                            Checker('content') >> unit, 
                            Checker('level') >> unit['property']
                        )
                    document.data << '</span>' << END
                case 'text':
                    if 'inherited' in unit['property']:
                        if isinstance(unit['property']['inherited'], str):
                            document.data << f'<span class="{unit["property"]}" style="'
                        else:
                            document.data << f'<span {document.add_fontStyle(unit["property"]["inherited"])}'
                    else:
                        document.data << f'<span style="'
                    if Checker('indent', None) >> unit['property'] is None:
                        document.data << '">' << END
                    else:
                        document.data << f"text-indent: {Checker('indent', 'initial') >> unit['property']}px" << '">' << END
                    document.data << END
                    document.add_comment('text')
                    document.add_text(
                        Checker('content') >> unit
                    )
                    document.data << '</span>' << END
                case 'latex':
                    if 'inherited' in unit['property']:
                        if isinstance(unit['property']['inherited'], str):
                            document.data << f'<span class="{unit["property"]}">' << END
                        else:
                            document.data << f'<span {document.add_fontStyle(unit["property"]["inherited"])}>' << END
                    else:
                        document.data << f'<span>' << END
                    document.data << END
                    _ = document.data << (Checker('content') >> unit)
                    document.data << '</span>' << END
                case 'image':
                    ...
                case 'header':
                    ...
                case 'footer':
                    ...
                case 'fontStyle':
                    ...
                
        return document


    @staticmethod
    def load(path: str) -> 'Markdown':
        with open(path, 'r+', encoding='utf-8') as file:
            text = file.read()
        return Markdown(text)

    def __document__(self):
        ...