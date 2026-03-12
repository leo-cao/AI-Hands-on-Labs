# Installing Docker 

> By Leo Cao | Version 1.0 | March 12, 2026

This article describes how to install Docker.

Docker Architecture:
![Docker Architecure](https://docs.docker.com/get-started/images/docker-architecture.webp)


## 1. Install Docker on Ubuntu 25H2
```
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o  /usr/share/keyrings/docker-archive-keyring.gpg
```
```
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

```
sudo apt-get update
```

```
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
Verification docker:
```
sudo docker run hello-world 
```

## 2. Create a Persist Volume

2.1 Create a html folder on Docker host.
```
mkdir -p /data/nginx
```

2.2 Run a nginx and point to the folder
```
docker run -d --name nginx_test -p 8080:80 -v /data/nginx:/usr/share/nginx/html nginx
```

## 3. Install nano on nginx container

PS: Install nano on nginx container
```
apt-get update && apt-get install nano -y
```

## 4. Build Docker Image

4.1 Create a file and name it as `dockerfile`.
Sample:
```
# Use an official Debian base image
FROM debian:bookworm-slim

# Update package lists and install nginx
RUN apt-get update && apt-get install -y nginx --no-install-recommends && rm -rf /var/lib/apt/lists/*
mkdir -p /usr/share/nginx/html
# Copy local website files into the container's NGINX web root
# COPY html/ /usr/share/nginx/html/

# Expose port 80 (standard HTTP port)
EXPOSE 80

# Command to run NGINX in the foreground
CMD ["nginx", "-g", "daemon off;"]
```

4.2 Build and run the iamge

Build nginx image.
```
docker build -t nginx-lc:v1 .

```

Run the new docker image.
```
docker run  -d --name nginx-lc-test -p 8082:80 nginx-lc:v1
```

Run the docker image with persist volume

```
docker run  -d --name nginx-lc-test -p 8082:80 -v /data/nginx:/usr/share/nginx/html nginx-lc:v1
```

## 5. Install docker-compose

5.1 Install docker-compose
```
curl -L "https://github.com/docker/compose/releases/download/v2.18.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
docker-compose version
```

5.2 Create a service with a docker-compose.yaml file:
```
services:
  nginx:
    image: nginx:latest
    container_name: nginx_test
    ports:
      - 8080:80
    volumes:
      - /opt/nginx:/opt/nginx/html
```

5.3 Start container

```
docker-compose up -d
```

Reference:
```
docker-compose down
docker-compose restart
docker-compose up --force-recreate -d
```

### 6. Run multi-applications using docker-compose

6.1 Edit a docker-compose.yml as follows:

```
services:
  nginx:
    image: nginx:latest
    container_name: nginx_host1
    ports:
      - 8081:80
    volumes:
      - /data/nginx:/usr/share/nginx/html
    networks:
      - host1-network


  redis:
    image: redis:latest
    container_name: redis_host1
    ports:
      - 63790:6379
    networks:
      - host1-network


  networks:
    host1-network:
      driver: bridge
      ipam:
        driver: default
        config:
          - subnet: 173.18.0.0/24
            gateway: 173.18.0.1

```

6.2 execute docker-compose up in the same folder of yaml file.
```
docker-compose up -d
```

6.3 Access nginx and redis

List container nginx IP address:
```
docker exec -it nginx bash
hostname -I
exit
```
curl the nginx pages on host:
```
curl http://<nginx IP address>:8081
```

List container redis_host1 IP address:
```
docker exec -it nginx_host1 bash
hostname -I
exit
```
Connect redis on host:
```
nc -zv <redis IP address> 6379
```


