from typing import Dict

import uiautomation


class tdElement:
    _element: uiautomation.Control

    isTopLevel: bool
    properties: Dict[str,str]

    @property
    def isExists(self) -> bool : ...
    @property
    def text(self) -> str : ...
