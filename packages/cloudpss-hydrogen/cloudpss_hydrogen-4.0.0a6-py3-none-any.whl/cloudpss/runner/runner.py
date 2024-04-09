from cProfile import run
import threading
import json
import time
import random
from .receiver import Receiver
from .result import IESLabSimulationResult, PowerFlowResult, EMTResult, Result, IESResult
from .IESLabPlanResult import IESLabPlanResult
from .IESLabEvaluationResult import IESLabEvaluationResult
from .IESLabTypicalDayResult import IESLabTypicalDayResult
from .storage import Storage
from ..utils import request
from typing import  TypeVar,  Generic

RECEIVER = {
    'default': Receiver,
}
T = TypeVar('T', Result, EMTResult, PowerFlowResult, IESResult,
            IESLabSimulationResult, IESLabPlanResult, IESLabEvaluationResult,IESLabTypicalDayResult)

IES_LAB_RESULT = {
    'function/ieslab/plan': IESLabPlanResult,
    'function/ieslab/evaluation': IESLabEvaluationResult
}

RESULT_DB = {
    'function/CloudPSS/emtp': EMTResult,
    'function/CloudPSS/emtps': EMTResult,
    'function/CloudPSS/sfemt': EMTResult,
    'function/CloudPSS/power-flow': PowerFlowResult,
    'function/CloudPSS/ies-simulation': IESResult,
    'function/CloudPSS/ies-optimization': IESResult,
    'function/ies/ies-optimization': IESResult,
    'function/CloudPSS/three-phase-powerFlow': PowerFlowResult,
    'function/ies/ies-simulation': IESLabSimulationResult,
    'function/ies/ies-gmm':IESLabTypicalDayResult,
    'function/CloudPSS/ieslab-simulation': IESLabSimulationResult,
    'function/CloudPSS/ieslab-gmm':IESLabTypicalDayResult,
    'function/CloudPSS/ieslab-optimization': IESResult,
}

class Runner(Generic[T]):
    def __init__(self, taskId, name, job, config, revision, modelRid,
                 **kwargs):
        self.taskId = taskId
        self.db = Storage(taskId, name, job, config, revision, modelRid)
        rid =job['rid'].replace('job-definition/','function/').replace('/cloudpss/','/CloudPSS/')
        result = RESULT_DB.get(rid, Result)
        self.result: T = result(self.db)
        self.receiver = kwargs.get('receiver', None)

    def __listenStatus(self):
        if self.receiver is None:
            return False
        if self.receiver.status() == -1:
            raise Exception(self.receiver.error)
        return self.receiver.isOpen

    def status(self):
        """
        运行状态
        :return: 运行状态  0/1/-1 1 表示正常结束，0 表示运行中， -1 表示数据接收异常


        >>>> runner.status()  
        """
        if self.receiver is None:
            raise Exception('not find receiver')
        return self.receiver.status()

    def __listen(self, **kwargs):

        receiver = kwargs.get('RECEIVER', 'default')
        receiverclass = None
        if type(receiver) is str:
            if receiver not in RECEIVER:
                receiverclass = RECEIVER['default']
            else:
                receiverclass = RECEIVER[receiver]
        if receiverclass is None:
            raise Exception('not find receiver')
        self.receiver = receiverclass(self.taskId, self.db, **kwargs)
        self.receiver.connect()

    def terminate(self):
        """
        结束当前运行的算例

        """
        r = request("DELETE", 'api/simulation/runner/' + str(self.taskId))

    @staticmethod
    def create(revisionHash, job, config, name=None, rid='', **kwargs):
        '''
            创建一个运行任务

            :params: revision 项目版本号
            :params: job 调用仿真时使用的计算方案，为空时使用项目的第一个计算方案
            :params: config 调用仿真时使用的参数方案，为空时使用项目的第一个参数方案
            :params: name 任务名称，为空时使用项目的参数方案名称和计算方案名称
            :params: rid 项目rid，可为空

            :return: 返回一个运行实例

            >>> runner = Runner.runRevision(revision,job,config,'')
        '''
        taskId = str(int(time.time() * random.random()))

        runner = Runner(taskId, name, job, config, revisionHash, rid, **kwargs)
        event = threading.Event()
        thread = threading.Thread(target=runner.__listen, kwargs=kwargs)
        thread.setDaemon(True)
        thread.start()
        payload = {
            'args': config['args'],
            'job': job,
            'implement': kwargs.get('topology', None)
        }
        while not runner.__listenStatus():
            time.sleep(0.1)
        r = request('POST',
                    'api/simulation/runner/' + revisionHash + '/' +
                    str(taskId),
                    data=json.dumps(payload))

        return runner


class HttpRunner(Runner[T]):
    def __init__(self, job, simulationId, **kwargs):
        self.simulationId = simulationId
        self.job = job
        self.__taskId = self.__getLastTask()
        result = IES_LAB_RESULT.get(job.get('rid', ''), IESLabPlanResult)
        self.result: T = result(self.simulationId, self.__taskId, **kwargs)

    def __getLastTask(self):
        r = request('GET',
                    'api/ieslab-plan/taskmanager/getSimuLastTasks',
                    params={'simuid': self.simulationId})
        result = json.loads(r.text)
        return result['data'].get('task_id', None)

    def status(self):
        if self.__taskId is None:
            return False
        return self.result.status()  # type: ignore
