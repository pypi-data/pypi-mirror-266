import unittest
import pyminerva as mi



def test(tickers):
    mi.analyse_DrawDown(tickers)



'''
Main Fuction
'''

if __name__ == "__main__":

    test(['SPY', 'QQQ', 'TLT'])








# from pyminerva import PyMinerva

# class Test(unittest.TestCase):
#     def test_lower_method(self):
#         self.assertEqual(PyMinerva.lower("TEST"), "test")
#         self.assertNotEqual(PyMinerva.lower("test"), "TEST")

#     def test_upper_method(self):
#         self.assertEqual(PyMinerva.upper("test"), "TEST")
#         self.assertNotEqual(PyMinerva.upper("TEST"), "test")

#     def test_title_method(self):
#         # self.assertEqual(PyMinerva.title("hello world"), "Hello world")
#         self.assertNotEqual(PyMinerva.title("hELLO wORLD"), "hello world")