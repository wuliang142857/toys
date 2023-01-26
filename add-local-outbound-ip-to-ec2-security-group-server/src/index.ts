/**
 * 入口
 */
import {
    AuthorizeSecurityGroupIngressCommand,
    DescribeSecurityGroupsCommand,
    EC2Client
} from "@aws-sdk/client-ec2";
import {
    DescribeSecurityGroupsCommandOutput
} from "@aws-sdk/client-ec2/dist-types/commands/DescribeSecurityGroupsCommand";
import Uri from "jsuri";

function getClientIP(request: Request): string | undefined | null {
    return request.headers.get('CF-Connecting-IP');
}


// @ts-ignore
const awsAccessKey:string = AWS_ACCESS_KEY;
// @ts-ignore
const awsRegion:string = AWS_REGION;
// @ts-ignore
const awsSecretKey:string = AWS_SECRET_KEY;
// @ts-ignore
const awsSecurityGroupId:string = AWS_SECURITY_GROUP_ID;
// @ts-ignore
const remotePort:number = parseInt(REMOTE_PORT);

async function handleRequest(request: Request): Promise<Response> {
    const uri: Uri = new Uri(request.url);
    if (uri.path() !== "/add-client-ip") {
        return new Response(`unknown path: ${uri.path()}`, {
            status: 500,
            headers: {
                'content-type': 'application/json;charset=UTF-8',
              }
        });
    }

    const clientIP:string | undefined | null = getClientIP(request);
    if (!clientIP) {
        return new Response("get client ip failed", {
            status: 500,
            headers: {
                'content-type': 'application/json;charset=UTF-8',
              }
        })
    }
    const fullClientIP:string = `${clientIP}/32`;

    const client = new EC2Client ({region: awsRegion, credentials: {
        accessKeyId: awsAccessKey,
        secretAccessKey: awsSecretKey
        }});
    const describeSecurityGroupsResponse:DescribeSecurityGroupsCommandOutput = await client.send(new DescribeSecurityGroupsCommand({
        DryRun: false,
        GroupIds: [awsSecurityGroupId]
    }));
    for (const securityGroup of describeSecurityGroupsResponse.SecurityGroups) {
        for (const rule of securityGroup.IpPermissions) {
            if (rule.FromPort === remotePort && rule.ToPort === remotePort) {
                for (const ip of rule.IpRanges) {
                    if (ip.CidrIp === fullClientIP) {
                        // 记录已经存在
                        return new Response(`${fullClientIP} 已存在`, {
                            status: 200,
                            headers: {
                                'content-type': 'application/json;charset=UTF-8',
                              }
                        })
                    }
                }
            }
        }
    }

    try {
        await client.send(new AuthorizeSecurityGroupIngressCommand({
            CidrIp: fullClientIP,
            FromPort: remotePort,
            ToPort: remotePort,
            GroupId: awsSecurityGroupId,
            IpProtocol: "tcp"
        }));
    } catch (e) {
        return new Response(`添加安全组规则失败: ${e}`, {
            status: 500,
            headers: {
                'content-type': 'application/json;charset=UTF-8',
              }
        });
    }

    client.destroy()
    return new Response(`${fullClientIP} 已添加到安全组规则`, {
        status: 200,
        headers: {
            'content-type': 'application/json;charset=UTF-8',
          }
    });
}

addEventListener("fetch", (event: FetchEvent) => {
    event.respondWith(handleRequest(event.request));
});
