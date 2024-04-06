import abc
import time
from typing import Literal, Self, Union

from ._base import document_type
from ._base import Message
from ._base import Data
from ._base import Checker
from ._base import MessageInit
from ._base import MetaData
generalProperty = MessageInit.generalProperty
fontStyleProperty = MessageInit.fontStyleProperty

def __import():
    global docTree
    from nodoc import docTree




class Document(metaclass=abc.ABCMeta):

    def __init__(self, data: str = "", metadata: MetaData = None) -> None:
        if metadata is None:
            metadata = MetaData({
            'access': time.strftime("%Y-%m-%d %H-%M-%S"),
            'change': time.strftime("%Y-%m-%d %H-%M-%S"),
            'create': time.strftime("%Y-%m-%d %H-%M-%S"),
            'modify': time.strftime("%Y-%m-%d %H-%M-%S"),
            'custom': {},
            'filename': 'File',
        })
        self.__message: Message = self.normalize()
        self.__data: Data = Data(data)
        self.__metadata: MetaData = metadata

    @property
    def data(self) -> Data:
        return self.__data
    
    @property
    def metadata(self) -> MetaData:
        return self.__metadata

    @property
    def content(self) -> str:
        return self.__data.content

    @property
    def message(self) -> Message:
        return self.__message

    @message.setter
    def message(self, message: Message) -> None:
        self.__message = message

    @abc.abstractmethod
    def __document__(self):
        ...

    @abc.abstractmethod
    def normalize(self) -> Message:
        "文档标准化为消息。"

    @abc.abstractmethod
    def export(self, name: str, directory: str = './'):
        "文档的导出方法。"

    @staticmethod
    @abc.abstractmethod
    def load(path: str) -> 'Document':
        "文档的导入方法。"

    @staticmethod
    @abc.abstractmethod
    def load_from_message(message: Message) -> 'Document':
        """
        从消息中加载文档。
        - message: Message, 传入的消息。
        """

    @staticmethod
    def transform(source: 'Document', to: document_type) -> Union['Document', None]:

        match to:
            case 'markdown':
                from . import Markdown
                return Markdown.transform(source)
            # case 'html':
            #     from . import Html
            #     return Html.transform(source)
            # case 'pdf':
            #     from . import PDF
            #     return PDF.transform(source)
            # case 'word':
            #     from . import Word
            #     return Word.transform(source)
            # case 'ppt':
            #     from . import PPT
            #     return PPT.transform(source)
            # case 'excel':
            #     from . import Excel
            #     return Excel.transform(source)
        
    def treeify(self) -> 'docTree':
        """
        将文档树化。
        """

    def __lshift__(self, other):
        return self.__data << other

    def __str__(self) -> str:
        return self.__data.content
