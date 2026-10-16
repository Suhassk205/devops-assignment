# DynamoDB and RDS: choosing a database model

DynamoDB and RDS both manage database infrastructure, but they suit different data models and access patterns. I would choose between them by examining the application's queries, relationships, transactions, and operational needs.

## DynamoDB

DynamoDB is a managed NoSQL database. A table holds items; each item contains attributes. Items do not need identical non-key attributes, but key definitions and access patterns must be planned.

A table has either a partition key alone or a composite primary key with a partition key and sort key. The partition key participates in distributing data. A sort key distinguishes and orders items sharing the same partition key. A query normally specifies a partition-key value and can restrict sort-key values. Secondary indexes support other planned query patterns. Repeated broad scans are often a sign that the key design does not match the application. [DynamoDB components](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.CoreComponents.html)

Example access pattern:

```text
Table: Orders
Partition key: CUSTOMER#10261
Sort key: ORDER#2026-10-16#0001
Attributes: total, status, delivery_address
```

This design groups a customer's orders and supports ordered queries within that customer. A different access pattern, such as looking up all orders by status, needs a suitable index or another design. IAM policies restrict table/index operations, and an application should use a role rather than embedded keys.

Common uses include carts, session data, event metadata, and high-volume key-based lookups. NoSQL does not mean DynamoDB has no transactions; it means the table model and query approach differ from relational SQL.

## RDS

RDS operates relational database engines, including PostgreSQL, MySQL, MariaDB, Oracle, SQL Server, and Db2. A DB instance provides database compute and storage; applications connect using the engine's protocol. AWS manages infrastructure tasks, while the application owner remains responsible for schema design, queries, access configuration, and data use. [RDS overview](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Welcome.html)

Relational tables fit entities such as customers, orders, and order items, with keys and constraints connecting them. SQL supports joins and flexible queries. This suits applications where relationships and transaction boundaries are central.

## Security and backups

Place database resources in suitable subnets and allow database traffic only from the application tier. IAM access to RDS management APIs is different from authenticating a database connection. Use separate database users with limited privileges, manage passwords outside source code, and configure encryption and TLS where supported.

Automated backups support recovery within the configured retention period. Manual snapshots provide separately retained restore points. Restoring a backup creates a database resource that must be configured and tested before applications use it. A backup policy should be paired with a tested recovery process. [RDS backups](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_CommonTasks.BackupRestore.html)

## Multi-AZ and read replicas

| Feature | Main purpose | Behavior |
|---|---|---|
| Multi-AZ DB instance | Availability and failover | Synchronous standby in another AZ; the standby does not serve application reads |
| Multi-AZ DB cluster | Availability with reader instances | Uses a different cluster architecture that can also serve reads |
| Read replica | Read scaling | Usually asynchronous replication; reads may lag behind the source |

Do not treat every Multi-AZ option as identical. A standard Multi-AZ DB instance's standby is for failover, while a read replica serves a read workload. Replicas also do not replace backups: unwanted writes can replicate. [Multi-AZ options](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.html), [read replicas](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ReadRepl.html)

## Comparison

| Question | DynamoDB | RDS |
|---|---|---|
| Data model | Items and attributes | Relational tables |
| Main query approach | Keys and planned indexes | SQL, indexes, joins |
| Good fit | Predictable key-based access at scale | Related business data and SQL transactions |
| Design concern | Partition/key distribution and access patterns | Schema, query plans, connections, capacity |

For an inventory or appointment application with related records, PostgreSQL on RDS is a natural option. For a key-based session store, DynamoDB can fit better. The decision should follow the workload rather than choosing a service just because it is managed.
