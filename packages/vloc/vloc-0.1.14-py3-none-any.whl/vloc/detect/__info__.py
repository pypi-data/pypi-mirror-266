from dataclasses import dataclass


@dataclass
class DetectInfo:
    x: int
    y: int
    label: str
    conf: float
    crop: str
    ocr: str = None
