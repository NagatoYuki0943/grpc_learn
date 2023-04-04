import grpc
from concurrent import futures
import trans_image_pb2
import trans_image_pb2_grpc
import asyncio
from funcs import detect


class Server(trans_image_pb2_grpc.TransImageServicer):
    async def trans(self, request: trans_image_pb2.DataRquest,
                    context: grpc.aio.ServicerContext)-> trans_image_pb2.DataResponse:
        """接收request,返回response
        trans是proto中service TransImage中的rpc trans
        """
        image_64, detect_64 = detect(request)

        #==================返回图片和结果===================#
        #                                   image和result是DataResponse中设定的变量
        return trans_image_pb2.DataResponse(image=image_64, detect=detect_64)


async def run():
    # 最大客户端连接10(max_workers=10)，这里可定义最大接收和发送大小(单位M)，默认只有4M
    # 异步要用 aio
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10),
                         options=[('grpc.max_send_message_length', 100 * 1024 * 1024),
                                  ('grpc.max_receive_message_length', 100 * 1024 * 1024)]
                        )
    # 绑定处理器
    trans_image_pb2_grpc.add_TransImageServicer_to_server(Server(), server)

    server.add_insecure_port("localhost:50054")
    await server.start()
    print('gRPC 服务端已开启，端口为50054...')
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(run())
