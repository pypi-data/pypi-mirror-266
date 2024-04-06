from typing import TypedDict, TypeAlias, Literal

ocrType: TypeAlias = Literal['text', 'title', 'header', 'reference', 'footer']

textRegion: TypeAlias = list[
    list[float, float],
    list[float, float],
    list[float, float],
    list[float, float],
]

bbox: TypeAlias = list[int, int, int, int]

class ocrResultElement(TypedDict):
    text: str
    confidence: float
    text_region: textRegion

ocrResult: TypeAlias = list[ocrResultElement]

class ocrDataElement(TypedDict):
    type: ocrType
    bbox: bbox
    res: ocrResult

ocrData: TypeAlias = list[ocrDataElement]