# Session 13: Storage, HPA & Probes

This repository contains the tasks completed for Session 13.

## Task 1: Kubernetes Volumes
The documentation for Kubernetes volumes (including `emptyDir`, `hostPath`, `PersistentVolume`, `PersistentVolumeClaim`, `StorageClass`, and Dynamic provisioning) with practical examples can be found here:
- [Kubernetes Volumes Documentation](./01-kubernetes-volumes/README.md)

## Task 2: HPA Hands-on
We deployed the application and HPA, followed by a load generator to simulate traffic.

**HPA Scaling Output:**
```text
NAME       REFERENCE             TARGETS         MINPODS   MAXPODS   REPLICAS   AGE
hpa-demo   Deployment/hpa-demo   cpu: 116%/50%   1         5         2          68s
NAME                        CPU(cores)   MEMORY(bytes)   
hpa-demo-5d6676989b-25dzn   46m          2Mi             
hpa-demo-5d6676989b-s7npf   58m          3Mi             
load-generator              523m         3Mi             
NAME                        READY   STATUS    RESTARTS   AGE
hpa-demo-5d6676989b-25dzn   1/1     Running   0          23s
hpa-demo-5d6676989b-fzthw   1/1     Running   0          8s
hpa-demo-5d6676989b-s7npf   1/1     Running   0          68s
load-generator              1/1     Running   0          58s
Name:                                                  hpa-demo
Namespace:                                             default
Labels:                                                <none>
Annotations:                                           <none>
CreationTimestamp:                                     Wed, 07 Oct 2026 22:57:46 +0530
Reference:                                             Deployment/hpa-demo
Metrics:                                               ( current / target )
  resource cpu on pods  (as a percentage of request):  116% (116m) / 50%
Min replicas:                                          1
Max replicas:                                          5
Deployment pods:                                       2 current / 3 desired
Conditions:
  Type            Status  Reason              Message
  ----            ------  ------              -------
  AbleToScale     True    SucceededRescale    the HPA controller was able to update the target scale to 3
  ScalingActive   True    ValidMetricFound    the HPA was able to successfully calculate a replica count from cpu resource utilization (percentage of request)
  ScalingLimited  False   DesiredWithinRange  the desired count is within the acceptable range
  ScaledToZero    False   NotScaledToZero     the HPA controller did not scale the workload to zero
Events:
  Type     Reason                        Age                From                       Message
  ----     ------                        ----               ----                       -------
  Warning  FailedGetResourceMetric       53s (x2 over 68s)  horizontal-pod-autoscaler  failed to get cpu utilization: unable to get metrics for resource cpu: no metrics returned from resource metrics API
  Warning  FailedComputeMetricsReplicas  53s (x2 over 68s)  horizontal-pod-autoscaler  invalid metrics (1 invalid out of 1), first error is: failed to get cpu resource metric value: failed to get cpu utilization: unable to get metrics for resource cpu: no metrics returned from resource metrics API
  Warning  FailedGetResourceMetric       38s                horizontal-pod-autoscaler  failed to get cpu utilization: did not receive metrics for targeted pods (pods might be unready)
  Warning  FailedComputeMetricsReplicas  38s                horizontal-pod-autoscaler  invalid metrics (1 invalid out of 1), first error is: failed to get cpu resource metric value: failed to get cpu utilization: did not receive metrics for targeted pods (pods might be unready)
  Normal   SuccessfulRescale             23s                horizontal-pod-autoscaler  New size: 2; reason: cpu resource utilization (percentage of request) above target
  Normal   SuccessfulRescale             8s                 horizontal-pod-autoscaler  New size: 3; reason: cpu resource utilization (percentage of request) above target
```

## Task 3: Mini Project
The mini-project has been fully deployed in the `production-webapp` namespace, including the Namespace, PVC, Deployment, Service, and HPA.

**Mini-Project Scaling Output:**
```text
NAME          REFERENCE            TARGETS      MINPODS   MAXPODS   REPLICAS   AGE
web-app-hpa   Deployment/web-app   cpu: 1%/1%   2         5         2          2m48s
NAME                      READY   STATUS              RESTARTS      AGE
ab-load                   0/1     ContainerCreating   0             24s
load-generator            1/1     Running             0             2m44s
load-generator-2          1/1     Running             0             95s
load-generator-3          1/1     Running             0             94s
load-generator-4          1/1     Running             0             94s
load-generator-5          1/1     Running             0             94s
load-generator-stress     1/1     Running             0             31s
web-app-d45775485-dw44r   1/1     Running             0             2m49s
web-app-d45775485-f5znn   1/1     Running             1 (63s ago)   2m49s
```
