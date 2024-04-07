"""
与图像文件有关的函数
get_support_extensions  获取PIL支持读取的所有文件拓展名
get_data_dirs           获取指定路径下所有指定格式的文件的绝对路径
type_as                 将图像类型转化为指定类型
change_image            改变图像的属性：后缀名、分辨率、RGB图像与灰度图像转换等
"""
from pathlib import Path
from PIL import features, Image
import numpy
import torch
from fplab.tools.array import imt2ima
from fplab.tools.tensor import ima2imt


def get_support_extensions():
    """获取PIL支持读取的所有文件扩展名"""
    path = Path('pil_info.txt')
    with open(path, 'w') as f:
        features.pilinfo(f, supported_formats=True)
    with open(path, 'r') as f:
        info = f.read()
    path.unlink()
    info = info.replace(', ', ' ')
    ext = []
    for s1 in info.split('-'):
        if 'open' in s1:
            for s2 in s1.split('\n'):
                if 'Extensions:' in s2:
                    for s3 in s2.split(' '):
                        if '.' in s3:
                            ext.append(s3)
    return ext


def get_data_dirs(data_folder_path, data_dirs, ext=None, top_flag=True):
    """
    获得data_folder_path路径下的所有指定格式ext（默认为PIL库支持读取的所有格式）的文件的绝对路径字符串列表
    当top_flag为True时，会对输出字符串排序
    data_folder_path是一个Path对象, data_dirs是一个字符串列表，ext是一个字符串列表，top_flag为布尔值
    """
    if not ext:
        ext = get_support_extensions()
    if isinstance(data_folder_path, str):
        data_folder_p = Path(data_folder_path)
    else:
        data_folder_p = data_folder_path
    for path in data_folder_p.iterdir():
        if path.is_dir():
            data_dirs = get_data_dirs(path, data_dirs, ext=ext, top_flag=False)
        elif path.suffix in ext:
            data_dirs.append(str(path.absolute()))
    if top_flag:
        data_dirs = sorted(data_dirs)
    return data_dirs


def type_as(im, md="t", device=None):
    """将im转化为指定类型
    md可以为"t"（张量形式），"a"（数组形式）或是图像
    当md为图像时。则将im转化为与md相同的形式
    当im已经符合要求时，则不做任何变化"""
    if not isinstance(im, (numpy.ndarray, torch.Tensor)):
        raise Exception("Type Error! The type of im should be numpy.ndarray or torch.Tensor!")
    if isinstance(md, str):
        if md == "t":
            if isinstance(im, numpy.ndarray):
                if not device:
                    out = ima2imt(im, "cpu")
                else:
                    out = ima2imt(im, device)
            else:
                if not device:
                    out = im.clone()
                else:
                    out = im.to(device).clone()
        elif md == "a":
            if isinstance(im, torch.Tensor):
                out = imt2ima(im)
            else:
                out = im.copy()
        else:
            raise Exception("Unknown Command!")
    else:
        if not isinstance(md, (numpy.ndarray, torch.Tensor)):
            raise Exception("Type Error! The type of md should be numpy.ndarray or torch.Tensor!")
        if isinstance(im, numpy.ndarray) and isinstance(md, torch.Tensor):
            out = ima2imt(im, md.device)
        elif isinstance(im, torch.Tensor) and isinstance(md, numpy.ndarray):
            out = imt2ima(im)
        elif isinstance(im, numpy.ndarray):
            out = im.copy()
        elif isinstance(im, torch.Tensor):
            out = im.clone()
        else:
            raise Exception("Error!")
    return out


def change_image(im_pt, sv_pt=None, ext=None, dpi=None, md=None, rm_flag=False, re_sz=None, rs_md='bicubic'):
    """改变图像的属性
    im_pt, 图像路径
    sv_pt, 图像保存路径，默认为图像所在文件夹的路径
    ext, 指定图像后缀名
    dpi, 指定图像分辨率
    md, 指定图像类型：'RGB' 表示转化为RGB图像, 'L' 表示转化为灰度图像的方法，
    rm_flag控制是否删除原图像
    re_sz, 指定图像大小，可以为整数或2元整数元组
    rs_md, 改变图像大小方法：'bicubic'、'nearest'、'box'、'bilinear'、'hamming'、'lanczos'"""
    if isinstance(im_pt, str):
        im_p = Path(im_pt)
    else:
        im_p = im_pt
    if not sv_pt:
        save_path = im_p.parent
    else:
        if isinstance(sv_pt, str):
            save_path = Path(sv_pt)
        else:
            save_path = sv_pt
    if not ext:
        save_path = save_path / im_p.name
    else:
        save_path = save_path / (im_p.stem+ext)
    im = Image.open(im_p)
    if md:
        im = im.convert(md)
    if re_sz:
        if isinstance(re_sz, int):
            sz = (re_sz, re_sz)
        else:
            sz = re_sz
        im = im.resize(sz, resample=eval("Image." + rs_md.upper()))
    if dpi:
        if isinstance(dpi, (int, float)):
            im_dpi = dpi, dpi
        else:
            im_dpi = dpi
        im.info['dpi'] = im_dpi
        im.save(save_path, dpi=im_dpi)
    else:
        im.save(save_path)
    if rm_flag:
        im_p.unlink()
    return save_path
