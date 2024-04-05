"""
与指纹频率场有关的函数
cal_origin_indices          计算旋转后的坐标的原坐标
cal_rotate_value            计算旋转后的灰度值
get_rotated_windows         旋转图像窗口
"""
import numpy as np
import gc
from fplab.tools.image import type_as
from fplab.tools.array import ima_pad_blk, ima_show, ima_save
from fplab.intrinsic.orientation.tools import average_orientation_nd
import typing


def cal_origin_indices(ind_h, ind_w, ag, md="c"):
    """计算逆时针旋转ag角度后的坐标(ind_h, ind_w)所对应的原坐标
    ind_h，ind_w为大小相同的数组或张量，对应元素分别为坐标的h坐标和w坐标，
    ag为旋转角度
    md决定旋转中心，"c"（图像中心）、"o"（图像左上角）
    返回的out_h，out_w形式与ind_h, ind_w相同，但是坐标值可能为负数或超出取值范围"""
    if md == "c":
        hm = ind_h.mean()
        wm = ind_w.mean()
    elif md == "o":
        hm = 0
        wm = 0
    else:
        raise Exception("Unknown mode!")
    ind_hn, ind_wn = ind_h-hm, ind_w-wm
    rad = ag/180*np.pi
    cos, sin = np.cos(rad), np.sin(rad)
    out_h = ind_hn*cos+ind_wn*sin+hm
    out_w = -ind_hn*sin+ind_wn*cos+wm
    del rad, cos, sin
    gc.collect()
    return out_h, out_w


def cal_rotate_value(ind_h, ind_w, ag, im, it_md="b", pad_md: typing.Any = "constant", **kwargs):
    """根据插值方法和填充方法计算旋转后给定坐标处的灰度值
    ind_h，ind_w为大小相同的数组，对应元素分别为坐标的h坐标和w坐标，
    ag为旋转角度，
    im为原图像，
    it_md为插值方法，支持："b"（双线性）、"n"（最近邻）
    pad_md为填充方法，可以为 'constant'，'edge'，'linear_ramp'，'maximum'，
    'mean'，'median'，'minimum'，'reflect'，'symmetric'，'wrap'，'empty' 或者自定义函数
    一些填充方法可能需要其他参数，可以通过**kwargs传递，具体可以参见numpy.pad
    比如对于"constant"，可以使用constant_values参数控制填充值，具体可以参见numpy.pad
    """
    # 计算给定坐标对应的旋转前的原始坐标
    if isinstance(ind_h, np.ndarray) and isinstance(ind_w, np.ndarray):
        pass
    else:
        raise Exception("ind_h and ind_w must be numpy.ndarray!")
    origin_h, origin_w = cal_origin_indices(ind_h, ind_w, ag)
    # 计算与原始坐标最相近的至多四个点
    neighbor_h_f, neighbor_h_c = np.floor(origin_h), np.ceil(origin_h)
    neighbor_w_f, neighbor_w_c = np.floor(origin_w), np.ceil(origin_w)
    # 计算左上点与右下点以及原始坐标与这右下点在两个方向上的距离
    dh_cf, dh_co = neighbor_h_c-neighbor_h_f, neighbor_h_c-origin_h
    dw_cf, dw_co = neighbor_w_c-neighbor_w_f, neighbor_w_c-origin_w
    # 根据距离计算插值权重，四个权重分别对应左上点、左下点、右上点、右下点
    w_h_co = np.where(dh_cf, dh_co, 0.5*np.ones_like(dh_co))
    w_w_co = np.where(dw_cf, dw_co, 0.5*np.ones_like(dw_co))
    if it_md == "b":
        w00 = w_h_co*w_w_co
        w10 = (1-w_h_co)*w_w_co
        w01 = w_h_co*(1-w_w_co)
        w11 = (1-w_h_co)*(1-w_w_co)
    elif it_md == "n":
        w00 = np.where((w_h_co > 0.5) & (w_w_co > 0.5), np.ones_like(w_h_co), np.zeros_like(w_h_co))
        w10 = np.where((w_h_co <= 0.5) & (w_w_co > 0.5), np.ones_like(w_h_co), np.zeros_like(w_h_co))
        w01 = np.where((w_w_co <= 0.5) & (w_h_co > 0.5), np.ones_like(w_h_co), np.zeros_like(w_h_co))
        w11 = np.where((w_h_co <= 0.5) & (w_w_co <= 0.5), np.ones_like(w_h_co), np.zeros_like(w_h_co))
    else:
        raise Exception("Unknown interpolation mode!")
    del origin_h, origin_w, dh_cf, dh_co, dw_cf, dw_co, w_h_co, w_w_co
    gc.collect()
    # 根据四个点坐标范围填补图像
    ima = type_as(im, md="a")
    h_min, h_max = neighbor_h_f.min(), neighbor_h_c.max()
    w_min, w_max = neighbor_w_f.min(), neighbor_w_c.max()
    pad_h0 = -1*h_min if h_min < 0 else 0
    pad_h1 = h_max-ima.shape[0]+1 if h_max > ima.shape[0]-1 else 0
    pad_w0 = -1*w_min if w_min < 0 else 0
    pad_w1 = w_max-ima.shape[1]+1 if w_max > ima.shape[1]-1 else 0
    if len(ima.shape) == 2:
        pad_width = np.array(((pad_h0, pad_h1), (pad_w0, pad_w1)), dtype=np.int32)
    elif len(ima.shape) == 3:
        pad_width = np.array(((pad_h0, pad_h1), (pad_w0, pad_w1), (0, 0)), dtype=np.int32)
    else:
        raise Exception("The number of dimension of im must be 2 or 3!")
    ima = np.pad(ima, pad_width, mode=pad_md, **kwargs)
    # 填补图像后调整坐标范围，通过插值获取各点像素值
    neighbor_h_f, neighbor_h_c = neighbor_h_f+pad_h0, neighbor_h_c+pad_h0
    neighbor_w_f, neighbor_w_c = neighbor_w_f+pad_w0, neighbor_w_c+pad_w0
    neighbor_h_f, neighbor_h_c = neighbor_h_f.astype(np.int32), neighbor_h_c.astype(np.int32)
    neighbor_w_f, neighbor_w_c = neighbor_w_f.astype(np.int32), neighbor_w_c.astype(np.int32)
    del h_min, h_max, w_min, w_max, pad_h0, pad_h1, pad_w0, pad_w1, pad_width
    gc.collect()
    if len(ima.shape) == 2:
        f00 = ima[neighbor_h_f, neighbor_w_f]
        f01 = ima[neighbor_h_f, neighbor_w_c]
        f10 = ima[neighbor_h_c, neighbor_w_f]
        f11 = ima[neighbor_h_c, neighbor_w_c]
    elif len(ima.shape) == 3:
        f00 = ima[neighbor_h_f, neighbor_w_f, :]
        f01 = ima[neighbor_h_f, neighbor_w_c, :]
        f10 = ima[neighbor_h_c, neighbor_w_f, :]
        f11 = ima[neighbor_h_c, neighbor_w_c, :]
    else:
        raise Exception("The number of dimension of im must be 2 or 3!")
    out = w00*f00 + w01*f01 + w10*f10 + w11*f11
    del neighbor_h_f, neighbor_h_c, neighbor_w_f, neighbor_w_c, ima
    del w00, w10, w01, w11, f00, f01, f10, f11
    return type_as(out, im)


def get_rotated_windows(im, ot, blk_sz=(16, 16), wd_sz=(32, 48), average_flag=True,
                        it_md="b", pad_md: typing.Any = "constant", pad_v=1.,
                        flag=("show", "save", "return"), save_path=None, **kwargs):
    """根据给定角度旋转图像块所在窗口。
    im是原始图像，
    ot是给定的旋转角度，每个窗口旋转角度由所在图像块的角度决定，
    blk_sz是图像块大小，
    wd_sz是旋转窗口大小，
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
    # ima是原始图像
    ima = type_as(im, md="a")
    ima = ima_pad_blk(ima, ksp)[0]
    # ota存放着每一点的方向
    ota = type_as(ot, md="a")
    ota = ima_pad_blk(ota, ksp)[0]
    if average_flag:
        # 经过角度平均之后，虽然ota的大小不变，但是每个图像块的元素值都是相同的
        ota = average_orientation_nd(ota, ksp, ksp)
    ha = np.arange((ksp[0]-1)/2, ota.shape[0], ksp[0])
    wa = np.arange((ksp[1]-1)/2, ota.shape[1], ksp[1])
    blk_n_h, blk_n_w = len(ha), len(wa)
    if len(ima.shape) == 3:
        out = np.zeros((int(blk_n_h*wd_sz[0]), int(blk_n_w*wd_sz[1]), 3))
        for i in range(blk_n_h):
            # 选取图像块中心的两个h
            h = (int(np.floor(ha[i])), int(np.ceil(ha[i])))
            for j in range(blk_n_w):
                # 选取图像块中心的两个w
                w = (int(np.floor(wa[j])), int(np.ceil(wa[j])))
                # 计算旋转角度
                o = np.array([[ota[h[0], w[0]], ota[h[0], w[1]]], [ota[h[1], w[0]], ota[h[1], w[1]]]])
                o = np.arctan2(np.sin(o).sum(), np.cos(o).sum())
                o = 90 - o / np.pi * 180
                start_h, start_w = int(h[0] - (wsp[0] - 1) // 2), int(w[0] - (wsp[1] - 1) // 2)
                end_h, end_w = int(h[0] + wsp[0] - (wsp[0] - 1) // 2), int(w[0] + wsp[1] - (wsp[1] - 1) // 2)
                ind_h, ind_w = np.mgrid[start_h:end_h, start_w:end_w]
                wd = cal_rotate_value(ind_h, ind_w, o, ima, it_md=it_md,
                                      pad_md=pad_md, constant_values=pad_v, **kwargs)
                out[int(i*wd_sz[0]):int((i+1)*wd_sz[0]), int(j*wd_sz[1]):int((j+1)*wd_sz[1]), :] = wd
    elif len(ima.shape) == 2:
        out = np.zeros((int(blk_n_h*wd_sz[0]), int(blk_n_w*wd_sz[1])))
        for i in range(blk_n_h):
            # 选取图像块中心的两个h
            h = (int(np.floor(ha[i])), int(np.ceil(ha[i])))
            for j in range(blk_n_w):
                # 选取图像块中心的两个w
                w = (int(np.floor(wa[j])), int(np.ceil(wa[j])))
                # 计算旋转角度
                o = np.array([[ota[h[0], w[0]], ota[h[0], w[1]]], [ota[h[1], w[0]], ota[h[1], w[1]]]])
                o = np.arctan2(np.sin(o).sum(), np.cos(o).sum())
                o = 90 - o / np.pi * 180
                start_h, start_w = int(h[0] - (wsp[0] - 1) // 2), int(w[0] - (wsp[1] - 1) // 2)
                end_h, end_w = int(h[0] + wsp[0] - (wsp[0] - 1) // 2), int(w[0] + wsp[1] - (wsp[1] - 1) // 2)
                ind_h, ind_w = np.mgrid[start_h:end_h, start_w:end_w]
                wd = cal_rotate_value(ind_h, ind_w, o, ima, it_md=it_md,
                                      pad_md=pad_md, constant_values=pad_v, **kwargs)
                out[int(i * wd_sz[0]):int((i + 1) * wd_sz[0]), int(j * wd_sz[1]):int((j + 1) * wd_sz[1])] = wd
    else:
        raise Exception("The number of dimension of im must be 2 or 3!")
    del ksp, wsp, ima, ota, ha, wa, blk_n_h, blk_n_w, i, j, h, w, o, start_h, start_w, end_h, end_w, ind_h, ind_w, wd
    gc.collect()
    if "show" in flag:
        ima_show(out)
    if "save" in flag and save_path:
        ima_save(out, save_path)
    if "return" in flag:
        return type_as(out, im)
