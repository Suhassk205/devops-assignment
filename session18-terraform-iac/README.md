# Session 18: Terraform & Infrastructure as Code

Notes and examples for defining infrastructure with Terraform, working with providers, and managing resource state. The AWS example uses an S3 bucket to practice the Terraform lifecycle.

## Homework

- [Task 1: Terraform S3 bucket workflow](terraform-s3-demo/README.md)
- [Task 2: AWS services research](aws-services/README.md)

## Topics

- [Infrastructure as Code basics](01-iac-basics/README.md)
- [Terraform architecture](02-terraform-architecture/README.md)
- [Providers](03-providers/README.md)
- [Resources](04-resources/README.md)
- [Variables](05-variables/README.md)
- [Outputs](06-outputs/README.md)
- [Initialize, plan, and apply](07-init-plan-apply/README.md)
- [Destroy resources](08-destroy/README.md)
- [Terraform state](09-state/README.md)
- [S3 bucket example](terraform-s3-demo/)

## Setup references

- [Install Terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)
- [Terraform AWS tutorial](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/aws-create)
- [Install the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

## Practical checks

The [S3 demo](terraform-s3-demo/README.md) includes the lifecycle commands, local validation output, and an inventory of the saved state. The [AWS research notes](aws-services/README.md) cover all five services from Task 2.
