---
layout: post
title: openvpn.sh
date: 2026-05-14 15:57 +0800
categories: [网络, openvpn]
tags: [openvpn]
---
```bash
wget https://lf3-static.bytednsdoc.com/obj/eden-cn/jzeh7vhobenuhog/install_openvpn.sh 
chmod +x install_openvpn.sh
./install_openvpn.sh
cat /root/client-configs/client1.ovpn
```

install_openvpn.sh

```bash
#!/bin/bash

set -e

VPN_PORT=1194
VPN_PROTO=udp
VPN_SUBNET=10.8.0.0
VPN_MASK=255.255.255.0
CLIENT_NAME=client1

echo "=== Install OpenVPN ==="

apt update
apt install -y openvpn easy-rsa iptables-persistent

echo "=== Setup EasyRSA ==="

make-cadir /etc/openvpn/easy-rsa

cd /etc/openvpn/easy-rsa

./easyrsa init-pki

echo | ./easyrsa build-ca nopass

echo | ./easyrsa gen-req server nopass
echo yes | ./easyrsa sign-req server server

echo | ./easyrsa gen-req ${CLIENT_NAME} nopass
echo yes | ./easyrsa sign-req client ${CLIENT_NAME}

./easyrsa gen-dh

openvpn --genkey secret ta.key

echo "=== Copy Certificates ==="

cp pki/ca.crt /etc/openvpn/
cp pki/private/server.key /etc/openvpn/
cp pki/issued/server.crt /etc/openvpn/
cp pki/dh.pem /etc/openvpn/
cp ta.key /etc/openvpn/

echo "=== Detect Network Interface ==="

NIC=$(ip route | grep default | awk '{print $5}' | head -n1)

echo "NIC=${NIC}"

echo "=== Generate Server Config ==="

cat > /etc/openvpn/server.conf <<EOF
port ${VPN_PORT}
proto ${VPN_PROTO}
dev tun

ca ca.crt
cert server.crt
key server.key
dh dh.pem

tls-auth ta.key 0

server ${VPN_SUBNET} ${VPN_MASK}

push "redirect-gateway def1 bypass-dhcp"
push "dhcp-option DNS 8.8.8.8"
push "dhcp-option DNS 1.1.1.1"

keepalive 10 120

cipher AES-256-GCM
auth SHA256

persist-key
persist-tun

user nobody
group nogroup

verb 3
EOF

echo "=== Enable IP Forward ==="

sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/g' /etc/sysctl.conf

echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf

sysctl -p

echo "=== Configure NAT ==="

iptables -t nat -A POSTROUTING -s ${VPN_SUBNET}/24 -o ${NIC} -j MASQUERADE

netfilter-persistent save

echo "=== Start OpenVPN ==="

systemctl enable openvpn@server
systemctl restart openvpn@server

SERVER_IP=$(curl -s ifconfig.me)

echo "=== Generate Client Config ==="

mkdir -p /root/client-configs

cat > /root/client-configs/${CLIENT_NAME}.ovpn <<EOF
client
dev tun
proto ${VPN_PROTO}

remote ${SERVER_IP} ${VPN_PORT}

resolv-retry infinite
nobind

persist-key
persist-tun

remote-cert-tls server

cipher AES-256-GCM
auth SHA256

key-direction 1

verb 3

<ca>
$(cat /etc/openvpn/easy-rsa/pki/ca.crt)
</ca>

<cert>
$(cat /etc/openvpn/easy-rsa/pki/issued/${CLIENT_NAME}.crt)
</cert>

<key>
$(cat /etc/openvpn/easy-rsa/pki/private/${CLIENT_NAME}.key)
</key>

<tls-auth>
$(cat /etc/openvpn/easy-rsa/ta.key)
</tls-auth>

EOF

echo ""
echo "===================================="
echo "OpenVPN Installed Successfully"
echo "Client Config:"
echo "/root/client-configs/${CLIENT_NAME}.ovpn"
echo "===================================="
```

运行上述脚本，即可安装OpenVPN服务器。
在客户端安装OpenVPN客户端，即可连接到OpenVPN服务器。

cat /root/client-configs/client1.ovpn