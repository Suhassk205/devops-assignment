mock_provider "aws" {
  mock_resource "aws_s3_bucket" {
    defaults = {
      id  = "session19-test-artifacts"
      arn = "arn:aws:s3:::session19-test-artifacts"
    }
  }

  mock_resource "aws_instance" {
    defaults = {
      public_ip = "192.0.2.10"
    }
  }
}

variables {
  ami_id = "ami-0123456789abcdef0"
}

run "configuration_plan" {
  command = plan

  assert {
    condition = (
      cidrsubnet(aws_vpc.main.cidr_block, 8, 1) == aws_subnet.public.cidr_block &&
      aws_instance.web.instance_type == "t3.micro" &&
      aws_s3_bucket_public_access_block.artifacts.block_public_policy &&
      aws_instance.web.metadata_options[0].http_tokens == "required"
    )
    error_message = "The local plan must include the expected subnet, instance size, private bucket, and required IMDSv2."
  }
}

run "network_and_compute_connections" {
  command = apply

  assert {
    condition = (
      cidrsubnet(aws_vpc.main.cidr_block, 8, 1) == aws_subnet.public.cidr_block &&
      aws_subnet.public.vpc_id == aws_vpc.main.id &&
      aws_instance.web.subnet_id == aws_subnet.public.id &&
      contains(aws_instance.web.vpc_security_group_ids, aws_security_group.web.id) &&
      aws_route_table_association.public.subnet_id == aws_subnet.public.id &&
      aws_route_table_association.public.route_table_id == aws_route_table.public.id
    )
    error_message = "The web server must use the project's subnet, security group, and associated route table."
  }

  assert {
    condition = anytrue([
      for route in aws_route_table.public.route :
      route.cidr_block == "0.0.0.0/0" && route.gateway_id == aws_internet_gateway.main.id
    ])
    error_message = "The public subnet needs its default route through the Internet Gateway."
  }
}

run "private_artifact_storage" {
  command = apply

  assert {
    condition = (
      aws_s3_bucket_public_access_block.artifacts.block_public_acls &&
      aws_s3_bucket_public_access_block.artifacts.block_public_policy &&
      aws_s3_bucket_public_access_block.artifacts.ignore_public_acls &&
      aws_s3_bucket_public_access_block.artifacts.restrict_public_buckets &&
      aws_s3_bucket_versioning.artifacts.versioning_configuration[0].status == "Enabled" &&
      one(aws_s3_bucket_server_side_encryption_configuration.artifacts.rule).apply_server_side_encryption_by_default[0].sse_algorithm == "AES256"
    )
    error_message = "Artifacts must remain private, versioned, and encrypted."
  }

  assert {
    condition = (
      aws_s3_object.homepage.bucket == aws_s3_bucket.artifacts.id &&
      aws_s3_object.homepage.key == "site/index.html" &&
      jsondecode(aws_s3_bucket_policy.tls_only.policy).Statement[0].Condition.Bool["aws:SecureTransport"] == "false"
    )
    error_message = "The website file must use the protected bucket, and its policy must reject insecure transport."
  }
}

run "instance_security_and_bootstrap" {
  command = apply

  assert {
    condition = (
      aws_instance.web.metadata_options[0].http_tokens == "required" &&
      aws_instance.web.root_block_device[0].encrypted &&
      aws_instance.web.iam_instance_profile == aws_iam_instance_profile.web.name &&
      length(aws_security_group.web.ingress) == 1 &&
      one(aws_security_group.web.ingress).from_port == 80 &&
      one(aws_security_group.web.ingress).to_port == 80 &&
      jsondecode(aws_iam_role_policy.artifact_read.policy).Statement[0].Action == ["s3:GetObject"] &&
      jsondecode(aws_iam_role_policy.artifact_read.policy).Statement[0].Resource == "${aws_s3_bucket.artifacts.arn}/site/*"
    )
    error_message = "Require IMDSv2, encrypted disks, HTTP-only ingress, and bucket-scoped read access."
  }

  assert {
    condition = (
      strcontains(aws_instance.web.user_data, "s3://${aws_s3_bucket.artifacts.id}/site/index.html") &&
      strcontains(aws_instance.web.user_data, "systemctl enable --now nginx") &&
      output.web_url == "http://192.0.2.10"
    )
    error_message = "Bootstrap must fetch the project's artifact and start Nginx."
  }
}

run "reject_invalid_project_name" {
  command = plan
  variables {
    project_name = "INVALID NAME"
  }
  expect_failures = [var.project_name]
}

run "reject_invalid_client_cidr" {
  command = plan
  variables {
    http_allowed_cidr = "not-a-cidr"
  }
  expect_failures = [var.http_allowed_cidr]
}
