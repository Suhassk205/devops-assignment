# EC2: compute, networking, and instance storage

Amazon EC2 runs virtual machines called instances. AWS manages the underlying physical infrastructure; the application owner still manages the guest operating system, installed packages, application configuration, and workload access. [EC2 overview](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/concepts.html)

## AMIs and instance types

An Amazon Machine Image supplies the operating system and initial disk image. It must match the instance architecture, such as x86_64 or arm64, and its AMI ID is regional. Reusing an ID from another region can cause an instance launch to fail. A maintained base image is a starting point; packages and application dependencies still need updates. [AMI characteristics](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ComponentsAMIs.html)

The instance type determines CPU, memory, networking, and supported storage. General-purpose families suit balanced workloads; compute-optimized and memory-optimized families suit different bottlenecks. Burstable types use CPU credits, so sustained work needs attention to credit consumption and the configured credit mode. The image architecture and instance architecture must agree.

## Key pairs and Security Groups

For a Linux instance, a key pair provides a public key installed on the instance and a private key retained by the operator. The private key must not be committed to Git. A key pair alone does not make SSH reachable: routing, an address, a listening SSH service, and allowed traffic are also needed. Session Manager can provide administration without opening SSH when its agent, IAM permissions, and network access are configured. [EC2 key pairs](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html)

A Security Group is a stateful traffic filter on the instance's network interfaces. Allow only the application ports required by the exercise. For example, an HTTP demo can allow TCP 80 while leaving SSH closed. Rules allowing all inbound traffic make troubleshooting easier temporarily but are a poor default. [Security Groups](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html)

## EBS and instance-store disks

EBS provides block storage, such as a boot disk or a filesystem volume. An EBS volume belongs to an Availability Zone and normally attaches to an instance in that zone. Volume type, capacity, throughput, and IOPS affect performance. Snapshots provide a point-in-time backup; encryption protects stored data. Whether an EBS volume is deleted at termination depends on its attachment settings.

Instance-store storage is tied to its host and should be treated as temporary. Important data should live on persistent storage with a separate backup strategy. [EBS overview](https://docs.aws.amazon.com/ebs/latest/userguide/what-is-ebs.html)

## Addresses and lifecycle

A private IP supports communication within connected private networks. A public IPv4 address provides an internet-addressable identity, but inbound access still needs the correct subnet route and traffic rules. An automatically assigned public IPv4 address can change after a stop/start; an Elastic IP has a separate allocation lifecycle.

```text
Launch -> pending -> running
                     |   |
                     |   +-> shutting-down -> terminated
                     +-> stopping -> stopped -> pending
```

Stopping an EBS-backed instance preserves its disks according to their configuration. Terminating removes the instance permanently. Storage and other allocated resources can remain chargeable even when compute is stopped, so cleanup must include the resources surrounding the instance. [Instance state changes](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-lifecycle.html)

## Common uses and troubleshooting

EC2 can host web servers, workers, build agents, or applications needing operating-system control. For an unreachable web server, I would check instance status, public address, route table, Security Group, subnet ACL, service status, and bootstrap logs in that order. An S3-backed web demo also needs an instance role with the correct object-read permissions.
