# Kubernetes Object Comparison

## Deployment vs ReplicaSet

| Question | Deployment | ReplicaSet |
|---|---|---|
| Purpose | Manage application releases | Maintain a specified number of matching Pods |
| Pod management | Creates and manages ReplicaSets | Creates replacement Pods when the count falls |
| Scaling | Change Deployment replicas | Change ReplicaSet replicas |
| Rolling updates | Creates a new ReplicaSet and shifts replicas gradually | Does not provide a release rollout strategy |
| Relationship | Owns ReplicaSets; normally the object you operate | Owned by a Deployment in typical applications |

## Deployment vs DaemonSet vs StatefulSet

| Property | Deployment | DaemonSet | StatefulSet |
|---|---|---|---|
| Typical use | Stateless API or web server | Node-level logging/monitoring agent | Workload requiring stable identity or per-Pod storage |
| Pod creation | Desired replica count | One Pod on each eligible node | Ordinal Pods, commonly ordered |
| Scaling | Set replicas or use HPA | Change eligible nodes; no replicas field | Set replicas, preserving ordinal identities |
| Networking | Service provides a stable entry point | Often node-oriented | Governing headless Service supports stable Pod DNS |
| Storage | Shared/external storage where needed | Often node-local mounts | Separate claims through volumeClaimTemplates |
| Example | Nginx frontend | Node exporter | Database node requiring stable identity |

A StatefulSet supplies identity and storage management; database replication must still be configured by the database or its operator.

## ReplicaSet vs Service

A ReplicaSet keeps the requested number of Pods running. A Service supplies a stable network address and selects the Pods that receive traffic. Scaling or replacing Pods changes their IP addresses; the Service updates its endpoints to follow eligible Pods.

```text
Deployment -> ReplicaSet -> Pods
                              ^
Client -> Service -> ready matching endpoints
```

The ReplicaSet selector determines which Pods it manages. The Service selector determines which Pods it routes to. Neither object replaces the other.
