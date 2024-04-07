import sys
from os import path

sys.path.append(path.dirname(path.abspath(__file__)))
from server import QianluService


def testfunc(func, args):
  print(f"args: {args}")

def run():
  qianluSvr = QianluService()
  qianluSvr.onMsg(testfunc)
  qianluSvr.run()
