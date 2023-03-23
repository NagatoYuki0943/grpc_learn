import grpc

import helloworld_pb2
import helloworld_pb2_grpc


def run():
    """发送request,接收response
    """
    # 本次不使用SSL，所以channel是不安全的
    channel = grpc.insecure_channel("localhost:50054")
    # 客户端实例
    stub = helloworld_pb2_grpc.GreeterStub(channel)
    # 调用服务端方法                             dept_id,dept_name,uid_list是GetDeptUserRequest中定义的变量
    request = helloworld_pb2.GetDeptUserRequest(dept_id=1, dept_name='tom', uid_list=[1, 2, 3])

    # 后续添加参数的方法
    # request = helloworld_pb2.GetDeptUserRequest()
    # request.dept_id = 110
    # request.dept_name = 'police'
    # request.uid_list.append(1)
    # request.uid_list.append(2)
    # request.uid_list.append(3)

    # 发送请求得到相应
    # GetDeptUser是proto中service中的rpc GetDeptUser
    response = stub.GetDeptUser(request)
    #              user_list,user_map是GetDeptUserResponse中定义的变量

    print(response.user_list)
    print(response.user_map)


if __name__ == "__main__":
    run()
