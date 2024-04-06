import uiautomation

from .tdObject import tdElement


class LocatorWindows():
    timeout: int  = None
	
    @staticmethod
    def findElement(selectorString: str = None, fromElement: tdElement | uiautomation.Control = None, timeout: int = None) -> tdElement: ...