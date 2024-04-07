"""
与图像数组有关的函数，numpy环境的图像处理函数
ima_read            读取图像
ima_show            展示图像
ima_save            保存图像
ima_float2uint      浮点型转化为无符号整型
ima_uint2float      无符号整型转化为浮点型
ima_minmax          归一化图像
ima_zscore          标准化图像
imt2ima             张量转化为数组
ima_l2rgb           转化为RGB图像
ima_rgb2l           转化为灰度图像
ima_pad_crop        图像填充和裁剪
ima_pad_blk         根据块大小填充图像
ima_conv2d          2维卷积
ima_sum_average     局部求和、求平均
ima_gaussian        高斯模糊
ima_cal_grad        计算梯度
"""
from PIL import Image
from pathlib import Path
import numpy as np
import gc
import typing
import cv2


class IMA:
    def __init__(self, ima):
        self.ima = ima
        self.shape = ima.shape

    @ staticmethod
    def read(path):
        """读取图像"""
        return IMA(ima_read(path))

    def show(self):
        """展示图像"""
        ima_show(self.ima)

    def save(self, path):
        """保存图像"""
        ima_save(self.ima, path)

    def float2uint(self):
        """浮点型转化为无符号整型"""
        return IMA(ima_float2uint(self.ima))

    def uint2float(self):
        """无符号整型转化为浮点型"""
        return IMA(ima_uint2float(self.ima))

    def minmax(self, min_v=0, max_v=1):
        """归一化图像"""
        return IMA(ima_minmax(self.ima, min_v=min_v, max_v=max_v))

    def zscore(self, specified_m=0.5, specified_s=0.5):
        """标准化图像"""
        return IMA(ima_zscore(self.ima, specified_m=specified_m, specified_s=specified_s))

    @ staticmethod
    def imt2ima(imt_in):
        """张量转化为数组"""
        return IMA(imt2ima(imt_in))

    def l2rgb(self):
        """转化为RGB图像"""
        return IMA(ima_l2rgb(self.ima))

    def rgb2l(self, md="a"):
        """转化为灰度图像"""
        return IMA(ima_rgb2l(self.ima, md=md))

    def pad_crop(self, sp, pad_md: typing.Any = 'reflect', **kwargs):
        """图像填充和裁剪"""
        return IMA(ima_pad_crop(self.ima, sp, pad_md=pad_md, **kwargs))

    def pad_blk(self, blk_sz, pad_md: typing.Any = 'reflect', **kwargs):
        """根据块大小填充图像"""
        pad, sp = ima_pad_blk(self.ima, blk_sz, pad_md=pad_md, **kwargs)
        return IMA(pad), sp

    def conv2d(self, k, b="reflect101"):
        """2维卷积"""
        return IMA(ima_conv2d(self.ima, k, b=b))

    def sum_average(self, ksz, kmd, pad_md="reflect101"):
        """局部求和、求平均"""
        return IMA(ima_sum_average(self.ima, ksz, kmd, pad_md=pad_md))

    def gaussian(self, ksz, sigma=(0, 0), pad_md="reflect101"):
        """高斯模糊"""
        return IMA(ima_gaussian(self.ima, ksz, sigma=sigma, pad_md=pad_md))

    def cal_grad(self, md="sobel", pad_md="reflect101"):
        """计算梯度"""
        g_h, g_w = ima_cal_grad(self.ima, md=md, pad_md=pad_md)
        return IMA(g_h), IMA(g_w)


def ima_read(im_p):
    """读取路径为im_p的图像，输出大小为(h, w)或(h, w, 3)，取值为0，1之间的float32值"""
    if isinstance(im_p, str):
        path = Path(im_p)
    else:
        path = im_p
    im = Image.open(path)
    if im.mode not in ["L", "RGB"]:
        im = im.convert("RGB")
    ima = np.asarray(im, dtype=np.float32) / 255.
    del im
    gc.collect()
    return ima


def ima_show(ima_in):
    """显示数组ima_in所表示的图像，ima_in形状为(h, w)或(h, w, 3)，取值为0，1之间的float32值"""
    ima = np.clip(ima_in, 0., 1.)
    ima = ima.squeeze()
    md = 'L'
    if ima.ndim == 3:
        md = 'RGB'
    ima = ima * 255
    ima = np.round(ima)
    ima = ima.astype(np.uint8)
    im = Image.fromarray(ima, mode=md)
    im.show()
    del ima, im, md
    gc.collect()


def ima_save(ima_in, im_p):
    """保存数组ima_in所表示的图像到im_p，
    ima_in形状为(h, w)或(h, w, 3)，取值为0，1之间的float32值，
    im_p为pathlib的Path对象"""
    if isinstance(im_p, str):
        path = Path(im_p)
    else:
        path = im_p
    ima = np.clip(ima_in, 0., 1.)
    ima = ima.squeeze()
    md = 'L'
    if ima.ndim == 3:
        md = 'RGB'
    ima = ima * 255
    ima = np.round(ima)
    ima = ima.astype(np.uint8)
    im = Image.fromarray(ima, mode=md)
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)
    del ima, im, md
    gc.collect()


def ima_float2uint(ima):
    """将图像元素类型由np.float32转化为np.uint8"""
    if np.issubdtype(ima.dtype, np.integer):
        out = ima.astype(np.uint8).copy()
    else:
        out = np.round(ima*255).astype(np.uint8).copy()
    return out


def ima_uint2float(ima):
    """将图像元素类型由np.uint8转化为np.float32"""
    if np.issubdtype(ima.dtype, np.integer):
        out = ima.astype(np.float32).copy()
        out = out/255.
    else:
        out = ima.astype(np.float32).copy()
    return out


def ima_minmax(ima, min_v=0, max_v=1):
    """将图像元素值线性映射到min_v，max_v之间"""
    ima_min = ima.min(axis=(0, 1), keepdims=True)
    ima_max = ima.max(axis=(0, 1), keepdims=True)
    out = (ima-ima_min)/(ima_max-ima_min+1e-9)*max_v+min_v
    del ima_min, ima_max
    gc.collect()
    return out


def ima_zscore(ima, specified_m=0.5, specified_s=0.5):
    """将图像标准化为均值为specified_m，标准差为specified_s"""
    ima_m = ima.mean(axis=(0, 1), keepdims=True)
    ima_s = ima.std(axis=(0, 1), keepdims=True)
    out = (ima-ima_m)/(ima_s+1e-9)*specified_s+specified_m
    del ima_m, ima_s
    gc.collect()
    return out


def imt2ima(imt_in):
    """将图像由张量形式转化为数组形式。
    元素大小将由(c, h, w)转化为(h, w)或(h, w, c)"""
    imt = imt_in.squeeze().clone()
    if imt.ndim == 3:
        imt = imt.permute(1, 2, 0)
    imt = imt.to('cpu')
    ima = imt.numpy()
    del imt
    gc.collect()
    return ima


def ima_l2rgb(ima):
    """将ima（由灰度图）转化为RGB图"""
    if ima.ndim == 2:
        out = ima[:, :, None]
        out = np.repeat(out, 3, axis=2)
    else:
        out = ima.copy()
    return out


def ima_rgb2l(ima, md="a"):
    """将ima（由RGB图）转化为灰度图
    提供多种转化方法"a"（均值）"m"（最小值）"c"（中值）"M"（最大值）"r"（R通道）"g"（G通道）"b"（B通道）"""
    if ima.ndim == 3:
        if md == "a":
            out = np.mean(ima, axis=2)
        elif md == "m":
            out = np.min(ima, axis=2)
        elif md == "c":
            out = np.median(ima, axis=2)
        elif md == "M":
            out = np.max(ima, axis=2)
        elif md == "r":
            out = (ima[:, :, 0]).squeeze().copy()
        elif md == "g":
            out = (ima[:, :, 1]).squeeze().copy()
        elif md == "b":
            out = (ima[:, :, 2]).squeeze().copy()
        else:
            raise Exception("Unknown Mode!")
    else:
        out = ima.copy()
    return out


def ima_pad_crop(ima, sp, pad_md: typing.Any = 'reflect', **kwargs):
    """将ima填补或裁剪为指定形状。
    由于以数组形式表示的图像大小可能为(h, w)或(h, w, c)，这里的sp必须为2维数组(specified_h, specified_w)
    若ima.shape的分量小于sp的对应分量，则在该维度上进行填补。
    填补为在维度的两侧填补，
    格式可以通过pad_md指定为 'constant'，'edge'，'linear_ramp'，'maximum'，
    'mean'，'median'，'minimum'，'reflect'，'symmetric'，'wrap'，'empty' 或者自定义函数
    一些替补格式可能需要其他参数，具体参见numpy.pad
    若进行填补且sp的分量与ima.shape的分量差值为奇数，则填补的前值比后值大1，
    比如ima.shape为[3,3]，sp为[3,6]，那么左方补2列，右方补1列。
    若ima.shape的分量大于sp的对应分量，则在该维度上进行裁剪。
    裁剪为在维度的两侧裁剪，通过sp的分量与ima.shape的分量的差值选取裁剪区间
    若差值为奇数，则裁剪的前值比后值大1
    比如ima.shape为[3,6]，sp为[3,3]，那么左方裁2列，右方裁1列。
    """
    # 计算填补和裁剪参数
    pad_n = np.zeros((len(ima.shape), 2), dtype=np.int32)
    crop_n = []
    for i in range(len(sp)):
        d = ima.shape[i] - sp[i]
        if d < 0:
            v = -1*d
            pad_n[i, 0] = v-v//2
            pad_n[i, 1] = v//2
            crop_n.append([0, 0])
        else:
            v = d
            pad_n[i, 0] = 0
            pad_n[i, 1] = 0
            crop_n.append([v-v//2, v//2])
    for i in range(len(ima.shape)-len(sp)):
        crop_n.append([0, 0])
    del i, d, v
    gc.collect()
    # 填补
    out = np.pad(ima, pad_n, pad_md, **kwargs)
    # 裁剪
    crop_slice = []
    for i in range(len(out.shape)):
        crop_slice.append(slice(crop_n[i][0], out.shape[i] - crop_n[i][1]))
    crop_slice = tuple(crop_slice)
    out = out[crop_slice]
    del pad_n, crop_n, crop_slice
    gc.collect()
    return out


def ima_pad_blk(ima, blk_sz, pad_md: typing.Any = 'reflect', **kwargs):
    """根据指定的块大小，将图像填补为合适大小，以便于分块。
    指定块大小blk_sz可以为整数或二维整数数组，
    函数还将返回原始图像的大小，以便于之后将图像恢复为原大小"""
    if isinstance(blk_sz, int):
        bh = bw = blk_sz
    else:
        bh, bw = blk_sz
    h, w = ima.shape[:2]
    ph = round(np.ceil(h/bh)*bh)
    pw = round(np.ceil(w/bw)*bw)
    if ph == h and pw == w:
        out = ima.copy()
    else:
        out = ima_pad_crop(ima, (ph, pw), pad_md, **kwargs)
    del bh, bw, h, w, ph, pw
    gc.collect()
    return out, ima.shape[:2]


def ima_conv2d(ima, k, b="reflect101"):
    """对图像ima进行二维卷积。
    ima应为大小为(h, w)或(h, w, c)且元素值为浮点数的数组。
    k为卷积核，b为边界填充方式，可选填充方式有"constant"，"replicate"，"reflect"，
    "wrap"，"reflect101（默认）"，"transparent"，"isolated"
    该函数实质上是opencv.filter2D的封装，因此处理速度很快。
    但是因此该函数形式固定，即只能采用有限的填充方式对图像各通道进行相同的卷积，
    卷积核只能为2维，输出的大小必定与输入相同，而且不能控制卷积的步长（因此不能通过卷积实现池化）"""
    bu = b.upper()
    bu = "cv2.BORDER_" + bu
    out = cv2.filter2D(ima, ddepth=-1, kernel=k, borderType=eval(bu))
    del bu
    gc.collect()
    return out


def ima_sum_average(ima, ksz, kmd, pad_md="reflect101"):
    """通过卷积实现局部平均和求和
    ksz控制卷积核大小，为整数或2维整数向量
    kmd决定是求平均（"m"）还是求和（"s"）
    pad_md决定边界填充方式，可选填充方式有"constant"，"replicate"，"reflect"，
    "wrap"，"reflect101（默认）"，"transparent"，"isolated"
    该函数实质上调用了opencv.boxFilter函数，因此存在一些限制，比如不能调整卷积步长等等"""
    if isinstance(ksz, int):
        spk = ksz, ksz
    else:
        spk = ksz
    if kmd == "m":
        n_flag = True
    else:
        n_flag = False
    bu = pad_md.upper()
    bu = "cv2.BORDER_" + bu
    bu = eval(bu)
    out = cv2.boxFilter(ima, -1, spk, normalize=n_flag, borderType=bu)
    del n_flag, spk, bu
    gc.collect()
    return out


def ima_gaussian(ima, ksz, sigma=(0, 0), pad_md="reflect101"):
    """实现高斯滤波
    ksz控制卷积核大小，可以为奇数也可以为2维奇数向量
    sigma是高斯核的标准差，当不指定sigma(sigma为非正数)时，sigma的值为((ksz-1)//2-1)*0.3+0.8
    pad_md决定边界填充方式，可选填充方式有"constant"，"replicate"，"reflect"，
    "wrap"，"reflect101（默认）"，"transparent"，"isolated"
    该函数实质上调用了opencv.GaussianBlur函数，因此存在一些限制，比如不能调整卷积步长等等"""
    if isinstance(ksz, int):
        spk = ksz, ksz
    else:
        spk = ksz
    if isinstance(sigma, (float, int)):
        sigma_x = sigma_y = sigma
    else:
        sigma_x, sigma_y = sigma
    bu = pad_md.upper()
    bu = "cv2.BORDER_" + bu
    bu = eval(bu)
    out = cv2.GaussianBlur(ima, spk, sigmaX=sigma_x, sigmaY=sigma_y, borderType=bu)
    del spk, sigma_x, sigma_y, bu
    gc.collect()
    return out


def ima_cal_grad(ima, md="sobel", pad_md="reflect101"):
    """使用卷积计算图像梯度
    md决定计算梯度的方法："sobel"
    pad_md决定填充方式，可选填充方式有"constant"，"replicate"，"reflect"，
    "wrap"，"reflect101（默认）"，"transparent"，"isolated"
    kwargs接收torch.nn.functional.conv2d的其他参数，以实现更精细的效果"""
    bu = pad_md.upper()
    bu = "cv2.BORDER_" + bu
    bu = eval(bu)
    if md == "sobel":
        out_h = cv2.Sobel(ima, -1, 1, 0, borderType=bu)
        out_w = cv2.Sobel(ima, -1, 0, 1, borderType=bu)
    elif md == "scharr":
        out_h = cv2.Scharr(ima, -1, 1, 0, borderType=bu)
        out_w = cv2.Scharr(ima, -1, 0, 1, borderType=bu)
    else:
        raise Exception("Unknown Mode!")
    del bu
    gc.collect()
    return out_h, out_w
