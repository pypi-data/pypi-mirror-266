# -*- coding: utf-8 -*-
from latexdocs import float_to_str_sig
from functools import partial


xlam_strs_labels = [
    "sxx_m_t",
    "syy_m_t",
    "sxy_m_t",
    "sxx_m_b",
    "syy_m_b",
    "sxy_m_b",
    "sxx_n",
    "syy_n",
    "sxy_n",
    "sxz_max",
    "syz_max",
    "srx_max",
    "sry_max",
]

xlam_strs_tex_labels = [
    r"$\sigma_{xx,m,t}$",
    r"$\sigma_{yy,m,t}$",
    r"$\sigma_{xy,m,t}$",
    r"$\sigma_{xx,m,b}$",
    r"$\sigma_{yy,m,b}$",
    r"$\sigma_{xy,m,b}$",
    r"$\sigma_{xx,n}$",
    r"$\sigma_{yy,n}$",
    r"$\sigma_{xy,n}$",
    r"$\sigma_{xz,max}$",
    r"$\sigma_{yz,max}$",
    r"$\sigma_{rx,max}$",
    r"$\sigma_{ry,max}$",
]


def combination_to_str(factors, names, tex=False, inline=True, sig=4):
    f2str = partial(float_to_str_sig, sig=sig)

    factors_str = list(map(f2str, factors))
    if not tex:
        return r" + ".join(
            [r"{} * {}".format(f, n) for f, n in zip(factors_str, names)]
        )
    else:
        if inline:
            return r"\,\,+\,\,".join(
                [r"${}$ $\cdot$ {}".format(f, n) for f, n in zip(factors_str, names)]
            )
        else:
            return r"\,\,+\,\,".join(
                [
                    r"{} \cdot \text{}".format(f, "{" + n + "}")
                    for f, n in zip(factors_str, names)
                ]
            )
