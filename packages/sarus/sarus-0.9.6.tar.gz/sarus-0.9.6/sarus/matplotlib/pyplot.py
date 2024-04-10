from sarus.utils import register_ops

try:
    from matplotlib.pyplot import *  # noqa: F401
except ModuleNotFoundError:
    pass
else:
    register_ops()
