# Session 19 mini-project: EC2 website with private S3 artifacts

This project defines a small AWS web application with Terraform. An EC2 instance runs Nginx in a public subnet. Its instance role downloads the website from a private S3 bucket, so the server needs no stored AWS access keys.

## Architecture

```mermaid
flowchart TD
    Browser[Browser] -->|HTTP 80| IGW[Internet Gateway]
    subgraph VPC["VPC: 10.20.0.0/16"]
        IGW --> RT["Public route table: 0.0.0.0/0 to IGW"]
        RT --> Subnet["Public subnet: 10.20.1.0/24"]
        Subnet --> SG["Security Group: HTTP only"]
        SG --> EC2["EC2: Amazon Linux and Nginx"]
    end
    Role["Instance role: GetObject on site/*"] -.-> EC2
    EC2 -->|HTTPS: download index.html| S3["Private S3 bucket: encrypted and versioned"]
```

S3 is a regional service outside the VPC. The instance reaches its API through the public subnet's outbound internet route. The bucket is private even though Nginx serves the downloaded page publicly.

## Terraform files

| File | Purpose |
|---|---|
| [versions.tf](versions.tf) | Terraform version, AWS provider, and region |
| [variables.tf](variables.tf) | Region, project prefix, instance size, optional AMI, and HTTP client CIDR |
| [main.tf](main.tf) | Network, EC2, IAM role/profile, S3 bucket protections, and website object |
| [outputs.tf](outputs.tf) | VPC, subnet, instance, bucket, and website outputs |
| [terraform.tfvars.example](terraform.tfvars.example) | Example settings without credentials |
| [user-data.sh.tftpl](user-data.sh.tftpl) | Install Nginx, download the private object, and start the service |
| [site/index.html](site/index.html) | Website content stored in S3 |
| [tests/architecture.tftest.hcl](tests/architecture.tftest.hcl) | Local plan, connection, security, and invalid-input tests |

Terraform resource references establish the dependencies. The instance also explicitly waits for the route association, object upload, and role policy before bootstrapping.

## Security choices

- The instance accepts HTTP on port 80 from `http_allowed_cidr`; SSH is closed.
- IMDSv2 is required, and the root EBS volume is encrypted.
- The instance role can read only `site/*` in this project's bucket.
- S3 public access is blocked, object ownership is enforced, and versioning is enabled.
- Bucket encryption uses AES256, and the bucket policy denies requests without secure transport.
- Terraform state, private variable files, and saved plans are excluded from Git.

HTTP is used for the classroom web page. HTTPS would need a certificate and a suitable TLS termination setup.

## AWS deployment results

I deployed the project in `ap-south-1`, checked the web response and S3 settings, then destroyed the resources.

| Resource or check | Result |
|---|---|
| VPC | `vpc-0e830c64665d7d388` |
| Public subnet | `subnet-0893da614b70f02b9` |
| Security Group | `sg-018f592dbc5d3d74b` |
| EC2 instance | `i-0c249f7e6fece35b3`; `t3.micro` |
| Private artifact bucket | `s19-suhas-1792170522-2978acab6f6418b0bcac97e282` |
| Website | HTTP 200 from `http://13.232.163.105` |
| S3 protections | Public access blocked; versioning enabled; AES256 encryption |
| Terraform cleanup | 17 resources destroyed; local state empty |
| AWS cleanup verification | Instance terminated; lab bucket, VPC, subnet, Security Group, EBS volume, and instance roles removed |

The website address above belongs to the completed lab run and is no longer serving the application after cleanup.

## Local verification

I initialized the provider, checked formatting, validated the configuration, and ran six Terraform tests. The tests use a **mocked AWS provider**: their plan, apply, and teardown operations happen in the test environment without creating cloud resources.

| Test | Result |
|---|---|
| Configuration plan | Passed |
| Subnet, routes, Security Group, and instance connections | Passed |
| Private, versioned, encrypted artifact storage | Passed |
| Instance permissions, IMDSv2, encrypted disk, and bootstrap content | Passed |
| Invalid project name rejected | Passed |
| Invalid HTTP client CIDR rejected | Passed |

The mock tests use a fixture AMI and generated resource IDs to check configuration relationships and safeguards. The AWS run above also verified the selected image, instance permissions, artifact download, and Nginx response.

Run from this directory:

```bash
terraform init -backend=false
terraform fmt -check -recursive
terraform validate
terraform test
terraform test -verbose
```

Or run `python3 scripts/run_session19.py` from the course repository root to save the output under `evidence/`.

## AWS deployment commands

Use a signed-in AWS CLI profile with the required permissions. Copy the example variables and review the plan before applying:

```bash
cp terraform.tfvars.example terraform.tfvars
aws sts get-caller-identity
terraform init
terraform fmt -check -recursive
terraform validate
terraform plan -out=deployment.tfplan
terraform apply deployment.tfplan
terraform show
terraform output
```

If `ami_id` is unset, Terraform resolves Amazon Linux 2023's x86_64 AMI through AWS's public SSM parameter. An explicit AMI must be valid in the selected region. Wait for the instance's bootstrap to finish before checking its URL:

```bash
curl --fail "$(terraform output -raw web_url)"
aws s3api get-public-access-block --bucket "$(terraform output -raw artifact_bucket)"
aws s3api get-bucket-versioning --bucket "$(terraform output -raw artifact_bucket)"
```

For a failed web response, inspect routes, Security Groups, instance status, and `/var/log/cloud-init-output.log`. Terraform creating an instance does not by itself confirm that Nginx started successfully.

## Cleanup

```bash
terraform plan -destroy
terraform destroy
terraform state list
```

The artifact bucket has `force_destroy = true` for this disposable lab. Destroying it removes its objects and versions too. The instance's root disk is configured for deletion at termination. Keep any required files elsewhere before cleanup.

## Command output and screenshots

- [Initialization, formatting, and validation](../evidence/01-terraform-validation.txt)
- [Six passing local tests](../evidence/02-terraform-tests.txt)
- [Full mocked plan and test output](../evidence/03-mocked-plan.txt)

![Terraform initialization and validation](../screenshots/01-terraform-validation.png)

![Mocked-provider Terraform tests](../screenshots/02-terraform-tests.png)

## AWS execution evidence

| Exercise | Full output | Screenshot |
|---|---|---|
| Initialize, format, validate, and plan | [Output](../evidence/04-aws-plan.txt) | [Screenshot](../screenshots/04-aws-plan.png) |
| Provision the infrastructure | [Output](../evidence/05-aws-apply.txt) | [Screenshot](../screenshots/05-aws-apply.png) |
| Inspect state, outputs, S3 protections, and HTTP response | [Output](../evidence/06-aws-verification.txt) | [Screenshot](../screenshots/06-aws-verification.png) |
| Destroy all 17 resources | [Output](../evidence/07-aws-destroy.txt) | [Screenshot](../screenshots/07-aws-destroy.png) |
| Verify cleanup through AWS service APIs | [Output](../evidence/08-cleanup-check.txt) | [Screenshot](../screenshots/08-cleanup-check.png) |

![AWS infrastructure created](../screenshots/05-aws-apply.png)

![HTTP response and AWS verification](../screenshots/06-aws-verification.png)

![AWS infrastructure destroyed](../screenshots/07-aws-destroy.png)
