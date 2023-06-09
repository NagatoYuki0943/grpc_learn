import grpc
import random
from concurrent import futures
import helloworld_pb2
import helloworld_pb2_grpc
import asyncio


# 实现定义的方法
class Greeter(helloworld_pb2_grpc.GreeterServicer):

    async def GetDeptUser(self, request: helloworld_pb2.GetDeptUserRequest,
                          context: grpc.aio.ServicerContext) -> helloworld_pb2.GetDeptUserResponse:
        """接收request,返回response
        GetDeptUser是proto中service中的rpc GetDeptUser
        """
        # 获取GetDeptUserRequest中的变量
        dept_id = request.dept_id
        dept_name = request.dept_name
        uid_list = request.uid_list
        if dept_id <= 0 or dept_name == "" or len(uid_list) <= 0:
            return helloworld_pb2.GetDeptUserResponse()

        print("dept_id is {0}, dept_name is {1}".format(dept_id, dept_name))
        user_list = []
        user_map = {}
        for id_ in uid_list:
            uid = id_ + random.randint(1, 1000)
            letters = "GetDeptUserResponse"
            name = "".join(random.sample(letters, 10))
            user = helloworld_pb2.BasicUser()
            user.id = uid
            user.name = name
            user_list.append(user)
            user_map[uid] = user
        #                                         user_list,user_map是GetDeptUserResponse中的变量
        return helloworld_pb2.GetDeptUserResponse(user_list=user_list, user_map=user_map)


async def serve():
    # 最大客户端连接10(max_workers=10)
    # 异步要用 aio
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    # 绑定处理器
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)

    # 绑定地址
    server.add_insecure_port("localhost:50054")
    await server.start()
    print('gRPC 服务端已开启，端口为50054...')
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
