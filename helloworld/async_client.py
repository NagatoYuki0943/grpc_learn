import grpc
import helloworld_pb2
import helloworld_pb2_grpc
import asyncio


async def run():
    """发送request,接收response
    """
    # 本次不使用SSL，所以channel是不安全的
    # 异步要用 aio
    async with grpc.aio.insecure_channel("localhost:50054") as channel:
        # 客户端实例
        stub = helloworld_pb2_grpc.GreeterStub(channel)
        # SayHello是proto中service Greeter中的rpc SayHello
        # 调用服务端方法                                      name是HelloRequest中的参数
        response = await stub.SayHello(helloworld_pb2.HelloRequest(name='World'))
    #                                    message是HelloResponse中的参数
    print("Greeter client receiverd: " + response.message)


if __name__ == "__main__":
    asyncio.run(run())

# https://www.bilibili.com/video/BV1F54y1K76g/?spm_id_from=333.337.search-card.all.click