import uiautomation

from .tdObject import tdElement


class LocatorWindows():
    timeout: int
	
    @staticmethod
    def findElement(selectorString: str = None, fromElement: tdElement | uiautomation.Control = None, timeout: int = None) -> tdElement: ...