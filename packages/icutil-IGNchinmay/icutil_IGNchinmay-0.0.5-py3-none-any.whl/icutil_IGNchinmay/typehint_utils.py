""" Type hints
 Make you have set vscode with settings changed from off to basic or strict,
 "python.analysis.typeCheckingMode": "basic"
 Check: demo(1) below should show type error
"""

from typing import Dict, List, TypeVar, Union, Optional
import numpy as np
from numpy.typing import NDArray

Mat = NDArray[np.uint8]  # n channel image

T = TypeVar("T", str, int)

# Labelme contour (list of points)
CntrL = Optional[List[List[Union[float, int]]]]  # labelme contour: [[x,y],]

# CV2 contour (list of list of points)
CntrC = Optional[Union[List[List[List[Union[int, float]]]], List[np.ndarray]]]
# CntrC = Optional[List[List[Union[int, float]]]]  # cv2 contour: [[[x,y]],]'

Cntr = Union[CntrL, CntrC]

# CntrL = Optional[Sequence[Tuple[Union[int, float], Union[int, float]]]]
# CntrC = Optional[Sequence[Tuple[Tuple[Union[int, float], Union[int, float]]]]]


if __name__ == "__main__":

    def demo(bar1: List[str]):
        """type hint example function"""
        print(bar1)

    def demo_cntrl(
        k: T,
        a: CntrL,
    ) -> Dict:
        """type hint example of contours"""
        return {"a": a, "k": k}

    def demo_cntrc(
        k: T,
        a: CntrC,
    ) -> Dict:
        """type hint example of contours"""
        return {"a": a, "k": k}

    def my_fun(img: Mat):
        """cv2 image typehint demo"""
        return img

    def optional_demo(i: Optional[int] = None) -> None:
        """optional example"""
        print("i=", i)

    def my_function(x: Optional[int] = None) -> None:
        """my func"""
        if x is None:
            print("x is None")
        else:
            print(x)

    demo(["hello"])
    # demo(1)
    res = demo_cntrl(1, [[1, 2], [1, 2]])
    res = demo_cntrc(1, [[[1, 2.1]], [[1, 2]]])
