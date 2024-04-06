def _dot_var(v,verbose=False):
  dot_var = '{}[label="{}",color=orange,style=filled]\n'
  try:
    name = "" if v.name is None else v.name
  except AttributeError:
    v.name = None
    name = ""
  if verbose and v.data is not None:
    if v.name is not None:
      name += ":"
    name += str(v.shape) + " " + str(v.dtype)

  return dot_var.format(id(v),name)

def _dot_func(f):
  dot_func = '{}[label="{}",color=lightblue,style=filled,shape=box]\n'
  txt = dot_func.format(id(f),f.__class__.__name__)

  dot_edge = "{}->{}\n"
  for x in f.inputs:
    txt += dot_edge.format(id(x),id(f))
  for y in f.outputs:
    txt += dot_edge.format(id(f),id(y()))  # y是weakref
  return txt

def get_dot_graph(output,verbose=True):
  txt = ""
  funcs = []
  seen_set = set()

  def add_func(f):
    if f not in seen_set:
      funcs.append(f)
      seen_set.add(f)

  add_func(output.creator)
  txt += _dot_var(output,verbose)

  while funcs:
    func = funcs.pop()
    txt += _dot_func(func)
    for x in func.inputs:
      txt += _dot_var(x,verbose)

      if x.creator is not None:
        add_func(x.creator)
  return "digraph g {\n" + txt + "}"

import os
import subprocess
#在logsumexp函数里引用
from dezero import cuda

def plot_dot_graph(output,verbose=True,to_file="graph.png"):
  dot_graph = get_dot_graph(output,verbose)

  tmp_dir = os.path.join(os.path.expanduser("{}".format(os.path.dirname(__file__))),"是DOT图像吖")
  if not os.path.exists(tmp_dir):
    os.mkdir(tmp_dir)
  graph_path = os.path.join(tmp_dir,"tmp_grah.dot")

  with open(graph_path,"w") as f:
    f.write(dot_graph)

  extension = os.path.splitext(to_file)[1][1:]
  cmd = "dot {} -T {} -o {}".format(graph_path,extension,to_file)
  subprocess.run(cmd,shell=True)

def sum_to(x, shape):
    ndim = len(shape)
    lead = x.ndim - ndim
    lead_axis = tuple(range(lead))

    axis = tuple([i + lead for i, sx in enumerate(shape) if sx == 1])
    y = x.sum(lead_axis + axis, keepdims=True)
    if lead > 0:
        y = y.squeeze(lead_axis)
    return y

#datasets.py引用
def get_file(url, file_name=None):
    """Download a file from the `url` if it is not in the cache.

    The file at the `url` is downloaded to the `~/.dezero`.

    Args:
        url (str): URL of the file.
        file_name (str): Name of the file. It `None` is specified the original
            file name is used.

    Returns:
        str: Absolute path to the saved file.
    """
    if file_name is None:
        file_name = url[url.rfind('/') + 1:]
    file_path = os.path.join(cache_dir, file_name)

    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)

    if os.path.exists(file_path):
        return file_path

    print("Downloading: " + file_name)
    try:
        urllib.request.urlretrieve(url, file_path, show_progress)
    except (Exception, KeyboardInterrupt) as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise
    print(" Done")

    return file_path
cache_dir = os.path.join(os.path.expanduser('~'), '.Rryyz')
#transforms.py引用
def pair(x):
    if isinstance(x, int):
        return (x, x)
    elif isinstance(x, tuple):
        assert len(x) == 2
        return x
    else:
        raise ValueError
#funcitons.py里的SoftmaxCrossEntropy类引用
def logsumexp(x, axis=1):
    xp = cuda.get_array_module(x)
    m = x.max(axis=axis, keepdims=True)
    y = x - m
    xp.exp(y, out=y)
    s = y.sum(axis=axis, keepdims=True)
    xp.log(s, out=s)
    m += s
    return m


