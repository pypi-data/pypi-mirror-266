from cloudpss.runner.IESLabPlanResult import IESLabPlanResult
from cloudpss.runner.runner import HttpRunner, Runner
from ..utils import request, fileLoad
import json
from enum import IntEnum, unique


class IESLabPlanModel(object):
    _baseUri = 'api/ieslab-plan/taskmanager/getSimuLastTasks'

    def __init__(self, simulationId):
        '''
            初始化
        '''
        self.simulationId = simulationId
        self.optimizationInfo = self.GetOptimizationInfo()
        self.OptimizationMode = OptimizationMode

    def _fetchItemData(self, url):
        '''
            获取当前算例的优化目标设置信息

            :return: enum 类型，代表经济性优化和环保性优化的类型
        '''
        r = request('GET', url, params={"simuid": self.simulationId})
        data = json.loads(r.text)
        return data

    def GetOptimizationInfo(self):
        '''
            获取当前算例的优化目标设置信息

            :return: enum 类型，代表经济性优化和环保性优化的类型
        '''
        try:
            data = self._fetchItemData(self._baseUri)
            for e in OptimizationMode:
                if (e.value == data['data']['optimizationpara']
                    ['OptimizationMode']):
                    return e
        except:
            return OptimizationMode['经济性']

    def SetOptimizationInfo(self, optType):
        '''
            无对应接口
            设置当前算例的优化目标

            :param optType: enum 类型，代表经济性优化和环保性优化的类型
        '''
        self.optimizationInfo = optType
        return True

    def run(self) -> Runner[IESLabPlanResult]:
        '''
            生成方案优选算例

            :return: Runner[IESLabPlanResult]
        '''
        isRunning = self.GetLastTaskResult()
        if isRunning:
            raise Exception('该算例正在运行！请从浏览器算例页面点击结束运行或者调用IESPlan对象的kill接口终止计算后重试！')
        else:
            url = 'api/ieslab-plan/taskmanager/runOptimization'
            if self.optimizationInfo is None:
                self.optimizationInfo = OptimizationMode['经济性']
            optType = self.optimizationInfo.value or 0
            try:
                r = request('GET',
                            url,
                            params={
                                "simuid":
                                self.simulationId,
                                "optPara":
                                json.dumps({
                                    "OptimizationMode": optType,
                                    "ProjectPeriod": "20"
                                })
                            })
                data = json.loads(r.text)
                return HttpRunner({}, self.simulationId)
            except:
                raise Exception('生成方案优选算例失败')

    def GetRunner(self) -> Runner[IESLabPlanResult]:
        '''
            获得运行实例

            :return: Runner[IESLabPlanResult]
        '''
        return HttpRunner({}, self.simulationId)
    
    def kill(self) -> bool:
        '''
            停止并删除当前运行的优化算例
        '''
        res = IESLabPlanResult(self.simulationId).getLastTaskResult()
        error = res.get('error', 0)
        if error == 0:
            data = res.get('data', {})
            if data is not None:
                taskID = data.get('task_id', '')
        url = f'api/ieslab-plan/taskmanager/removeOptimizationTask'
        try:
            r = request('GET',
                        url,
                        params={
                            "taskid": taskID,
                            "stopFlag": '2'
                        })
            json.loads(r.text)
            return True
        except:
            return False

    def GetLastTaskResult(self)-> bool:
        '''
            获取最后一次运行的taskID的运行结果与日志

            :return: boolean 类型
        '''
        isRunning = True
        res = IESLabPlanResult(self.simulationId).getLastTaskResult()
        error = res.get('error', 0)
        if error == 0:
            data = res.get('data', {})
            if data is not None:
                status = data.get('status', '')
                if status == 'stop':
                    isRunning = False
        logs = IESLabPlanResult(self.simulationId).GetLogs()
        if logs is not None:
            for log in logs:
                if(log.get('data', '') == 'run ends'):
                    isRunning = False
                    break
        return isRunning


# @unique
class OptimizationMode(IntEnum):
    经济性 = 0
    环保性 = 1