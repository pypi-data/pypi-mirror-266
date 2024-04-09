

# 生成测试
import unittest
import mipx


class TestMultidict(unittest.TestCase):

    def test_debug_var(self):
        model = mipx.Model()
        x = model.addVars(1, 3, name='x')
        y = model.addVar(name='y')
        status = model.optimize()
        mipx.debugVar(x.select("*", 2), False)
        mipx.debugVar(y, False)
        mipx.debugVar(x, False)
        mipx.debugVar([y], False)

    def test_tuple_list(self):
        a = mipx.tuplelist([1, 2, 3])
        print(a.quickselect(1))


if __name__ == '__main__':
    unittest.main()
