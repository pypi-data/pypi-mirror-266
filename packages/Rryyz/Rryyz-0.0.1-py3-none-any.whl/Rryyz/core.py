import numpy as np
import weakref
import contextlib
import Rryyz

class Config:
  enable_backprop = True

class Variable:#意为变量

  __array_priority__ = 200
  def __init__(self,data,name=None):
    if data is not None:
      if not isinstance(data,np.ndarray):
        raise TypeError("不支持{}类型的数据，您需要使用ndarray实例".format(type(data)))
    self.data = data
    self.name = name
    self.grad = None
    self.creator = None
    self.generation = 0

  @property
  def shape(self):
    return self.data.shape

  @property
  def dtype(self):
    return self.data.dtype
    
  def set_creator(self,func):
    self.creator = func
    self.generation = func.generation + 1

  def backward(self,retain_grad=False,create_graph=False):
    if self.grad is None:
      self.grad = Variable(np.ones_like(self.data))
      #ones_like函数会把nparray里面的所有数据都替换成1，
      #为什么要用？因为后面有张量的反向传递。


    funcs = []
    seen_set = set()

    def add_func(f):
      if f not in seen_set:
        funcs.append(f)
        seen_set.add(f)
        funcs.sort(key=lambda x:x.generation)

    add_func(self.creator)
    
    while funcs:
      f = funcs.pop()
      gys = [output().grad for output in f.outputs]

      with using_config("enable_backprop",create_graph):
        gxs = f.backward(*gys)
        if not isinstance(gxs,tuple):
          gxs = (gxs,)

        for x,gx in zip(f.inputs,gxs):
          if x.grad is None:
            x.grad = gx
          else:
            x.grad = x.grad + gx

          if x.creator is not None:
            add_func(x.creator)

      if not retain_grad:
        for y in f.outputs:
          y().grad = None
    
  def cleargrad(self):
    self.grad = None

  def __len__(self):
    return len(self.data)

  def __repr__(self):
    if self.data is None:
      return "variable(None)"
    p = str(self.data).replace("\n","\n" + " " * 9)
    return "variable(" + p + ")"

  def reshape(self,*shape):
    #此函数解决了在之前只能有reshape(x,(2,3))的用法
    #现在和np的reshape一样可以用x.reshape(2,3),x.reshape((2,3)),x.reshape([2,3])
    if len(shape) == 1 and isinstance(shape[0],(tuple,list)):
      shape = shape[0]
    return Rryyz.functions.reshape(self,shape)

  def transpose(self):
    return Rryyz.functions.transpose(self)

  @property
  def T(self):
    #通过property可以作为示例变量来使用,x.transpose()等于x.T
    return Rryyz.functions.transpose(self)

class Function:
  def __call__(self,*inputs):
    inputs = [as_variable(x) for x in inputs]

    xs = [x.data for x in inputs]
    ys = self.forward(*xs)
    if not isinstance(ys,tuple):
      ys = (ys,)
    outputs = [Variable(as_array(y)) for y in ys]

    if Config.enable_backprop:
      self.generation = max([x.generation for x in inputs])
      for output in outputs:
        output.set_creator(self)
      self.inputs = inputs
      self.outputs = [weakref.ref(output) for output in outputs]

    return outputs if len(outputs)>1 else outputs[0]

  def forward(self,x):
    raise NotImplementedError()

  def backward(self,gy):
    raise NotImplementedError()  

class Parameter(Variable):
  pass


class Add(Function):
  def forward(self,x0,x1):
    #P278
    self.x0_shape,self.x1_shape = x0.shape,x1.shape
    y = x0 + x1
    return y

  def backward(self,gy):
    gx0,gx1 = gy,gy
    #P278
    if self.x0_shape != self.x1_shape:
      gx0 = Rryyz.functions.sum_to(gx0,self.x0_shape)
      gx1 = Rryyz.functions.sum_to(gx1,self.x1_shape)
    return gx0,gx1

class Mul(Function):
  def forward(self,x0,x1):
    y = x0 * x1
    return y

  def backward(self,gy):
    x0,x1 = self.inputs
    gx0 = gy * x1
    gx1 = gy * x0
    if x0.shape != x1.shape:  # for broadcast
      gx0 = Rryyz.functions.sum_to(gx0, x0.shape)
      gx1 = Rryyz.functions.sum_to(gx1, x1.shape)
    return gx0, gx1

class Sub(Function):
  def forward(self,x0,x1):
    self.x0_shape, self.x1_shape = x0.shape, x1.shape
    y = x0 - x1
    return y

  def backward(self,gy):
    gx0 = gy
    gx1 = -gy
    if self.x0_shape != self.x1_shape:  # for broadcast
      gx0 = Rryyz.functions.sum_to(gx0, self.x0_shape)
      gx1 = Rryyz.functions.sum_to(gx1, self.x1_shape)
    return gx0, gx1

class Div(Function):
  def forward(self,x0,x1):
    y = x0 / x1
    return y

  def backward(self,gy):
    x0,x1 = self.inputs
    gx0 = gy / x1
    gx1 = gy * (-x0 / x1 ** 2)
    if x0.shape != x1.shape:  # for broadcast
      gx0 = Rryyz.functions.sum_to(gx0, x0.shape)
      gx1 = Rryyz.functions.sum_to(gx1, x1.shape)
    return gx0,gx1

class Pow(Function):
  def __init__(self,c):
    self.c = c

  def forward(self,x):
    y = x ** self.c
    return y

  def backward(self,gy):
    x = self.inputs[0]
    c = self.c
    gx = c * x ** (c-1) * gy
    return gx

class Neg(Function):
  def forward(self,x):
    return -x

  def backward(self,gy):
    return -gy

@contextlib.contextmanager
def using_config(name,value):
  old_value = getattr(Config,name)
  setattr(Config,name,value)
  try:
    yield
  finally:
    setattr(Config,name,old_value)

def no_grad():
  return using_config("enable_backprop",False)

def as_array(x):
  if np.isscalar(x):
    return np.array(x)
  return x

def as_variable(obj):
  if isinstance(obj,Variable):
    return obj
  return Variable(obj)

def add(x0,x1):
  x1 = as_array(x1)
  return Add()(x0,x1)

def mul(x0,x1):
  x0,x1 = as_array(x0),as_array(x1)
  return Mul()(x0,x1)

def sub(x0,x1):
  x1 = as_array(x1)
  return Sub()(x0,x1)

def rsub(x0,x1):
  x1 = as_array(x1)
  return Sub()(x1,x0)

def div(x0,x1):
  x1 = as_array(x1)
  return Div()(x0,x1)

def rdiv(x0,x1):
  x1 = as_array(x1)
  return Div()(x1,x0)

def pow(x,c):
  return Pow(c)(x)

def neg(x):
  return Neg()(x)

def setup_variable():
  Variable.__add__ = add
  Variable.__radd__ = add
  Variable.__mul__ = mul
  Variable.__rmul__ = mul
  Variable.__neg__ = neg
  Variable.__sub__ = sub
  Variable.__rsub__ = rsub
  Variable.__truediv__ = div
  Variable.__rtruediv__ = rdiv
  Variable.__pow__ = pow
  # 允许以这种形式切片,y=x[1]
  Variable.__getitem__ = Rryyz.functions.get_item
