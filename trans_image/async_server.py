import numpy as np
import cv2
import grpc
import pickle
from concurrent import futures
import base64
import trans_image_pb2
import trans_image_pb2_grpc
import asyncio


class Server(trans_image_pb2_grpc.TransImageServicer):
    async def trans(self, request: trans_image_pb2.DataRquest,
                    context: grpc.aio.ServicerContext)-> trans_image_pb2.DataResponse:
        """接收request,返回response
        trans是proto中service TransImage中的rpc trans
        """
        #=====================接收图片=====================#
        # 解码图片                               image是DataRquest中设定的变量
        image_decode = base64.b64decode(request.image)
        # 变成一个矩阵 单维向量
        array = np.frombuffer(image_decode, dtype=np.uint8)
        # print("array shape:", array.shape)
        # 再解码成图片 三维图片
        image_bgr = cv2.imdecode(array, cv2.IMREAD_COLOR)
        print("image shape:", image_bgr.shape)
        cv2.imwrite("images/server_save.jpg", image_bgr)

        #=====================修改图片=====================#
        cross = np.random.uniform(0, 1, image_bgr.shape)
        image = image_bgr * cross
        image = image.astype(np.uint8)

        #=====================编码图片=====================#
        # 返回True和编码,这里只要编码
        image_encode = cv2.imencode(".jpg", image)[1]
        # image_bytes = image_encode.tobytes()
        # image_64 = base64.b64encode(image_bytes)
        image_64 = base64.b64encode(image_encode)

        #=====================编码结果=====================#
        # 假设检测结果
        detect = [
            {"class_index": 0, "confidence": 0.9, "box": [1, 2, 100, 200]},
            {"class_index": 1, "confidence": 0.8, "box": [100, 12, 300, 400]},
            {"class_index": 1, "confidence": 0.7, "box": [102, 200, 300, 520]},
        ]
        # 使用pickle序列化预测结果
        pickle_detect = pickle.dumps(detect)
        # 编码
        detect_64 = base64.b64encode(pickle_detect)

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
