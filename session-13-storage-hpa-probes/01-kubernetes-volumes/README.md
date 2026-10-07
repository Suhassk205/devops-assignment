# Kubernetes Volumes Documentation

This document summarizes the core Kubernetes storage concepts and provides practical examples for each.

## 1. `emptyDir`

An `emptyDir` volume is first created when a Pod is assigned to a Node, and exists as long as that Pod is running on that node. It is initially empty. All containers in the Pod can read and write the same files in the `emptyDir` volume. When a Pod is removed from a node for any reason, the data in the `emptyDir` is deleted permanently.

**Use cases:** Scratch space, caching, temporary storage between containers.

**Practical Example:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: test-emptydir
spec:
  containers:
  - name: test-container
    image: busybox:1.28
    command: ["sh", "-c", "sleep 3600"]
    volumeMounts:
    - mountPath: /cache
      name: cache-volume
  volumes:
  - name: cache-volume
    emptyDir: {}
```

## 2. `hostPath`

A `hostPath` volume mounts a file or directory from the host node's filesystem into your Pod. This is not something that most Pods will need, but it offers a powerful escape hatch for some applications.

**Use cases:** Running a container that needs access to Docker internals, running cAdvisor in a container.

**Practical Example:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: test-hostpath
spec:
  containers:
  - name: test-container
    image: busybox:1.28
    command: ["sh", "-c", "sleep 3600"]
    volumeMounts:
    - mountPath: /var/local/host-data
      name: host-data-volume
  volumes:
  - name: host-data-volume
    hostPath:
      path: /data
      type: DirectoryOrCreate
```

## 3. PersistentVolume (PV)

A `PersistentVolume` (PV) is a piece of storage in the cluster that has been provisioned by an administrator or dynamically provisioned using Storage Classes. It is a resource in the cluster just like a node is a cluster resource. PVs are volume plugins like Volumes, but have a lifecycle independent of any individual Pod that uses the PV.

**Practical Example:**
```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: task-pv-volume
  labels:
    type: local
spec:
  storageClassName: manual
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: "/mnt/data"
```

## 4. PersistentVolumeClaim (PVC)

A `PersistentVolumeClaim` (PVC) is a request for storage by a user. It is similar to a Pod. Pods consume node resources and PVCs consume PV resources. Pods can request specific levels of resources (CPU and Memory). Claims can request specific size and access modes (e.g., they can be mounted ReadWriteOnce, ReadOnlyMany or ReadWriteMany).

**Practical Example:**
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: task-pv-claim
spec:
  storageClassName: manual
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 3Gi
```

## 5. StorageClass

A `StorageClass` provides a way for administrators to describe the "classes" of storage they offer. Different classes might map to quality-of-service levels, backup policies, or arbitrary policies determined by the cluster administrators. 

**Practical Example:**
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: standard
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp2
reclaimPolicy: Retain
allowVolumeExpansion: true
```

## 6. Dynamic Provisioning

Dynamic volume provisioning allows storage volumes to be created on-demand. Without dynamic provisioning, cluster administrators have to manually make calls to their cloud or storage provider to create new storage volumes, and then create `PersistentVolume` objects to represent them in Kubernetes. With dynamic provisioning, a `PersistentVolumeClaim` will automatically trigger the creation of a PV according to the rules specified in a `StorageClass`.

**Practical Example:**
If we create a PVC and do NOT specify an existing PV, Kubernetes will use the default `StorageClass` (or a specified one) to create the disk in the cloud (like AWS EBS, GCP PD) and create the corresponding PV automatically.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: dynamic-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
  # Omitting storageClassName often falls back to the default dynamic provisioner
  storageClassName: standard 
```
