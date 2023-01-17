package main

import (
	"context"
	"encoding/json"
	"flag"
	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/credentials"
	"github.com/aws/aws-sdk-go-v2/service/ec2"
	"io"
	"log"
	"net/http"
)

// 得到出口IP
func GetExportIP() string {
	response, err := http.Get("http://api.ipify.org/?format=json")
	defer response.Body.Close()
	if err != nil {
		log.Fatalf("获取出口IP失败: %v", err)
	}
	if response.StatusCode != 200 {
		log.Fatalf("获取出口IP失败: %d", response.StatusCode)
	}

	body, err := io.ReadAll(response.Body)
	if err != nil {
		log.Fatalf("解析IP结果失败: %v", err)
	}

	type IPIfyResult struct {
		IP string `json:"ip"`
	}
	ipifyResult := &IPIfyResult{}
	err = json.Unmarshal(body, ipifyResult)
	if err != nil {
		log.Fatalf("反序列化IP结果失败: %v", err)
	}
	return ipifyResult.IP
}

func MakeSecurityGroup(client *ec2.Client, clientIP, groupIP *string, port *int32) {
	_, err := client.AuthorizeSecurityGroupIngress(context.TODO(), &ec2.AuthorizeSecurityGroupIngressInput{
		CidrIp:     aws.String(*clientIP + "/32"),
		DryRun:     aws.Bool(false),
		FromPort:   port,
		ToPort:     port,
		GroupId:    groupIP,
		IpProtocol: aws.String("tcp"),
	})
	if err != nil {
		log.Fatalf("添加安全组规则失败: %v", err)
	}
}

func main() {
	accessKey := flag.String("accessKey", "", "AWS访问密钥")
	secretKey := flag.String("secretKey", "", "AWS秘密访问密钥")
	region := flag.String("region", "", "安全组所在的地域")
	securityGroupID := flag.String("securityGroupID", "", "目标安全组")
	port := flag.Int("port", 0, "访问EC2的哪个端口")
	flag.Parse()
	if *accessKey == "" || *secretKey == "" || *region == "" || *securityGroupID == "" || *port == 0 {
		log.Fatal("参数缺失: -accessKey AWS访问密钥 -secretKey AWS秘密访问密钥 -region 安全组所在的地域 -securityGroupID 目标安全组 -port 访问EC2的哪个端口")
		return
	}

	exportIP := GetExportIP()

	client := ec2.New(ec2.Options{
		Region:      *region,
		Credentials: aws.NewCredentialsCache(credentials.NewStaticCredentialsProvider(*accessKey, *secretKey, "")),
	})

	portIn32 := int32(*port)

	MakeSecurityGroup(client, &exportIP, securityGroupID, &portIn32)
}
