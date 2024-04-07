#Layer，意为层
from Rryyz.core import Parameter
import weakref
import numpy as np
import Rryyz.functions as F
from Rryyz.core import Parameter

class Layer:
  def __init__(self):
    self._params = set()
  
  def __setattr__(self,name,value):#设置类的实例变量时被调用的特殊方法，变量的名字和值会分别作为name,value参数
    if isinstance(value,(Parameter,Layer)):#只有value是Parameter实例时，才加入_params里
      self._params.add(name)
    super().__setattr__(name,value)#调用父类的_setattr__方法，但是Layer没有父类啊，不理解？？？？

  def __call__(self,*inputs):
    outputs = self.forward(*inputs)
    if not isinstance(outputs,tuple):
      outputs = (outputs,)
    self.inputs = [weakref.ref(x) for x in inputs]
    self.outputs = [weakref.ref(y) for y in outputs]
    return outputs if len(outputs) > 1 else outputs[0]

  def forward(self,inputs):
    raise NotImplementedError
  
  def params(self):#返回该层所持有的所有的parameter实例
    for name in self._params:
      obj = self.__dict__[name]

      if isinstance(obj,Layer):#如果取出来的是Layer，则取出它所有的参数
        yield from obj.params()
      else:
        yield obj

  def cleargrads(self):
    for param in self.params():
      param.cleargrad()

class Linear(Layer):
  def __init__(self,out_size,nobias=False,dtype=np.float32,in_size=None):
    super().__init__()
    self.in_size = in_size
    self.out_size = out_size
    self.dtype = dtype

    self.W = Parameter(None,name="W")
    if self.in_size is not None:#如果没有指定输入数据的尺寸，则延后处理
      self._init_W()

    if nobias:
      self.b = None
    else:
      self.b = Parameter(np.zeros(out_size,dtype=dtype),name="b")

  def _init_W(self):
    I,O = self.in_size,self.out_size
    W_data = np.random.randn(I,O).astype(self.dtype) * np.sqrt(1/I)
    self.W.data = W_data

  def forward(self,x):
    if self.W.data is None:
      self.in_size = x.shape[1]
      #将I设置为X的列尺寸，参与运算
      #我们发现，IO分别是W的行和列，但被称为输入和输出尺寸
      #其原因是X乘W，其输出的数据Y，行数与X，列数与W保持一致
      #所以实际上O输出尺寸指的是Y的列尺寸
      self._init_W()

    y = F.linear(x,self.W,self.b)
    return y