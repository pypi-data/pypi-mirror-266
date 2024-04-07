import numpy as np
from Rryyz.core import Function, Variable, as_variable, as_array
from Rryyz import cuda,utils
class Square(Function):
  def forward(self,x):
    y = x ** 2
    return y
  
  def backward(self,gy):
    x = self.inputs[0].data
    gx = 2 * x * gy
    return gx

class Exp(Function):
  def forward(self,x):
    y = np.exp(x)
    return y

  def backward(self,gy):
    x = self.inputs[0].data
    gx = np.exp(x) * gy
    return gx

class Sin(Function):
  def forward(self,x):
    y = np.sin(x)
    return y

  def backward(self,gy):
    x, = self.inputs
    gx = gy * cos(x)
    return gx

class Cos(Function):
  def forward(self,x):
    y = np.cos(x)
    return y

  def backward(self,gy):
    x, = self.inputs
    gx = gy * -sin(x)
    return gx

class Tanh(Function):
  def forward(self,x):
    y = np.tanh(x)
    return y

  def backward(self,gy):
    y = self.outputs[0]()
    gx = gy * (1 - y * y)
    return gx

class Reshape(Function):
  def __init__(self,shape):
    self.shape = shape
  
  def forward(self,x):
    self.x_shape = x.shape
    y = x.reshape(self.shape)
    return y

  def backward(self,gy):
    return reshape(gy,self.x_shape)

class Transpose(Function):
  def forward(self,x):
    y = np.transpose(x)
    return y

  def backward(self,gy):
    gx = transpose(gy)
    return gx

class Sum(Function):
  def __init__(self,axis,keepdims):
    self.axis = axis
    self.keepdims = keepdims

  def forward(self,x):
    self.shape = x.shape
    y = x.sum(axis=self.axis,keepdims=self.keepdims)
    return y

  def backward(self,gy):
    gy = utils.reshape_sum_backward(gy,self.x_shape,self.axis,self.keepdims)
    gx = broadcast_to(gy,self.x_shape)
    return gx

class BroadcastTo(Function):
  def __init__(self,shape):
    self.shape = shape

  def forward(self,x):
    self.x_shape = x.shape
    y = np.broadcast_to(x,self.shape)
    return y

  def backward(self,gy):
    gx = sum_to(gy,self.x_shape)
    return gx

class SumTo(Function):
  def __init__(self,shape):
    self.shape = shape

  def forward(self,x):
    self.x_shape = x.shape
    y = utils.sum_to(x,self.shape)
    return y

  def backward(self,gy):
    gx = broadcast_to(gy,self.x_shape)
    return gx

class MatMul(Function):
  def forward(self,x,W):
    y = x.dot(W) #X乘以W
    return y

  def backward(self,gy):
    x,W = self.inputs
    gx = matmul(gy,W.T)
    gW = matmul(x.T,gy)
    return gy,gW

def square(x):
  return Square()(x)

def exp(x):
  return Exp()(x)

def sin(x):
  return Sin()(x)

def cos(x):
  return Cos()(x)
  
def tanh(x):
  return Tanh()(x)

def reshape(x,shape):
  if x.data.shape == shape:
    #不仅variable有data属性，nparray也有data属性，
    #并且nparray.data.shape等于nparray.shape
    #所以这里reshape可以处理variable和nparray
    return as_variable(x)
  return Reshape(shape)(x)

def transpose(x):
  return Transpose()(x)

def sum(x,axis=None,keepdims=False):
  return Sum(axis,keepdims)(x)

def broadcast_to(x,shape):
  if x.shape == shape:
    return as_variable(x)
  return BroadcastTo(shape)(x)

def sum_to(x,shape):
  if x.shape == shape:
    return as_variable(x)
  return SumTo(shape)(x)

def matmul(x,W):
  return MatMul()(x,W)

class Linear(Function):
  def forward(self, x, W, b):
    y = x.dot(W)
    if b is not None:
      y += b
    return y

  def backward(self, gy):
    x, W, b = self.inputs
    gb = None if b.data is None else sum_to(gy, b.shape)
    gx = matmul(gy, W.T)
    gW = matmul(x.T, gy)
    return gx, gW, gb
def linear(x, W, b=None):
  return Linear()(x, W, b)

class Sigmoid(Function):
  def forward(self, x):
    xp = cuda.get_array_module(x)
    # y = 1 / (1 + xp.exp(-x))
    y = xp.tanh(x * 0.5) * 0.5 + 0.5  # Better implementation
    return y

  def backward(self, gy):
    y = self.outputs[0]()
    gx = gy * y * (1 - y)
    return gx
def sigmoid(x):
  return Sigmoid()(x)

class MeanSquaredError(Function):
  def forward(self, x0, x1):
    diff = x0 - x1
    y = (diff ** 2).sum() / len(diff)
    return y

  def backward(self, gy):
    x0, x1 = self.inputs
    diff = x0 - x1
    gx0 = gy * diff * (2. / len(diff))
    gx1 = -gx0
    return gx0, gx1
def mean_squared_error(x0, x1):
  return MeanSquaredError()(x0, x1)

class Softmax(Function):
    def __init__(self, axis=1):
        self.axis = axis

    def forward(self, x):
        xp = cuda.get_array_module(x)
        y = x - x.max(axis=self.axis, keepdims=True)
        y = xp.exp(y)
        y /= y.sum(axis=self.axis, keepdims=True)
        return y

    def backward(self, gy):
        y = self.outputs[0]()
        gx = y * gy
        sumdx = gx.sum(axis=self.axis, keepdims=True)
        gx -= y * sumdx
        return gx
def softmax(x, axis=1):
    return Softmax(axis)(x)

class GetItem(Function):
    def __init__(self, slices):
        self.slices = slices

    def forward(self, x):
        y = x[self.slices]
        return y

    def backward(self, gy):
        x, = self.inputs
        f = GetItemGrad(self.slices, x.shape)
        return f(gy)
class GetItemGrad(Function):
    def __init__(self, slices, in_shape):
        self.slices = slices
        self.in_shape = in_shape

    def forward(self, gy):
        xp = dezero.cuda.get_array_module(gy)
        gx = xp.zeros(self.in_shape, dtype=gy.dtype)

        if xp is np:
            np.add.at(gx, self.slices, gy)
        else:
            xp.scatter_add(gx, self.slices, gy)
        return gx

    def backward(self, ggx):
        return get_item(ggx, self.slices)
def get_item(x, slices):
    f = GetItem(slices)
    return f(x)

class Softmax(Function):
    def __init__(self, axis=1):
        self.axis = axis

    def forward(self, x):
        xp = cuda.get_array_module(x)
        y = x - x.max(axis=self.axis, keepdims=True)
        y = xp.exp(y)
        y /= y.sum(axis=self.axis, keepdims=True)
        return y

    def backward(self, gy):
        y = self.outputs[0]()
        gx = y * gy
        sumdx = gx.sum(axis=self.axis, keepdims=True)
        gx -= y * sumdx
        return gx
def softmax(x, axis=1):
    return Softmax(axis)(x)

class SoftmaxCrossEntropy(Function):
    def forward(self, x, t):
        N = x.shape[0]
        # 虽然我不明白发生了什么，但毫无疑问，x已从3列的矩阵变成了log_z这样1列的向量
        log_z = utils.logsumexp(x, axis=1)
        log_p = x - log_z
        # ravel将多维数组改为一维向量
        # log_p很多行[A B C],t.ravel()[1 2 1 ~]
        # 新的log_p是一维[B C B ~]
        # 这一步是在实现P338所述，交叉熵误差可以通过提取正确类别编号的概率p来进行计算
        log_p = log_p[np.arange(N), t.ravel()]
        # 全部加起来除以X的行数，返回
        y = -log_p.sum() / np.float32(N)
        return y

    def backward(self, gy):
        x, t = self.inputs
        N, CLS_NUM = x.shape

        gy *= 1/N
        y = softmax(x)
        # convert to one-hot
        xp = cuda.get_array_module(t.data)
        t_onehot = xp.eye(CLS_NUM, dtype=t.dtype)[t.data]
        y = (y - t_onehot) * gy
        return y
def softmax_cross_entropy(x, t):
    return SoftmaxCrossEntropy()(x, t)

class Clip(Function):
    def __init__(self, x_min, x_max):
        self.x_min = x_min
        self.x_max = x_max

    def forward(self, x):
        xp = cuda.get_array_module(x)
        y = xp.clip(x, self.x_min, self.x_max)
        return y

    def backward(self, gy):
        x, = self.inputs
        mask = (x.data >= self.x_min) * (x.data <= self.x_max)
        gx = gy * mask
        return gx
def clip(x, x_min, x_max):
    return Clip(x_min, x_max)(x)

class Log(Function):
  # 默认以e为底
  def forward(self, x):
      xp = cuda.get_array_module(x)
      y = xp.log(x)
      return y

  def backward(self, gy):
      x, = self.inputs
      gx = gy / x
      return gx
def log(x):
    return Log()(x)

# 计算y相对于t的正确率
def accuracy(y, t):
    """
    [警告] 不能对该函数求导
    """
    # 将参数转化为Variable实例
    y, t = as_variable(y), as_variable(t)

    # 获得y.data中每行最大值的索引，并与t同形状
    pred = y.data.argmax(axis=1).reshape(t.shape)
    # nparray数组之间用“==”运算，得出来的是[True,True,False,False]这样的形式
    result = (pred == t.data)
    # 求出平均数，false为0，true为1
    acc = result.mean()
    return Variable(as_array(acc))









