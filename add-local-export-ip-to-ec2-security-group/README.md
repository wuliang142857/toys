# 添加本机的出口IP到AWS EC2的安全组中

## 背景

有时候，我们期望只有本机才能部署在EC2上的服务，而本机的出口IP却又是动态的。因此，通过此工具，再配合crontab等工具来自动更新.

## 使用

```
Usage of add-local-export-ip-to-ec2-security-group:
  -accessKey string
    	AWS访问密钥
  -port int
    	访问EC2的哪个端口
  -region string
    	安全组所在的地域
  -secretKey string
    	AWS秘密访问密钥
  -securityGroupID string
    	目标安全组
```

