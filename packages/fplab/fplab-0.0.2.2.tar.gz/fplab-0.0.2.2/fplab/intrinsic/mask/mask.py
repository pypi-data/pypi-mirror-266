"""指纹mask相关函数，包括一些mask获取方法
orc2msk             基于方向场可信度获取mask"""
import numpy as np
from scipy.ndimage import binary_fill_holes, binary_opening, binary_closing
from fplab.tools.image import type_as


def orc2msk(oc, th_oc=0.95, md="o", itn=10):
    """基于方向场可信度oc获取指纹mask
    oc      指纹方向场可信度
    th_oc   可信度阈值，基于此阈值获取mask
    md      平滑mask使用开运算"o"还是闭运算"c"
    itn     对mask进行开运算次数
    """
    oca = type_as(oc, "a")
    mka = np.where(oca > th_oc, np.ones_like(oca), np.zeros_like(oca))
    mka = binary_fill_holes(mka)
    if md == "o":
        mka = binary_opening(mka, iterations=itn)
    else:
        mka = binary_closing(mka, iterations=itn)
    return type_as(mka, oc)
