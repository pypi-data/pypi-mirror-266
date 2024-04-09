# -*- coding: utf-8 -*-
# @Time    : 2023/4/28 15:33
# @Author  : luyi
# 定义接口。统一类型。
from abc import ABCMeta, abstractmethod
from collections import UserDict, UserList
from typing import List, Literal, Union, Dict, Generator, Tuple

from .constants import Vtype, ObjType, CmpType, OptimizationStatus, Params

INFINITY = float("inf")

Real = Union[float, int]


class IVar(metaclass=ABCMeta):
    def __init__(self):
        # 变量类型
        self.v_type = None
        self._solver = None

    @property
    @abstractmethod
    def X(self) -> Real:
        ...

    @property
    @abstractmethod
    def VarIndex(self) -> Real:
        ...

    @property
    @abstractmethod
    def VarName(self) -> str:
        ...

    @property
    @abstractmethod
    def Lb(self) -> Real:
        ...

    @property
    @abstractmethod
    def Ub(self) -> Real:
        ...

    @abstractmethod
    def setValue(self, value: Real):
        ...

    @abstractmethod
    def setUb(self, ub: Real):
        ...

    @abstractmethod
    def setLb(self, lb: Real):
        ...

    @abstractmethod
    def Not(self) -> "IVar":
        """
        返回一个相反的变量，仅用于0,1变量。
        :return:
        """
        ...

    @abstractmethod
    def setBounds(self, lb, ub):
        ...

    def __add__(self, expr) -> 'IVar':
        ...

    def __radd__(self, cst) -> 'IVar':
        ...

    def __sub__(self, expr) -> "IVar":
        ...

    def __rsub__(self, cst) -> "IVar":
        ...

    def __mul__(self, other) -> 'IVar':
        ...

    def __rmul__(self, other) -> 'IVar':
        ...

    def __ge__(self, other) -> "IVar":
        ...

    def __le__(self, other) -> "IVar":
        ...


class ITupledict(UserDict):
    """
    Custom Gurobi class: tupledict is a subclass of dict where
      the keys are a tuplelist.
    """

    @abstractmethod
    def prod(self, coeff: Dict, *pattern): ...

    @abstractmethod
    def select(self, *pattern) -> List: ...

    @abstractmethod
    def sum(self, *pattern) -> IVar: ...

    @abstractmethod
    def quicksum(self, *pattern) -> IVar: ...

    @abstractmethod
    def quickselect(self, *pattern) -> List: ...

    @abstractmethod
    def quickprod(self, coeff: Dict, *pattern) -> List: ...


class ITuplelist(UserList):
    @abstractmethod
    def select(self, *args) -> List: ...


class IModel(metaclass=ABCMeta):
    def __init__(self, solver_id: Literal["SCIP", "CBC", "CP", "SAT", "CLP", "CPLEX", "CPLEX_CP", "GLOP", "BOP"], name=""):
        self.Params: Params = Params()
        self.solver_id = solver_id

    @property
    @abstractmethod
    def Infinity(self) -> Real:
        ...

    @staticmethod
    @abstractmethod
    def Sum(expr_array):
        ...

    @abstractmethod
    def setHint(self, start: Dict[IVar, Real]):
        ...

    @abstractmethod
    def setTimeLimit(self, time_limit_seconds: int):
        """
        设置程序最大运行时间
        :param time_limit_seconds: 秒
        """
        ...

    @abstractmethod
    def wall_time(self) -> Real:
        """
        求解所花费的时间
        :return: 求解所花费的时间，单位毫秒
        """
        ...

    @abstractmethod
    def iterations(self) -> Real:
        """

        :return: 算法迭代的次数
        """
        ...

    @abstractmethod
    def nodes(self) -> Real:
        """

        :return: 节点数
        """
        ...

    @abstractmethod
    def addVar(self, lb: float = 0, ub: float = INFINITY,
               vtype: Vtype = Vtype.CONTINUOUS, name: str = "") -> IVar:
        """
        创建变量
        :param lb: 变量下界
        :param ub: 变量上界
        :param vtype: 变量类型： Vtype.CONTINUOUS（连续）,Vtype.BINARY(0-1变量), Vtype.BINARY（整数变量）
        :param name:变量名
        :return:变量实体
        """
        ...

    @abstractmethod
    def addVars(self, *indices, lb: float = 0, ub: float = INFINITY,
                vtype: Vtype = Vtype.CONTINUOUS, name: str = "") -> ITupledict:
        """
        创建多维变量
        :param indices:多维的参数，如addVars(1,2),addVars(mList,nList),addVars([1,2,3],[3,4,5])等。
        :param lb:变量下界
        :param ub:变量上界
        :param vtype:变量类型： Vtype.CONTINUOUS（连续）,Vtype.BINARY(0-1变量), Vtype.BINARY（整数变量）
        :param name:变量名
        :return:tupledict类型
        """
        ...

    @abstractmethod
    def getVars(self) -> List[IVar]:
        """
        获取所有的变量对象
        :return:
        """
        ...

    @abstractmethod
    def getVar(self, i) -> IVar:
        """
        获取第i个变量
        :param i:
        :return:
        """
        ...

    @abstractmethod
    def addConstr(self, lin_expr, name=""):
        """
        向模型添加约束条件，
        :param lin_expr:线性约束表达式
        :param name: 约束名称
        :return:
        """
        ...

    @abstractmethod
    def addConstrs(self, lin_exprs: Union[List, Generator, Tuple], name=""):
        """
        向模型添加多个约束条件，
        :param lin_exprs: 线性约束表达式集合 可以为列表或者元组。
        :param name:名称
        :return:
        """
        ...

    @abstractmethod
    def setObjective(self, expr):
        """
        设置模型的单一目标
        :param expr: 目标表达式
         优化方向。ObjType.MINIMIZE（最小值），ObjType.MAXIMIZE(最大值)
        :return:
        """
        ...

    @abstractmethod
    def setObjectiveN(self, expr, index: int, priority: int = 0, weight: float = 1, name: str = ""):
        """
         多目标优化，优化最小值
        :param expr: 表达式
        :param index: 目标函数对应的序号 (默认 0，1，2，…), 以 index=0 作为目标函数的值, 其余值需要另外设置参数
        :param priority: 分层序列法多目标决策优先级(整数值), 值越大优先级越高【未实现】
        :param weight: 线性加权多目标决策权重(在优先级相同时发挥作用)
        :param name: 名称
        :return:
        """
        ...

    @abstractmethod
    def addGenConstrAnd(self, resvar, varList: List[IVar], name=""):
        """
        and 运算。
        addGenConstrAnd(y, [x1, x2]) 表示y = max(x1,x2)。 所有变量均为0-1变量
        :param resvar:
        :param varList:
        :param name:
        :return:
        """
        ...

    @abstractmethod
    def addGenConstrOr(self, resvar: IVar, varList: List[IVar], name=""):
        """
        或运算
        addGenConstrOr(y, [x1, x2]) 表示y = min(x1,x2)。 所有变量均为0-1变量
        :param resvar:
        :param varList:
        :param name:
        :return:
        """
        ...

    @abstractmethod
    def addGenConstrXOr(self, resvar: IVar, varList: List[IVar], name=""):
        """
        异或运算
        addGenConstrXOr(y, [x1, x2])。 所有变量均为0-1变量
        :param resvar:
        :param varList:
        :param name:
        :return:
        """
        ...

    @abstractmethod
    def addGenConstrPWL(self, var_y, var_x, x, y, name=""):
        """
        设置分段约束
        参考gurobi
        model.setPWLObj(var, [1, 3, 5], [1, 2, 4])
        :param var_y: f(x)
        :param var_x:指定变量的目标函数是分段线性
        :param x:  定义分段线性目标函数的点的横坐标值(非减序列)
        :param y:定义分段线性目标函数的点的纵坐标值
        :return:
        """
        ...

    @abstractmethod
    def addGenConstrIndicator(self, binvar: IVar, binval: bool, lhs: IVar, sense: CmpType, rhs: float, M: float,
                              name: str = ""):
        """
        若 binvar 为binval ,则 lhs 与 rhs 之间有sense 的关系
        若M不指定,则程序会给与默认。但仍推荐给出M。程序自动给出的可能会存在问题。
        :param binvar: 0-1变量
        :param binval: bool 常量
        :param lhs:  左侧变量
        :param sense: 等号，大于等于，小于等于
        :param rhs: 右侧常量
        :param M: 大M
        :return:
        """
        ...

    @abstractmethod
    def addIndicator(self, binvar: IVar, binval: bool, expr,
                     name: str = ""):
        """
        若 binvar 为binval ,则 lhs 与 rhs 之间有sense 的关系
        若M不指定，则程序会给与默认。但仍推荐给出M。程序自动给出的可能会存在问题。
        :param binvar: 0-1变量
        :param binval: bool 常量
        :param lhs:  左侧变量
        :param sense: 等号，大于等于，小于等于
        :param rhs: 右侧常量
        :param M: 大M
        :return:
        """
        ...

    @abstractmethod
    def addGenConstrAbs(self, resvar: any, var_abs: IVar, M=None, name=""):  # type: ignore
        """
        绝对值 resvar = |var_abs|
        :param resvar:
        :param var_abs:
        :param name:
        :return:
        """
        ...

    @abstractmethod
    def addConstrMultiply(self, z: IVar, l: Tuple[IVar, IVar], name=""):
        """
        满足 z = x * y
        其中 x 为0,1变量
        :param l:
        :param z: 变量
        :param name:
        :return:
        """
        if len(list(l)) != 2:
            raise RuntimeError("Only need two variables")

    @abstractmethod
    def addRange(self, expr, min_value: Real, max_value: Real, name=""):
        """
        添加范围约束
        :param expr: 表达式
        :param min_value: 最小值
        :param max_value: 最大值
        :param name:名称
        :return:
        """
        ...

    @abstractmethod
    def addConstrOr(self, constrs: List, ok_num: int = 1, cmpType: CmpType = CmpType.EQUAL, name: str = "", M=None):
        """
        约束的满足情况,满足的次数
        :param constr: 所有的约束
        :param ok_num:  需要满足的个数，具体则根据cmpType
        :param cmpType: CmpType.LESS_EQUAL CmpType.EQUAL,CmpType.GREATER_EQUAL
        :param name: 名称
        :param M: M值，推荐指定M值。
        :return:
        """
        ...

    @abstractmethod
    def addKpi(self) -> int:
        """
        变量个数
        :return:
        """
        ...

    @abstractmethod
    def numVars(self) -> int:
        """
        变量个数
        :return:
        """
        ...

    @abstractmethod
    def numConstraints(self) -> int:
        """
        约束个数
        :return:
        """
        ...

    @abstractmethod
    def write(self, filename: str, obfuscated=False):
        """
        写入到文件
        :param filename:文件名，支持后缀 .lp .mps .proto(目前有问题)
        :param obfuscated: 是否混淆，默认不混淆
        :return:
        """
        ...

    @abstractmethod
    def read(self, path: str) -> 'IModel':
        """读取文件 lp,mps 文件。

        Args:
            path (str): _description_
        """
        ...

    @property
    @abstractmethod
    def ObjVal(self) -> Real:
        """目标值"""
        ...

    @abstractmethod
    def optimize(self, obj_type: ObjType = ObjType.MINIMIZE) -> OptimizationStatus:
        """
        优化目标
        :param time_limit_milliseconds:最大运行时长
        :param obj_type:优化目标。ObjType.MINIMIZE（最小值），ObjType.MAXIMIZE(最大值)
        :param enable_output: 是否显示gap日志。
        :return:
        """
        ...

    @abstractmethod
    def clear(self):
        """清空所有的目标和约束
        """
        ...

    @abstractmethod
    def close(self):
        """关闭
        """
        ...

    @abstractmethod
    def valueExpression(self, expression):
        """
        计算表达式的值。
        :param expression:
        :return:
        """
        ...

    @abstractmethod
    def newIntervalVar(self, start, size, end, name=""):
        """
        创建变量： start+size=end

        Args:
            start (_type_): 开始
            size (_type_): 大小
            end (_type_): 结束
            name (str, optional): 名称. Defaults to "".
        """
        ...

    @abstractmethod
    def addNoOverlap(self, interval_vars: List, M):
        """
        互相之间不重复

        Args:
            interval_vars (List): 间隔变量
        """
        pass

    @abstractmethod
    def setNumThreads(self, num_theads: int):
        """
        设置线程的个数

        Args:
            num_theads (int): 线程个数
        """
        ...

        ...


def debugVar(vars, no_zero=True):
    """
    调试var的方法

    :param _type_ vars: 可以是变量的集合或者单个变量
    :param bool no_zero: 不输出<=0的值, defaults to True
    """
