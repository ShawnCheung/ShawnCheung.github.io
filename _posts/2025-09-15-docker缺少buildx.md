---
title: docker缺少buildx
date: 2025-09-15 11:00:00
categories: [linux系统, 运维]
tags: [运维]
---

## 缺少buildx

docker buildx version
docker: 'buildx' is not a docker command.
See 'docker --help'

## 安装buildx


```bash
# 创建插件目录
mkdir -p ~/.docker/cli-plugins

# 下载适合你系统的buildx二进制文件
# 如果下载不到，请转到https://github.com/docker/buildx/releases/获取下载链接
curl -L https://github.com/docker/buildx/releases/latest/download/buildx-linux-amd64 -o ~/.docker/cli-plugins/docker-buildx

# 添加执行权限
chmod +x ~/.docker/cli-plugins/docker-buildx
cp ~/.docker/cli-plugins/docker-buildx /usr/lib/docker/cli-plugins/docker-buildx
```

## 检查buildx是否安装成功

```bash
docker buildx version
```

