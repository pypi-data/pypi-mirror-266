"""
基于变换的频率估计方法
chikkerur2007       基于STFT的频率场估计方法
"""
import numpy as np
from scipy import fft, ndimage
from fplab.tools.image import type_as
from fplab.tools.array import IMA, ima_gaussian
from fplab.intrinsic.multiple.transform import get_cartesian_function


def chikkerur2007(im, blk_sz=(8, 8), wd_sz=(32, 32), smf_sz=(3, 3), smf_itn=1):
    """2007年chikkerur使用STFT分析指纹的频率场部分，将这一部分单独列为一个函数是因为基于投影的频率估计方法速度太慢。
    im是需要处理的指纹图像，RGB图会被转化为灰度图
    blk_sz是图像块大小，可以为整数或2维向量，每个图像块估计一次频率作为块内所有像素的频率。
    wd_sz是傅里叶变换的窗口大小，可以为整数或2维向量。
    smf_sz是平滑频率场使用的滤波核大小，
    smf_itn控制滤波核迭代次数（文章中认为使用小滤波器多次平滑的效果要比大滤波器好）"""
    # 处理输入参数
    if isinstance(blk_sz, int):
        ksp = blk_sz, blk_sz
    else:
        ksp = blk_sz
    if isinstance(wd_sz, int):
        wsp = wd_sz, wd_sz
    else:
        wsp = wd_sz
    if isinstance(smf_sz, int):
        sf_sp = smf_sz, smf_sz
    else:
        sf_sp = smf_sz
    # ima 待处理的图像
    ima = type_as(im, md="a")
    ima, im_sp = IMA(ima).rgb2l().minmax().pad_blk(ksp)
    # ima_pad 填充后的图像，便于窗口选取
    pad_sp = ima.shape[0]+wsp[0]-ksp[0], ima.shape[1]+wsp[1]-ksp[1]
    ima_pad = ima.pad_crop(pad_sp).ima
    # ha, wa 图像块的中心
    ha = np.arange((ksp[0]-1)//2, ima.shape[0], ksp[0])
    wa = np.arange((ksp[1]-1)//2, ima.shape[1], ksp[1])
    # wd_h0, wd_w0 窗口左上角坐标
    wd_h0 = ha-(wsp[0]-1)//2 + wsp[0]-ksp[0]-(wsp[0]-ksp[0])//2
    wd_w0 = wa-(wsp[1]-1)//2 + wsp[1]-ksp[1]-(wsp[1]-ksp[1])//2
    # 极径和极角取值，转化函数
    r, t, transform_func = get_cartesian_function(wsp, min_v=(0, -np.pi/2), max_v=(np.sqrt(2)/2, np.pi/2), c=wsp)
    # 方向场，频率场，指纹区域
    out_f = np.zeros((len(ha), len(wa)))
    for i in range(len(ha)):
        for j in range(len(wa)):
            wd = ima_pad[wd_h0[i]:wd_h0[i]+wsp[0], wd_w0[j]:wd_w0[j]+wsp[1]]
            f_uv = fft.fft2(wd-wd.mean())
            f_rt = np.abs(ndimage.geometric_transform(f_uv, transform_func, output_shape=wsp, mode='grid-wrap'))
            p_rt = f_rt**2/((f_rt**2).sum()+1e-8)
            p_r = p_rt.sum(1)
            out_f[i, j] = (p_r*r).sum()
    # 频率场平滑
    fi = np.where((out_f < 1 / 3) & (out_f > 1 / 25), np.ones_like(out_f), np.zeros_like(out_f))
    for _ in range(smf_itn):
        out_f = ima_gaussian(out_f*fi, sf_sp)/(ima_gaussian(fi, sf_sp)+1e-8)
        fi = np.where((out_f < 1 / 3) & (out_f > 1 / 25), np.ones_like(out_f), np.zeros_like(out_f))
    # 处理输出
    out_f = out_f.repeat(ksp[0], axis=0).repeat(ksp[1], axis=1)
    out_f = IMA(out_f).pad_crop(im_sp).ima
    out_f = type_as(out_f, im)
    return out_f
