---
layout: post
title: 在docker中使用GPU
date: 2025-09-12 14:56 +0800
categories: [linux系统, 运维]
tags: [运维]
---

1. 安装完docker后直接使用GPU

```bash
docker run --gpus all ...
```

如果遇到报错：

```bash
docker: Error response from daemon: could not select device driver "" with capabilities: [[gpu]].
ERRO[0000] error waiting for container: context canceled 
```
说明docker没有识别到GPU，需要安装nvidia-docker2。

2. 安装nvidia-container-toolkit插件

```bash
# 添加仓库
curl -s -L https://nvidia.github.io/nvidia-container-toolkit/gpgkey | sudo apt-key add -
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-container-toolkit/$distribution/nvidia-container-toolkit.list | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# 安装
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# 配置 Docker runtime
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

3. 检查docker默认的runtime设置

查看 Docker 配置文件 /etc/docker/daemon.json 是否包含：
```json
{
  "runtimes": {
    "nvidia": {
      "path": "nvidia-container-runtime",
      "runtimeArgs": []
    }
  },
  "default-runtime": "nvidia"
}
```

如果没有，加上后：
```bash
sudo systemctl restart docker
```

4. 运行容器的方式

```bash
docker run --gpus all <image>
```