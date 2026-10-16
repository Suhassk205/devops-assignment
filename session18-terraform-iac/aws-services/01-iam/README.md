# IAM: identities, permissions, and least privilege

IAM controls who can use an AWS account and which actions they can perform. Authentication establishes an identity; authorization evaluates whether that identity may make a particular request. For example, signing in successfully does not automatically grant permission to delete an S3 bucket.

## Users, groups, and roles

| Identity | Purpose | Example |
|---|---|---|
| Root user | Account owner with broad account access | Account-level operations that require root |
| IAM user | An identity with its own credentials | A legacy integration that cannot use federation |
| IAM group | A collection of users that share policies | Read-only access for a support team |
| IAM role | Permissions assumed through temporary credentials | An EC2 application reading its own S3 bucket |

A group is useful for assigning permissions consistently, but applications do not sign in as a group. A role has a trust policy describing who may assume it and permission policies describing what the resulting session may do. Human access should normally use federation or IAM Identity Center rather than a separate long-lived access key for each service. See [IAM identities](https://docs.aws.amazon.com/IAM/latest/UserGuide/id.html).

## Policies and effective permissions

Policies are JSON documents. The main fields are `Effect`, `Action`, `Resource`, and optional `Condition`. Resource policies, such as S3 bucket policies, also identify a `Principal`. Identity policies attach to users, groups, or roles. A permissions boundary limits what an identity can be granted; an Organizations service control policy limits permissions available in member accounts.

A request needs an applicable allow. An explicit deny overrides an allow. Boundaries, session policies, and organization controls can restrict the result, so an administrator must check the complete policy context when investigating `AccessDenied`. [AWS policy documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html)

## Least-privilege example

An application that only downloads web files needs object reads, not permission to create buckets or change their policies. This example is limited to one prefix:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::example-course-artifacts/site/*"
    }
  ]
}
```

`ListBucket` is a separate bucket-level permission. If the application lists objects, add it on the bucket ARN and restrict the prefix with a condition. Reading an SSE-KMS object can also require access to the KMS key.

## Practices I would use

- Protect root with MFA and keep it out of routine deployment workflows.
- Use temporary role credentials for EC2, containers, and CI where possible.
- Grant only the required actions, resources, and conditions.
- Separate deployment permissions from the application's runtime permissions.
- Remove unused users, keys, and permissions; investigate unexpected access with CloudTrail.
- Keep credentials outside source code, container images, screenshots, and Terraform variable files committed to Git.

These follow [AWS IAM security best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html).

## Common uses

IAM connects the other services: developers get access to selected environments, EC2 assumes an instance role, and a deployment pipeline gets permission to update only its application resources. In the Session 19 mini-project, the instance role reads the project's S3 files without storing access keys on the server.
