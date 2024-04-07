# optimizers,优化器。用于更新参数
class Optimizer:
  def __init__(self):
    self.target = None
    self.hooks = []

  def setup(self,target):
    self.target = target
    return self
  
  def update(self):
    # 将None之外的参数汇总到列表
    params = [p for p in self.target.params() if p.grad is not None]

    #预处理
    for f in self.hooks:
      f(params)

    # 更新参数
    for param in params:
      self.update_one(param)

  def update_one(self,param):# 具体参数通过此方法进行更新，需要在继承Optimizer的类里重写实现
    raise NotImplementedError

  def add_hook(self,f):# 添加预处理函数
    self.hooks.append(f)

# SGD(Stochastic Gradient Descent),意为随机梯度下降法
class SGD(Optimizer):
  def __init__(self,lr=0.01):
    super().__init__()
    self.lr = lr 

  def update_one(self,param):
    param.data -= self.lr * param.grad.data

import numpy as np
# 动量梯度下降法
class MomentumSGD(Optimizer):
  def __init__(self,lr=0.01,momentum=0.9):
    super().__init__()
    self.lr = lr 
    self.momentum = momentum
    self.vs = {}

  def update_one(self,param):
    # 这段代码的意义？？？
    v_key = id(param)
    if v_key not in self.vs:
      self.vs[v_key] = np.zeros_like(param.data)
    
    v = self.vs[v_key]
    # 对动量进行减速
    v *= self.momentum
    # 对动量按导数增减
    v -= self.lr * param.grad.data
    # 更新参数
    param.data += v
