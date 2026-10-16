# VPC: addressing, routing, and network boundaries

A VPC is a logically isolated network in an AWS region. It provides the address space and networking structure for resources such as EC2 instances. Subnets divide that space, while routes and traffic controls determine which connections work. [How VPC works](https://docs.aws.amazon.com/vpc/latest/userguide/how-it-works.html)

## CIDR and subnets

CIDR describes an address range. For example, `10.20.0.0/16` can contain smaller, non-overlapping subnets such as `10.20.1.0/24` and `10.20.2.0/24`. A subnet belongs to one Availability Zone; a VPC can span several AZs. AWS reserves some subnet addresses, so the full mathematical address count is not available to instances.

Avoid overlap when networks must connect through peering, VPN, or another routing arrangement. A valid subnet CIDR must also fit inside its VPC's address space.

## Route tables and Internet Gateway

A route table maps a destination range to a target. A subnet uses one route table, either through an explicit association or the VPC's main table. The local route supports communication within the VPC. More-specific routes take precedence over less-specific matches. [Subnet route tables](https://docs.aws.amazon.com/vpc/latest/userguide/subnet-route-tables.html)

An Internet Gateway connects the VPC to the internet. A subnet with a default route such as `0.0.0.0/0 -> igw` is public. For IPv4 internet communication, an instance also needs an appropriate public address and traffic permissions. The route alone does not expose every instance. [Internet Gateway](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Internet_Gateway.html)

```text
Internet
   |
Internet Gateway
   |
Public route table: 0.0.0.0/0 -> IGW
   |
Public subnet: web server

Private subnet: application/database resources
   |
Optional outbound route -> NAT Gateway
```

## NAT Gateway and private subnets

A private subnet has no direct default route to an Internet Gateway. A public NAT Gateway, placed in a public subnet with the required routing and Elastic IP, allows private IPv4 workloads to initiate outbound internet connections. It does not provide unsolicited inbound access to those workloads. Its availability design and ongoing charges matter when planning multiple AZs. [NAT Gateway](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-gateway.html)

A small one-subnet web exercise does not need a NAT Gateway. Private workloads accessing supported AWS services may use VPC endpoints instead, depending on the service and endpoint type.

## Security Groups and network ACLs

| Property | Security Group | Network ACL |
|---|---|---|
| Attached to | Resource network interfaces | Subnet |
| Rules | Allow rules | Allow and deny rules |
| Connection tracking | Stateful | Stateless |
| Rule evaluation | Combined applicable allows | Numbered rules, first match |
| Return traffic | Allowed for tracked permitted connections | Needs matching traffic rules, including return ports |

Security Groups are the main application-level network boundary in this exercise. An ACL can provide an additional subnet boundary, but overly restrictive return-port rules can break otherwise valid connections. [Security Groups](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html), [network ACLs](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html)

## Troubleshooting a connection

1. Confirm source and destination addresses and the actual listening port.
2. Inspect subnet associations and routes in both directions.
3. Check the Internet Gateway, public address, or NAT path as applicable.
4. Inspect Security Groups and ACLs, including response traffic.
5. Check the application process and use flow logs when packet-level visibility is needed.

The Session 19 project uses one public subnet, one explicitly associated route table, an Internet Gateway, and an HTTP-only inbound rule. IAM controls S3 API access separately from these network rules.
