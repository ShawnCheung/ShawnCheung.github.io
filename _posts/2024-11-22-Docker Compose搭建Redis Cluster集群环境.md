---
layout: post
title: Docker Compose 搭建 Redis Cluster 集群环境
date: 2024-11-22 14:56 +0800
categories: [linux系统, 部署]
tags: [部署]
---

## 环境
整体安装分以下几个步骤：

* 安装docker-compose与docker
* 编写redis配置文件
* 编写docker-compose.yaml
* 创建所有服务容器
* 创建Redis Cluster集群

1. 安装docker-compose与docker，参照以下[安装教程](https://shawncheung.github.io/posts/%E5%AE%89%E8%A3%85docker/)：


2. 编写redis配置文件
    *  创建目录及文件

10.186.38.79
10.186.38.78

redis-cli -a TYPY4RCMnziJ5kjc --cluster create 10.186.38.79:6371 10.186.38.79:6372 10.186.38.79:6373 10.186.38.78:6374 10.186.38.78:6375 10.186.38.78:6376 --cluster-replicas 1

![](https://raw.githubusercontent.com/ShawnCheung/MyPic/img/img/202504181620946.png)
![](https://raw.githubusercontent.com/ShawnCheung/MyPic/img/img/202504181617476.png)
redis-cli -a TYPY4RCMnziJ5kjc --cluster check 10.186.38.78:6375
redis-cli -c -a TYPY4RCMnziJ5kjc -h 10.186.38.78 -p 6376

10.186.38.79:6371