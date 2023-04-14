import grpc
from concurrent import futures
import object_detect_pb2
import object_detect_pb2_grpc
from funcs import detect



SERVER_HOST = "localhost:50054"


class Server(object_detect_pb2_grpc.YoloDetectServicer):
    def v5_detect(self, request: object_detect_pb2.Request,
                    context: grpc.ServicerContext)-> object_detect_pb2.Response:
        """接收request,返回response
        v5_detect是proto中service YoloDetectServicer v5_detect
        """
        image_64, detect_str = detect(request)

        #==================返回图片和结果===================#
        #                                 image和detect是Response中设定的变量
        return object_detect_pb2.Response(image=image_64, detect=detect_str)

    def v8_detect(self, request: object_detect_pb2.Request,
                    context: grpc.ServicerContext)-> object_detect_pb2.Response:
        """写的和V5的完全相同,用来测试多个方法
        """
        image_64, detect_str = detect(request)

        #==================返回图片和结果===================#
        #                                 image和detect是Response中设定的变量
        return object_detect_pb2.Response(image=image_64, detect=detect_str)

def run():
    # 最大客户端连接10(max_workers=10)，这里可定义最大接收和发送大小(单位M)，默认只有4M
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10),
                         options=[('grpc.max_send_message_length', 100 * 1024 * 1024),
                                  ('grpc.max_receive_message_length', 100 * 1024 * 1024)]
                        )
    # 绑定处理器
    object_detect_pb2_grpc.add_YoloDetectServicer_to_server(Server(), server)

    server.add_insecure_port(SERVER_HOST)
    server.start()
    print(f'gRPC 服务端已开启，地址为 {SERVER_HOST}...')
    server.wait_for_termination()


if __name__ == "__main__":
    run()
