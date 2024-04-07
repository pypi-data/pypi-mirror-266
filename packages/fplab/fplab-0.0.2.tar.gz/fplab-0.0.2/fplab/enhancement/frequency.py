"""
使用频域滤波的指纹增强方法
Chikkerur2007
"""
import numpy as np
import gc
from fplab.tools.image import type_as
from fplab.tools.array import ima_minmax, ima_pad_blk, ima_pad_crop, ima_rgb2l
from fplab.intrinsic.multiple import transform
from scipy import fft


def get_filter_chikkerur(wd_sz, n=2, bw_rc=np.sqrt(2), bw_t=np.pi/4):
    """根据滤波器大小wd_sz返回与频率和角度有关的滤波器模板生成函数
    n是带通巴特沃斯滤波器的阶数
    bw_rc控制径向带宽，频率与bw_rc的乘积为径向带宽
    bw_t是角度带宽"""
    if isinstance(wd_sz, int):
        wsp = wd_sz, wd_sz
    else:
        wsp = wd_sz
    x, y = np.indices(wsp)
    x, y = x - wsp[0] // 2, y - wsp[1] // 2
    x, y = x / wsp[0], y / wsp[0]
    rho = np.sqrt(x ** 2 + y ** 2)
    theta = np.arctan(y / (x + 1e-8))

    def get_filter(r, t):
        """获得频率域滤波器，r、t分别为频率和角度"""
        hr = np.sqrt((rho*r*bw_rc)**(2*n)/((rho*r*bw_rc)**(2*n)+(rho**2-r**2)**(2*n)+1e-8))
        ht = np.cos(np.pi / 2 * (theta - t) / bw_t) ** 2
        ht = np.where(np.cos(2 * (theta - t)) > np.sqrt(3) / 2, ht, np.zeros_like(ht))
        return ht * hr

    return get_filter


def filter_chikkerur(im, ot, fq, blk_sz=(8, 8), wd_sz=(32, 32), n=2, bw_rc=np.sqrt(2), bw_t=np.pi/4):
    """使用2007年chikkerur使用的频率域滤波增强指纹。
    im是需要处理的指纹图像，RGB图会被转化为灰度图
    ot、fq分别对应指纹的方向场和频率图
    blk_sz是图像块大小，可以为整数或2维向量，每个图像块估计一次方向作为块内所有像素的方向。
    wd_sz是傅里叶变换的窗口大小，可以为整数或2维向量。
    n是带通巴特沃斯滤波器的阶数
    bw_rc控制径向带宽，频率与bw_rc的乘积为径向带宽
    bw_t是角度带宽"""
    # 处理输入参数
    if isinstance(blk_sz, int):
        ksp = blk_sz, blk_sz
    else:
        ksp = blk_sz
    if isinstance(wd_sz, int):
        wsp = wd_sz, wd_sz
    else:
        wsp = wd_sz
    # ima 待处理的图像
    ima = type_as(im, md="a")
    ima = ima_rgb2l(ima)
    ima = ima_minmax(ima)
    ima, im_sp = ima_pad_blk(ima, ksp)
    # ima_pad 填充后的图像，便于窗口选取
    pad_sp = ima.shape[0]+wsp[0]-ksp[0], ima.shape[1]+wsp[1]-ksp[1]
    ima_pad = ima_pad_crop(ima, pad_sp)
    # ota存放着每一点的方向
    ota = type_as(ot, md="a")
    # fqa存放着每一点的频率
    fqa = type_as(fq, md="a")
    # ha, wa 图像块的中心
    ha = np.arange((ksp[0]-1)//2, ima.shape[0], ksp[0])
    wa = np.arange((ksp[1]-1)//2, ima.shape[1], ksp[1])
    # blk_h0, blk_w0 图像块左上角坐标
    blk_h0 = ha-(ksp[0]-1)//2
    blk_w0 = wa-(ksp[1]-1)//2
    # wd_h0, wd_w0 窗口左上角坐标
    wd_h0 = ha-(wsp[0]-1)//2 + wsp[0]-ksp[0]-(wsp[0]-ksp[0])//2
    wd_w0 = wa-(wsp[1]-1)//2 + wsp[1]-ksp[1]-(wsp[1]-ksp[1])//2
    # out_h0, out_w0 输出对应的窗口左上角坐标
    out_h0 = wsp[0]-wsp[0]//2-ksp[0]//2
    out_w0 = wsp[1]-wsp[1]//2-ksp[1]//2
    out = np.zeros_like(ima)
    filter_func = get_filter_chikkerur(wsp, n, bw_rc, bw_t)
    for i in range(len(ha)):
        for j in range(len(wa)):
            wd = ima_pad[wd_h0[i]:wd_h0[i]+wsp[0], wd_w0[j]:wd_w0[j]+wsp[1]]
            f_uv = fft.fftshift(fft.fft2(wd-wd.mean()))
            k = filter_func(fqa[ha[i], wa[j]], ota[ha[i], wa[j]])
            i_xy = fft.ifft2(fft.ifftshift(f_uv*k))
            i_xy = np.real(i_xy+wd.mean())[out_h0:out_h0+ksp[0], out_w0:out_w0+ksp[1]]
            out[blk_h0[i]:blk_h0[i]+ksp[0], blk_w0[j]:blk_w0[j]+ksp[1]] = i_xy
    out = ima_pad_crop(out, im_sp)
    out = type_as(out, im)
    del ksp, wsp, ima, im_sp, pad_sp, ima_pad, ota, fqa, ha, wa
    del blk_h0, blk_w0, wd_h0, wd_w0, out_h0, out_w0, filter_func
    del i, j, wd, f_uv, k, i_xy
    gc.collect()
    return out


def chikkerur2007(im):
    """2007年Chikkerur提出的指纹指纹增强算法"""
    o, f, m, c = transform.chikkerur2007(im)
    out = filter_chikkerur(im, o, f)
    out = m*out
    return out, o, f, m, c


def chikkerur2007_no_smooth(im):
    """2007年Chikkerur提出的指纹指纹增强算法"""
    o, f, m, c = transform.chikkerur2007(im, smo_itn=0, smf_itn=0)
    out = filter_chikkerur(im, o, f)
    out = m*out
    return out, o, f, m, c
