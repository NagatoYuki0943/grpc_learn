import grpc
from concurrent import futures
import object_detect_pb2
import object_detect_pb2_grpc
import asyncio
from funcs import detect


class Server(object_detect_pb2_grpc.YoloDetectServicer):
    async def V5Detect(self, request: object_detect_pb2.Request,
                    context: grpc.aio.ServicerContext)-> object_detect_pb2.Response:
        """接收request,返回response
        V5Detect是proto中service YoloDetectServicer V5Detect
        """
        image_64, detect_64 = detect(request)

        #==================返回图片和结果===================#
        #                                 image和detect是Response中设定的变量
        return object_detect_pb2.Response(image=image_64, detect=detect_64)


async def run():
    # 最大客户端连接10(max_workers=10)，这里可定义最大接收和发送大小(单位M)，默认只有4M
    # 异步要用 aio
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10),
                         options=[('grpc.max_send_message_length', 100 * 1024 * 1024),
                                  ('grpc.max_receive_message_length', 100 * 1024 * 1024)]
                        )
    # 绑定处理器
    object_detect_pb2_grpc.add_YoloDetectServicer_to_server(Server(), server)

    server.add_insecure_port("localhost:50054")
    await server.start()
    print('gRPC 服务端已开启，端口为50054...')
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(run())
