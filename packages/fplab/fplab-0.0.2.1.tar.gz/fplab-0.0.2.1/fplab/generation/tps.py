"""薄板样条tps的有关函数
get_box             获取盒子点集
get_ellipse         获取椭圆点集
get_index           计算变换坐标关系
display_point       展示控制点及对应关系
display_transform   展示扭曲效果
tps                 薄板样条扭曲图像
"""
import cv2
import numpy as np
from scipy.interpolate import RBFInterpolator
from scipy.ndimage import map_coordinates
from fplab.tools.image import type_as
from fplab.tools.array import IMA


def get_box(h, w, dt, db, dl, dr, step_h=1, step_w=1):
    """生成盒子的边界点集
    h, w                    图像大小
    dt, db, dl, dr          盒子距离四个边界的距离
    step_h, step_w          生成点时的步长
    """
    h0, h1 = dt, h-db-1
    w0, w1 = dl, w-dr-1
    pts = []
    for i in [h0, h1]:
        for j in range(w0, w1 + 1, step_h):
            pts.append([i, j])
    for j in [w0, w1]:
        for i in range(h0 + step_h, h1, step_w):
            pts.append([i, j])
    return np.array(pts)


def get_ellipse(ch, cw, ra, rb, pn, ag):
    """生成椭圆点集
    ch, cw      中心位置
    ra, rb      长短轴长度
    pn          点数
    ag          旋转弧度"""
    pts = []
    for n in range(pn):
        t = (n/pn)*2*np.pi
        u, v = ra*np.cos(t), rb*np.sin(t)
        du, dv = u*np.cos(ag)-v*np.sin(ag), u*np.sin(ag)+v*np.cos(ag)
        pts.append([ch+du, cw+dv])
    return np.array(pts)


def get_index(fix_p: np.ndarray, old_p: np.ndarray, new_p: np.ndarray, sp):
    """计算tps的坐标对应关系
    fix_p       变换过程不动点
    old_p       原图像需要变动的点
    new_p       old_p变动后的点
    sp          图像的大小，整数或2维整数元组
    fix_p、old_p和new_p形式为n*2维ndarray数组，old_p和new_p的点应该对应"""
    if isinstance(sp, int):
        h, w = sp, sp
    else:
        h, w = sp[:2]
    pt0 = np.vstack((old_p, fix_p))
    pt1 = np.vstack((new_p, fix_p))
    # 根据两个点集坐标的变换关系，插值出两个坐标的变换函数
    dh, dw = pt1[:, 0]-pt0[:, 0], pt1[:, 1]-pt0[:, 1]
    predictor_dh = RBFInterpolator(pt1, dh, kernel='thin_plate_spline')
    predictor_dw = RBFInterpolator(pt1, dw, kernel='thin_plate_spline')
    # 计算出图像每一个像素位置对应的变换后的位置
    grid = np.mgrid[0:h, 0:w].reshape(2, -1).T
    res_dh, res_dw = predictor_dh(grid), predictor_dw(grid)
    ind_h = grid[:, 0] + res_dh
    ind_h = ind_h.reshape(h, w)
    ind_w = grid[:, 1] + res_dw
    ind_w = ind_w.reshape(h, w)
    return ind_h, ind_w


def display_point(fix_p, old_p, new_p, sp, step=5,
                  fix_color=(0, 0, 0), old_color=(0, 255, 0), new_color=(0, 0, 255),
                  arrow_color=(255, 0, 0), thickness=1, tip_length=0.3):
    """展示三个点集以及old_p和new_p之间的对应关系（有向箭头）
    fix_p                               变换过程不动点
    old_p                               原图像需要变动的点
    new_p                               old_p变动后的点
    sp                                  图像的大小，整数或2维整数元组
    step                                每几个点展示一次对应关系，若都展示则太密，效果不好
    fix_p、old_p和new_p形式为n*2维ndarray数组，old_p和new_p的点应该对应
    fix_color, old_color, new_color     点的颜色
    arrow_color, thickness, tip_length  箭头属性
    """
    ima = np.ones((sp[0], sp[1], 3))
    for p in fix_p:
        ima[round(p[0]), round(p[1]), :] = fix_color
    for p in old_p:
        ima[round(p[0]), round(p[1]), :] = old_color
    for p in new_p:
        ima[round(p[0]), round(p[1]), :] = new_color
    for i in range(len(old_p)):
        if i % step == 0:
            cv2.arrowedLine(ima, (round(old_p[i, 1]), round(old_p[i, 0])),
                            (round(new_p[i, 1]), round(new_p[i, 0])),
                            arrow_color, thickness, tipLength=tip_length)
    IMA(ima).show()


def display_transform(sp, index, blk_sz=(16, 16), g_color=(1., 0, 0)):
    """在网格上展示变换效果
    sp              图像的大小，整数或2维整数元组
    index           用于变换的索引，两个分量分别为两个方向的索引
    blk_sz          网格大小
    g_color         网格颜色
    """
    if isinstance(blk_sz, (float, int)):
        bsp = blk_sz, blk_sz
    else:
        bsp = blk_sz
    if isinstance(g_color, (float, int)):
        grid_color = g_color, g_color, g_color
    else:
        grid_color = g_color
    grid_im = np.ones((sp[0], sp[1], 3))
    for i in range(sp[0]):
        for j in range(sp[1]):
            if (i % bsp[0] == 0) or (j % bsp[1] == 0):
                grid_im[i, j, :] = grid_color
    out = np.zeros_like(grid_im)
    for i in range(grid_im.shape[2]):
        out[:, :, i] = map_coordinates(grid_im[:, :, i], [index[0], index[1]], cval=1.)
    IMA(out).show()


def tps(im, fix_p_c=None, old_p_c=None, new_p_c=None, pad_md='constant', pad_v=0.,
        display_point_flag=False, display_transform_flag=False, display_out_flag=False):
    """使用薄板样条(ThinPlateSpline)方法扭曲图像"""
    ima = type_as(im, md="a")
    h, w = ima.shape[:2]
    if fix_p_c is None:
        fix_p_dict = {"dt": 15, "db": 15, "dl": 15, "dr": 15, "step_h": 1, "step_w": 1}
    else:
        fix_p_dict = fix_p_c
    fix_p_dict["h"], fix_p_dict["w"] = h, w
    if old_p_c is None:
        old_p_dict = {"ch": h-h//2, "cw": w-w//2, "ra": h//12, "rb": w//16, "pn": 200, "ag": 0}
    else:
        old_p_dict = old_p_c
    if new_p_c is None:
        new_p_dict = {"ch": h-h//2, "cw": w-w//2, "ra": h//6, "rb": w//8, "pn": 200, "ag": 0.15}
    else:
        new_p_dict = new_p_c
    # 获取点集
    fix_p = get_box(**fix_p_dict)
    old_p = get_ellipse(**old_p_dict)
    new_p = get_ellipse(**new_p_dict)
    if display_point_flag:
        display_point(fix_p, old_p, new_p, sp=(h, w), step=round(old_p_dict["pn"]/20))
    ind_h, ind_w = get_index(fix_p, old_p, new_p, sp=(h, w))
    if display_transform_flag:
        display_transform((h, w), index=[ind_h, ind_w])
    if ima.ndim == 2:
        out = map_coordinates(ima, [ind_h, ind_w], mode=pad_md, cval=pad_v)
    else:
        # 当im是RGB图像时，对每一个通道作相同的处理
        out = np.zeros_like(ima)
        for i in range(ima.shape[2]):
            pv = pad_v
            if pad_md == 'constant':
                if isinstance(pad_v, (list, tuple, np.ndarray)):
                    pv = pad_v[i]
            out[:, :, i] = map_coordinates(ima[:, :, i], [ind_h, ind_w], mode=pad_md, cval=pv)
    if display_out_flag:
        IMA(out).show()
    out = type_as(out, im)
    return out
