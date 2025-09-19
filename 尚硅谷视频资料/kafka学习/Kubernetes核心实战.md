



### 删除部署

`kubectl get deploy`获取部署的名字

` kubectl delete deploy mytomcat`   删除部署



` kubectl set image deploy/my-dep nginx=nginx:1.16.1 --record=true` 更新部署

`kubectl rollout undo deployment/my-dep --to-revision=1` 回退到指定版本



### service

将一个服务对外暴露

如我本次需要将部署的两个my-dep服务统一暴露

![image-20211031121753425](typora-user-images\image-20211031121753425-16465317567481.png)

`kubectl expose deploy my-dep --port=8000 --target-port=80`使用这个命令通过8000端口进行暴露

使用`kubectl get service`查看对应集群内IP

![image-20211031121855113](typora-user-images\image-20211031121855113-16465317736412.png)

1. 就可以通过`curl  10.96.87.39:8000`这种方式，直接访问集群ip:port的方式进行访问

2. **在容器内**，也可以通过这种方式访问` curl my-dep.default.svc:8000`(服务名.所在命名空间.svc:port)

`kubectl expose deployment my-dep --port=8000 --target-port=80 --type=NodePort`集群外也可以访问

`kubectl expose deployment my-dep --port=8000 --target-port=80 --type=ClusterIP`集群内部访问



![image-20211031123247959](typora-user-images\image-20211031123247959-16465317832893.png)

如上图，会在集群每个节点打开30710端口，暴露服务。可以使用集群IP:30710访问服务

### ingress

![image-20211031125452989](typora-user-images\image-20211031125452989-16465317869914.png)

ingress对外暴露的端口。可以看到30242代理的是80，31679代理的是443。





### 磁盘挂载

```yml
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: nginx-pv-demo
  name: nginx-pv-demo
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx-pv-demo
  template:
    metadata:
      labels:
        app: nginx-pv-demo
    spec:
      containers:
      - image: nginx
        name: nginx
        volumeMounts:
        - name: html #名字要对应
          mountPath: /usr/share/nginx/html   #容器内路径
      volumes:
        - name: html #名字要对应
          nfs:
            server: 192.168.50.19
            path: /nfs/data/nginx-pv  #本地路径
```



