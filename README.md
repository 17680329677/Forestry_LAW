#### Python 调用 nsq 消费者启动方式

> 启动lookup
	
```
nsqlookupd
```

> 启动一个nsqd , 并指定lookup的地址

```
nsqd --lookupd-tcp-address=127.0.0.1:4160
```
