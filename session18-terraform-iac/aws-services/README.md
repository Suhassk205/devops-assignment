# AWS services research

These notes cover the services used to build, secure, and operate a small AWS application.

- [IAM: identities, roles, policies, and least privilege](01-iam/README.md)
- [EC2: images, instance types, networking, and storage](02-ec2/README.md)
- [S3: objects, storage classes, versioning, and encryption](03-s3/README.md)
- [VPC: subnets, routing, gateways, and traffic controls](04-vpc/README.md)
- [DynamoDB and RDS: data models, availability, and replication](05-dynamodb-rds/README.md)

A web application combines these services: its EC2 instance runs in a VPC, assumes an IAM role to read private S3 artifacts, and uses a database chosen for the application's access patterns.
