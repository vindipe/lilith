# Lilith execution modes

Lilith is a topology-aware blockchain benchmarking tool originally designed to run on multi-machine cloud or cluster environments.

The repository also supports a local smoke-test mode. This mode is useful for validating repository structure, Docker build paths, runtime file generation, SSH orchestration, and Docker Swarm initialization on a single machine.

Local smoke-test mode is not intended to produce scientifically meaningful benchmark results.

## 1. Cluster or cloud mode

This is the intended mode for full experiments.

In this mode, `machines.txt` contains one SSH target per machine.

Examples:

- `ubuntu@10.0.0.10`
- `user@node-1.example.com`
- `eiger-1.maas`
- `cluster-node-01`

Requirements:

- each machine must be reachable through SSH;
- the benchmark user must be able to run non-interactive sudo;
- Docker must be available or installable;
- Docker Swarm must be supported;
- the kernel/network stack must support Kollaps requirements;
- the machines must provide enough CPU, RAM, disk, and network resources for the selected workload.

Lilith checks non-interactive sudo during the remote preflight phase.

If a machine requires an interactive sudo password, Lilith fails early instead of blocking during a detached run.

## 2. Local smoke-test mode

Local mode is intended for development and repository validation.

It is activated with:

`LILITH_EXECUTION_PROFILE=local`

In this mode, `machines.txt` should contain:

`localhost`

Local mode changes the runtime behavior:

- Docker is executed without sudo;
- Docker Desktop / WSL credential issues are avoided through an isolated Docker config;
- host package installation is skipped during runtime;
- Docker stack deploy is skipped by default;
- dashboard-triggered benchmark execution is disabled by default;
- post-processing scripts skip cleanly when no primary results exist.

Example:

`LILITH_EXECUTION_PROFILE=local ./run.sh --implementation poa --secondaries 1 --dataset diablo --mode full-mesh --size 1 --link hop --check 0 --dynamic 0 --switch 0 --latency 0`

Expected local smoke-test behavior:

- runtime preparation succeeds;
- SSH localhost preflight succeeds;
- Docker Swarm manager initialization succeeds;
- Docker/Kollaps build and generation steps are exercised;
- execution stops before the heavy deploy/benchmark phase;
- exit code is 0.

## 3. Forcing local deploy

Full local deploy can be forced with:

`LILITH_ALLOW_LOCAL_DEPLOY=1`

This is not recommended on WSL2 or low-resource machines.

A full local deploy may consume large amounts of CPU, RAM, disk, and Docker resources. It may also fail because Kollaps relies on kernel/network functionality that may not be fully available in WSL2 or Docker Desktop environments.

Use this only for debugging specific deployment issues.

## Validate-only mode

Use `--validate-only` to check the repository layout and selected run configuration without building Docker images, deploying Docker Swarm services, or launching a benchmark.

Example:

`LILITH_EXECUTION_PROFILE=local ./run.sh --validate-only --implementation poa --secondaries 1 --dataset diablo --mode full-mesh --size 1 --link hop --check 0 --dynamic 0 --switch 0 --latency 0`

Validate-only mode checks:

- active machines from `machines.txt`;
- local profile consistency when `LILITH_EXECUTION_PROFILE=local`;
- blockchain-specific Lilith worker under `misc/lilith/`;
- selected dataset under `misc/`;
- `misc/cloudping/ping.csv`;
- workload YAML files under `kollaps/examples/diablo/primary/fixes/`;
- primary runtime helper directory under `kollaps/examples/diablo/primary/tmp/`.

This mode should be the first check when editing the repository or preparing a new environment.

## Recommended workflow

For development:

1. use local smoke-test mode;
2. verify that generated files and Docker build paths are correct;
3. avoid full benchmark execution locally;
4. run complete experiments only on a suitable cloud or cluster environment.

For real experiments:

1. prepare `machines.txt` with real SSH targets;
2. run `./scripts/requirements.sh` manually before the benchmark campaign;
3. ensure non-interactive sudo works on every machine;
4. launch experiments through `run.sh`, `multi-run.sh`, or `smart-handler.sh`.
