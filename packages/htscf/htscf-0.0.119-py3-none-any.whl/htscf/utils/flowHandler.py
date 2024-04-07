import socketserver
from multiprocessing import Process, Value, Semaphore, Manager
from os import kill
from signal import SIGKILL


class FlowHandler:
    def __init__(self, DEBUG=False):
        self.value = Value("l", -1)
        self.value2 = Value("l", -1)
        self.signal = Semaphore(1)
        self.data = Manager().dict()
        self.DEBUG = DEBUG

    def handle(self, data):
        pass

    def handleRunning(self, data):
        pass

    def handleExit(self, data):
        pass

    def runFlow(self, signal, value, value2, data):
        """
        执行流程的代码
        """
        try:
            p = Process(target=self.handleRunning, args=[data])
            p.start()
            with self.value2.get_lock():
                if self.DEBUG:
                    print(f"running pid:{p.pid}")
                self.value2.value = p.pid
            self.handle(data)
        except Exception as e:
            print(e)
        finally:
            self.stopRunningProcess(value2)
            FlowHandler.resetValue(value)
            FlowHandler.resetValue(value2)
            signal.release()

    @staticmethod
    def resetValue(value):
        """重置共享内存值为-1"""
        with value.get_lock():
            value.value = -1

    def stopRunningProcess(self, value2):
        """流程进程结束时，同时也结束同步运行的进程"""
        with value2.get_lock():
            if value2.value != -1:
                try:
                    kill(value2.value, SIGKILL)
                except Exception:
                    print(f"running process(pid:{value2.value}) already exit")
                FlowHandler.resetValue(value2)

    def create(self, value, value2, signal, data):
        """
        用于创建流程，每次只能创建一个，当上一个流程被终止或运行结束时，启动新的流程
        """
        while signal.acquire():
            process = Process(target=self.runFlow, args=[signal, value, value2, data])
            process.start()
            with value.get_lock():
                if self.DEBUG:
                    print(f"flow pid:{process.pid}")
                value.value = process.pid

    def createHandler(self):
        value = self.value
        value2 = self.value2
        signal = self.signal
        data = self.data
        this = self
        p1 = Process(target=self.create, args=[value, value2, signal, data])  # 初始化"创建流程进程"以创建"流程进程"
        p1.start()

        class MyTCPHandler(socketserver.BaseRequestHandler):
            def handle(self):
                self.data = self.request.recv(1024).strip()
                if self.data.decode("utf-8") == "stop":
                    with value.get_lock():
                        pid = value.value
                        try:
                            kill(value.value, SIGKILL)
                        except Exception:
                            print(f"Flow process(pid:{value.value}) already exit")
                        value.value = -1
                        this.handleExit(this.data)
                        this.stopRunningProcess(value2)
                        signal.release()  # 释放锁，以是的创建流程的进程激活以创建新的流程进程
                        self.request.sendall(b"OK,killed " + bytes(str(pid), "utf-8"))
                elif self.data.decode("utf-8") == "getpid":
                    pid = value.value
                    self.request.sendall(bytes(str(pid), "utf-8"))

        return MyTCPHandler

    def createServer(self, host, port):
        with socketserver.TCPServer((host, port), self.createHandler()) as server:
            print(f"Server started at tcp://{host}:{port}")
            server.serve_forever()


if __name__ == '__main__':
    import time


    class MyFlowHandler(FlowHandler):
        def __init__(self):

            super().__init__(DEBUG=True)

        def handle(self, data):
            while True:
                time.sleep(1)
                print("hi")

        def handleExit(self, data):
            print("exit 0。。。")

        def handleRunning(self, data):
            while True:
                time.sleep(1)
                print("Running")


    MyFlowHandler().createServer("localhost", 8086)
