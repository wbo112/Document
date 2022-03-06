### kafka学习

------

| IP    | hostname       |
| ----- | -------------- |
| node1 | 192.168.50.227 |
| node2 | 192.168.50.12  |
| node3 | 192.168.50.173 |

1、在node1服务器上解压kafka

```
tar -zxvf kafka_2.12-2.7.0.tgz
```

2、修改配置文件

vim  kafka_2.12-2.7.0/config/zookeeper.properties

```shell
#设置以下属性

dataDir=/root/data/zookeeper/zkdata

server.1=node1:2888:3888
server.2=node2:2888:3888
server.3=node3:2888:3888
```



vim kafka_2.12-2.7.0/config/server.properties

```shell
#设置以下属性
broker.id=0

#本机IP:端口
listeners=PLAINTEXT://192.168.50.227:9092
advertised.listeners=PLAINTEXT://192.168.50.227:9092

#这个配置是数据存储目录，可以根据实际需要调整
log.dirs=/root/data/kafka/kafka-logs
#这个是设置分片数，和性能相关。如果只是单纯的只要跑起来，可以设置成1
num.partitions=10  

#设置zookeeper集群信息
zookeeper.connect=node1:2181,node2:2181,node3:2181

```



3、分发kafka

拷贝kafka到其他服务

```shell
 scp -r ./kafka_2.12-2.7.0/   192.168.50.12:/root/
 scp -r ./kafka_2.12-2.7.0/   192.168.50.173:/root/
```

登录192.168.50.12服务器修改kafka_2.12-2.7.0/config/server.properties文件

```shell
broker.id=1

#本机IP:端口
listeners=PLAINTEXT://192.168.50.12:9092
advertised.listeners=PLAINTEXT://192.168.50.12:9092

```

登录192.168.50.173服务器修改kafka_2.12-2.7.0/config/server.properties文件

```shell
broker.id=2
#本机IP:端口
listeners=PLAINTEXT://192.168.50.173:9092
advertised.listeners=PLAINTEXT://192.168.50.173:9092
```



4、启动kafka

```shell
 #在每台服务器上执行
 ./kafka-server-start.sh -daemon ../config/server.properties
```



```shell
 ./kafka-topics.sh --list --zookeeper node1:2181,node2:2181,node3:2181  #查看topic
 
 
 ./kafka-console-consumer.sh --bootstrap-server   192.168.50.227:9092,192.168.50.12:9092,192.168.50.173:9092 --topic test --from-beginning   #查看数据
```

