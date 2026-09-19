# AI Ops --- Assignment 2

**Name:** Sri Harsha V\
**Roll No:** DA24B034

This repository contains the implementation, configuration files,
evidence, and supporting files for AI Ops Module 3 Assignment 2.

The assignment covers:

-   Single-stage and multi-stage Docker builds
-   Redis caching using Docker Compose
-   Kubernetes Indexed Jobs for parallel data validation
-   Kubernetes Deployments, Services, self-healing, and rolling updates

------------------------------------------------------------------------

## Repository Structure

``` text
DA3408_DA24B034_2/
├── README.md
├── AI_DISCLOSURE.md
├── report.pdf
│
├── app/
│   ├── app.py
│   ├── generate_data.py
│   ├── model.joblib
│   ├── requirements.txt
│   ├── spam_dataset.csv
│   └── train.py
│
├── Q1/
│   ├── Dockerfile.multistage
│   ├── Dockerfile.naive
│   └── evidence/
│       ├── 01_naive_build_and_size.png
│       ├── 02_multistage_size_run_and_base_images.png
│       ├── 03_multistage_build.png
│       └── 04_naive_run_and_predict.png
│
├── Q2/
│   ├── app_with_cache.py
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── evidence/
│   │   └── 01_compose_build_and_cache_timing.png
│   └── requirements-cache.txt
│
├── Q3/
│   ├── collect_results.py
│   ├── Dockerfile
│   ├── evidence/
│   │   ├── 01_cluster_cpu_setup.png
│   │   ├── 02_job_execution_start.png
│   │   ├── 03_job_execution_progress.png
│   │   ├── 04_job_execution_completion.png
│   │   ├── 05_results_collection.png
│   │   └── 06_final_pods_and_resources.png
│   ├── generate_shards.py
│   ├── job.yaml
│   ├── shard_results.json
│   ├── shards/
│   │   ├── shard_0.csv
│   │   ├── shard_1.csv
│   │   ├── shard_2.csv
│   │   ├── shard_3.csv
│   │   ├── shard_4.csv
│   │   ├── shard_5.csv
│   │   ├── shard_6.csv
│   │   └── shard_7.csv
│   └── shard_validator.py
│
└── Q4/
    ├── app.py
    ├── deployment.yaml
    ├── Dockerfile
    ├── evidence/
    │   ├── 01_deployment_service_self_healing.png
    │   ├── 02_build_v1.png
    │   ├── 03_build_v2_update.png
    │   ├── 04_rollout_and_api_v2.png
    │   └── 05_replicaset_and_history.png
    └── service.yaml
```

  -----------------------------------------------------------------------
  Question                Directory               Contents
  ----------------------- ----------------------- -----------------------
  **Q1** --- Single-Stage `Q1/`                   Dockerfiles,
  vs. Multi-Stage Docker                          application files,
                                                  image-size comparison,
                                                  and evidence

  **Q2** --- Redis Cache  `Q2/`                   Cached API, Compose
  with Docker Compose                             configuration, Redis
                                                  setup, and cache timing
                                                  evidence

  **Q3** --- Kubernetes   `Q3/`                   Shard generator,
  Indexed Job                                     validator, Indexed Job,
                                                  result collection,
                                                  shards, and evidence

  **Q4** --- Kubernetes   `Q4/`                   Deployment, Service,
  Deployment                                      self-healing, rolling
                                                  update, and evidence
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## Prerequisites

The following tools are required:

-   Docker
-   Docker Compose
-   Minikube
-   kubectl
-   Python 3
-   Python virtual environment

Create and activate the Python virtual environment from the repository
root:

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

------------------------------------------------------------------------

# Question 1 --- Single-Stage vs. Multi-Stage Docker

**Directory:** `Q1/`

Q1 compares a naive single-stage Docker image with a multi-stage Docker
image for the spam-detection API.

### Build the Naive Image

``` bash
docker build -t spam-api-naive -f Q1/Dockerfile.naive app/
```

Check the image:

``` bash
docker images spam-api-naive
```

### Run the Naive Image

``` bash
docker run --rm -p 8000:8000 spam-api-naive
```

In another terminal:

``` bash
curl http://localhost:8000/healthz
```

Test the prediction endpoint:

``` bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text":"WIN a FREE iPhone now!"}'
```

### Build the Multi-Stage Image

``` bash
docker build -t spam-api-multistage -f Q1/Dockerfile.multistage app/
```

Check the image:

``` bash
docker images spam-api-multistage
```

Run the multi-stage image:

``` bash
docker run --rm -p 8000:8000 spam-api-multistage
```

The same `/healthz` and `/predict` endpoints can be used to verify the
application.

### Evidence

Q1 evidence is available in:

``` text
Q1/evidence/
```

The screenshots contain the Docker build, image-size measurements,
runtime verification, and prediction testing. The naive image
measured 515MB, the multi-stage image measured 154MB --- a 70.1%
reduction.

------------------------------------------------------------------------

# Question 2 --- Redis Cache with Docker Compose

**Directory:** `Q2/`

Q2 extends the spam-detection API with Redis caching. This uses a
separate `app_with_cache.py`, isolated from `app/app.py`, so that
Q1 and Q4 continue to build from the original, cache-free API.

The Compose application consists of:

-   `api` --- FastAPI spam-detection service (built from `Q2/Dockerfile`)
-   `cache` --- Redis 7 Alpine

The API connects to Redis using the Compose service name `cache`.

### Start the Compose Application

From the repository root:

``` bash
docker compose -f Q2/docker-compose.yml up --build
```

The API is available at:

``` text
http://localhost:8000
```

Check the API:

``` bash
curl http://localhost:8000/healthz
```

Test the prediction endpoint:

``` bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text":"WIN a FREE iPhone now!"}'
```

Send the same request again to observe the cached response.

### Stop the Compose Application

``` bash
docker compose -f Q2/docker-compose.yml down
```

### Evidence

Q2 evidence is available in:

``` text
Q2/evidence/
```

The evidence contains the Compose build and measured cache timing
(cache miss vs. cache hit).

------------------------------------------------------------------------

# Question 3 --- Kubernetes Indexed Job

**Directory:** `Q3/`

Q3 validates eight CSV shards using a Kubernetes Indexed Job.

The Job uses:

-   `completions: 8`
-   `parallelism: 8`
-   `completionMode: Indexed`
-   CPU request and limit of `500m` per validation Pod
-   Two-node Minikube cluster (2 allocatable CPUs per node)

Each Indexed Job completion processes one CSV shard using the
`JOB_COMPLETION_INDEX`.

## Start the Minikube Cluster

The demonstrated setup uses:

``` bash
minikube start \
  --driver=docker \
  --nodes=2 \
  --cpus=2 \
  --memory=4096 \
  --container-runtime=docker \
  --extra-config=kubelet.kube-reserved=cpu=10
```

The `kubelet.kube-reserved=cpu=10` flag reserves 10 of the 12 CPUs
that `kubelet` detects on this development machine, leaving exactly
2 allocatable CPUs per node --- matching the assignment's stated
4-CPU-total assumption. See `report.pdf` (Question 3) for the full
investigation of why this was necessary.

The Docker-level CPU limits used in the demonstrated environment
(applied in addition to the flag above) are:

``` bash
docker update --cpus=2 minikube
docker update --cpus=2 minikube-m02
```

Check the node resources:

``` bash
kubectl get nodes \
  -o custom-columns=NAME:.metadata.name,CAPACITY:.status.capacity.cpu,ALLOCATABLE:.status.allocatable.cpu
```

Expected output: `CAPACITY: 12`, `ALLOCATABLE: 2` on both nodes.

## Build the Validator Image

``` bash
cd Q3
docker build -t shard-validator:latest .
```

## Load the Image into Minikube

``` bash
minikube image load shard-validator:latest
```

Verify the image on both nodes:

``` bash
minikube ssh --node minikube docker images | grep shard-validator
minikube ssh --node minikube-m02 docker images | grep shard-validator
```

## Run the Indexed Job

Remove a previous Job if necessary:

``` bash
kubectl delete job shard-validation-job --ignore-not-found
```

Apply the Job:

``` bash
kubectl apply -f job.yaml
```

Watch the Pods:

``` bash
kubectl get pods -l job-name=shard-validation-job -o wide -w
```

After the Pods have completed, press `Ctrl+C`.

Check the final state:

``` bash
kubectl get pods -l job-name=shard-validation-job -o wide
```

## Collect Results

From the `Q3` directory:

``` bash
python3 collect_results.py
```

The result-collection script uses the Kubernetes Python API to find the
Job Pods, read their logs, extract the `RESULT_JSON` results, and
combine the results from all eight shards. Results are collected via
the Kubernetes API rather than a shared volume, since minikube's
default storage provisioner binds a `PersistentVolume` to a single
node, and pods in this cluster may land on either node.

The complete results are saved to:

``` text
Q3/shard_results.json
```

The validation run processes 50 rows from each of the eight shards and
identifies 47 invalid rows in total.

### Evidence

Q3 evidence is available in:

``` text
Q3/evidence/
```

The evidence includes:

-   Cluster CPU configuration
-   Indexed Job execution
-   Pod scheduling across the two nodes
-   Pod completion
-   Result collection
-   Final Pod/resource state

------------------------------------------------------------------------

# Question 4 --- Kubernetes Deployment and Service

**Directory:** `Q4/`

Q4 deploys the spam-detection API using a Kubernetes Deployment with two
replicas and exposes it using a Kubernetes Service. `Q4/app.py` is a
copy of `app/app.py`, used to build the `v1` image; it is later
modified in place (adding a `version` field to `/healthz`) to build
the `v2` image for the rolling-update demonstration.

The Deployment also includes a readiness probe on `/healthz`.

## Build and Load the v1 Image

`Q4/Dockerfile` was used to build the initial image, at a point when
`Q4/app.py` was a plain copy of `app/app.py` (no version field):

``` bash
docker build -t spam-api-multistage:v1 -f Q4/Dockerfile .
minikube image load spam-api-multistage:v1
```

Verify the image on both nodes:

``` bash
minikube ssh --node minikube docker images | grep spam-api
minikube ssh --node minikube-m02 docker images | grep spam-api
```

> **Note:** `Q4/app.py` as committed in this repository reflects its
> **final (v2)** state, since it was edited in place for the rolling
> update below rather than kept as a separate file. The `v1` image
> tag above was built and loaded *before* that edit was made, and is
> not affected by it. To reproduce the `v1` build from a fresh clone
> of this repository, first copy the original API file over it:
>
> ``` bash
> cp app/app.py Q4/app.py
> docker build -t spam-api-multistage:v1 -f Q4/Dockerfile .
> ```
>
> Then re-apply the one-line change shown below before building `v2`.

## Apply the Deployment

``` bash
kubectl apply -f Q4/deployment.yaml
```

Apply the Service:

``` bash
kubectl apply -f Q4/service.yaml
```

Check the Deployment:

``` bash
kubectl get deployment
```

Check the Pods:

``` bash
kubectl get pods -l app=spam-api
```

Check the Service:

``` bash
kubectl get service spam-api-service
```

Get a reachable URL for the Service:

``` bash
minikube service spam-api-service --url
```

## Self-Healing Demonstration

Check the running Pods:

``` bash
kubectl get pods -l app=spam-api
```

Delete one running Pod:

``` bash
kubectl delete pod <pod-name>
```

Observe the replacement:

``` bash
kubectl get pods -l app=spam-api
```

The Deployment manages a ReplicaSet, which maintains the desired number
of Pods. When one Pod is deleted, the ReplicaSet detects that the
desired replica count is no longer satisfied and creates a replacement
Pod. The surviving Pod is left untouched throughout.

## Rolling Update

The small, visible change made for this demonstration is in
`Q4/app.py`'s `/healthz` endpoint:

``` diff
  @app.get("/healthz")
  def healthz():
      if _model is None:
          return JSONResponse(status_code=503, content={"status": "loading"})
-     return {"status": "ok"}
+     return {"status": "ok", "version": "v2"}
```

`Q4/app.py` as committed already contains this change (see the note
above). Build and load the `v2` image directly:

``` bash
docker build -t spam-api-multistage:v2 -f Q4/Dockerfile .
minikube image load spam-api-multistage:v2
```

Update the Deployment:

``` bash
kubectl set image deployment/spam-api-deployment \
  spam-api=spam-api-multistage:v2
```

Check rollout progress:

``` bash
kubectl rollout status deployment/spam-api-deployment
```

Check rollout history:

``` bash
kubectl rollout history deployment/spam-api-deployment
```

The updated `/healthz` endpoint reports the new API version, while the
`/predict` endpoint continues to work correctly with no downtime
during the update.

### (Optional) Rollback

To demonstrate reverting to the previous revision:

``` bash
kubectl rollout undo deployment/spam-api-deployment
kubectl rollout status deployment/spam-api-deployment
```

Kubernetes retains previous ReplicaSets specifically to make this
possible without rebuilding any image.

### Evidence

Q4 evidence is available in:

``` text
Q4/evidence/
```

The screenshots demonstrate:

-   Deployment and Service setup
-   Pod self-healing after deletion
-   Building the v1 and v2 images
-   Rolling update
-   API version verification
-   ReplicaSet and rollout history

------------------------------------------------------------------------

# Evidence

All evidence screenshots are organized separately by question:

``` text
Q1/evidence/
Q2/evidence/
Q3/evidence/
Q4/evidence/
```

The evidence demonstrates the actual Docker builds and image sizes,
Redis cache timing, Kubernetes Indexed Job execution and results, and
Deployment self-healing and rolling-update behavior.

------------------------------------------------------------------------

