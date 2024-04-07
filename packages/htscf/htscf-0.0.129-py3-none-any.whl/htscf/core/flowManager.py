import time
from multiprocessing import Process, Manager
from os import kill
from signal import SIGKILL

from htscf.utils.logging import Logger
from htscf.core.flow import Workflow

logger = Logger()


class FlowHandler:
    def __init__(self, workflow_definition):
        self.manager = Manager()
        self.sharedDict = self.manager.dict()
        self.flow_id = None
        self.sharedDict["workflow_definition"] = workflow_definition

    def run(self):
        p1 = Process(target=FlowHandler.run_flow, args=(self.sharedDict,))
        p2 = Process(target=self._handler, args=(self.sharedDict,))
        p1.start()
        self.sharedDict["p1_pid"] = p1.pid
        p2.start()
        p1.join()
        p2.terminate()  # 确保 _handler 进程也会被终止
        p2.join()
        self.manager.shutdown()  # 显式关闭 Manager

    @staticmethod
    def run_flow(sharedDict):
        workflow_definition = sharedDict["workflow_definition"]
        workflow = Workflow(workflow_definition)
        sharedDict["flow_id"] = workflow.flow_id
        try:
            workflow.run()
        except Exception as e:
            sharedDict["error"] = str(e)
            logger.error({
                "content": f"流程运行错误：{e}"
            })
        finally:
            sharedDict["status"] = "complete"
            logger.info({
                "content": f"流程{workflow.flow_id}运行结束"
            })

    def _handler(self, sharedDict):
        p1_pid = sharedDict["p1_pid"]
        while True:
            if sharedDict.get('status') == 'complete' or sharedDict.get('error'):
                break
            else:
                if not self.handler(sharedDict):
                    kill(p1_pid, SIGKILL)
                    break
                time.sleep(0.5)

    def handler(self, sharedDict):
        return True
