import re
import json
from kubernetes import client, config

job_name = "shard-validation-job"
namespace = "default"

config.load_kube_config()

v1 = client.CoreV1Api()

pods = v1.list_namespaced_pod(
    namespace=namespace,
    label_selector=f"job-name={job_name}"
)

results = []

for pod in pods.items:
    pod_name = pod.metadata.name

    logs = v1.read_namespaced_pod_log(
        pod_name,
        namespace
    )

    match = re.search(r"RESULT_JSON:(\{.*\})", logs)

    if not match:
        print(
            f"WARNING: no RESULT_JSON found in logs for {pod_name}"
        )
        continue

    result = json.loads(match.group(1))
    results.append(result)

results.sort(
    key=lambda result: result["completion_index"]
)

print(
    f"{'Shard':<8}"
    f"{'Total Rows':<12}"
    f"{'Invalid Rows':<14}"
    f"{'Pod':<40}"
    f"{'Node'}"
)

for result in results:
    print(
        f"{result['completion_index']:<8}"
        f"{result['total_rows']:<12}"
        f"{result['invalid_rows']:<14}"
        f"{result['pod_name']:<40}"
        f"{result['node_name']}"
    )

total_invalid = sum(
    result["invalid_rows"]
    for result in results
)

print(
    f"\nTotal invalid rows across all shards: "
    f"{total_invalid}"
)

with open("shard_results.json", "w") as file:
    json.dump(results, file, indent=2)

print("\nSaved full results to shard_results.json") 