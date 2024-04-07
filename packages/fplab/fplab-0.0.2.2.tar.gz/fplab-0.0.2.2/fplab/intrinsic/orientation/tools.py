"""
与指纹方向场有关的函数
average_orientation_nd              计算方向场的局部角度平均值
display_orientation                 展示方向场
quick_correctness_estimation        快速估计方向场可信度
compare_orientation_nd              比较方向场（无朝向）
"""
import gc
import torch
import numpy as np
import cv2
from scipy.ndimage import generic_filter
from fplab.tools.image import type_as
from fplab.tools.array import ima_pad_blk, ima_l2rgb, ima_pad_crop, ima_show, ima_save
from fplab.tools.tensor import imt_sum_average
from fplab.intrinsic.multiple.transform import get_coherence_filter_function


def average_orientation_nd(ot, blk_sz, s=(1, 1), keep_shape=True):
    """计算方向场每一个像素点周围像素的角度平均值。
    该函数以张量的形式处理图像，通过二维卷积实现角度平均值的计算
    这个函数期望的取值区间长度为pi，相差pi的两个方向视作一个方向
    函数名中的nd是no direction的缩写，表示方向与反方向视为同一方向"""
    if isinstance(blk_sz, int):
        ksp = blk_sz, blk_sz
    else:
        ksp = blk_sz
    if isinstance(s, int):
        sps = s, s
    else:
        sps = s
    ott = type_as(ot, md="t")
    cos2t = torch.cos(2*ott)
    cos2t = imt_sum_average(cos2t, ksp, s=sps, keep_shape=keep_shape)
    sin2t = torch.sin(2*ott)
    sin2t = imt_sum_average(sin2t, ksp, s=sps, keep_shape=keep_shape)
    out = 0.5*torch.atan2(sin2t, cos2t)
    out = type_as(out, ot)
    del ott, cos2t, sin2t
    gc.collect()
    return out


def display_orientation(im, ot, cd=None, blk_sz=(16, 16), md="m",
                        color=(255, 0, 0), thickness=1, tip_length=0.3,
                        flag=("show", "save", "return"), save_path=None):
    """在指纹图像im上画出方向场ot。
    该函数以数组的形式处理图像，将图像分成小块，并计算小块处的方向，以小块中心为起点绘制沿着该方向的线段
    im为指纹图像，可以为(h, w, 3)或(h, w)的数组，(1, h, w)或(3, h, w)的张量，
    ot为对应的方向场，可以为(h, w)的数组或(1, h, w)的张量，以弧度形式表示角度，
    cd为方向场置信度，可以为(h, w)的数组或(1, h, w)的张量，值为0，1之间的浮点数，控制方向向量的长度，
    当cd缺省时，则取与ot大小相同的全一数组
    blk_sz为展示方向场的块大小，可以为整数或2维向量
    md决定计算块方向的方法，"m"表示使用块所有方向的均值，"c"表示使用块中心处的方向
    color为三元元组，控制绘制线段的RGB值，默认为红色
    thickness为整数，控制绘制线段的宽度，默认为1
    tip_length为0，1之间的浮点数，控制箭头相对于线段的长度，默认为0.3
    flag控制函数的行为：展示结果图像（"show"）、保存结果图像（"save"）、返回结果图像（"return"）
    "save"命令需要配合save_path使用，若未指定save_path，则该命令将不会起作用"""
    if isinstance(blk_sz, int):
        ksp = blk_sz, blk_sz
    else:
        ksp = blk_sz
    # 方向线段将画到ima上
    ima = type_as(im, md="a")
    if ima.ndim == 2:
        ima = ima_l2rgb(ima)
    ima, ima_sp = ima_pad_blk(ima, ksp)
    # ota存放着每一点的方向
    ota = type_as(ot, md="a")
    ota = ima_pad_blk(ota, ksp)[0]
    if md == "m":
        ota = average_orientation_nd(ota, ksp, ksp)
    # ca是该点处方向的置信度，控制方向线段的长度
    if cd is None:
        ca = np.ones_like(ota)
    else:
        ca = type_as(cd, md="a")
    ca = ima_pad_blk(ca, ksp)[0]
    # max_l是方向线段的最大长度
    if isinstance(ksp, int):
        max_l = ksp//3
    else:
        max_l = ksp[0]//3 if ksp[0] < ksp[1] else ksp[1]//3
    # 计算每一个小块方向线段的起点和终点并绘制方向线段
    for i in np.arange((ksp[0]-1)/2, ota.shape[0], ksp[0]):
        if ksp[0] % 2 == 0:
            h = (int(np.floor(i)), int(np.ceil(i)))
        else:
            h = (int(i), int(i))
        for j in np.arange((ksp[1]-1)/2, ota.shape[1], ksp[1]):
            if ksp[1] % 2 == 0:
                w = (int(np.floor(j)), int(np.ceil(j)))
            else:
                w = (int(j), int(j))
            o = np.array([[ota[h[0], w[0]], ota[h[0], w[1]]], [ota[h[1], w[0]], ota[h[1], w[1]]]])
            o = np.arctan2(np.sin(o).sum(), np.cos(o).sum())
            c = np.array([[ca[h[0], w[0]], ca[h[0], w[1]]], [ca[h[1], w[0]], ca[h[1], w[1]]]])
            c = np.clip(c.sum()/4, 0, 1)
            start_h = h[0] if np.sin(o) > 0 else h[1]
            start_w = w[0] if np.cos(o) < 0 else w[1]
            end_h = round(start_h - np.sin(o) * c * max_l)
            end_w = round(start_w + np.cos(o) * c * max_l)
            cv2.arrowedLine(ima, (start_w, start_h), (end_w, end_h), color, thickness, tipLength=tip_length)
    out = ima_pad_crop(ima, ima_sp)
    del ima, ima_sp, ota, ca, max_l, i, j, h, w, o, c, start_h, start_w, end_h, end_w
    gc.collect()
    if "show" in flag:
        ima_show(out)
    if "save" in flag and save_path:
        ima_save(out, save_path)
    if "return" in flag:
        return type_as(out, im)


def quick_correctness_estimation(ot, ksz=(16, 16)):
    """快速获取方向场可信度
    ot          方向场
    ksz         估计可信度使用的窗口大小，整数或整数序列"""
    ft, filter_func = get_coherence_filter_function(ksz)
    ota = type_as(ot, "a")
    out = generic_filter(ota, filter_func, footprint=ft)
    return type_as(out, ot)


def compare_orientation_nd(ot1, ot2, oc=None):
    """比较两个无向方向场的相似度
    ot1, ot2        无向方向场，可以为数组或张量
    oc              方向场可信度或者mask，可以为数组或张量
    """
    ota1, ota2 = type_as(ot1, "a"), type_as(ot2, "a")
    if oc is None:
        oca = np.ones_like(ota1)
    else:
        oca = type_as(oc, "a")
    return ((np.cos(2*(ota1-ota2)))*oca).sum()/oca.sum()
