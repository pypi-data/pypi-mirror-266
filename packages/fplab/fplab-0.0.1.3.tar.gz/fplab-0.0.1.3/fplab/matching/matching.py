"""
匹配过程常用函数
default_judge_func      判断两个文件名字是否相等
get_paired              通过指定判断函数判断配对指纹
analyse_score           分析匹配矩阵
"""


from pathlib import Path
import numpy as np
from matplotlib import pyplot as plt


def default_judge_func(x, y, **kwargs):
    """判断文件x和y是否名字相同
    x和y为文件的字符串形式地址"""
    if kwargs:
        pass
    x_stem, y_stem = Path(x).stem, Path(y).stem
    if x_stem == y_stem:
        return True
    else:
        return False


def get_paired(p_list, g_list, j_func=None, **kwargs):
    """根据指定的判断函数，寻找与p_list的元素对应的g_list的元素
    p_list, g_list为字符串形式地址组成的列表
    j_func为判断函数，参数中必须有两个输入，其余参数通过**kwargs传递"""
    if not j_func:
        judge_func = default_judge_func
    else:
        judge_func = j_func
    paired_list = []
    for i in range(len(p_list)):
        temp_list = []
        for j in range(len(g_list)):
            if judge_func(p_list[i], g_list[j], **kwargs):
                temp_list.append(j)
            else:
                continue
        paired_list.append(temp_list)
    return paired_list


def analyse_score_identify(score, paired_list, rk=None):
    """根据匹配关系paired_list分析匹配矩阵score，输出识别结果
    score是匹配器产生的匹配分数矩阵，行对应目标指纹，列对应库指纹
    paired_list是匹配关系列表，每一个子列表表示一个目标指纹对应的库指纹
    rk表示允许匹配指纹的匹配分数出现在前rk位，rk可以为整数或整数列表，默认为1"""
    if isinstance(rk, int):
        ranks = [rk,]
    elif isinstance(rk, list) and isinstance(rk[0], int):
        ranks = rk
    else:
        ranks = [1,]
    ranks_max = np.array(ranks).max()
    index_sorted_max = (np.argsort(score, axis=1)[:, -ranks_max:]).copy()
    out = dict()
    for r in ranks:
        key = f"rank{r}"
        out[key] = 0
        index_sorted = (index_sorted_max[:, -r:]).copy()
        for i in range(len(paired_list)):
            p_list = paired_list[i]
            index = index_sorted[i, :]
            for ind in p_list:
                # 只要某一个对应的库指纹被指出，那么就认为识别成功
                if ind in index:
                    out[key] = out[key]+1
                    break
        out[key] = out[key]/len(paired_list)
    return out


def analyse_score_verify(score, paired_list, rk=None):
    """根据匹配关系paired_list分析匹配矩阵score，输出匹配结果
    score是匹配器产生的匹配分数矩阵，行对应目标指纹，列对应库指纹
    paired_list是匹配关系列表，每一个子列表表示一个目标指纹对应的库指纹
    rk表示匹配分数阈值，可以为一维数组或整数"""
    if isinstance(rk, int):
        ranks = np.linspace(score.min(), score.max(), rk)
    elif isinstance(rk, np.ndarray):
        ranks = rk
    else:
        ranks = np.linspace(score.min(), score.max(), num=8)
    ranks = np.round(ranks, 2)
    out = {}
    genuine, imposter = [], []
    for i in range(score.shape[0]):
        p_list = paired_list[i]
        for j in range(score.shape[1]):
            if j in p_list:
                genuine.append(score[i, j])
            else:
                imposter.append(score[i, j])
    genuine, imposter = np.array(genuine), np.array(imposter)
    g_n, i_n = genuine.size, imposter.size
    difference, average = [], []
    for r in np.nditer(ranks):
        key = f"score{r}"
        pf_ft_n = (genuine[genuine < r]).size
        pt_ff_n = (imposter[imposter >= r]).size
        pf_ft_r, pt_ff_r = pf_ft_n/g_n, pt_ff_n/i_n
        out[key] = {"pt_ft_n": g_n-pf_ft_n,
                    "pf_ft_n": pf_ft_n,
                    "pt_ff_n": pt_ff_n,
                    "pf_ff_n": i_n-pt_ff_n,
                    "pf_ft_r": round(pf_ft_r, 4),
                    "pt_ff_r": round(pt_ff_r, 4),
                    "difference": round(np.abs(pf_ft_r-pt_ff_r), 4),
                    "average": round((pf_ft_r+pt_ff_r)/2, 2)}
        difference.append(np.abs(pf_ft_r-pt_ff_r))
        average.append((pf_ft_r+pt_ff_r)/2)
    eer = average[np.argmin(np.array(difference))]
    return out, eer, genuine, imposter


def analyse_score(score, p_dirs, g_dirs, script_stem, rk_i=None, rk_v=None, j_func=None, **kwargs):
    """分析匹配矩阵score
    score是匹配器产生的匹配分数矩阵，行对应目标指纹，列对应库指纹
    p_dirs和g_dirs是目标指纹和库指纹的地址列表，分别与score的行列对应
    script_stem是所有生成的文本文件的前缀，需要为字符串形式
    rk_i，rk_v分别表示识别的rank-n和匹配的分数阈值，可以为一维数组或整数
    j_func，**kwargs用于判断p_dirs和g_dirs的匹配项，使用方法见get_paired"""
    paired_list = get_paired(p_dirs, g_dirs, j_func=j_func, **kwargs)
    out_identify = analyse_score_identify(score, paired_list, rk=rk_i)
    out_verify, eer, genuine, imposter = analyse_score_verify(score, paired_list, rk=rk_v)
    paired_file = Path(script_stem) / 'paired_list.txt'
    analyse_file = Path(script_stem) / 'analyse.txt'
    analyse_fig = Path(script_stem) / 'verify_out.png'
    with open(paired_file, "w") as pf:
        pf.write("目标指纹\t\t\t\t库指纹\n")
        for i in range(len(paired_list)):
            pd = p_dirs[i]
            for gd in paired_list[i]:
                pf.write(pd + "\t\t\t\t" + g_dirs[gd] + "\n")
    with open(analyse_file, "w") as af:
        af.write(f"文件前缀:\t\t{script_stem}\n")
        af.write(f"匹配关系:\t\t{paired_file}\n")
        af.write(f"识别等级:\t\t{rk_i}\n")
        af.write(f"验证等级:\t\t{rk_v}\n")
        af.write(f"判别函数:\t\t{j_func}\n")
        af.write(f"额外参数:\t\t{kwargs}\n")
        af.write(f"真指纹对数目:\t\t{genuine.size}\n")
        af.write(f"假指纹对数目:\t\t{imposter.size}\n")
        af.write(f"识别结果：\n")
        for k, v in out_identify.items():
            af.write(f"{k}:\t{round(v, 4)}\n")
        af.write(f"验证结果：\n")
        af.write(f"相等错误率：{eer}\n")
        af.write(f"score:\tpt_ft_n\tpf_ft_n\tpt_ff_n\tpf_ff_n\tpf_ft_r\tpt_ff_r\tdifference\taverage\n")
        for k, v in out_verify.items():
            af.write(f"{k}:\t{v['pt_ft_n']}\t{v['pf_ft_n']}\t{v['pt_ff_n']}\t{v['pf_ff_n']}\t"
                     f"{v['pf_ft_r']}\t{v['pt_ff_r']}\t{v['difference']}\t{v['average']}\n")
    plt.hist([genuine, imposter], 40, (score.min(), score.max()), density=True)
    plt.savefig(analyse_fig)
    return out_identify, out_verify
