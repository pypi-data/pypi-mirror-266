import os
import re
from pathlib import Path
from inspect import Parameter, currentframe, signature
from typing import Callable, Type
from PIL import Image
from ultralytics import YOLO


class __VLHorcrux(type):

    def __new__(cls, name, bases, namespace):

        horcrux = super().__new__(cls, name, bases, namespace)
        attrs = [attr for attr, value in namespace.items() if not value]

        def load(history_path: str,
                 device_resolution: dict,
                 windows_size: dict,
                 screenshot_method: Callable,
                 model_path: str,
                 max_detect_num: int,
                 conf_score: float,
                 timeout: int):

            for name, argument in signature(load).parameters.items():

                match argument.default:
                    case Parameter.empty:
                        value = locals()[name]
                    case _:
                        value = argument.default

                match name:
                    case 'history_path':
                        try:
                            os.makedirs(value)
                        except:
                            pass

                        if not Path(f'{value}/blank.png').is_file():
                            with Image.new('RGB', (128, 128)) as img:
                                img.save(f'{value}/blank.png')
                        setattr(horcrux, name, value)

                    case 'model_path':
                        pt_path = [dir.as_posix() for dir in Path(value).rglob('*.pt')]
                        pt_name = [(re.search(r'\/(\w+).pt', dir)).group(1) for dir in pt_path]
                        yolos = [YOLO(dir, task='detect') for dir in pt_path]
                        setattr(horcrux, 'model', dict(zip(pt_name, yolos)))

                    case _:
                        setattr(horcrux, name, value)

        def quit():
            for attr in attrs:
                setattr(horcrux, attr, None)

        funcs = {func: value for func, value in currentframe().f_locals.items()
                 if isinstance(value, Callable)
                 and not isinstance(value, Type)}

        for func, value in funcs.items():
            setattr(horcrux, func, value)

        return horcrux
