# Kubernetes DevOps HOL-2604-K8S-Install Hands-On Lab Installation Guide

> By Leo Cao, Apr. 19, 2026

# 1. Install Ubuntu and Set up Environment

## 1.1 Install Ubuntu 25.10 servers

1. Intall ubuntu virtual machine with `OpenSSH` on VMware Fusion or WorkStation with the VM configuration below:


| ID | Server Name    | Ext. IP(Bridge)|  Int. IP (NAT)  | Role          |                   Config                     |
|----|----------------|:--------------:|-----------------|---------------|----------------------------------------------|
|  0 |  k8s-master10  | 192.168.2.10  | 192.168.158.10 |control plane 1  | 4 vCPUs, 8 GB RAM, 64 GB Disk, 2 NICs, disable swap|
|  1 |  k8s-master11  | 192.168.2.11  | 192.168.158.11 |control plane 2  | 4 vCPUs, 8 GB RAM, 32 GB Disk, 2 NICs, disable swap|
|  2 |  k8s-master12  | 192.168.2.12  | 192.168.158.12 |control plane 3  | 4 vCPUs, 8 GB RAM, 32 GB Disk, 2 NICs, disable swap|
|  3 |  k8s-master21  | 192.168.2.21  | 192.168.158.21 |    worker 1     | 2 vCPUs, 4 GB RAM, 32 GB Disk, 2 NICs, disable swap|
|  4 |  k8s-master22  | 192.168.2.22  | 192.168.158.22 |    worker 2     | 2 vCPUs, 4 GB RAM, 32 GB Disk, 2 NICs, disable swap|
|  5 |  lb.uni        | 192.168.2.200 | 192.168.158.200|     lb          |                                                    |


## 1.2 Ensure OS is using cgroup v2 
```Shell
stat -fc %T /sys/fs/cgroup/
```
1. Ensure the Cgroup versino is V2, configure if it is not V2 (optional).
```Shell
sudo vim /etc/default/grub
```
2. Update below line `GRUB_CMDLINE_LINUX="systemd.unified_cgroup_hierarchy=1"` in file `/etc/default/grub`

```Shell
GRUB_CMDLINE_LINUX="systemd.unified_cgroup_hierarchy=1"
```

3. update GRUB and Reboot
```Shell
sudo update-grub
sudo reboot
```

4. Validation
```Shell
mount | grep cgroup
```

## 1.3 Disable firewall

```Shell
sudo systemctl disable --now ufw
```

## 1.3 Append below code into all your users' ~/.bashrc (optional)

```Shell
vim ~/.bashrc
```
```Shell
export PS1="\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]$ "
alias k=kubectl
source /etc/bash_completion
source <(kubectl completion bash)
complete -o default -F __start_kubectl k

# PATH=$PATH:/usr/local/go/bin
# PATH=$PATH:/snap/bin
# [[ "$PWD" = /root ]] && cd ~
# [[ "$PWD" = /root/Desktop ]] && cd ~su
```

## 1.4 Update apt source (optional)

Replace apt source list with tsinghua.edu.cn below in `sudo vim /etc/apt/sources.list.d/ubuntu.sources`
```Shell
Types: deb
URIs: https://mirrors.tuna.tsinghua.edu.cn/ubuntu
Suites: noble noble-updates noble-backports
Components: main restricted universe multiverse
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg

# Types: deb
# URIs: http://fi.archive.ubuntu.com/ubuntu/
# Suites: questing questing-updates questing-backports
# Components: main restricted universe multiverse
# Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg

Types: deb
URIs: http://security.ubuntu.com/ubuntu/
Suites: questing-security
Components: main restricted universe multiverse
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
```

## 1.5 Configure Ubuntu hostname
Modify Ubuntu hostname by `vim` as unique names of Kuberntes cluster(`k8s-master`, `k8s-node1` and `k8s-node2`).
```Shell
cat /etc/hostname
cat /etc/hosts
# or
sudo hostnamectl set-hostname k8s-master10 # Run on master node
sudo hostnamectl set-hostname k8s-master11 # Run on master node
sudo hostnamectl set-hostname k8s-master12 # Run on master node
sudo hostnamectl set-hostname k8s-node21 # Run on node1
sudo hostnamectl set-hostname k8s-node22 # Run on node2
```

Append hosts into `/etc/hosts`on master
```Shell
sudo vim /etc/hosts
```
```Shell
192.168.158.10 k8s-master10
192.168.158.11 k8s-master11
192.168.158.12 k8s-master12
192.168.158.21 k8s-node21
192.168.158.22 k8s-node22
192.168.158.200 lb.leohol.com
```

Read values from all system directories
```Shell
sudo sysctl --system
```

## 1.6 Modify IP and DNS
Modify and verify Kubernetes cluster and nodes IP and DNS.
```Shell
cd /etc/netplan
ls
# the files are usually 00-installer-config.yaml, modify or verify the IP address is correct.
sudo vim /etc/netplan/00-installer-config.yaml
sudo netplan apply
# or
sudo netplan try # It needs to precess ENTER in 120 seconds if the config is good.
ip a
```
a `00-installer-config.yaml` sample:
```yaml
# This is the network config written by 'subiquity'
network:
  ethernets:
    ens33:
      addresses:
      - 192.168.158.12/24
      match:
        macaddress: 00:0c:29:62:09:f3
      nameservers:
        addresses:
        - 8.8.8.8
        search:
        - uni
      routes:
      - to: default
        via: 192.168.158.2
      set-name: ens33

      set-name: ens33

    ens34:
      addresses:
      - 192.168.2.10/24
      dhcp6: true
      match:
        macaddress:: 00:0c:29:84:fc:1a
      nameservers:
        addresses:
        - 192.168.2.1
        search:
        - uni
      routes:
      - to: default
        via: 192.168.2.1
      set-name: ens34

  version: 2
```


## 1.7 Check Sycn time between Kubernetes cluster - (Optinal)
Check synchronizing time suing chrony.
```Shell
chronyc -N tracking
```

## 1.8 
> Reference: https://ubuntu.com/server/docs/how-to/networking/chrony-client/#chrony-client

## 1.7 Diable swap

To imporve Kuberntes total architecture's performance, disable swap.
```Shell
# Optional 1, disable swap preprtually
sudo sed -ri 's/.*swap.*/#&/' /etc/fstab

# Optional 2, disable swap teporaryly, it will be enable again after restart;
sudo swapoff -a

# Check swap status
sudo free -h 

# or 
swapon --show

# reboot to enable
reboot
```

## 1.8 Verify Environment !!!

1. Verify `hostname` and `/etc/hosts`
2. Verify and sync time
```Shell
ntpdate ntp.aliyun.com
# Or add ntpdate into crontab
crontab -e
# Add command below
0 0 * * * ntpdate ntp.aliyun.com
```
3. Configure bridge filter and forward
```Shell
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF

sudo modprobe overlay
sudo modprobe br_netfilter
```

4. Core route forward
```Shell
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables  = 1
net.ipv4.ip_forward                 = 1
EOF

sudo sysctl --system
```
5. install ipset ipvsadm for Kubernetes 1.35
```Shell
apt install ipset ipvsadm
```
Add related modules:

```Shell
cat << EOF | tee /etc/modules-load.d/ipvs.conf
ip_vs
ip_vs_rr
ip_vs_wrr
ip_vs_sh
nf_conntrack
EOF
```
6. swap off
```
free -h
```

Reboot needed, or verify if by command
```Shell
lsmod |grep ip_vrr
```

# 2. Install containerd

## 2.1 Download containerd v2.2.2 from https://containerd.io/downloads/ by wget
```Shell
wget https://github.com/containerd/containerd/releases/download/v2.2.2/containerd-2.2.2-linux-amd64.tar.gz
tar xvf ./containerd-2.2.2-linux-amd64.tar.gz
sudo mv bin/* /usr/bin/
which containerd
```

## 2.2 Configure containerd

Create a containerd.service below:
```Shell
sudo vim /etc/systemd/system/containerd.service
```
Reference: https://github.com/containerd/containerd/blob/main/containerd.service
```Shell
# Only systemd 226 and above supports this version.
# Copyright The containerd Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

[Unit]
Description=containerd container runtime
Documentation=https://containerd.io
After=network.target dbus.service

[Service]
ExecStartPre=-/sbin/modprobe overlay
ExecStart=/usr/bin/containerd

Type=notify
Delegate=yes
KillMode=process
Restart=always
RestartSec=5

# Having non-zero Limit*s causes performance problems due to accounting overhead
# in the kernel. We recommend using cgroups to do container-local accounting.
LimitNPROC=infinity
LimitCORE=infinity

# Comment TasksMax if your systemd version does not supports it.
# Only systemd 226 and above support this version.
TasksMax=infinity
OOMScoreAdjust=-999

[Install]
WantedBy=multi-user.target
```

### 3. Install containerd

a) Genereate a default config.toml.
```Shell
sudo mkdir -p /etc/containerd
sudo su
containerd config default > /etc/containerd/config.toml
```

b) Important! Update images resource in `/etc/containerd/config.toml` from registry.k8s.io as local resource.

1. Update sandbox image
```Shell
sudo vim /etc/containerd/config.toml
```

```Shell
#sandbox ='registry.aliyuncs.com/google_containers/pause:3.10.1'
sandbox ='registry.cn-hangzhou.aliyuncs.com/google_containers/pause:3.10.1'
```

c) Install runc

```Shell
wget https://github.com/opencontainers/runc/releases/download/v1.4.0/runc.amd64
chmod +x runc.adm64
sudo mv runc.amd64 /usr/sbin/runc
runc --version
```

d) Enable containerd auto-start

```Shell
sudo systemctl enable --now containerd
```

## 2.3  Verify containerd by command below:
```Shell
sudo ls /var/run/containerd

```

## 2.4 Set nerdctl on master10 ONLY!

```Shell
wget https://github.com/containerd/nerdctl/releases/download/v2.2.1/nerdctl-2.2.1-linux-amd64.tar.gz
sudo tar xf nerdctl-2.2.1-linux-amd64.tar.gz -C /usr/bin/
which nerdctl
```

# 3. Install Kubernetes

## 3.1 Prepare Kubernetes management tools
### 3.1.1 Get gpg key of kubernetes
```Shell
# sudo curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.35/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg

sudo curl -fsSL https://mirrors.tuna.tsinghua.edu.cn/kubernetes/core:/stable:/v1.35/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
```


### 3.1.2 Update apt source

```Shell
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://mirrors.tuna.tsinghua.edu.cn/kubernetes/core:/stable:/v1.35/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
apt update
```

### 3.1.3 Install kubeadm, kubelet and kubectl

```Shell
apt-cache policy kubeadm kubelet kubectl

apt -y install kubeadm kubelet kubectl=1.35.4-1.1

# lock the current version for stablize current env
apt-mark hold kubeadmin kubelet kubectl
```

## 3.2 Preare Kubeneretes images

### 3.2.1 Configure kubelet drivers for containerd
```Shell
sudo vim /etc/default/kubelet
```
Update parameters in `/etc/default/kubelet`.
> It may lead to automatically restart if the papameter is misconfigured.
```Shell
KUBELET_EXTRA_ARGS="--cgroup-driver=systemd"
```

```Shell
sudo systemctl enable kubelet
sudo systemctl status kubelet
```
### 3.2.2 Prepare container images on all master node only!

```Shell
kubeadm config images list
# kubeadm config images pull
kubeadm config images pull --image-repository registry.cn-hangzhou.aliyuncs.com/google_containers
```

## 3.3 Prepare CNA loadbalancer kube-vip on only one master (k8s-master10) ONLY!

### 3.3.1 Set up Environment parameter

```Shell
sudo su
export VIP=192.168.158.200
export INTERFACE=ens33
export KVVERSION=v1.1.2
```
```Shell
ls /etc/kubernetes/manifests/
```
### 3.3.2 nerdctl run a container

Run kube-vip with original source (optional).
```Shell
# nerdctl -n k8s.io run -it --rm --net=host ghcr.io/kube-vip/kube-vip:$KVVERSION manifest pod \
--interface $INTERFACE \
--address $VIP \
--controlplane \
--services \
--arp \
--enableLoadBalancer \
--leaderElection | tee /etc/kuberntes/manifests/kube-vip.yaml
```
Run kube-vip with nju.edu.cn source.
```Shell
nerdctl -n k8s.io run -it --rm --net=host swr.cn-north-4.myhuaweicloud.com/ddn-k8s/ghcr.io/kube-vip/kube-vip:$KVVERSION manifest pod \
--interface $INTERFACE \
--address $VIP \
--controlplane \
--services \
--arp \
--enableLoadBalancer \
--leaderElection | tee /etc/kuberntes/manifests/kube-vip.yaml
```

> recoures: https://github.com/SUSTech-CRA/chinese-opensource-mirror-site
> https://docker.aityp.com/i/search?search=kube-vip


Check and copy kube-vip.yaml to other k8s-master nodes.

```Shell
cp kube-vip.yaml /etc/kubernetes/manifests/kube-vip.yaml
ls /etc/kubernetes/manifests/kube-vip.yaml
scp /etc/kubernetes/manifests/kube-vip.yaml k8s-master11:/etc/kubernetes/manifests/
scp /etc/kubernetes/manifests/kube-vip.yaml k8s-master12:/etc/kubernetes/manifests/
```
### 3.3.3 Initialize kube-vip by admin-super.conf 

Update the hostPath in /etc/kubernetes/manifests/kube-vip.yaml.

Notes. It needs to change back after initialization.
```Shell
volumes:
- hostPath:
#    path /etc/kubernetes/admin.conf
    path /etc/kubernetes/super-admin.conf
```

## 3.4 Initial Kubernetes cluster and validate availability on Master10 ONLY!

### 3.4.1 Genereate kubernetes config file.

```Shell
kubeadm config print init-defaults --component-configs KubeProxyConfiguration > kubeadm-config.yaml
```
### 3.4.1 
Update ```sudo vim kubeadm.config.yaml``` below:
```Shell
KubeletConfiguration.cgroupDriver is empty; setting it to "systemd"
# ...
localAPIEndpoint:
  advertiseAddress: 192.168.158.10
# ...
  name: k8s-master10

# ...
apiServer:
  certSANs:
  - lb.leohol.com
  - k8s-master10
  - k8s-master11
  - k8s-master12
  - 192.168.158.10
  - 192.168.158.11
  - 192.168.158.12
controlPlaneEndpoint: lb.leohol.com:6443
# ...
# It needs to deploy etcd to outside of Kuberntes cluster
# ectd:
#   local:
#     dataDir: /var/lib/etcd

# imageRepository: registry.k8s.io
imageRepository: registry.cn-hangzhou.aliyuncs.com/google_containers
#...
serviceSubnet: 10.96.0.0/12
podSubnet: 10.244.0.0./12
#...
# Set KubeProxy as ipvs
ipvs:
  strictARP: true
#...
mode: "ipvs"

---
kind: KubeletConfiguration
apiVersion: kubelet.config.k8s.io/v1beta1
cgroupDriver: systemd
```

### 3.4.2 Initial Kubernetes Cluster
```Shell
kubeadm init --config kubeadm-config.yaml --upload-certs --v=9
```

### 3.4.3 Start Kubernetes cluster
```Shell
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

Alternatively, if you are the root user, you can run:
```Shell
export KUBECONFIG=/etc/kubernetes/admin.conf
```



### 3.4.4 Add control plane nodes into cluster
Check logs of initialization:
You can now join any number of control-plane nodes running the following command on each as root:
```Shell
  kubeadm join lb.leohol.com:6443 --token abcdef.0123456789abcdef \
        --discovery-token-ca-cert-hash sha256:fcb872efe188974020d19f3ff74a7d1706b86ba058223bd6372fa3814fc3f8e7 \
        --control-plane --certificate-key 515539344d9087f0250f0f77ef8d2d6acfecd279984617efb46b99df0ebe6705
```
> NOTE! The above command is only for containerd, it needs to change (crsocket crd.socket) for Docker.

Please note that the certificate-key gives access to cluster sensitive data, keep it secret!
As a safeguard, uploaded-certs will be deleted in two hours; If necessary, you can use
`kubeadm init phase upload-certs --upload-certs` to reload certs afterward.


### 3.4.5 Add workers into cluster
Then you can join any number of worker nodes by running the following on each as root:

```Shell
kubeadm join lb.leohol.com:6443 --token abcdef.0123456789abcdef \
        --discovery-token-ca-cert-hash sha256:fcb872efe188974020d19f3ff74a7d1706b86ba058223bd6372fa3814fc3f8e7
```


### 3.4.6 Verify kube-vip

```Shell
ip a s
vim /root/.kube/config
```

## 4. Install Container Network Interface Calico

1. Install Calico by Operator on ONE Kubernetes Master:

```Shell
# kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.31.4/manifests/operator-crds.yaml
kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.31.4/manifests/tigera-operator.yaml
```
> Reference: https://docs.tigera.io/calico/latest/getting-started/kubernetes/self-managed-onprem/onpremises
> 
------

2. The namespace and pods of tigera-operator should be there.

```Shell
kubectl get ns
kubectl get pods -n tigera-operator
```

3. Config Calico Cluster
```Shell
wget https://raw.githubusercontent.com/projectcalico/calico/v3.31.4/manifests/custom-resources.yaml
```
Update cidr as `10.244.0.0/16`in Calico custom-resources.yaml
on k8s-master10.
```Shell
vim custom-resources.yaml
```
```yaml
apiVersion: operator.tigera.io/v1
kind: Installation
metadata:
  name: default
spec:
  # Configures Calico networking.
  calicoNetwork:
    ipPools:
      - name: default-ipv4-ippool
        blockSize: 26
        cidr: 10.244.0.0/16
        encapsulation: VXLANCrossSubnet
        natOutgoing: Enabled
        nodeSelector: all()
```

And create Calico by yaml. 
```Shell
kubectl create -f custom-resources.yaml
kubectl get ns # tigera-operator, calico-system
kubectl get pod -n calico-system -o wide
wath kubectl get pod -n calico-system
```
> Refernce: https://docker.aityp.com/r/docker.io/calico
>


## 5. Test API HA

### 5.1 Stop master10
```Shell
init 0
```

## 6. Images Sources Acceleration
Important! Update images resource in `/etc/containerd/config.toml` from registry.k8s.io as local resource.

1. Update sandbox image
```Shell
sudo vim /etc/containerd/config.toml
```

```Shell
#sandbox ='registry.aliyuncs.com/google_containers/pause:3.10.1'
sandbox ='registry.cn-hangzhou.aliyuncs.com/google_containers/pause:3.10.1'
```

2. Update other images, WITHOUT RESTARTING containerd EVERYTIME.

_a. Set `config_path` pointiong to new directory after `  [plugins."io.containerd.grpc.v1.cri"]` in file `/etc/containerd/certs.d` 
```Shell
    [plugins."io.containerd.grpc.v1.cri".registry]
      config_path = "/apps/containerd/conf/certs.d"
```
_b. Restart containerd only one time (CAREFUL).
```Shell
sudo systemctl restart containerd
sudo systemctl status containerd
sudo journalctl -u containered -f |grep -i registry
```
_c. Create file `/etc/containerd/certs.d/docker.io/hosts.toml` and add acceleartion address:

### Docker hub Images Acceleration
```Shell
# Create docker.io's configuration directory
sudo mkdir -p /etc/containerd/certs.d/docker.io


# Create hosts.toml configureation file
sudo tee /etc/containerd/certs.d/docker.io/hosts.toml << 'EOF'
server = "https://registry-1.docker.io"

[host."https://docker.m.daocloud.io"]
  capabilities = ["pull", "resolve"]
 
[host."https://reg-mirror.qiniu.com"]
  capabilities = ["pull", "resolve"]
 
[host."https://registry.docker-cn.com"]
  capabilities = ["pull", "resolve"]

[host."https://docker.mirrors.ustc.edu.cn"]
  capabilities = ["pull", "resolve"]

EOF
``` 

### registry.k8s.io images acceleration:
```Shell
mkdir -p /etc/containerd/certs.d/registry.k8s.io
tee /etc/containerd/certs.d/registry.k8s.io/hosts.toml << 'EOF'
server = "https://registry.k8s.io"
 
[host."https://k8s.m.daocloud.io"]
  capabilities = ["pull", "resolve", "push"]
EOF
```

### docker.elastic.co images acceleration:
```Shell
mkdir -p /etc/containerd/certs.d/docker.elastic.co
tee /etc/containerd/certs.d/docker.elastic.co/hosts.toml << 'EOF'
server = "https://docker.elastic.co"
 
[host."https://elastic.m.daocloud.io"]
  capabilities = ["pull", "resolve", "push"]
EOF
```


### gcr.io
```Shell
mkdir -p /etc/containerd/certs.d/gcr.io
tee /etc/containerd/certs.d/gcr.io/hosts.toml << 'EOF'
server = "https://gcr.io"
 
[host."https://gcr.m.daocloud.io"]
  capabilities = ["pull", "resolve", "push"]
EOF
```

### ghcr.io

```Shell
mkdir -p /etc/containerd/certs.d/ghcr.io
tee /etc/containerd/certs.d/ghcr.io/hosts.toml << 'EOF'
server = "https://ghcr.io"
 
[host."https://ghcr.m.daocloud.io"]
  capabilities = ["pull", "resolve", "push"]
EOF
```

### k8s.gcr.io
```Shell
mkdir -p /etc/containerd/certs.d/k8s.gcr.io
tee /etc/containerd/certs.d/k8s.gcr.io/hosts.toml << 'EOF'
server = "https://k8s.gcr.io"
 
[host."https://k8s-gcr.m.daocloud.io"]
  capabilities = ["pull", "resolve", "push"]
EOF
```

### mcr.m.daocloud.io
```Shell
mkdir -p /etc/containerd/certs.d/mcr.microsoft.com
tee /etc/containerd/certs.d/mcr.microsoft.com/hosts.toml << 'EOF'
server = "https://mcr.microsoft.com"
 
[host."https://mcr.m.daocloud.io"]
  capabilities = ["pull", "resolve", "push"]
EOF
```

### nvcr.io
```Shell
mkdir -p /etc/containerd/certs.d/nvcr.io
tee /etc/containerd/certs.d/nvcr.io/hosts.toml << 'EOF'
server = "https://nvcr.io"
 
[host."https://nvcr.m.daocloud.io"]
  capabilities = ["pull", "resolve", "push"]
EOF
```

### quay.io
```Shell
mkdir -p /etc/containerd/certs.d/quay.io
tee /etc/containerd/certs.d/quay.io/hosts.toml << 'EOF'
server = "https://quay.io"
 
[host."https://quay.m.daocloud.io"]
  capabilities = ["pull", "resolve", "push"]
EOF
```

### registry.jujucharms.com
```Shell
mkdir -p /etc/containerd/certs.d/registry.jujucharms.com
tee /etc/containerd/certs.d/registry.jujucharms.com/hosts.toml << 'EOF'
server = "https://registry.jujucharms.com"
 
[host."https://jujucharms.m.daocloud.io"]
  capabilities = ["pull", "resolve", "push"]
EOF
```

### rocks.canonical.com
```Shell
mkdir -p /etc/containerd/certs.d/rocks.canonical.com
tee /etc/containerd/certs.d/rocks.canonical.com/hosts.toml << 'EOF'
server = "https://rocks.canonical.com"
 
[host."https://rocks-canonical.m.daocloud.io"]
  capabilities = ["pull", "resolve", "push"]
EOF
```


_d Verify new images registry
```Shell
sudo nerdctl pull busybox:latest
sudo nerdctl pull busybox:latest 2>&1 | grep -i mirror

```
## 7. Delete and rejoin wokers 

### 7.1 Migrate pods on workkers

Run on Master
```Shell
kubectl drain k8s-node11 --ignore-daemonsets --delete-emptydir-data
kubectl delete node k8s-node11
```

Run on workder.
```Shell
sudo kubeadm reset -f
hostnamectl set-hostname k8s-node21
```

Rejoin cluster
Run command below on master.
```Shell
kubeadm token create --print-join-command
```
Run command genereted on workder.


## REFERENCE:
> 1. https://zahui.fan/posts/t4ve3m/
> 2. https://zhuanlan.zhihu.com/p/634372250
> 3. https://blog.huweihuang.com/kubernetes-notes/setup/installer/install-k8s-by-kubeadm/
> 4. https://www.cnblogs.com/gaoyuechen/p/19652343
