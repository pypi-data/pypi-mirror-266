from ..post_processing import ocrData
from . import Message
from . import Checker

"""
A special program which processing the last flow.
"""

def parse(data: ocrData) -> Message:
    """
    Parse the message from the last flow.
    - data: ocrData,  used to parse to normal message.
    """
    final_info: list[tuple[str, float, float]] = []
    # 解码内容，左右总字符距，上下字符距
    message: Message = {
        "metadata": None,
        "pipeline": []
    }
    fontSizes = set([
        unit['text_region'][2][1] - unit['text_region'][0][1] 
        for element in data 
        for unit in element['res']
        if element['type'] == 'title'
    ])
    fontSizes = list(fontSizes)
    fontSizes.sort()
    for element in data:
        if element['type'] == 'figure': 
            continue
        for unit in element['res']:
            if element['type'] == 'text':

                fontHeight: str = unit['text_region'][2][1] - unit['text_region'][0][1] # 字符高度
                textWidth: str = unit['text_region'][2][0] - unit['text_region'][0][0]  # 文本宽度
                indent: float = unit['text_region'][0][0] - element['bbox'][0]          # 字符缩进（像素）
                tailIndent: float = unit['text_region'][0][0] - element['bbox'][0]      # 文本尾部内边距（像素）
                content: str = u"" + unit['text']                                       # 内容
                charCount = len(content)
                message['pipeline'].append({
                    'type': element['type'],
                    'property': {
                        'indent':  indent,
                        'inherited': {
                            'font_size': fontHeight,
                            'font_distance': textWidth / charCount - fontHeight,
                            'position': [
                                unit['text_region'][0][0], unit['text_region'][2][0],
                            ],
                            'width': textWidth,
                            'height': fontHeight
                        }
                    },
                    'content': content
                })

            elif element['type'] == 'title':

                fontHeight: str = unit['text_region'][2][1] - unit['text_region'][0][1] # 字符高度
                textWidth: str = unit['text_region'][2][0] - unit['text_region'][0][0]  # 文本宽度
                indent: float = unit['text_region'][0][0] - element['bbox'][0]          # 字符缩进（像素）
                tailIndent: float = unit['text_region'][0][0] - element['bbox'][0]      # 文本尾部内边距（像素）
                content: str = u"" + unit['text']                                       # 内容
                charCount = len(content)
                message['pipeline'].append({
                    'type': element['type'],
                    'property': {
                        'inherited': {
                            'font_size': fontHeight,
                            'font_distance': textWidth / charCount - fontHeight,
                            'position': [
                                unit['text_region'][0][0], unit['text_region'][2][0],
                            ],
                            'width': textWidth,
                            'height': fontHeight
                        },
                        'level': fontSizes.index(fontHeight) + 1
                    },
                    'content': content,
                })
    return message
