k8s 安装

```shell
#所有机器添加master域名映射，以下需要修改为自己的
echo "192.168.50.19  cluster-endpoint" >> /etc/hosts



#主节点初始化,只在主节点执行
kubeadm init \
--apiserver-advertise-address=192.168.50.19 \   #这个ip是上面的master节点ip
--control-plane-endpoint=cluster-endpoint \     #这个cluster-endpoint 和上面的对应就可以
--image-repository registry.cn-hangzhou.aliyuncs.com/lfy_k8s_images \
--kubernetes-version v1.20.9 \
--service-cidr=10.96.0.0/16 \   # 1  这里的3个ip要在不同网段
--pod-network-cidr=192.160.0.0/16   #2 这里的3个ip要在不同网段

#所有网络范围不重叠

```





```shell
curl https://docs.projectcalico.org/manifests/calico.yaml -O

kubectl apply -f calico.yaml    #这里面默认会有192.168.0.0/16(已经注释),这个要和上面pod-network-cidrip保持一致，如果不一致，就手动修改
```

![image-20211001214243933](C:\Users\wbo11\AppData\Roaming\Typora\typora-user-images\image-20211001214243933.png)





### 4、加入node节点

```bash
kubeadm join cluster-endpoint:6443 --token x5g4uy.wpjjdbgra92s25pp \
	--discovery-token-ca-cert-hash sha256:6255797916eaee52bf9dda9429db616fcd828436708345a308f4b917d3457a22
```

创建新令牌，在master执行

`kubeadm token create --print-join-command`

5.查询kubernetes-dashboard端口号

```
kubectl get svc -A |grep kubernetes-dashboard
```

![image-20211015210353768](C:\Users\wangbo\AppData\Roaming\Typora\typora-user-images\image-20211015210353768.png)

通过https://xxx:31214就可以访问  

> xxx表示集群中节点IP

5.进入容器  

```shell
 kubectl exec -it mynginx -- /bin/bash
```





```shell
kubectl delete pod mynginx#删除pod
kubectl replace --force -f  dash.yml#重新部署pod
```



`kubectl describe pod kube-proxy-k85m2 --namespace=kube-system` 查看pod状态
