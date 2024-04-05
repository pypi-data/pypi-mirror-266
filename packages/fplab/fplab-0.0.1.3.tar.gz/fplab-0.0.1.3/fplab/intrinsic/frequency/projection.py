"""
基于投影的指纹频率场估计方法
这里预先假设指纹为灰度图或二值图，不能保证函数在RGB图像的适用性
"""
import numpy as np
import gc
from fplab.tools.image import type_as
from fplab.tools.array import ima_pad_blk, ima_show, ima_save, ima_gaussian, ima_pad_crop
from fplab.intrinsic.orientation.tools import average_orientation_nd
from fplab.intrinsic.frequency.tools import cal_rotate_value
import typing
from scipy.ndimage import minimum_filter1d


def hong1998(im, ot, mk=None, blk_sz=(16, 16), wd_sz=(32, 48), min_sz=5, sm_sz=(7, 7),
             average_flag=True, freq_m=(1/25, 1/3),
             it_md="b", pad_md: typing.Any = "constant", pad_v=1.,
             flag=("show", "save", "return"), save_path=None, **kwargs):
    """计算指纹的频率场，基于Hong1998年提出的方法。
    im是原始图像，
    ot是给定的旋转角度，每个窗口旋转角度由所在图像块的角度决定，
    mk是指纹区域图，值为1为指纹，值为0则为背景，
    blk_sz是图像块大小，
    wd_sz是旋转窗口大小，
    min_sz是检测峰谷时的最小值滤波大小，
    sm_sz是频率插值时的平滑滤波大小，
    average_flag控制是否需要求取图像块角度的均值作为旋转角度（否则取图像块中心角度）
    it_md为插值方法，支持："b"（双线性）、"n"（最近邻）
    pad_md为填充方法，可以为 'constant'，'edge'，'linear_ramp'，'maximum'，
    'mean'，'median'，'minimum'，'reflect'，'symmetric'，'wrap'，'empty' 或者自定义函数
    pad_v为"constant"方法的填充值，
    一些填充方法可能需要其他参数，可以通过**kwargs传递，具体可以参见numpy.pad
    比如对于"constant"，可以使用constant_values参数控制填充值，具体可以参见numpy.pad
    flag控制函数的行为：展示结果图像（"show"）、保存结果图像（"save"）、返回结果图像（"return"），
    "save"命令需要配合save_path使用，若未指定save_path，则该命令将不会起作用"""
    if isinstance(blk_sz, int):
        ksp = blk_sz, blk_sz
    else:
        ksp = blk_sz
    if isinstance(wd_sz, int):
        wsp = wd_sz, wd_sz
    else:
        wsp = wd_sz
    if isinstance(sm_sz, int):
        gsp = sm_sz, sm_sz
    else:
        gsp = sm_sz
    # ima是原始图像
    ima = type_as(im, md="a")
    ima, im_sp = ima_pad_blk(ima, ksp)
    # ota存放着每一点的方向
    ota = type_as(ot, md="a")
    ota = ima_pad_blk(ota, ksp)[0]
    # mka标记指纹区域
    if mk is None:
        mka = np.ones_like(ota)
    else:
        mka = type_as(mk, md="a")
        mka = ima_pad_blk(mka, ksp)[0]
    if average_flag:
        # 经过角度平均之后，虽然ota的大小不变，但是每个图像块的元素值都是相同的
        ota = average_orientation_nd(ota, ksp, ksp)
    ha = np.arange((ksp[0]-1)/2, ota.shape[0], ksp[0])
    wa = np.arange((ksp[1]-1)/2, ota.shape[1], ksp[1])
    blk_n_h, blk_n_w = len(ha), len(wa)
    freq = np.zeros((int(blk_n_h), int(blk_n_w)))
    mask = np.zeros((int(blk_n_h), int(blk_n_w)))
    for i in range(blk_n_h):
        # 选取图像块中心的两个h
        h = (int(np.floor(ha[i])), int(np.ceil(ha[i])))
        for j in range(blk_n_w):
            # 选取图像块中心的两个w
            w = (int(np.floor(wa[j])), int(np.ceil(wa[j])))
            # 该区域如果不存在指纹，则直接跳过
            mask[i, j] = mka[i*ksp[0]:(i+1)*ksp[0], j*ksp[1]:(j+1)*ksp[1]].max()
            if mask[i, j] == 0:
                freq[i, j] = 0
                continue
            # 计算旋转角度
            o = np.array([[ota[h[0], w[0]], ota[h[0], w[1]]], [ota[h[1], w[0]], ota[h[1], w[1]]]])
            o = np.arctan2(np.sin(o).sum(), np.cos(o).sum())
            o = 90-o/np.pi*180
            start_h, start_w = int(h[0]-(wsp[0]-1)//2), int(w[0]-(wsp[1]-1)//2)
            end_h, end_w = int(h[0]+wsp[0]-(wsp[0]-1)//2), int(w[0]+wsp[1]-(wsp[1]-1)//2)
            ind_h, ind_w = np.mgrid[start_h:end_h, start_w:end_w]
            wd = cal_rotate_value(ind_h, ind_w, o, ima, it_md=it_md,
                                  pad_md=pad_md, constant_values=pad_v, **kwargs)
            # 获得该窗口的投影
            projection = wd.mean(axis=0)
            # 获得每一点处的局部最小值
            minimum = minimum_filter1d(projection, min_sz)
            # 获得投影的均值
            average = projection.mean()
            # 获得每一点处的相对强度
            difference = projection - minimum
            # 峰谷处的投影强度应小于投影均值，且相对强度小于0.05
            position = ((projection < average) & (difference < 0.05)).nonzero()[0]
            if position.size < 1:
                freq[i, j] = 0
                continue
            # 检测峰谷的左边缘和右边缘
            position_r, position_l = np.zeros_like(position), np.zeros_like(position)
            position_r[1:], position_l[:-1] = position[:-1].copy(), position[1:].copy()
            position_r[0], position_l[-1] = -1, projection.size
            edge_l = np.where((position - position_r) > 3)[0]
            edge_r = np.where((position_l - position) > 3)[0]
            # 将左边缘和右边缘对准
            if edge_l.size > edge_r.size:
                edge_l = edge_l[:-1]
            elif edge_l.size < edge_r.size:
                edge_r = edge_r[1:]
            else:
                if edge_r.size == 0 and edge_l.size == 0:
                    freq[i, j] = 0
                    continue
                if edge_r[0] + 1 == edge_l[0]:
                    edge_l = edge_l[:-1]
                    edge_r = edge_r[1:]
            # 计算峰谷位置并估计频率
            peak = (position[edge_l]+position[edge_r])/2
            if peak.size < 2:
                # 峰谷数目过少结果无效
                freq[i, j] = -1
            else:
                if freq_m[0] < (peak.size-1)/(peak[-1]-peak[0]) < freq_m[1]:
                    freq[i, j] = (peak.size-1)/(peak[-1]-peak[0])
                else:
                    # 频率不在正常范围内结果无效
                    freq[i, j] = -1
            del o, start_h, start_w, end_h, end_w, ind_h, ind_w, wd,
            del projection, minimum, average, difference
            del position, position_r, position_l, edge_r, edge_l, peak
            gc.collect()
    del wsp, ima, ota, mka, ha, wa, blk_n_h, blk_n_w, i, j, h, w
    gc.collect()
    # 对无效的频率进行插值
    while freq.min() < 0:
        ind_mu = np.where(freq > 0, freq, np.zeros_like(freq))
        ind_delta = np.where(freq+1 > 0, np.ones_like(freq), np.zeros_like(freq))
        numerator = ima_gaussian(ind_mu, gsp)
        denominator = ima_gaussian(ind_delta, gsp)
        numerator = np.where(denominator > 0, numerator, -1*np.ones_like(numerator))
        denominator = np.where(denominator > 0, denominator, np.ones_like(denominator))
        freq = mask*(numerator/denominator)
    out = freq.repeat(ksp[0], axis=0).repeat(ksp[1], axis=1)
    out = ima_pad_crop(out, im_sp)
    del ind_mu, ind_delta, numerator, denominator, freq, ksp, gsp, im_sp
    if "show" in flag:
        ima_show(out)
    if "save" in flag and save_path:
        ima_save(out, save_path)
    if "return" in flag:
        return type_as(out, im)
