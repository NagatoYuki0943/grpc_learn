import grpc
from concurrent import futures
import helloworld_pb2
import helloworld_pb2_grpc
import multiprocessing


# 实现定义的方法
class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def __init__(self, port: int) -> None:
        super().__init__()
        # 保存port用来打印
        self.port = port

    def SayHello(self, request: helloworld_pb2.HelloRequest,
                       context: grpc.ServicerContext) -> helloworld_pb2.HelloResponse:
        """接收request,返回response
        SayHello是proto中service Greeter中的rpc SayHello
        """
        #                                   message是HelloResponse中的参数            name是HelloRequest中的参数
        return helloworld_pb2.HelloResponse(message="hello,{msg}, server port is {port}".format(msg=request.name, port=self.port))


def serve(port: int):
    # 最大客户端连接10(max_workers=10)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # 绑定处理器
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(port), server)

    # 绑定地址
    server.add_insecure_port("localhost:" + str(port))
    server.start()
    print(f'gRPC 服务端已开启，端口为{port}...')
    server.wait_for_termination()


# 线程数
_PROCESS_COUNT = multiprocessing.cpu_count()
# 每个线程分配一个端口
_PORTS = [50054 + i for i in range(_PROCESS_COUNT)]


def multiprocess():
    workers: list[multiprocessing.Process] = []
    for _, port in zip(range(_PROCESS_COUNT), _PORTS):
        # 每个线程分配一个端口
        worker = multiprocessing.Process(target=serve, args=(port,))
        worker.start()
        workers.append(worker)
    for worker in workers:
        worker.join()


if __name__ == "__main__":
    # serve()
    multiprocess()
