## AI Usage Disclosure

**AI tool used: Claude (Anthropic)**

AI assistance was used throughout the assignment primarily for understanding syntax, troubleshooting, and verifying command usage. The final implementations and experimental results were executed and verified manually in the student's development environment.

| Question | AI Usage |
|---|---|
| **Report** | Used for LaTeX formatting, document structure, tables, and code-block formatting within the 2-page limit. |
| **Q1** | Used to understand single-stage and multi-stage Dockerfile syntax, including `COPY --from=builder`, `WORKDIR`, and `CMD`, and to troubleshoot Docker build and dependency issues. |
| **Q2** | Used to understand Docker Compose syntax, service-name-based networking, Redis integration, and caching logic, and to troubleshoot Compose and Redis-related issues. |
| **Q3** | Used to understand Kubernetes Job configuration, including `completions`, `parallelism`, `completionMode: Indexed`, and the Downward API. Also used for troubleshooting the shard validator, Job manifest, and Kubernetes commands. |
| **Q4** | Used to understand Kubernetes Deployment and Service configuration, including `readinessProbe`, resource requests/limits, and label selectors. Also used to understand and troubleshoot rolling-update commands such as `kubectl set image`, `rollout status`, and `rollout history`. |

### Overall Impact

AI assistance was mainly used as a **learning, syntax-reference, and troubleshooting tool** rather than for making the core infrastructure design decisions.

The **Q3 parallelism and CPU configuration, Q4 resource and readiness-probe configuration, interpretation of the terminal evidence, experimental execution, and final results were determined and verified manually**. The Docker builds, Docker Compose services, Kubernetes resources, and tests were run in the student's own development environment.

All final code, configurations, evidence, experimental results, and explanations were reviewed and adapted to match the actual implementation and observed behavior.