import grpc
from concurrent import futures
import helloworld_pb2
import helloworld_pb2_grpc
import asyncio


# 实现定义的方法
class Greeter(helloworld_pb2_grpc.GreeterServicer):

    async def SayHello(self, request: helloworld_pb2.HelloRequest,
                       context: grpc.aio.ServicerContext) -> helloworld_pb2.HelloResponse:
        """接收request,返回response
        SayHello是proto中service Greeter中的rpc SayHello
        """
        print("request name is", request.name)
        #                                   message是HelloResponse中的参数            name是HelloRequest中的参数
        return helloworld_pb2.HelloResponse(message="hello,{msg}".format(msg=request.name))


async def serve():
    # 最大客户端连接10(max_workers=10)
    # 异步要用 aio
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    # 绑定处理器
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)

    server.add_insecure_port("localhost:50054")
    await server.start()
    print('gRPC 服务端已开启，端口为50054...')
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
