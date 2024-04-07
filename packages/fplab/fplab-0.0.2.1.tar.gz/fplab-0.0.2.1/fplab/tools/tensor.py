"""
与图像张量有关的函数，pytorch环境的图像处理函数
imt_read            读取图像
imt_show            展示图像
imt_save            保存图像
imt_minmax          归一化图像
imt_zscore          标准化图像
ima2imt             数组转化为张量
imt_l2rgb           转化为RGB图像
imt_rgb2l           转化为灰度图像
imt_pad_crop        图像填充和裁剪
imt_pad_blk         根据块大小填充图像
imt_conv2d          2维卷积
imt_sum_average     局部求和、求平均
imt_gaussian        高斯模糊、高斯池化
imt_cal_grad        计算梯度
"""
from PIL import Image
from pathlib import Path
import numpy as np
import torch
import gc


class IMT:
    def __init__(self, imt):
        self.imt = imt
        self.shape = imt.shape

    @ staticmethod
    def read(path, device='cpu'):
        """读取图像"""
        return IMT(imt_read(path, device=device))

    def show(self):
        """展示图像"""
        imt_show(self.imt)

    def save(self, path):
        """保存图像"""
        imt_save(self.imt, path)

    def minmax(self, min_v=0, max_v=1):
        """归一化图像"""
        return IMT(imt_minmax(self.imt, min_v=min_v, max_v=max_v))

    def zscore(self, specified_m=0.5, specified_s=0.5):
        """标准化图像"""
        return IMT(imt_zscore(self.imt, specified_m=specified_m, specified_s=specified_s))

    @ staticmethod
    def ima2imt(ima, device='cpu'):
        """数组转化为张量"""
        return IMT(ima2imt(ima, device=device))

    def l2rgb(self):
        """转化为RGB图像"""
        return IMT(imt_l2rgb(self.imt))

    def rgb2l(self, md="a"):
        """转化为灰度图像"""
        return IMT(imt_rgb2l(self.imt, md=md))

    def pad_crop(self, sp, pad_md='reflect', pad_v=0):
        """图像填充和裁剪"""
        return IMT(imt_pad_crop(self.imt, sp, pad_md=pad_md, pad_v=pad_v))

    def pad_blk(self, blk_sz, pad_md='reflect', pad_v=0):
        """根据块大小填充图像"""
        pad, sp = imt_pad_blk(self.imt, blk_sz, pad_md=pad_md, pad_v=pad_v)
        return IMT(pad), sp

    def conv2d(self, kt, s=1, **kwargs):
        """2维卷积"""
        return IMT(imt_conv2d(self.imt, kt, s=s, **kwargs))

    def sum_average(self, ksz, kmd="m", s=1, pad_md="reflect", pad_v=0, keep_shape=True, **kwargs):
        """局部求和、求平均"""
        return IMT(imt_sum_average(self.imt, ksz, kmd=kmd, s=s, pad_md=pad_md, pad_v=pad_v,
                                   keep_shape=keep_shape, **kwargs))

    def gaussian(self, ksz, sigma=(0, 0), n_flag=True, s=1, pad_md="reflect", pad_v=0, keep_shape=True, **kwargs):
        """高斯模糊、高斯池化"""
        return IMT(imt_gaussian(self.imt, ksz, sigma=sigma, n_flag=n_flag, s=s, pad_md=pad_md, pad_v=pad_v,
                                keep_shape=keep_shape, **kwargs))

    def cal_grad(self, md="sobel", pad_md="reflect", pad_v=0, **kwargs):
        """计算梯度"""
        g_h, g_w = imt_cal_grad(self.imt, md=md, pad_md=pad_md, pad_v=pad_v,  **kwargs)
        return IMT(g_h), IMT(g_w)


def imt_read(im_p, device='cpu'):
    """读取路径为im_p的图像，设置device为指定值，
    图像元素类型为0，1之间的float32值，大小为(3,h,w)或(1,h,w)"""
    if isinstance(im_p, str):
        path = Path(im_p)
    else:
        path = im_p
    im = Image.open(path)
    if im.mode not in ["L", "RGB"]:
        im = im.convert("RGB")
    ima = np.asarray(im, dtype=np.float32) / 255.
    imt = torch.from_numpy(ima)
    imt = imt.to(device)
    if imt.ndim == 3:
        imt = imt.permute(2, 0, 1)
    elif imt.ndim == 2:
        imt = imt.unsqueeze(0)
    del im, ima
    gc.collect()
    return imt


def imt_show(imt_in):
    """显示tensor向量imt_in所表示的图像，imt_in元素应为0，1之间的值，形状为(3,h,w)或(h,w)"""
    imt = torch.clip(imt_in, 0., 1.)
    imt = imt.squeeze()
    md = 'L'
    if imt.ndim == 3:
        imt = imt.permute(1, 2, 0)
        md = 'RGB'
    imt = imt.to('cpu')
    ima = imt.numpy()
    ima = ima*255
    ima = np.round(ima)
    ima = ima.astype(np.uint8)
    im = Image.fromarray(ima, mode=md)
    im.show()
    del imt, ima, im, md
    gc.collect()


def imt_save(imt_in, im_p):
    """保存tensor向量imt_in所表示的图像到im_p，
    imt_in元素应为0，1之间的值，形状为(3, h, w)或(h, w)，
    im_p为pathlib的Path对象"""
    if isinstance(im_p, str):
        path = Path(im_p)
    else:
        path = im_p
    imt = torch.clip(imt_in, 0., 1.)
    imt = imt.squeeze()
    md = 'L'
    if imt.ndim == 3:
        imt = imt.permute(1, 2, 0)
        md = 'RGB'
    imt = imt.to('cpu')
    ima = imt.numpy()
    ima = ima*255
    ima = np.round(ima)
    ima = ima.astype(np.uint8)
    im = Image.fromarray(ima, mode=md)
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)
    del imt, ima, im, md
    gc.collect()


def imt_minmax(imt, min_v=0, max_v=1):
    """将图像元素值线性映射到min_v，max_v之间"""
    imt_min = imt.min(dim=-1, keepdim=True)[0]
    imt_min = imt_min.min(dim=-2, keepdim=True)[0]
    imt_max = imt.max(dim=-1, keepdim=True)[0]
    imt_max = imt_max.max(dim=-2, keepdim=True)[0]
    out = (imt-imt_min)/(imt_max-imt_min+1e-9)*max_v+min_v
    del imt_min, imt_max
    gc.collect()
    return out


def imt_zscore(imt, specified_m=0.5, specified_s=0.5):
    """将图像标准化为均值为specified_m，标准差为specified_s"""
    imt_m = imt.mean((-2, -1), keepdim=True)
    imt_s = imt.std((-2, -1), keepdim=True)
    out = (imt-imt_m)/(imt_s+1e-9)*specified_s+specified_m
    del imt_m, imt_s
    gc.collect()
    return out


def ima2imt(ima, device='cpu'):
    """将图像由数组形式转化为张量形式，大小将由(h, w)或(h, w, c)转化为(c, h, w)"""
    imt = torch.from_numpy(ima)
    imt = imt.to(device)
    if imt.ndim == 3:
        imt = imt.permute(2, 0, 1)
    elif imt.ndim == 2:
        imt = imt.unsqueeze(0)
    return imt


def imt_l2rgb(imt):
    """将imt（由灰度图）转化为RGB图"""
    if imt.shape[0] == 1:
        out = imt.expand(3, -1, -1).clone()
    else:
        out = imt.clone()
    return out


def imt_rgb2l(imt, md="a"):
    """将imt（由RGB图）转化为灰度图
    提供多种转化方法"a"（均值）"m"（最小值）"c"（中值）"M"（最大值）"r"（R通道）"g"（G通道）"b"（B通道）"""
    if imt.shape[0] != 1:
        if md == "a":
            out = torch.mean(imt, dim=0, keepdim=True)
        elif md == "m":
            out = torch.min(imt, dim=0, keepdim=True)[0]
        elif md == "c":
            out = torch.median(imt, dim=0, keepdim=True)[0]
        elif md == "M":
            out = torch.max(imt, dim=0, keepdim=True)[0]
        elif md == "r":
            out = (imt[0, :, :]).clone()
        elif md == "g":
            out = (imt[1, :, :]).clone()
        elif md == "b":
            out = (imt[2, :, :]).clone()
        else:
            raise Exception("Unknown Mode!")
    else:
        out = imt.clone()
    return out


def imt_pad_crop(imt, sp, pad_md='reflect', pad_v=0):
    """将imt填补或裁剪为指定形状。
    以张量表示的图像大小可能为(1, h, w)或(c, h, w)，这里的sp可以为2维数组(specified_h, specified_w)
    若imt.shape的分量小于sp的对应分量，则在该维度上进行填补。
    填补为在维度的两侧填补，
    格式可以通过pad_md指定为 'constant'，'reflect'，'replicate' 或者 'circular'，
    'constant' 的填补值可以由pad_v指定，
    若进行填补且sp的分量与imt.shape的分量差值为奇数，则填补的前值比后值大1，
    比如imt.shape为[3,3]，sp为[3,6]，那么左方补2列，右方补1列。
    若imt.shape的分量大于sp的对应分量，则在该维度上进行裁剪。
    裁剪为在维度的两侧裁剪，通过sp的分量与imt.shape的分量的差值选取裁剪区间
    若差值为奇数，则裁剪的前值比后值大1
    比如imt.shape为[3,6]，sp为[3,3]，那么左方裁2列，右方裁1列。
    """
    # 计算填补和裁剪参数
    pad_n = []
    crop_n = []
    for i in range(len(sp)):
        n = int(-1*(i+1))
        d = imt.shape[n] - sp[n]
        if d < 0:
            v = -1*d
            pad_n += [v-v//2, v//2]
            crop_n.append([0, 0])
        else:
            v = d
            pad_n += [0, 0]
            crop_n.append([v-v//2, v//2])
    pad_n = tuple(pad_n)
    for i in range(len(imt.shape)-len(sp)):
        crop_n.append([0, 0])
    crop_n = crop_n[-1::-1]
    del i, n, d, v
    gc.collect()
    # 填补
    out = torch.nn.functional.pad(imt, pad_n, mode=pad_md, value=pad_v)
    # 裁剪
    crop_slice = []
    for i in range(len(out.shape)):
        crop_slice.append(slice(crop_n[i][0], out.shape[i] - crop_n[i][1]))
    out = out[crop_slice]
    del pad_n, crop_n, crop_slice
    gc.collect()
    return out


def imt_pad_blk(imt, blk_sz, pad_md='reflect', pad_v=0):
    """根据指定的块大小，将图像填补为合适大小，以便于分块。
    指定块大小blk_sz可以为整数或二维整数数组，
    函数还将返回原始图像的大小，以便于之后将图像恢复为原大小"""
    if isinstance(blk_sz, int):
        bh = bw = blk_sz
    else:
        bh, bw = blk_sz
    h, w = imt.shape[-2:]
    ph = round(np.ceil(h/bh)*bh)
    pw = round(np.ceil(w/bw)*bw)
    if ph == h and pw == w:
        out = imt.clone()
    else:
        out = imt_pad_crop(imt, (ph, pw), pad_md=pad_md, pad_v=pad_v)
    del bh, bw, h, w, ph, pw
    gc.collect()
    return out, imt.shape[-2:]


def imt_conv2d(imt, kt, s=1, **kwargs):
    """对图像imt进行二维卷积。
    imt的大小应为(c, h, w)。
    k为卷积核，s为步长，
    kwargs负责接受其余可用参数，见torch.nn.functional.conv2d
    可用参数groups将不起作用，本函数将根据k的大小自动调节groups的大小
    当k的大小为(kh, kw)时，groups的值取imt的c值
    若k的大小为(f, kh, kw)且f=k时，groups的值取1
    当k的大小为(f, kh, kw)但是f！=k时，程序将报错"""
    c = imt.shape[-3]
    im = imt.unsqueeze(0).clone()
    if kt.ndim == 2:
        g = c
        k = kt.unsqueeze(0).clone()
        k = k.unsqueeze(0)
        if c != 1:
            k = torch.cat([k for _ in range(c)])
    elif kt.ndim == 3 and kt.shape[-3] == c:
        g = 1
        k = kt.unsqueeze(0).clone()
    else:
        raise Exception("Error of the kernel size!")
    k = k.type(im.type())
    k = k.to(im.device)
    out = torch.nn.functional.conv2d(im, k, groups=g, stride=s, **kwargs)
    out = out.squeeze()
    if out.ndim == 2:
        out = out.unsqueeze(0)
    del im, k, c, g
    gc.collect()
    return out


def imt_sum_average(imt, ksz, kmd="m", s=1, pad_md="reflect", pad_v=0, keep_shape=True, **kwargs):
    """通过卷积实现局部平均和求和
    ksz控制卷积核大小，可以为整数也可以为2维或3维整数向量
    kmd决定是求平均（"m"）还是求和（"s"）
    s控制卷积的步长，s>1时将填补图像使得图像的大小能被s整除。
    卷积前将对图像填补以使卷积输出大小为（imt.h/s0, imt.w/s1）
    pad_md和pad_v决定填充方式
    keep_shape=True时将在s>1时对图像进行上采样并裁剪，使得函数输出的长宽与输入相同
    kwargs接收torch.nn.functional.conv2d的其他参数，以实现更精细的效果"""
    # 考虑三维卷积的情况，不能直接指定sp有两个分量h，w
    if isinstance(ksz, int):
        spk = ksz, ksz
    else:
        spk = ksz
    conv_k = torch.ones(spk)
    if kmd == "m":
        conv_k = conv_k/conv_k.numel()
    if isinstance(s, int):
        sps = s, s
    else:
        sps = s
    im, imt_sp = imt_pad_blk(imt, sps, pad_md, pad_v)
    pd_sp = spk[-2]-sps[-2], spk[-1]-sps[-1]
    im = imt_pad_crop(im, (im.shape[-2]+pd_sp[-2], imt.shape[-1]+pd_sp[-1]), pad_md, pad_v)
    out = imt_conv2d(im, conv_k, s=s, **kwargs)
    if keep_shape:
        out = out.repeat_interleave(sps[-1], -1).repeat_interleave(sps[-2], -2)
        out = imt_pad_crop(out, imt_sp)
    del spk, conv_k, sps, im, imt_sp, pd_sp
    gc.collect()
    return out


def imt_gaussian(imt, ksz, sigma=(0, 0), n_flag=True, s=1, pad_md="reflect", pad_v=0, keep_shape=True, **kwargs):
    """实现高斯滤波
    ksz控制卷积核大小，可以为整数也可以为2维整数向量，该函数中卷积核大小可以非奇数
    sigma是高斯核的标准差，当不指定sigma(sigma为非正数)时，sigma的值为((ksz-1)//2-1)*0.3+0.8（opencv的计算方式）
    n_flag控制是否对生成的高斯核进行归一化
    s控制卷积的步长，s>1时将填补图像使得图像的大小能被s整除。
    卷积前将对图像填补以使卷积输出大小为（imt.h/s[0], imt.w/s[1]）
    pad_md和pad_v决定填充方式
    keep_shape=True时将对图像进行上采样(s>1时)并裁剪，使得函数输出的长宽与输入相同
    kwargs接收torch.nn.functional.conv2d的其他参数，以实现更精细的效果"""
    # 考虑三维卷积的情况，不能直接指定sp有两个分量h，w
    if isinstance(ksz, int):
        spk = ksz, ksz
    else:
        spk = ksz
    if isinstance(sigma, (float, int)):
        sigma_x = sigma_y = sigma
    else:
        sigma_x, sigma_y = sigma
    sigma_x = (((spk[0]-1)//2-1)*0.3+0.8) if sigma_x <= 0 else sigma_x
    sigma_y = (((spk[1]-1)//2-1)*0.3+0.8) if sigma_y <= 0 else sigma_y
    conv_k = np.fromfunction(lambda x, y: ((x-spk[0]//2)/sigma_x)**2+((y-spk[1]//2)/sigma_y)**2, spk)
    conv_k = np.exp(-0.5*conv_k)/(2*np.pi*sigma_x*sigma_y)
    conv_k = torch.from_numpy(conv_k)
    if n_flag:
        conv_k = conv_k/conv_k.sum()
    if isinstance(s, int):
        sps = s, s
    else:
        sps = s
    im, imt_sp = imt_pad_blk(imt, sps, pad_md, pad_v)
    pd_sp = spk[-2]-sps[-2], spk[-1]-sps[-1]
    im = imt_pad_crop(im, (im.shape[-2]+pd_sp[-2], imt.shape[-1]+pd_sp[-1]), pad_md, pad_v)
    out = imt_conv2d(im, conv_k, s=s, **kwargs)
    if keep_shape:
        out = out.repeat_interleave(sps[-1], -1).repeat_interleave(sps[-2], -2)
        out = imt_pad_crop(out, imt_sp)
    del spk, conv_k, sps, im, imt_sp, pd_sp
    gc.collect()
    return out


def imt_cal_grad(imt, md="sobel", pad_md="reflect", pad_v=0, **kwargs):
    """使用卷积计算图像梯度
    md决定计算梯度的方法："sobel"
    pad_md和pad_v决定填充方式
    kwargs接收torch.nn.functional.conv2d的其他参数，以实现更精细的效果"""
    if md == "sobel":
        conv_hk = torch.tensor([[-1., -2., -1.,], [0., 0., 0.,], [1., 2., 1.,]])
        conv_wk = torch.tensor([[-1., 0., 1.,], [-2., 0., 2.,], [-1., 0., 1.,]])
        pd_sp = 2, 2
    elif md == "scharr":
        conv_hk = torch.tensor([[-3., -10., -3,], [0., 0., 0.,], [3., 10., 3.,]])
        conv_wk = torch.tensor([[-3., 0., 3.,], [-10., 0., 10.,], [-3., 0., 3.,]])
        pd_sp = 2, 2
    else:
        raise Exception("Unknown Mode!")
    im = imt_pad_crop(imt, (imt.shape[-2]+pd_sp[-2], imt.shape[-1]+pd_sp[-1]), pad_md, pad_v)
    out_h = imt_conv2d(im, conv_hk, **kwargs)
    out_w = imt_conv2d(im, conv_wk, **kwargs)
    del conv_hk, conv_wk, pd_sp, im
    gc.collect()
    return out_h, out_w
