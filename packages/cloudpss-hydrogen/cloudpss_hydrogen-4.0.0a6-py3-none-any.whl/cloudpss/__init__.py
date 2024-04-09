# coding=UTF-8
from cloudpss.ieslab import IESLabSimulation, IESLabPlan
from .verify import setToken
from .runner import Runner, Result, EMTResult, PowerFlowResult
from .model import Model, ModelRevision, ModelTopology
from .project import Project
from .utils import MatlabDataEncoder, DateTimeEncode
from . import function

from .function import FunctionExecution
from .version import __version__
__all__ = [
    'setToken', 'Model', 'ModelRevision', 'ModelTopology', 'Runner', 'Result',
    'PowerFlowResult', 'EMTResult', 'MatlabDataEncoder', 'DateTimeEncode',
    'function', 'Project', 'currentJob', 'IESLabSimulation', 'IESLabPlan','__version__'
]



def currentJob():
    """
        获取当前的 currentExecution 实例
    """
    return FunctionExecution.current()