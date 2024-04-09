# -*- coding: utf-8 -*-
# @Time    : 2023/4/12 9:12
# @Author  : luyi
"""
约束规划
"""

from collections import defaultdict
from typing import Union, List, Dict, Tuple
from docplex.cp.model import CpoModel
from docplex.cp.model import interval_var, binary_var, minimize
from .constants import Vtype, ObjType, OptimizationStatus, CmpType
from .interface_ import IVar, IModel
from .tupledict import tupledict
from .utilx import is_list_or_tuple, get_combinations, \
    name_str, check_bool_var, is_bool_var
from .variable import CPlexVar


Real = Union[float, int]
INFINITY = 1e+10


class CplexCpSolver(IModel):
    """
    约束规划CPLEX 未实现

    :param _type_ IModel: _description_
    """

    def __init__(self, name=""):
        super().__init__()
        self.name = name
        self.__model = CpoModel(self.name)

        self.__line_expr_object = defaultdict(list)
        self._flag_objective_n = False
        self._flag_objective = False

    @property
    def Infinity(self) -> float:
        return INFINITY

    def Sum(self, expr_array) -> 'IVar':

        return self.__model.sum(expr_array)  # type: ignore

    def setHint(self, start: Dict[IVar, Real]):
        raise RuntimeError('not implemented')

    def setTimeLimit(self, time_limit_seconds: int):
        self.Params.TimeLimit = time_limit_seconds

    def wall_time(self) -> int:
        solver_details: SolveDetails = self.__model.solve_details  # type: ignore
        return solver_details.time*1000

    def iterations(self) -> Real:
        solver_details: SolveDetails = self.__model.solve_details  # type: ignore
        return solver_details.nb_iterations

    def nodes(self) -> Real:
        solver_details: SolveDetails = self.__model.solve_details  # type: ignore
        return solver_details.nb_nodes_processed

    def addVar(self, lb=None, ub=None,
               vtype: Vtype = Vtype.CONTINUOUS, name: str = "") -> IVar:
        """
            Add a decision variable to a model.
        :param lb: Lower bound for new variable.
        :param ub: Upper bound for new variable.
        :param vtype: variable type for new variable(Vtype.CONTINUOUS, Vtype.BINARY, Vtype.INTEGER).
        :param name: Name for new variable.
        :return: variable.
        """

        if vtype == Vtype.CONTINUOUS or vtype == Vtype.INTEGER:
            var1 = interval_var(start=lb, end=ub, name=name)
        else:
            var1 = binary_var(name=name)
        return var1

    def addVars(self, *indices, lb=None, ub=None, vtype: Vtype = Vtype.CONTINUOUS,
                name: str = "") -> tupledict:

        li = []
        for ind in indices:
            if isinstance(ind, int):
                ind = [i for i in range(ind)]
            elif is_list_or_tuple(ind):
                pass
            elif isinstance(ind, str):
                ind = [ind]
            else:
                raise ValueError("error input")
            li.append(ind)
        all_keys_tuple = get_combinations(li)
        tu_dict = tupledict(
            [[key, self.addVar(lb, ub, vtype, name_str(name, key))] for key in all_keys_tuple])
        return tu_dict

    def getVars(self) -> List[IVar]:
        raise RuntimeError("not implemented")

    def getVar(self, i) -> IVar:
        return self.__model.get_all_variables()  # type: ignore

    def addConstr(self, lin_expr, name=""):
        self.__model.add_constraint(lin_expr)

    def addConstrs(self, lin_exprs, name=""):
        # 检查下是否可以迭代。
        self.__model.add(lin_exprs)

    def setObjective(self, expr):
        self._flag_objective = True
        if self._flag_objective_n:
            raise RuntimeError(
                "setObjective and setObjectiveN can only be used for one of them")
        self.__model.add(minimize(expr))

    def setObjectiveN(self, expr, index: int, priority=None, weight: float = 1, name: str = ""):
        """
        :param expr:
        :param index:
        :param priority:
        :param weight:
        :param name:
        :return:
        """
        self._flag_objective_n = True
        if self._flag_objective:
            raise RuntimeError(
                "setObjective and setObjectiveN can only be used for one of them")

        self.__line_expr_object['exprs'].append(expr)
        self.__line_expr_object['priority'].append(priority)
        self.__line_expr_object['weight'].append(weight)

    def addGenConstrAnd(self, resvar, varList: List[IVar], name=""):
        """
        和 addGenConstrAnd(y, [x1,x2])
        :param resvar:
        :param varList:
        :param name:
        :return:
        """

        self.addConstr(resvar == self.__model.logical_and(*varList))

    def addGenConstrOr(self, resvar: IVar, varList: List[IVar], name=""):
        self.addConstr(resvar == self.__model.logical_or(*varList))

    def addGenConstrXOr(self, resvar: IVar, varList: List[IVar], name=""):
        if len(varList) != 2:
            raise ValueError("length of vars must be 2")
        check_bool_var(resvar, varList)
        self.addConstr(resvar >= varList[0] - varList[1])
        self.addConstr(resvar >= varList[1] - varList[0])
        self.addConstr(resvar <= varList[0] + varList[1])
        self.addConstr(resvar <= 2 - varList[0] - varList[1])

    def addGenConstrPWL(self, var_y, var_x, x, y, name=""):
        pass

    def addGenConstrIndicator(self, binvar: IVar, binval: bool, lhs: IVar, sense: CmpType, rhs: int, M,
                              name: str = ""):
        # TODO:
        raise RuntimeError("not implemented")

    def addIndicator(self, binvar: IVar, binval: bool, expr,
                     name=None):
        if name == "":
            name = None
        self.__model.add_indicator(binvar, expr, binval, name)

    def addGenConstrAbs(self, resvar, var_abs: IVar, M, name=""):
        self.addConstr(self.__model.abs(var_abs) == resvar)

    def addConstrMultiply(self, z: IVar, l: Tuple[IVar, IVar], name=""):
        """x * y = z"""
        super().addConstrMultiply(z, l)
        x = l[0]
        y = l[1]
        if not is_bool_var(x) and not is_bool_var(y):
            raise RuntimeError("At least one binary variable is required.")
        if is_bool_var(y):
            x, y = y, x
        M = y.Ub
        self.addConstr(z <= y)
        self.addConstr(z <= x * M)
        self.addConstr(z >= y + (x - 1) * M)

    def addRange(self, expr, min_value: Union[float, int], max_value: Union[float, int], name=''):
        self.__model.add_range(min_value, expr, max_value, rng_name=name)

    def addConstrOr(self, constrs: List, ok_num: int = 1, cmpType: CmpType = CmpType.EQUAL, name: str = "", M=None):
        """
         约束的满足情况

        :param constr: 所有的约束
        :param ok_num: 需要满足的个数，具体则根据cmpType
        :param cmpType: CmpType.LESS_EQUAL CmpType.EQUAL,CmpType.GREATER_EQUAL
        :param name: 名称
        :return:
        """
        constr_num = len(constrs)
        x = []
        for i in range(constr_num):
            x.append(self.addVar(vtype=Vtype.BINARY))
            constr = constrs[i]
            lb, ub = constr.Bounds()
            expr = constr.Expression()
            tempM = 100000000
            if M is not None:
                tempM = M
            if lb > -INFINITY:  # 若大于
                self.addConstr(expr + tempM * (1 - x[i]) >= lb)
            if ub < INFINITY:
                self.addConstr(expr - tempM * (1 - x[i]) <= ub)
        if cmpType == CmpType.EQUAL:
            self.addConstr(self.Sum(x) == ok_num)
        elif cmpType == CmpType.GREATER_EQUAL:
            self.addConstr(self.Sum(x) >= ok_num)
        elif cmpType == CmpType.LESS_EQUAL:
            self.addConstr(self.Sum(x) <= ok_num)  # type: ignore
        else:
            raise Exception("error value of cmpType")

    def addKpi(self, kpi_arg, name=None) -> IVar:  # 为了统一，暂时考虑
        return self.__model.add_kpi(kpi_arg, name)  # type: ignore

    def numVars(self) -> int:
        return self.__model.number_of_variables

    def numConstraints(self) -> int:
        return self.__model.number_of_constraints

    def write(self, filename: str, obfuscated=False):
        filename = filename.lower()
        if filename.endswith(".lp"):
            self.__model.export_as_lp(filename)
        elif filename.endswith(".mps"):
            self.__model.export_as_mps(filename)
        elif filename.endswith(".proto"):
            raise TypeError(".proto 导出异常，待修复")

    def read(self, path: str):
        self.clear()
        m = ModelReader.read_model(path)
        self.__model = m

    @property
    def ObjVal(self) -> Real:
        return self.__model.objective_value

    def optimize(self, obj_type: ObjType = ObjType.MINIMIZE) -> OptimizationStatus:
        if self.Params.TimeLimit:
            self.setTimeLimit(self.Params.TimeLimit)
        if self.Params.MIPGap:
            self.__model.parameters.mip.tolerances.mipgap = self.Params.MIPGap  # type: ignore

        if self._flag_objective_n:
            self.__model.set_multi_objective(
                'min' if obj_type is ObjType.MINIMIZE else 'max', self.__line_expr_object['exprs'], self.__line_expr_object['priority'], self.__line_expr_object['weight'])
        status: SolveSolution = self.__model.solve(
            log_output=self.Params.EnableOutput, checker=self.Params.Checker)  # type: ignore
        if status:
            if status.is_feasible_solution or status.is_valid_solution:
                result = OptimizationStatus.OPTIMAL
            else:
                result = OptimizationStatus.FEASIBLE
        else:
            result = OptimizationStatus.ERROR
        return result

    def clear(self):
        self.__model.clear()

    def close(self):
        self.__model.end()
    # 独有。

    def addNoOverlap(self, interval_vars, M):
        """
        相邻不重复。

        :param interval_vars:
        :return:
        """
        raise RuntimeError("not implemented")

    def newIntervalVar(self, start, size, end, name=""):
        raise RuntimeError("not implemented")

    def valueExpression(self, expression):
        raise RuntimeError("not implemented")

    def setNumThreads(self, num_theads: int):
        self.__model.context.cplex_parameters.threads = num_theads
