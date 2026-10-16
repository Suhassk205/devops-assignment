# S3: objects, storage classes, and data protection

S3 stores objects in buckets. An object contains data and metadata and is addressed by a key such as `reports/build-17.txt`. Slash-separated keys look like directories, but ordinary S3 buckets store keys rather than a traditional mounted filesystem. S3 is useful for artifacts, uploads, backups, logs, and static assets.

## Buckets and access

A general-purpose bucket is created in a region and needs a unique name within the relevant AWS partition. IAM policies and bucket policies control access. Keeping Block Public Access enabled is a sensible starting point for an artifact bucket. An application can use an IAM role to retrieve private objects; public access is not required just because a web server uses the files.

Bucket policies can grant or deny resource access. For example, a deny condition on `aws:SecureTransport=false` rejects unencrypted transport. An explicit deny can block access even when an identity policy allows it. [Policies and permissions](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html)

## Storage classes

| Class | Suitable access pattern |
|---|---|
| Standard | Frequently accessed application data |
| Intelligent-Tiering | Changing or unpredictable access patterns |
| Standard-IA | Infrequent reads with immediate retrieval |
| One Zone-IA | Infrequent access to reproducible data stored in one AZ |
| Glacier Instant Retrieval | Archive data needing millisecond access |
| Glacier Flexible Retrieval | Archive data that can wait for restoration |
| Glacier Deep Archive | Long-term archives with longer restoration times |
| Express One Zone | Low-latency workloads using a directory bucket in one AZ |

The choice depends on access frequency, retrieval delay, resilience requirements, and minimum storage/retrieval charges. A cheaper storage rate is not necessarily a cheaper total workload. [S3 storage classes](https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html)

## Versioning

Versioning keeps separate versions when an object is overwritten. Deleting an object without specifying a version normally adds a delete marker rather than removing all previous versions. Restoring an earlier version can recover an accidental overwrite, but versioning is not protection against every account-level or administrative failure.

Old versions still occupy storage. Before deleting a versioned bucket, remove its versions and delete markers as well as current objects. [S3 Versioning](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html)

## Lifecycle policies

Lifecycle rules can transition eligible objects to another storage class or expire them. Filters can select a prefix or tags. Noncurrent-version rules handle old versions separately. For example, build artifacts might remain in Standard while actively used, then transition to an archive class and eventually expire. The retention policy should reflect recovery requirements rather than deleting evidence immediately. [Lifecycle management](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html)

## Encryption

New S3 object uploads are encrypted at rest by default with S3-managed keys. Explicit bucket encryption configuration makes the intended setting visible in infrastructure code. SSE-KMS provides KMS key controls and requires the corresponding key permissions; client-side encryption happens before upload. Use HTTPS for transport. Encryption alone does not decide who may download an object. [S3 encryption](https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingEncryption.html)

## Applying this to the coursework

The Terraform S3 demo practices creation, state inspection, outputs, and destruction. The Session 19 artifact bucket adds public-access blocking, versioning, encryption, and an EC2 role limited to reads. The web server copies a private `index.html` object during startup and serves it over HTTP; the S3 bucket itself stays private.
