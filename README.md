# Development Environment

For this project, we are providing a docker image pre-configured with the software you will need. You can choose other environment, but we strongly recommend that you do all development and testing in this image. **Your code must compile and run correctly on this image as we will be using it for grading.**

## Docker Installation

**Windows**

Chinese tutorial: https://www.runoob.com/docker/windows-docker-install.html

You ***had better*** select WSL or Hyper-V option if you use installer. For more info, read this manual: https://docs.docker.com/desktop/windows/install/ .

**MacOS**

English manual: https://docs.docker.com/desktop/mac/install/

**Linux**

Install using the convenience script

```shell
curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun
```



# Video Distribution System

## IMPORTANT!!!!!!
If you are using windows, you should run the command `git config --global core.autocrlf input` before clone this repository!!!

### 1. Build Image

```sh
git clone https://github.com/Nancyzxy/CS305-proj.git
cd /docker_setup
sudo docker build -t project:latest -f ./DockerFile .
```

It will take a few minutes to clone from Github and build the image.

You can transfer this repo to Gitee. And if it takes too much time to download packages during building process, using mirrors like `aliyun` may be helpful.

### 2. Run Image

You can use `docker images` to check images you have built.

If you have a image, you can run it with `docker run -it -p 7778:7778 -p 7779:7779 project:latest /bin/bash`. This command will launch a container inside your machine with port mapping configured for ports 7778 and 7779. With port mapping, you can access ports 7778 and 7779 of your container from your machine. These port numers are just an example. You may need to map other ports instead.

You can find more info about port mapping of Docker in this guide [Docker Network](https://docs.docker.com/config/containers/container-networking/).

## Docker Usage

- `docker ps`

  Check all the running containers.

- `docker exec -it <CONTAINER_ID> /bin/bash`

  You can use this command to run multiple terminals inside a container. Every time you run this command, you will open a new terminal with the same container ID.

- `docker start <CONTAINER_ID>`

  Enter a container. You can use Ctrl-D to exit a container, but it will not be removed. You can enter it again by its ID.

- `docker rm <CONTAINER_ID>`

  Remove a container and all of its files will be deleted.

- `docer cp <CONTAINER_ID>:PATH DEST_PATH`

  Copy files from a container.

- `docker cp SRC_PATH <CONTAINER_ID>:DEST_PATH`

  Copy files into a container from your machine. 

  Another way to share a file or directory with a container is by using `bind mounts` or `volume`. You can specify such a mapping when you start your container. For example, `docker run -it -p 7778:7778 -p 7779:7779 -v /tmp:/home project:latest /bin/bash` will replace the contents of the container’s `/home/` directory with the `/tmp/` directory on your machine. You can find more info about this [here](https://docs.docker.com/storage/bind-mounts/).

You can find more info about Docker [here](https://docs.docker.com/get-started/) and [here](https://docs.docker.com/engine/reference/commandline/container/).

## Starter Proxy Code

The `starter_proxy` directory contains some code to help you get started with this project. See the project handout for a detailed description of the proxy's command line arguments.

### File Description

- `grapher.py`: Generate plots for CP1 writeup. 

  Usage: `python grapher.py <netsim log> <proxy1 log> <proxy2 log>`

### Running Example



## Problems

Here are some problems you may occur. It is not possible for us to consider all problems and you should try to find some solutions on your own.

If you think your questions and solutions may be applicable for other students, or there are errors or unclear descriptions in our code or documentation, we are welcome your Github issues.
### the file is too short problem

see the good first issue!
### Flash Player

You can use your browser in your machine to access ports inside the container. Note that most browsers no longer support flash and you may need to install a [tool](https://soft.flash.cn/flashcenter/index.html) to play flash on your browser. Find more info from https://www.flash.cn/support/help.html.

If you use MacOS, you may need to install a browser with a lower version in order to use Adobe Flash Player. For more info: https://www.flash.cn/download
### Browser

Microsoft Edge and 360 browser is proven to work well.

### Git Clone

You may encounter some line endings problems when clone code. This command may be helpful: `git config --global core.autocrlf input`.

### Docker Installation

Windows needs a Linux kernel to run docker. If you encounter a problem like 'docker daemon is not running', you can try to install WSL2.

### Docker Network

If you can't access ports of the container, you may need to do some configurations.

> MacOS

IP forward: `sysctl -w net.inet.ip.forwarding=1`

> Linux

IP forward: 

```sh
echo 1 > /proc/sys/net/ipv4/ip_forward
iptables -P FORWARD ACCEPT

iptables -L -n # check
```
