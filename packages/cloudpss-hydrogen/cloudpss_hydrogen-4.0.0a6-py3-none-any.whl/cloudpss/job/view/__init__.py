from .IESView import IESView
from .view import View
from .EMTView import EMTView
from .PowerFlowView import PowerFlowView
from .IESLabSimulationView import IESLabSimulationView
from .IESLabTypicalDayView import IESLabTypicalDayView
from ..messageStreamReceiver import MessageStreamReceiver
from ..messageStreamSender import MessageStreamSender
__all__ = [
    'View','EMTView','PowerFlowView','IESLabSimulationView','IESView','IESLabTypicalDayView'
]

VIEW = {
    'function/CloudPSS/emtp': EMTView,
    'function/CloudPSS/emtps': EMTView,
    'function/CloudPSS/sfemt': EMTView,
    'function/CloudPSS/power-flow': PowerFlowView,
    'function/CloudPSS/ies-simulation': IESView,
    'function/CloudPSS/ies-optimization': IESView,
    'function/ies/ies-optimization': IESView,
    'function/CloudPSS/three-phase-powerFlow': PowerFlowView,
    'function/ies/ies-simulation': IESLabSimulationView,
    'function/ies/ies-gmm':IESLabTypicalDayView,
    'function/CloudPSS/ieslab-simulation': IESLabSimulationView,
    'function/CloudPSS/ieslab-gmm':IESLabTypicalDayView,
    'function/CloudPSS/ieslab-optimization': IESView,
}


def getViewClass(rid: str) -> View:
    """
    获取仿真结果视图

    :param rid: 仿真任务的 rid
    :param db: 仿真任务的数据库

    :return: 仿真结果视图

    >>> view = get_view('function/CloudPSS/emtp', db)
    >>> view.getPlots()
    """
    return VIEW.get(rid, View)