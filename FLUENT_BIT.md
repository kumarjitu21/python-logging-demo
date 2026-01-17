# Fluent Bit Integration Guide

This guide covers the Fluent Bit log aggregation setup for collecting logs from Kubernetes and forwarding them to Azure Log Analytics.

## Fluent Bit Architecture

Fluent Bit runs as a DaemonSet on every Kubernetes node and:
1. Collects container logs from `/var/log/containers/`
2. Parses JSON logs from the container runtime
3. Enriches logs with Kubernetes metadata
4. Forwards logs to Azure Log Analytics

## Configuration Files

### fluent-bit.conf (Standalone)
Located in `fluent-bit/fluent-bit.conf`, this is the main configuration file.

**Sections:**
- `[SERVICE]` - Global configuration (flush interval, log level, HTTP server)
- `[INPUT]` - Log sources (tail plugin for container logs, systemd for system logs)
- `[FILTER]` - Log processing (Kubernetes metadata, enrichment)
- `[OUTPUT]` - Destinations (Azure, Stackdriver, etc.)

### custom_parsers.conf
JSON parser configuration for different log formats.

## Input Plugins

### Tail Plugin (Container Logs)
```conf
[INPUT]
    Name              tail
    Path              /var/log/containers/*_fastapi-app_*.log
    Parser            docker
    Tag               app.*
    Refresh_Interval  5
    Mem_Buf_Limit     50MB
    Skip_Long_Lines   On
    DB                /var/log/flb_app.db
    DB.Locking        true
```

**Key Options:**
- `Path` - Pattern to match log files
- `Parser` - How to parse each log line
- `Tag` - Tag applied to logs (used in routing)
- `Mem_Buf_Limit` - Maximum memory before dropping logs
- `DB` - Persistent position database

### Systemd Plugin
Collects system logs from journald.

```conf
[INPUT]
    Name            systemd
    Tag             systemd.*
    Read_From_Tail  On
    Strip_Underscores On
```

## Filter Plugins

### Kubernetes Filter
Enriches logs with Kubernetes metadata (pod name, namespace, labels, etc.)

```conf
[FILTER]
    Name                kubernetes
    Match               app.*
    Kube_URL            https://kubernetes.default.svc:443
    Kube_CA_File        /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    Kube_Token_File     /var/run/secrets/kubernetes.io/serviceaccount/token
    Kube_Tag_Prefix     app.var.log.containers.
    Merge_Log           On
    Keep_Log            Off
    K8S-Logging.Parser  On
    K8S-Logging.Exclude Off
    Labels              On
    Annotations         On
```

### Modify Filter
Adds custom fields to log records.

```conf
[FILTER]
    Name    modify
    Match   app.*
    Add     cluster_name ${CLUSTER_NAME}
    Add     environment ${ENVIRONMENT}
    Add     application fastapi-logging-demo
```

### Nest Filter
Restructures JSON objects (lifting nested Kubernetes metadata).

```conf
[FILTER]
    Name    nest
    Match   app.*
    Operation lift
    Nested_under kubernetes
    Add_prefix k8s_
```

## Output Plugins

### Azure Output
Sends logs to Azure Log Analytics.

```conf
[OUTPUT]
    Name            azure
    Match           app.*
    Customer_ID     ${AZURE_WORKSPACE_ID}
    Shared_Key      ${AZURE_WORKSPACE_KEY}
    Log_Type        FastAPILogs
    Retry_Limit     5
    Time_Generated  Off
```

**Log_Type:** Creates a custom table in Log Analytics (suffix `_CL` added automatically)

### Stackdriver Output
For Google Cloud integration (optional).

```conf
[OUTPUT]
    Name                stackdriver
    Match               systemd.*
    google_service_credentials /var/secrets/google/key.json
    resource            k8s_pod
```

## Environment Variables

These are set via Kubernetes secret or configmap:

```bash
AZURE_WORKSPACE_ID=<workspace-id>
AZURE_WORKSPACE_KEY=<shared-key>
CLUSTER_NAME=aks-cluster
ENVIRONMENT=production
```

## ConfigMap Setup

The Kubernetes ConfigMap (`k8s/fluent-bit-configmap.yaml`) includes:
- `fluent-bit.conf` - Main configuration
- `custom_parsers.conf` - Parser definitions

To update configuration:
```bash
kubectl edit configmap fluent-bit-config -n fluent-bit
# Then restart DaemonSet
kubectl rollout restart daemonset/fluent-bit -n fluent-bit
```

## DaemonSet Deployment

The DaemonSet runs Fluent Bit on every node:

```yaml
spec:
  template:
    spec:
      containers:
      - name: fluent-bit
        image: fluent/fluent-bit:2.1.8
        volumeMounts:
        - name: fluent-bit-config
          mountPath: /fluent-bit/etc/
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
```

**Volume Mounts:**
- `/fluent-bit/etc/` - Configuration files
- `/var/log` - Host logs
- `/var/lib/docker/containers` - Container logs

## Log Flow Example

```
1. Pod produces log:
   {"timestamp": "2024-01-17T10:30:45.123", "level": "INFO", "message": "Request received"}

2. Logged to container stdout → captured in:
   /var/log/containers/fastapi-app-abc123_fastapi-app_app-container-0ae1234567890.log

3. Fluent Bit tail plugin reads file

4. Docker parser extracts JSON:
   {
     "time": "2024-01-17T10:30:45.123",
     "level": "INFO",
     "message": "Request received"
   }

5. Kubernetes filter enriches:
   {
     "time": "2024-01-17T10:30:45.123",
     "level": "INFO",
     "message": "Request received",
     "kubernetes": {
       "pod_name": "fastapi-app-abc123",
       "namespace_name": "fastapi-app",
       "pod_id": "12345-67890",
       "labels": {...},
       "annotations": {...}
     }
   }

6. Nest filter lifts Kubernetes fields:
   {
     "time": "2024-01-17T10:30:45.123",
     "level": "INFO",
     "message": "Request received",
     "k8s_pod_name": "fastapi-app-abc123",
     "k8s_namespace_name": "fastapi-app",
     ...
   }

7. Modify filter adds custom fields:
   {
     "time": "2024-01-17T10:30:45.123",
     "level": "INFO",
     "message": "Request received",
     "k8s_pod_name": "fastapi-app-abc123",
     "cluster_name": "aks-cluster",
     "environment": "production",
     "application": "fastapi-logging-demo"
   }

8. Azure output sends to Log Analytics
```

## Monitoring Fluent Bit

### Health Check
```bash
kubectl port-forward -n fluent-bit daemonset/fluent-bit 2020:2020
curl http://localhost:2020/api/v1/health
```

### Metrics
```
http://localhost:2020/api/v1/metrics/prometheus
```

### View Logs
```bash
kubectl logs -n fluent-bit -l app=fluent-bit -f
```

### Check Configuration
```bash
kubectl exec -n fluent-bit -it <pod-name> -- fluent-bit -c /fluent-bit/etc/fluent-bit.conf -o dummy
```

## Performance Tuning

### Memory Usage
Control with `Mem_Buf_Limit` in tail input:
```conf
[INPUT]
    Mem_Buf_Limit  50MB
```

### Throughput
Adjust flush interval in SERVICE:
```conf
[SERVICE]
    Flush  5  # Flush every 5 seconds
```

### Retry
Configure retry logic in output:
```conf
[OUTPUT]
    Retry_Limit  5
```

## Troubleshooting

### Logs not reaching Azure
1. Check Fluent Bit pod status:
   ```bash
   kubectl get pods -n fluent-bit
   ```

2. Check Azure credentials secret:
   ```bash
   kubectl get secret azure-credentials -n fluent-bit
   ```

3. View Fluent Bit logs:
   ```bash
   kubectl logs -n fluent-bit -l app=fluent-bit --tail=50
   ```

4. Verify connectivity to Azure:
   ```bash
   kubectl exec -n fluent-bit <pod> -- curl https://management.azure.com
   ```

### High memory usage
- Reduce `Mem_Buf_Limit`
- Increase Flush interval
- Check for large log files

### Logs being dropped
- Look for "drop" in Fluent Bit logs
- Increase `Mem_Buf_Limit`
- Check Azure quota/throttling

### Missing Kubernetes metadata
- Verify RBAC permissions (ClusterRole)
- Check service account token
- Enable debug logging: `Log_Level debug`

## Advanced Configuration

### Multiple Outputs
Route different logs to different destinations:

```conf
[OUTPUT]
    Name   azure
    Match  app.*
    Customer_ID  ${AZURE_WORKSPACE_ID}
    Shared_Key   ${AZURE_WORKSPACE_KEY}

[OUTPUT]
    Name   stdout
    Match  systemd.*
    Format json_lines
```

### Custom Parsers
Add to `custom_parsers.conf`:

```conf
[PARSER]
    Name    my_custom_log
    Format  regex
    Regex   ^(?<time>[^ ]+) (?<level>[^ ]+) (?<message>.*)$
    Time_Key time
    Time_Format %Y-%m-%d %H:%M:%S
```

### Conditional Routing
Use `Match` pattern to filter logs:

```conf
[FILTER]
    Name  grep
    Match app.*
    Regex message .*ERROR.*

[OUTPUT]
    Name      azure
    Match     app.*
    Log_Type  FastAPIErrors
```

## Resources

- [Fluent Bit Documentation](https://docs.fluentbit.io/)
- [Fluent Bit Kubernetes Plugin](https://docs.fluentbit.io/manual/pipeline/filters/kubernetes)
- [Azure Output Plugin](https://docs.fluentbit.io/manual/pipeline/outputs/azure)
- [Azure Log Analytics](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/log-analytics-overview)
