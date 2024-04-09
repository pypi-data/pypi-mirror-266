from typing import Dict, List, Tuple
import mipx
import time


def solver(kL: List[int], jL: List[int], aT: Dict[int, int], lL: List[List[int]],
           aK: List[List[List[int]]], shutp: List[Tuple[int]], tt: Dict[Tuple[int, int], int],
           wt: List[List[int]]):

    model = mipx.Model(solver_id="SAT")
    N = len(lL)  # 所有可行的工艺路线个数
    # 定义变量
    M = 100000000
    x = model.addVars(N, name='x')  # 采用第几种工艺路线方案
    y = mipx.tupledict({})
    for n in range(N):
        for l, _ in enumerate(lL[n]):  # 第n种方案的工序
            for k in aK[n][l]:
                y[n, l, k] = model.addVar(
                    vtype=mipx.Vtype.BINARY, name=mipx.name_str("y", n, l, k))
    st = mipx.tupledict({})  # 炉次在工序上的加工时间和结束时间
    et = mipx.tupledict({})  # 炉次在工序上的加工时间和结束时间
    for n in range(N):
        for l, _ in enumerate(lL[n]):
            st[n, l] = model.addVar(name=mipx.name_str("st", n, l))
            et[n, l] = model.addVar(name=mipx.name_str("et", n, l))
    e = mipx.tupledict({})
    u = mipx.tupledict({})  # 运输时间之间的差值
    for n in range(N):
        for l, _ in enumerate(lL[n][:-1]):
            u[n, l] = model.addVar(name='u')
            for k1 in ak[n][l]:
                for k2 in ak[n][l+1]:
                    e[n, l, k1, k2] = model.addVar(
                        vtype=mipx.Vtype.BINARY, name=mipx.name_str('e', n, l, k1, k2))

    dc = model.addVar(name='dc')  # 与开浇时间的偏差
    dg = model.addVar(name='dg')  # 与连浇时间的偏差
    ct = 8000  # 开浇时间
    gt = 0  # 断浇时间
    # 约束条件
    # 1. 只能采用其中一种模式
    bt1 = time.perf_counter()
    model.addConstr(x.quicksum() == 1)

    # 2. 只有采用了某种模式时相关的参数才能有相应的值
    for n in range(N):
        model.addConstr(y.quicksum(n, "*", "*") <= M * x[n])
        model.addConstr(st.quicksum(n, "*") <= M * x[n])
        model.addConstr(et.quicksum(n, "*") <= M * x[n])
        model.addConstr(e.quicksum(n, "*", "*", "*") <= M * x[n])

    # 3.只能分配工序一个工位
    for n in range(N):
        for l, _ in enumerate(lL[n]):
            model.addConstr(y.quicksum(n, l, "*") == x[n])

    # 4. 炉次在工位上的加工时与结束时间的关系
    for n in range(N):
        for l, _ in enumerate(lL[n]):
            model.addConstr(
                st[n, l]+model.Sum([y[n, l, k]*w[n][l] for k in ak[n][l]]) == et[n, l])
    # 5.若炉次在工位上加工,那么在工位上的开始时间应晚于工位的最早可用时间

    for n in range(N):
        for l, _ in enumerate(lL[n]):
            for k in ak[n][l]:
                model.addConstr(st[n, l]+M*(1-y[n, l, k]) >= at[k])
    # 6. 工位间的运输时间的限制
    for n in range(N):
        for l, _ in enumerate(lL[n][:-1]):
            for k1 in ak[n][l]:
                for k2 in ak[n][l+1]:
                    model.addConstrMultiply(
                        e[n, l, k1, k2], (y[n, l, k1], y[n, l+1, k2]))
            model.addConstr(et[n, l]+model.Sum([e[n, l, k1, k2] * tt[k1, k2]
                            for k1 in ak[n][l] for k2 in ak[n][l+1]])+u[n, l] == st[n, l+1])
    # 7. 连铸机上的限制
    # 7.1 开浇时间的偏差
    c_k = ak[0][-1][0]  # 连铸机上的工位
    if ct > 0:
        model.addConstr(
            ct+dc == model.Sum([st[n, len(lL[n])-1] for n in range(N)]))
    if gt > 0:
        model.addConstr(
            gt+dg == model.Sum([st[n, len(lL[n])-1] for n in range(N)]))

    # 8 停机计划
    # -------------------
    # print("约束:", model.numConstraints())
    # print("变量:", model.numVars())
    # 1. 采用最优方案
    model.setObjectiveN(
        x.prod({0: 0, 1: 1, 2: 2, 3: 3}, "*"), index=0, weight=1)
    et1 = time.perf_counter()
    print("构建时间:{}ms".format(1000*(et1 - bt1)))
    # 2.运输时间的
    status = model.optimize()
    if status == mipx.OptimizationStatus.OPTIMAL:
        print(f"time is {model.wall_time()} ms")
        # mipx.debugVar(x)
        # mipx.debugVar(st)
        # mipx.debugVar(et)


if __name__ == '__main__':
    # 定义相关的参数
    # KR 0,1,2;BOF:3,4,5,RH:2个,LF:四个.连铸机:五个.
    k_names = ["1#BOF", "2#BOF", "3#BOF", "1#RH-1", "1#RH-2", "2#RH-1",
               "2#RH-2", "1#LF-1", "1#LF-2", "2#LF-1", "2#LF-2", "3#LF-1", "3#LF-2", "5#LF-1",
               "5#LF-2", "1#ESP", "2#ESP", "3#ESP", "4#ESP", "5#ESP"]
    j_names = ["BOF", "RH", "LF", "CC"]
    jkMap = {"BOF": ["1#BOF", "2#BOF", "3#BOF"], "RH": ["1#RH-1", "1#RH-2", "2#RH-1", "2#RH-2"],
             "LF": ["1#LF-1", "1#LF-2", "2#LF-1", "2#LF-2", "3#LF-1", "3#LF-2", "5#LF-1", "5#LF-2"],
             "CC": ["1#ESP", "2#ESP", "3#ESP", "4#ESP", "5#ESP"]}
    ks = [i for i, _ in enumerate(k_names)]
    js = [i for i, _ in enumerate(j_names)]
    at = {k: 0 for k in ks}  # 每个工位的最早可用时间
    # 记录单个炉次的工艺路径的选择
    lL = [[0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 3]]
    ak = [[[k_names.index(kName) for kName in jkMap[j_names[j]]]
           for j in l] for l in lL]
    # 加工时间的
    w = [[40, 30, 40,  60], [40, 20, 50, 65], [40, 30,   60]]
    sp = []  # 停机检修计划
    # 运输时间
    tt = {(k1, k2): 10*60 for k1 in ks for k2 in ks if k1 != k2}
    for i in range(1):
        solver(ks, js, at, lL, ak, sp, tt, w)
        print("------------")
