# -*- coding: utf-8 -*-
# @Time    : 2023/4/28 23:54
# @Author  : luyi
from typing import List
from .utilx import is_list_or_tuple
from .tupledict import tupledict
# TODO：通过方法的方式实现逻辑暂时未实现，可通过具体的对象方法来实现。


def abs_(*args):
    pass


def all_(*args):
    pass


def and_(*args):
    pass


def any_(*args):
    pass


def debugVar(vars, no_zero=True):
    """
    调试var的方法

    :param _type_ vars: 可以是变量的集合或者单个变量
    :param bool no_zero: 不输出<=0的值, defaults to True
    """
    is_list = False
    if type(vars) == type(tupledict()):
        vars = vars.values()
        is_list = True
    if is_list_or_tuple(vars):
        is_list = True
    if is_list:
        for var in vars:
            if no_zero:
                if var.X <= 0.01:
                    continue
            print(f"{var.VarName}:{var.X}")
    else:
        print(f"{vars.VarName}:{vars.X}")  # type:ignore
