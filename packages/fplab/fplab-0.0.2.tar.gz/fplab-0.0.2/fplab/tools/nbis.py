"""调用NBIS的一些函数
nfiq
nfiq2
nfiq_n
mindtct_n
bozorth_xyt
bozorth
"""
import numpy as np
from os import popen, system
from pathlib import Path
from fplab.tools.image import change_image, get_data_dirs
from time import strftime, localtime
from tqdm import tqdm
from fplab.matching.tools import analyse_score


def nfiq(im_dir, src_dir=r'C:\SRC\NBIS\Main\bin\nfiq.exe', temp_flag=True, temp_dir=None):
    """封装NBIS的NFIQ程序
    im_dir是图像路径
    src_dir是NFIQ源程序路径
    temp_flag控制是否生成缓存文件
    temp_dir为缓存图像所在路径，默认为./temp_images
    由于NFIQ对输入有一定要求（图像格式、分辨率、通道数等），当temp_flag为真时程序会对输入进行一定处理，产生缓存图像
    正常输出是1-5，若出现其余结果则返回-1"""
    if temp_flag:
        if isinstance(temp_dir, str):
            temp_path = Path(temp_dir)
        else:
            temp_path = Path("temp_images")
        temp_path.mkdir(parents=True, exist_ok=True)
        im = change_image(Path(im_dir), sv_pt=temp_path, ext='.png', dpi=(500, 500), md="L")
        im = str(im.absolute())
    else:
        im = im_dir
    q = popen(src_dir + f" -d {im}").read().strip()
    if q.isdigit():
        return int(q), q
    else:
        return -1, q


def nfiq2(im_dir, src_dir=r'C:\SRC\NFIQ2\bin\nfiq2.exe', temp_flag=True, temp_dir=None):
    """封装NBIS的NFIQ2程序
    im_dir是图像路径
    src_dir是NFIQ2源程序路径
    temp_flag控制是否生成缓存文件
    temp_dir为缓存图像所在路径，默认为./temp_images
    由于NFIQ2对输入有一定要求（图像格式、分辨率、通道数等），当temp_flag为真时程序会对输入进行一定处理，产生缓存图像
    正常输出是0-100，若出现其余结果则返回-1"""
    if temp_flag:
        if isinstance(temp_dir, str):
            temp_path = Path(temp_dir)
        else:
            temp_path = Path("temp_images")
        temp_path.mkdir(parents=True, exist_ok=True)
        im = change_image(Path(im_dir), sv_pt=temp_path, ext='.png', dpi=(500, 500), md="L")
        im = str(im.absolute())
    else:
        im = im_dir
    q = popen(src_dir + f" -i {im}").read().strip()
    if q.isdigit():
        return int(q), q
    else:
        return -1, q


def nfiq_n(ims_dir, md="nfiq", src_dir=None, name=None,
           script_flag=True, script_dir=None, temp_flag=True, temp_dir=None, keep_temp=False):
    """使用NFIQ或NFIQ2处理多张指纹图像
    ims_dir是图像路径
    md是质量评价函数
    src_dir是源程序路径
    name是处理数据集的名字
    script_flag控制是否生成结果文本文件
    script_dir为结果文本文件所在路径，默认为./scripts
    temp_flag控制是否生成缓存文件
    temp_dir为缓存图像所在路径，默认为./temp_images
    keep_temp决定是否保留生成的缓存文件
    由于NFIQ和NFIQ2对输入有一定要求（图像格式、分辨率、通道数等），当temp_flag为真时程序会对输入进行一定处理，产生缓存图像
    正常输出是1-5或0-100，若出现其余结果则返回-1"""
    if isinstance(ims_dir, list):
        im_dirs = ims_dir
    else:
        im_dirs = []
        im_dirs = get_data_dirs(Path(ims_dir), im_dirs)
    if md == "nfiq":
        q_func = nfiq
    elif md == "nfiq2":
        q_func = nfiq2
    else:
        raise Exception("Unknown Quality Function!")
    if src_dir:
        src = src_dir
    else:
        src = q_func.__defaults__[0]
    if isinstance(temp_dir, str):
        temp_path = Path(temp_dir)
    else:
        temp_path = Path("temp_images")
    if temp_flag:
        temp_path.mkdir(parents=True, exist_ok=True)
    quality, information, directory = [], [], []
    with tqdm(total=len(im_dirs)) as pbar:
        pbar.set_description("正在计算指纹的质量分数:")
        for im_dir in im_dirs:
            q, i = q_func(im_dir, src, temp_flag, str(temp_path.absolute()))
            quality.append(q)
            information.append(i)
            directory.append(im_dir)
            pbar.update(1)
    quality = np.array(quality)
    if script_flag:
        if isinstance(script_dir, str):
            script_path = Path(script_dir)
        else:
            script_path = Path("scripts")
        script_path.mkdir(parents=True, exist_ok=True)
        script_file = script_path/strftime("%Y%m%d%H%M%S.txt", localtime())
        with open(script_file, "w") as sf:
            sf.write(f"数据集:\t\t{name}\n")
            sf.write(f"模式:\t\t{md}\n")
            sf.write(f"源程序路径:\t\t{src}\n")
            sf.write(f"生成文本:\t\t{script_flag}\n")
            sf.write(f"文本路径:\t\t{str(script_path.absolute())}\n")
            sf.write(f"生成缓存:\t\t{temp_flag}\n")
            sf.write(f"缓存路径:\t\t{str(temp_path.absolute())}\n")
            sf.write(f"是否保留缓存:\t\t{keep_temp}\n")
            sf.write(f"图像数目:\t\t{quality.size}\n")
            sf.write(f"有效图像数目:\t\t{quality[quality != -1].size}\n")
            sf.write(f"质量均值:\t\t{quality.mean()}\n")
            if quality[quality != -1].size > 0:
                sf.write(f"有效质量均值:\t\t{quality[quality != -1].mean()}\n")
            else:
                sf.write(f"有效质量均值:\t\terror\n")
            sf.write("质量分数\t\t文件地址\t\t\t\t\t\t\t\t\t\t\t\t提示信息\n")
            for i in range(quality.size):
                sf.write(f"{quality[i]}\t\t\t{directory[i]}\t\t\t{information[i]}\n")
    if (not keep_temp) and temp_flag:
        temp_dirs = []
        temp_dirs = get_data_dirs(temp_path, temp_dirs)
        for d in temp_dirs:
            Path(d).unlink()
        temp_path.rmdir()
    return quality, directory, information


def mindtct_n(ims_dir, out_dir, need_out=None, src_dir=r'C:\SRC\NBIS\Main\bin\mindtct.exe',
              temp_flag=True, temp_dir=None, keep_temp=False):
    """封装NBIS的mindtct程序
    ims_dir是图像地址，可以为单个图像地址或图像文件夹地址
    out_dir是输出结果文件夹地址
    need_out返回指定文件类型地址，如need_out=".xyt"，那么函数将返回后缀名为".xyt"的所有输出地址
    src_dir是mindtct源程序地址
    temp_flag控制是否生成缓存文件
    temp_dir为缓存图像所在路径，默认为./temp_images
    keep_temp决定是否保留生成的缓存文件
    由于mindtct对输入有一定要求（图像格式、分辨率、通道数等），当temp_flag为真时程序会对输入进行一定处理，产生缓存图像
    mindtct [-b] [-m1] <img> <out>
    -b  增强图像对比度
    -m1 细节点格式
    xyt文件 x y 角度 质量
    """
    if Path(ims_dir).is_file():
        root_dir = str(Path(ims_dir).parent.absolute())
        im_dirs = [str(Path(ims_dir).absolute()),]
    else:
        root_dir = str(Path(ims_dir).absolute())
        im_dirs = []
        im_dirs = get_data_dirs(Path(ims_dir), im_dirs)
    if isinstance(temp_dir, str):
        temp_path = Path(temp_dir)
    else:
        temp_path = Path("temp_images")
    if temp_flag:
        temp_path.mkdir(parents=True, exist_ok=True)
    out = []
    with tqdm(total=len(im_dirs)) as pbar:
        pbar.set_description("正在提取细节点:")
        for im_dir in im_dirs:
            save_dir = im_dir.replace(root_dir, out_dir).split(".")[0]
            Path(save_dir).parent.mkdir(parents=True, exist_ok=True)
            if temp_flag:
                im_d = change_image(Path(im_dir), sv_pt=temp_path, ext='.png', dpi=(500, 500), md="L")
                im_d = str(im_d.absolute())
            else:
                im_d = im_dir
            system(src_dir+" "+im_d+" "+save_dir)
            if need_out:
                out.append(save_dir+need_out)
            pbar.update(1)
    if (not keep_temp) and temp_flag:
        temp_dirs = []
        temp_dirs = get_data_dirs(temp_path, temp_dirs)
        for d in temp_dirs:
            Path(d).unlink()
        temp_path.rmdir()
    return out


def bozorth_xyt(p_xyt_dirs, g_xyt_dirs, src_dir=r'C:\SRC\NBIS\Main\bin\bozorth3.exe',
                script_flag=True, script_dir=None, p_name=None, g_name=None):
    """封装NIST的Bozorth程序
    p_xyt_dirs是待识别细节点，可以为细节点文件地址列表或细节点文件所在目录
    g_xyt_dirs是模板细节点，可以为细节点文件地址列表或细节点文件所在目录
    script_flag控制是否生成结果文本文件
    script_dir为结果文本文件所在路径，默认为./scripts
    p_name, g_name用来标识数据
    函数将输出p_xyt_dirs与g_xyt_dirs的匹配分数矩阵"""
    if isinstance(p_xyt_dirs, list):
        probe_dirs = p_xyt_dirs
    else:
        probe_dirs = []
        probe_dirs = get_data_dirs(Path(p_xyt_dirs), probe_dirs, ext=".xyt")
    if isinstance(g_xyt_dirs, list):
        gallery_dirs = g_xyt_dirs
    else:
        gallery_dirs = []
        gallery_dirs = get_data_dirs(Path(g_xyt_dirs), gallery_dirs, ext=".xyt")
    match_score = np.zeros((len(probe_dirs), len(gallery_dirs)), dtype=np.int8)
    with tqdm(total=match_score.size) as pbar:
        pbar.set_description("正在匹配:")
        for i in range(len(probe_dirs)):
            for j in range(len(gallery_dirs)):
                s = popen(src_dir + f" {probe_dirs[i]} {gallery_dirs[j]}").read().strip()
                if s.isdigit():
                    match_score[i, j] = min(int(s), 127)
                else:
                    match_score[i, j] = -1
                pbar.update(1)
    if isinstance(script_dir, str):
        script_path = Path(script_dir)
    else:
        script_path = Path("scripts") / strftime("%Y%m%d%H%M%S", localtime())
    if script_flag:
        script_path.mkdir(parents=True, exist_ok=True)
        score_file = script_path / "match_score.txt"
        score_data = script_path / 'match_score.npy'
        probe_file = script_path / 'probe_dirs.txt'
        gallery_file = script_path / 'gallery_dirs.txt'
        np.save(score_data, match_score)
        with open(probe_file, "w") as pf:
            for pd in probe_dirs:
                pf.write(pd+"\n")
        with open(gallery_file, "w") as gf:
            for gd in gallery_dirs:
                gf.write(gd+"\n")
        with open(score_file, "w") as sf:
            sf.write(f"目标数据集:\t\t{p_name}\n")
            sf.write(f"库数据集:\t\t{g_name}\n")
            sf.write(f"源程序路径:\t\t{src_dir}\n")
            sf.write(f"生成文本:\t\t{script_flag}\n")
            sf.write(f"文本路径:\t\t{str(script_path.absolute())}\n")
            sf.write(f"匹配结果路径:\t\t{str(score_data.absolute())}\n")
            sf.write(f"目标路径列表:\t\t{str(probe_file.absolute())}\n")
            sf.write(f"库路径列表:\t\t{str(gallery_file.absolute())}\n")
            sf.write(f"目标数据数目:\t\t{len(probe_dirs)}\n")
            sf.write(f"库数据数目:\t\t{len(gallery_dirs)}\n")
            sf.write(f"匹配分数最大值:\t\t{match_score.max()}\n")
            sf.write(f"匹配分数最小值:\t\t{match_score.min()}\n")
            sf.write(f"若匹配分数最小值小于0，则该结果没有参考性。\n")
            sf.write(f"匹配分数均值:\t\t{match_score.mean()}\n")
            sf.write(f"匹配分数中值:\t\t{np.median(match_score)}\n")
            sf.write("匹配分数\t\t目标指纹\t\t\t\t\t\t\t\t\t\t\t\t库指纹\n")
            for i in range(len(probe_dirs)):
                for j in range(len(gallery_dirs)):
                    sf.write(f"{match_score[i, j]}\t\t\t{probe_dirs[i]}\t\t\t{gallery_dirs[j]}\n")
    return match_score, probe_dirs, gallery_dirs, script_path


def bozorth(p_dirs=None, g_dirs=None, p_xyt_dirs=None, g_xyt_dirs=None,
            min_dir=None, script_dir=None, p_name=None, g_name=None,
            need_analyse=False, identify_ranks=None, verify_ranks=None,
            j_func=None, **kwargs):
    """将NBIS的mindtct和bozorth组合到一起
    p_dirs, g_dirs为目标图像地址和库图像地址
    p_xyt_dirs, g_xyt_dirs为目标图像细节点地址和库图像细节点地址，
    p_dirs, g_dirs, p_xyt_dirs, g_xyt_dirs可以为单个图像地址或图像文件夹地址，且dirs和xyt_dirs只需存在一个
    min_dir用来存放提取的细节点
    script_dir为结果文本文件所在路径，默认为./scripts
    p_name, g_name用来标识数据
    need_analyse控制是否分析数据
    identify_ranks是识别精度，比如rank-1, rank-5，可以为整数或整数列表
    verify_ranks控制匹配分数阈值，可以为整数或整数列表
    j_func和**kwargs用来根据文件地址判断两个文件是否属于同一个指纹"""
    if isinstance(min_dir, str):
        min_path = Path(min_dir)
    else:
        min_path = Path("min_data")
    if p_xyt_dirs:
        if Path(p_xyt_dirs).is_file():
            probe_xyt_dirs = [str(Path(p_xyt_dirs).absolute()),]
        else:
            probe_xyt_dirs = []
            probe_xyt_dirs = get_data_dirs(Path(p_xyt_dirs), probe_xyt_dirs, ext=".xyt")
    elif p_dirs:
        out_dir = str((min_path/"probe").absolute())
        probe_xyt_dirs = mindtct_n(p_dirs, out_dir, need_out='.xyt')
    else:
        raise Exception("No p_dirs is specified!")
    if g_xyt_dirs:
        if Path(g_xyt_dirs).is_file():
            gallery_xyt_dirs = [str(Path(g_xyt_dirs).absolute()),]
        else:
            gallery_xyt_dirs = []
            gallery_xyt_dirs = get_data_dirs(Path(g_xyt_dirs), gallery_xyt_dirs, ext=".xyt")
    elif g_dirs:
        out_dir = str((min_path/"gallery").absolute())
        gallery_xyt_dirs = mindtct_n(g_dirs, out_dir, need_out='.xyt')
    else:
        raise Exception("No g_dirs is specified!")
    if isinstance(script_dir, str):
        script_path = Path(script_dir) / strftime("%Y%m%d%H%M%S", localtime())
        script_d = str(script_path.absolute())
    else:
        script_path = Path("scripts") / strftime("%Y%m%d%H%M%S", localtime())
        script_d = str(script_path.absolute())
    score, probe_dirs, gallery_dirs, script_path = bozorth_xyt(probe_xyt_dirs, gallery_xyt_dirs,
                                                               script_dir=script_d, p_name=p_name, g_name=g_name)
    if need_analyse:
        script_stem = str(script_path.absolute())
        out_i, out_v = analyse_score(score, probe_dirs, gallery_dirs, script_stem,
                                     rk_i=identify_ranks, rk_v=verify_ranks, j_func=j_func, **kwargs)
        return out_i, out_v
    else:
        return score, probe_dirs, gallery_dirs, script_path
