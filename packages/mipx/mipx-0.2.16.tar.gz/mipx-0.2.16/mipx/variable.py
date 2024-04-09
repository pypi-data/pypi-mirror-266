# -*- coding: utf-8 -*-
# @Time    : 2023/4/7 8:07
# @Author  : luyi
"""
变量
"""
from abc import ABC
from ortools.linear_solver.pywraplp import Variable
from ortools.sat.python.cp_model import IntVar, CpSolver
from ortools.util.python.sorted_interval_list import Domain
from docplex.mp.dvar import Var as DVar
from docplex.mp.kpi import DecisionKPI
from .interface_ import *


class IntervalVar:
    def __init__(self, start, size, end) -> None:
        self.start = start
        self.size = size
        self.end = end


class Var(Variable, IVar):

    def Not(self) -> "IVar":
        if self.v_type == Vtype.BINARY or self.v_type == Vtype.INTEGER:
            z = self._solver.IntVar(  # type: ignore
                lb=0, ub=1, name=f"{self.VarName}.Not")  # type: ignore
            self._solver.Add(z + self == 1)  # type: ignore
            return z
        else:
            raise RuntimeError("Only for binary variable .")  # type: ignore

    def setUb(self, ub):
        self.SetUb(ub)

    def setLb(self, lb):
        self.SetLb(lb)

    def setBounds(self, lb, ub):
        self.SetBounds(lb, ub)

    def setValue(self, value):
        self.SetBounds(value, value)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.v_type = None

    @property
    def X(self):
        return self.solution_value()

    @property
    def VarIndex(self):
        return self.index()

    @property
    def VarName(self) -> str:
        return self.name()

    @property
    def Lb(self):
        return self.lb()

    @property
    def Ub(self):
        return self.ub()


Variable.X = Var.X  # type: ignore
Variable.VarName = Var.VarName  # type: ignore
Variable.VarIndex = Var.VarIndex  # type: ignore
Variable.Lb = Var.Lb  # type: ignore
Variable.Ub = Var.Ub  # type: ignore
Variable.setValue = Var.setValue  # type: ignore
Variable.setLb = Var.setLb  # type: ignore
Variable.setUb = Var.setUb  # type: ignore
Variable.setBounds = Var.setBounds  # type: ignore
Variable.Not = Var.Not  # type: ignore


class CpVar(IntVar, IVar, ABC):
    def __init__(self, model, domain, name, solver):
        self._solver: CpSolver = solver
        self.__domain: Domain = domain
        super().__init__(model, domain, name)

    def Not(self):
        y = super().Not()
        y.VarName = f"{self.VarName}.not"  # type: ignore
        y.X = lambda: self._solver.valueExpression(y)  # type: ignore
        return y

    def setValue(self, value):
        raise Exception("not impl")

    def setUb(self, ub):
        raise Exception("not impl")

    def setLb(self, lb):
        raise Exception("not impl")

    def setBounds(self, lb, ub):
        raise Exception("not impl")

    @property
    def X(self):
        return self._solver.valueExpression(self)  # type: ignore

    @property
    def VarIndex(self):
        return self.Index()

    @property
    def VarName(self):
        return self.Name()

    @property
    def Lb(self):
        return self.__domain.Min()

    @property
    def Ub(self):
        return self.__domain.Max()


class CPlexVar(DVar, IVar):

    def Not(self) -> "IVar":
        return self.logical_not()

    def setUb(self, ub):
        self.set_ub(ub)

    def setLb(self, lb):
        self.set_lb(lb)

    def setBounds(self, lb, ub):
        self.setLb(lb)
        self.setUb(ub)

    def setValue(self, value):
        self.setBounds(value, value)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def X(self):
        return self.solution_value

    @property
    def VarIndex(self):
        return self.index

    @property
    def VarName(self) -> str:
        return self.get_name()

    @property
    def Lb(self):
        return self.lb

    @property
    def Ub(self):
        return self.ub


DVar.X = CPlexVar.X  # type: ignore
DVar.VarName = CPlexVar.VarName  # type: ignore
DVar.VarIndex = CPlexVar.VarIndex  # type: ignore
DVar.Lb = CPlexVar.Lb  # type: ignore
DVar.Ub = CPlexVar.Ub  # type: ignore
DVar.setValue = CPlexVar.setValue  # type: ignore
DVar.setLb = CPlexVar.setLb  # type: ignore
DVar.setUb = CPlexVar.setUb  # type: ignore
DVar.setBounds = CPlexVar.setBounds  # type: ignore
DVar.Not = CPlexVar.Not  # type: ignore

DecisionKPI.X = CPlexVar.X  # type: ignore
