"""指纹骨架相关函数，包括一些骨架获取方法
basic           基本的骨架获取方法"""

import cv2
import numpy as np
from fplab.tools.image import type_as
from fplab.tools.array import IMA
from fplab.intrinsic.orientation.gradient import rao1990
from fplab.intrinsic.mask.mask import orc2msk


def basic(im, mk=None, th=None, th_w=1.1, connect_n=20):
    """基本的骨架获取方法
    im          需要提取骨架的图像
    mk          图像的mask，默认使用rao1990返回的方向场可信度获取
    th          二值化图像阈值，默认使用mask=1处像素的均值
    th_w        通过均值获取的阈值乘以该系数后才为最后的阈值
    connect_n   连通分支最小像素数
    注意，默认情况下，该函数的输入的背景的像素值为1而指纹脊像素值为0，
    经过二值化后背景像素为0而指纹脊像素为1。"""
    ima = type_as(im, "a")
    if mk is None:
        mka = orc2msk(rao1990(ima, (16, 16))[1])
    else:
        mka = type_as(mk, "a")
    if isinstance(th, (int, float)):
        th_v = th
    else:
        th_v = ima[mka].mean()*th_w
    # 二值化
    ima_bin = mka*np.where(ima > th_v, np.zeros_like(ima), np.ones_like(ima))
    ima_bin = IMA(ima_bin).float2uint().ima
    # 细化
    ima_thin = cv2.ximgproc.thinning(ima_bin, thinningType=cv2.ximgproc.THINNING_GUOHALL)
    # 去除小连通区域
    comp_n, labels = cv2.connectedComponents(ima_thin, connectivity=8)
    temp_a = np.ones_like(ima_thin)
    for i in range(comp_n):
        if temp_a[labels == i].sum() <= connect_n:
            ima_thin[labels == i] = 0
    out = IMA(ima_thin).uint2float().ima
    return type_as(out, im)
