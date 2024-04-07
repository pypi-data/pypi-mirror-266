"""
基于变换的多目标估计方法
这里预先假设指纹为灰度图或二值图，不能保证函数在RGB图像的适用性
"""
import numpy as np
from fplab.tools.image import type_as
from fplab.tools.array import ima_minmax, ima_pad_blk, ima_pad_crop, ima_rgb2l, ima_gaussian
from fplab.tools.array import ima_float2uint, ima_uint2float
from scipy import fft, ndimage
import cv2
import gc


def get_cartesian_function(out_sp, min_v, max_v, c):
    """该函数根据参数计算两个向量，同时定义一个转换函数。
    两个向量表示采样点在极坐标系下的极径和极角取值，各个分量一一组合就可以得到所有可能的采样点，
    转换函数用于scipy.ndimage.geometric_transform，用于获得采样点的笛卡尔坐标。
    out_sp，极径和极角取值个数
    min_v、max_v控制极径和极角的取值范围，[min_v, max_v)
    c，比例系数，获得的笛卡尔坐标将与该系数向量相乘，以获得与真实数据对应的结果"""
    r = np.linspace(min_v[0], max_v[0], out_sp[0], endpoint=False)
    theta = np.linspace(min_v[1], max_v[1], out_sp[1], endpoint=False)
    out = r[:, None]*np.cos(theta[None, :])*c[0], r[:, None]*np.sin(theta[None, :])*c[1]

    def transform_function(rt_ind):
        """rt_ind，采样点索引，第一个分量表示极径索引，第二个分量表示极角索引"""
        return out[0][rt_ind[0], rt_ind[1]], out[1][rt_ind[0], rt_ind[1]]

    return r, theta, transform_function


def get_coherence_filter_function(ksp, c_ind=None):
    """获取用于scipy.ndimage.generic_filter的自定义滤波函数，
    ksp可以为整数，二维整数元组或numpy.ndarray，用于指定邻域元素
    c_ind是待处理元素索引，默认取待处理元素的中心位置"""
    if isinstance(ksp, int):
        n = ksp*ksp
        f = np.ones((ksp, ksp))
    elif isinstance(ksp, (list, tuple)):
        n = ksp[0]*ksp[1]
        f = np.ones((ksp[0], ksp[1]))
    else:
        n = (ksp.nonzero()[0]).size
        f = ksp.copy()
    if c_ind is None:
        ind = n-n//2
    else:
        ind = c_ind

    def filter_function(in_elements):
        """in_elements是待处理元素及其邻域元素"""
        # 这里角度乘2是考虑到方向场的取值范围为Pi
        out = (np.cos(2*(in_elements-in_elements[ind])).sum()/n+1)/2
        return out

    return f, filter_function


def chikkerur2007(im, blk_sz=(8, 8), wd_sz=(32, 32), smo_sz=(3, 3), smf_sz=(3, 3), smo_itn=1, smf_itn=1, win_c=5):
    """使用2007年chikkerur使用的方法(STFT)分析指纹，输出方向场、频率场、感兴趣区域和方向置信度。
    im是需要处理的指纹图像，RGB图会被转化为灰度图
    blk_sz是图像块大小，可以为整数或2维向量，每个图像块估计一次方向作为块内所有像素的方向。
    wd_sz是傅里叶变换的窗口大小，可以为整数或2维向量。
    smo_sz和smf_sz分别是平滑方向场和频率场使用的滤波核大小，
    smo_itn和smf_itn控制滤波核迭代次数（文章中认为使用小滤波器多次平滑的效果要比大滤波器好）
    win_c控制计算方向场置信度时使用的窗口，可以为整数、整数元组或numpy.ndarray"""
    # 处理输入参数
    if isinstance(blk_sz, int):
        ksp = blk_sz, blk_sz
    else:
        ksp = blk_sz
    if isinstance(wd_sz, int):
        wsp = wd_sz, wd_sz
    else:
        wsp = wd_sz
    if isinstance(smo_sz, int):
        so_sp = smo_sz, smo_sz
    else:
        so_sp = smo_sz
    if isinstance(smf_sz, int):
        sf_sp = smf_sz, smf_sz
    else:
        sf_sp = smf_sz
    # ima 待处理的图像
    ima = type_as(im, md="a")
    ima = ima_rgb2l(ima)
    ima = ima_minmax(ima)
    ima, im_sp = ima_pad_blk(ima, ksp)
    # ima_pad 填充后的图像，便于窗口选取
    pad_sp = ima.shape[0]+wsp[0]-ksp[0], ima.shape[1]+wsp[1]-ksp[1]
    ima_pad = ima_pad_crop(ima, pad_sp)
    # ha, wa 图像块的中心
    ha = np.arange((ksp[0]-1)//2, ima.shape[0], ksp[0])
    wa = np.arange((ksp[1]-1)//2, ima.shape[1], ksp[1])
    # wd_h0, wd_w0 窗口左上角坐标
    wd_h0 = ha-(wsp[0]-1)//2 + wsp[0]-ksp[0]-(wsp[0]-ksp[0])//2
    wd_w0 = wa-(wsp[1]-1)//2 + wsp[1]-ksp[1]-(wsp[1]-ksp[1])//2
    # 极径和极角取值，转化函数
    r, t, transform_func = get_cartesian_function(wsp, min_v=(0, -np.pi/2), max_v=(np.sqrt(2)/2, np.pi/2), c=wsp)
    # 方向场，频率场，指纹区域
    out_o, out_f, out_m = np.zeros((len(ha), len(wa))), np.zeros((len(ha), len(wa))), np.zeros((len(ha), len(wa)))
    for i in range(len(ha)):
        for j in range(len(wa)):
            wd = ima_pad[wd_h0[i]:wd_h0[i]+wsp[0], wd_w0[j]:wd_w0[j]+wsp[1]]
            f_uv = fft.fft2(wd-wd.mean())
            f_rt = np.abs(ndimage.geometric_transform(f_uv, transform_func, output_shape=wsp, mode='grid-wrap'))
            p_rt = f_rt**2/((f_rt**2).sum()+1e-8)
            p_r, p_t = p_rt.sum(1), p_rt.sum(0)
            out_o[i, j] = np.arctan2((p_t*np.sin(2*t)).sum(), (p_t*np.cos(2*t)).sum())/2
            out_f[i, j] = (p_r*r).sum()
            out_m[i, j] = np.log((f_rt**2+1e-8).sum()+1e-8)
    # 方向场平滑
    sin, cos = np.sin(2*out_o), np.cos(2*out_o)
    for _ in range(smo_itn):
        sin = ima_gaussian(sin, so_sp)
        cos = ima_gaussian(cos, so_sp)
    out_o = np.arctan2(sin, cos)/2
    # 频率场平滑
    fi = np.where((out_f < 1 / 3) & (out_f > 1 / 25), np.ones_like(out_f), np.zeros_like(out_f))
    for _ in range(smf_itn):
        out_f = ima_gaussian(out_f*fi, sf_sp)/(ima_gaussian(fi, sf_sp)+1e-8)
        fi = np.where((out_f < 1 / 3) & (out_f > 1 / 25), np.ones_like(out_f), np.zeros_like(out_f))
    # 指纹区域分割（Otsu's算法）
    out_m = ima_float2uint(ima_minmax(out_m))
    out_m = cv2.threshold(out_m, 0, 255, cv2.THRESH_OTSU)[1]
    out_m = ima_uint2float(out_m)
    # 方向场置信度
    ft, filter_func = get_coherence_filter_function(win_c)
    out_c = ndimage.generic_filter(out_o, filter_func, footprint=ft)
    # 处理输出
    out_o = out_o.repeat(ksp[0], axis=0).repeat(ksp[1], axis=1)
    out_o = ima_pad_crop(out_o, im_sp)
    out_o = type_as(out_o, im)
    out_f = out_f.repeat(ksp[0], axis=0).repeat(ksp[1], axis=1)
    out_f = ima_pad_crop(out_f, im_sp)
    out_f = type_as(out_f, im)
    out_m = out_m.repeat(ksp[0], axis=0).repeat(ksp[1], axis=1)
    out_m = ima_pad_crop(out_m, im_sp)
    out_m = type_as(out_m, im)
    out_c = out_c.repeat(ksp[0], axis=0).repeat(ksp[1], axis=1)
    out_c = ima_pad_crop(out_c, im_sp)
    out_c = type_as(out_c, im)
    del ksp, wsp, so_sp, sf_sp, ima, im_sp, pad_sp, ima_pad, ha, wa, wd_h0, wd_w0
    del r, t, transform_func, i, j, wd, f_uv, f_rt, p_r, p_t, sin, cos, fi, ft, filter_func
    gc.collect()
    return out_o, out_f, out_m, out_c
