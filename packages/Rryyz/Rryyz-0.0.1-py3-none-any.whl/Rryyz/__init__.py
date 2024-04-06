is_simple_core = False

if is_simple_core:
  from Rryyz.core_simple import Variable,Function,using_config,no_grad,as_array,as_variable,setup_variable
else:
  from Rryyz.core import Variable,Function,using_config,no_grad,as_array,as_variable,setup_variable
  from Rryyz.models import Model
  from Rryyz.dataloaders import DataLoader
  import Rryyz.cuda,Rryyz.datasets

setup_variable()

def start():
    print("import successful")