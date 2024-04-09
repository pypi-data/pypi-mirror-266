from importlib.util import find_spec
from functools import lru_cache
from pathlib import Path
from datetime import datetime
from enum import Enum
from typing import Any, Literal
import cv2
import re
import os
import time
import pytesseract
from vloc.config.catalog import VL
from vloc.exception.catalog import AiDetectException, OcrException

if find_spec('vloc.plugin'):
    from vloc.plugin.__info__ import DetectInfo
else:
    from vloc.detect.__info__ import DetectInfo

if ALLURE_LOAD := find_spec('allure'):
    import allure


def ai_detect_not_exist(model: str,
                        label: Enum,
                        multi_num: bool | int = False,
                        delay_start: int = 1,
                        timeout: int = None,
                        show: bool = False) -> bool:

    time.sleep(delay_start)

    try:
        ai_detect(model=model,
                  label=label,
                  multi_num=multi_num,
                  timeout=timeout,
                  show=show)

    except AiDetectException:
        return True

    return False


def ai_detect_text(model: str,
                   label: Enum,
                   text: re.Pattern,
                   multi_num: Literal[True] | int = True,
                   search_only_first: bool = True,
                   segment: bool = False,
                   timeout: int = None,
                   show: bool = False) -> DetectInfo | list[DetectInfo]:

    text = [text] if type(text) is str else text

    detect_infos: list[DetectInfo] = ai_detect(model=model,
                                               label=label,
                                               multi_num=multi_num,
                                               timeout=timeout,
                                               show=show)
    parse_infos: list[DetectInfo] = []
    for txt in text:

        ocr_items = [setattr(info, 'ocr', __reocr(info.crop, txt, segment).group(0)) or info
                     if __reocr(info.crop, txt, segment) else None
                     for info in detect_infos]

        if all(item is None for item in ocr_items):
            raise OcrException(f'OCR not detect text:{txt} in label:{label}')

        if search_only_first:
            ocr_items = [next(item for item in ocr_items if item)]

        parse_infos += ocr_items

    return parse_infos[0] if len(parse_infos) == 1 else parse_infos


def ai_detect(model: str,
              label: Enum,
              multi_num: bool | int = False,
              sort_axis: Literal['y', 'x'] = 'y',
              timeout: int = None,
              show: bool = False) -> DetectInfo | list[DetectInfo]:

    time_stamp = datetime.now().strftime('%Y.%m.%d %H.%M.%S')
    temp_png = Path(VL.history_path).joinpath('temp.png').as_posix()

    match multi_num:
        case _ if multi_num <= 1 and type(multi_num) is int:
            raise ValueError('multi_num must be bool or greater than 1')
        case _ if multi_num > 1:
            max_det = multi_num if multi_num < 300 else 300
        case False:
            max_det = 1
        case True:
            max_det = VL.max_detect_num

    if not timeout:
        timeout = VL.timeout

    for times in range(timeout):
        name = f'[{label.name}] {time_stamp} retry {times}'
        VL.screenshot_method(temp_png)
        predict = VL.model[model].predict(source=temp_png,
                                          project=Path(VL.history_path).as_posix(),
                                          name=name,
                                          classes=label.value,
                                          max_det=max_det,
                                          conf=VL.conf_score,
                                          save=True,
                                          save_crop=True,
                                          show=show)

        os.remove(temp_png)
        check_predict = len(*[p.boxes.cls for p in predict])

        if check_predict:
            break
        else:
            time.sleep(timeout / timeout)

    if not check_predict:
        if ALLURE_LOAD:
            allure.attach.file(Path(VL.history_path).joinpath(f'{name}/temp.png').as_posix(), f'AI not detect {name}')
        raise AiDetectException(f'AI not detect label:{label}')

    if ALLURE_LOAD:
        allure.attach.file(Path(VL.history_path).joinpath(f'{name}/temp.png').as_posix(), name)

    crop_path = Path(VL.history_path).joinpath(f'{name}/crops/{label.name}').as_posix()
    crop_list = [f'{crop_path}/{item}' for item in os.listdir(crop_path)]
    crop_list = __magic_sort(crop_list)

    infos = __parse_ai_infos(label, predict, crop_list, sort_axis)
    return infos[0] if check_predict == 1 else infos


def __parse_ai_infos(label: Enum, predict: Any, crop_list: list, sort_axis: str) -> list:
    x_scale = VL.windows_size['width']/VL.device_resolution['width']
    y_scale = VL.windows_size['height']/VL.device_resolution['height']

    infos = [DetectInfo(label=label.__class__(int(index)).name,
                        x=int((x1+x2)/2*x_scale),
                        y=int((y1+y2)/2*y_scale),
                        conf=round(float(conf), 2),
                        crop=crop)

             for p in predict
             for index, (x1, y1, x2, y2), conf, crop in zip(p.boxes.cls,
                                                            p.boxes.xyxy,
                                                            p.boxes.conf,
                                                            crop_list)]

    infos = sorted(infos, key=lambda i: getattr(i, sort_axis))
    return infos


def __magic_sort(items: list) -> list:
    def convert(text): return int(text) if text.isdigit() else 0
    def custom_key(key): return [convert(i) for i in re.split('([0-9]+)', key)]
    return sorted(items, key=custom_key)


@lru_cache(maxsize=2)
def __reocr(path: str, search: re.Pattern, segment: bool) -> re.Match | None:
    config = '--psm 4' if segment else '--psm 7'
    img = cv2.imread(path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    txt = str(pytesseract.image_to_string(img, config=config)).replace('\n', '')
    txt = re.search(search, txt)
    return txt
