import requests

# # 调用函数获取内网 IP
# ip = get_internal_ip()
# print(ip)

def get_config(env, group, key):
    url = f"http://127.0.0.1:5000/get_config?group={group}&key={key}&env={env}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['statusCode'] == 200:
            return data['data']
        else:
            print(f"Failed to get config. Status code: {data['statusCode']}, Message: {data['statusMessage']}")
    else:
        print(f"Failed to send request. Status code: {response.status_code}")

    return None


def add_config(env, group, key, config):
    url = "http://localhost:5000/add_config"

    data = {
        'env': env,
        'group': group,
        'key': key,
        'config': config
    }

    response = requests.post(url, json=data)
    if response.status_code == 200:
        data = response.json()
        if data['statusCode'] == 200:
            print("Config added successfully.")
        else:
            print(f"Failed to add config. Status code: {data['statusCode']}, Message: {data['statusMessage']}")
    else:
        print(f"Failed to send request. Status code: {response.status_code}")


import socket


def get_internal_ip():
    try:
        # 创建一个 UDP 套接字
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # 连接到一个外部的 IP 地址（此处选择了 Google 的 DNS 服务器）
        sock.connect(('8.8.8.8', 80))

        # 获取套接字绑定的本地地址信息
        internal_ip = sock.getsockname()[0]

        return internal_ip
    except socket.error:
        return None


if __name__ == '__main__':
    # 示例用法
    env = "dev"
    group = "spider"
    key = "server_url"
    config = "http://example.com"
    print(get_config(env, group, key))
