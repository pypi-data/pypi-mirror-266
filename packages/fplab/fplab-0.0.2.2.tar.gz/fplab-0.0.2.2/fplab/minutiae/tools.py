"""指纹细节点相关函数
xyt2array       从xyt文件中读取细节点
array2xyt       将细节点保存到xyt文件
show_mnt        展示细节点
select_mnt      根据质量选取细节点
mnt2map         根据细节点分布生成权重图
"""
import cv2
import numpy as np
from pathlib import Path
from functools import partial
from fplab.tools.image import type_as
from fplab.tools.array import IMA, ima_gaussian


def xyt2array(xyt_d, sp):
    """从xyt文件中读取细节点信息
    xyt_d   xyt文件地址，字符串形式或Path形式
    sp      xyt文件对应的图像长宽，整数或2维整数元组
    返回细节点行列索引、弧度和质量以及对应图像高宽"""
    # 处理输入sp
    if isinstance(sp, int):
        h, w = sp, sp
    else:
        h, w = sp
    # 读取xyt文件
    with open(xyt_d, 'r') as xyt_f:
        mts = xyt_f.readlines()
    # 行索引、列索引、弧度和质量
    ind_h, ind_w, angle, quality = [], [], [], []
    for i in range(len(mts)):
        mt = mts[i].strip().split()
        # xy直角坐标系转化为hw坐标系
        ind_h.append(h-int(mt[1])-1)
        ind_w.append(int(mt[0]))
        # 转化为弧度
        angle.append(int(mt[2])/180.*np.pi)
        # 考虑xyt可能无质量信息
        if len(mt) == 3:
            quality.append(1.)
        else:
            quality.append(int(mt[3])/100.)
    out = {"ind_hw": np.array([ind_h, ind_w], dtype=np.int32),
           "angle": np.array(angle, dtype=np.float32),
           "quality": np.array(quality, dtype=np.float32),
           "shape": (h, w)}
    return out


def array2xyt(mt, xyt_d):
    """将细节点mt保存到xyt文件
    mt      字典，格式需要与xyt2array的输出格式相同
    xyt_d   xyt文件地址，字符串形式或Path形式"""
    if isinstance(xyt_d, str):
        xyt_p = Path(xyt_d)
    else:
        xyt_p = xyt_d
    xyt_p.parent.mkdir(parents=True,exist_ok=True)
    with open(xyt_p, 'w') as xyt_f:
        for i in range(mt["ind_hw"].shape[1]):
            x = mt["ind_hw"][1, i]
            y = mt["shape"][0]-mt["ind_hw"][0, i]-1
            t = round(mt["angle"][i]/np.pi*180)
            q = round(mt["quality"][i]*100)
            xyt_f.write(f"{x} {y} {t} {q}\n")


def show_mnt(mt, im, th_q=0, q_flag=False, max_l=12,
             color=(255, 0, 0), thickness=1, tip_length=0.3,
             flag=("show", "save", "return"), save_path=None):
    """在图像im上展示细节点mt。
    mt          细节点，格式需要与xyt2array的输出相同。
    im          指纹图像，可以为(h, w, 3)或(h, w)的数组，(1, h, w)或(3, h, w)的张量。
    th_q        质量阈值，质量小于该值的细节点不显示
    q_flag      是否根据细节点质量控制线段长度
    max_l       最大线段长度
    color       三元元组，控制绘制线段的RGB值，默认为红色
    thickness   整数，控制绘制线段的宽度，默认为1
    tip_length  0，1之间的浮点数，控制箭头相对于线段的长度，默认为0.3
    flag        控制函数的行为：展示结果图像（"show"）、保存结果图像（"save"）、返回结果图像（"return"）
                "save"命令需要配合save_path使用，若未指定save_path，则该命令将不会起作用
    save_path   可以为字符串或Path对象
    一般地，该程序返回RGB图像，若是需要L图像，可以手动转换"""
    # 方向线段将画到ima上
    ima = IMA(type_as(im, md="a")).l2rgb()
    # 计算每一个细节点对应的线段的起点、终点，并绘制线段
    for i in range(mt["ind_hw"].shape[1]):
        q = mt["quality"][i]
        if q < th_q:
            continue
        start_h, start_w = mt["ind_hw"][0, i], mt["ind_hw"][1, i]
        t = mt["angle"][i]
        if q_flag:
            c = q
        else:
            c = 1
        end_h = round(start_h-np.sin(t)*c*max_l)
        end_w = round(start_w+np.cos(t)*c*max_l)
        cv2.arrowedLine(ima.ima, (start_w, start_h), (end_w, end_h), color, thickness, tipLength=tip_length)
    if "show" in flag:
        ima.show()
    if "save" in flag and save_path:
        if isinstance(save_path, str):
            save_pt = Path(save_path)
        else:
            save_pt = save_path
        ima.save(save_pt)
    if "return" in flag:
        return type_as(ima.ima, im)


def select_mnt(mt, th_q):
    """选取mt中质量大于等于th_q的细节点
    mt              细节点，格式需要与xyt2array的输出相同。
    th_q            质量阈值，去除质量小于该值的细节点"""
    q = mt["quality"]
    flag = (q >= th_q)
    ind_h = mt["ind_hw"][0][flag]
    ind_w = mt["ind_hw"][1][flag]
    angle = mt["angle"][flag]
    quality = mt["quality"][flag]
    shape = mt["shape"]
    out = {"ind_hw": np.array([ind_h, ind_w], dtype=np.int32),
           "angle": angle.copy(),
           "quality": quality.copy(),
           "shape": shape}
    return out


def mnt2map(mt, th_q=0.2, fix_v=1., use_quality=False, filter_fn=None):
    """根据细节点mt生成权重图
    mt              细节点，格式需要与xyt2array的输出相同。
    th_q            质量阈值，去除质量小于该值的细节点
    fix_v           初始细节点图细节点处的值
    use_quality     使用细节点质量还是fix_v作为初始细节点图细节点处的值
    filter_fn       处理初始细节点的函数，接受细节点（np.ndarray）作为参数
                    默认使用大小为35标准差为8的高斯滤波（FingerGAN）
    该函数没有限定权重的最小值，也没有将结果线性映射到某一范围，需要额外设置"""
    if filter_fn is None:
        filter_fn = partial(ima_gaussian, ksz=35, sigma=8)
    mnt = select_mnt(mt, th_q)
    mta = np.zeros(mnt["shape"])
    if use_quality:
        mta[mnt["ind_hw"][0], mnt["ind_hw"][1]] = mnt["quality"]
    else:
        mta[mnt["ind_hw"][0], mnt["ind_hw"][1]] = fix_v
    out = filter_fn(mta)
    return out
