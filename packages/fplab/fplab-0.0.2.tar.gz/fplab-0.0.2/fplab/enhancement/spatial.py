"""
使用空域滤波的指纹增强方法
Hong1998
"""
import numpy as np
import gc
from scipy import ndimage
from fplab.tools.image import type_as
from fplab.tools.array import ima_rgb2l, ima_minmax
from fplab.intrinsic.orientation import gradient as ort_gradient
from fplab.intrinsic.frequency import projection as frq_projection


def get_gabor_filter_function(k_sz, delta, oa, fa):
    """定义用于scipy.ndimage.generic_filter的自定义滤波函数，
    用于实现参数随像素位置变化的Gabor滤波
    k_sz是滤波核大小
    delta是Gabor滤波的参数
    oa，fa分别是方向场和频率场"""
    if isinstance(k_sz, int):
        ksp = k_sz, k_sz
    else:
        ksp = k_sz
    if isinstance(delta, (float, int)):
        d = delta, delta
    else:
        d = delta
    # 计算与方向场和频率场无关的系数，用于简化计算
    ft = np.ones(ksp)
    x, y = np.indices(ksp)
    x, y = x-ksp[0]//2, y-ksp[1]//2
    c1 = (x**2/d[1]**2+y**2/d[0]**2)*(-0.5)
    c2 = (x**2/d[0]**2+y**2/d[1]**2)*(-0.5)
    c3 = (x*y/d[0]**2-x*y/d[1]**2)*(-1)
    c4 = 2*np.pi*x
    c5 = 2*np.pi*y

    class FilterFunction:
        def __init__(self):
            self.shape = oa.shape
            self.n = 0

        def __call__(self, in_elements):
            coordinates = np.unravel_index(self.n, self.shape)
            o = oa[coordinates]
            f = fa[coordinates]
            k = np.exp(c1*(np.sin(o)**2)+c2*(np.cos(o)**2)+c3*np.sin(o)*np.cos(o))
            k = k*np.cos(c4*f*np.cos(o)+c5*f*np.sin(o))
            k = k.flatten()/(np.abs(k.sum()))
            out = (k*in_elements).sum()
            self.n = self.n + 1
            return out

    return ft, FilterFunction()


def gabor_filter(im, ot, fq, k_sz=(11, 11), delta=(4, 4)):
    """根据计算的方向场ot和频率场fq，对指纹图像im进行Gabor滤波增强
    k_sz是滤波器大小
    delta是滤波器的系数
    """
    # ima是原始图像
    ima = type_as(im, md="a")
    ima = ima_rgb2l(ima)
    ima = ima_minmax(ima)
    # ota存放着每一点的方向
    ota = type_as(ot, md="a")
    # fqa存放着每一点的频率
    fqa = type_as(fq, md="a")
    ft, filter_func = get_gabor_filter_function(k_sz, delta, ota, fqa)
    out = ndimage.generic_filter(ima, filter_func, footprint=ft)
    out = type_as(out, im)
    del ima, ota, fqa, ft, filter_func
    gc.collect()
    return out


def hong1998(im):
    """1998年Hong提出的指纹指纹增强算法，复现了除分割外的处理过程"""
    o = ort_gradient.hong1998(im)
    f = frq_projection.hong1998(im, o, flag=("return",))
    out = gabor_filter(im, o, f)
    return out, o, f


def get_diffusion_function(oa, c1, c2, s):
    """定义用于scipy.ndimage.generic_filter的自定义滤波函数，
    用于实现参数随像素位置变化的方向扩散滤波
    oa是方向场，c1和c2是正交方向的权重，s是迭代步长"""
    # 扩散需要多次迭代，每次迭代同一位置使用的核是相同的
    # 预先计算这些核以减少运算量
    ft = np.ones((3, 3))
    k = []
    for i in range(oa.size):
        coordinates = np.unravel_index(i, oa.shape)
        o = oa[coordinates]
        cos, sin = np.cos(o), np.sin(o)
        a = (c1-c2)*cos*cos+c2
        b = (c1-c2)*cos*sin
        c = (c1-c2)*sin*sin+c2
        k.append(np.array([b, 2*a, -b, 2*c, -4*(c1+c2), 2*c, -b, 2*a, b])*s/2)

    class FilterFunction:
        def __init__(self):
            self.n = 0

        def __call__(self, in_elements):
            out = in_elements[4]+(k[self.n]*in_elements).sum()
            self.n = (self.n + 1) % oa.size
            return out

    return ft, FilterFunction()


def diffusion_filter(im, ot, c1, c2, s, itn):
    """根据计算的方向场ot，对指纹图像im进行方向扩散增强
    c1和c2是正交方向的权重，s是迭代步长，itn是迭代次数
    """
    # ima是原始图像
    ima = type_as(im, md="a")
    ima = ima_rgb2l(ima)
    ima = ima_minmax(ima)
    # ota存放着每一点的方向
    ota = type_as(ot, md="a")
    ft, filter_func = get_diffusion_function(ota, c1, c2, s)
    for i in range(itn):
        ima = ndimage.generic_filter(ima, filter_func, footprint=ft)
    ima = type_as(ima, im)
    del ota, ft, filter_func
    gc.collect()
    return ima
