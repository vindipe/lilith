# Repository layout

This document explains which files are source assets, which files are generated at runtime, and which files are local-only.

## Top-level scripts

- `run.sh`: main experiment orchestrator.
- `multi-run.sh`: batch runner for multiple experiment configurations.
- `smart-handler.sh`: optional remote handler launcher, typically used with detached `tmux` sessions.
- `scripts/requirements.sh`: manual/local setup helper. Runtime executions use a lightweight mode and should not perform package installation.

## Machine inventory

- `machines.example.txt`: versioned template.
- `machines.txt`: local inventory file, ignored by Git.

`machines.txt` contains one active SSH target per line. Empty lines and comments are ignored.

Local smoke-test mode should use:

`localhost`

Full benchmark campaigns should use real cloud or cluster SSH targets.

## Kollaps runtime tree

- `kollaps/build-kollaps.sh`: remote-side build/deploy helper used by `run.sh`.
- `kollaps/examples/`: Lilith-specific Kollaps/Diablo integration assets.
- `kollaps/Kollaps/`: generated local clone of the upstream Kollaps source tree. It is created by `scripts/requirements.sh` and is ignored.

## Diablo primary container

The primary container assets are under:

`kollaps/examples/diablo/primary/`

Important files:

- `Dockerfile`: primary container image.
- `minion.sh`: benchmark runtime bootstrap script.
- `init-minion.sh`: initialization helper.
- `fixes/`: static fixes, installer scripts, blockchain workers, and workload definitions.
- `tmp/`: runtime helper assets copied into the container under `/tmp`.

## `fixes/`

The `fixes/` directory contains static assets consumed by the primary container and Minion/Diablo.

It includes:

- installer scripts;
- blockchain-specific runtime scripts;
- workload YAML definitions;
- static integration patches.

The file `kollaps/examples/diablo/primary/fixes/lilith` is generated at runtime from:

`misc/lilith/lilith-<implementation>`

and must not be committed.

## `tmp/`

The `tmp/` directory contains tracked runtime helper assets, not ordinary temporary files.

Tracked files include:

- `export.sh`
- `out.py`
- `latencies.sh`
- `start_measurements.sh`
- `kollaps-p2p-latencies.py`

Generated files must not be committed:

- `id_ed25519`
- `aws.csv`
- `run.tmp`
- `*.tmp`
- `*.log`

Workload YAML files belong in `fixes/`, not in `tmp/`.

## Datasets and large files

- `misc/cloudping/ping.csv`: cloud latency dataset required by topology generation.
- `misc/*-aws.csv`: workload/region input datasets.
- `misc/lilith/lilith-*`: blockchain-specific Lilith workers.

`ping.csv` is large and should be managed through Git LFS.

## Generated outputs

These paths are generated during setup or runtime and are ignored:

- `kollaps/Kollaps/`
- `kollaps/examples/topology.xml`
- `kollaps/examples/topology.yaml`
- `kollaps/examples/arguments.txt`
- `misc/logs/`
- `results/`
- `temp/`
- Python `__pycache__/` directories
- container SSH keys generated for the runtime image

## Recommended development checks

Use validate-only mode after structural changes:

`LILITH_EXECUTION_PROFILE=local ./run.sh --validate-only --implementation poa --secondaries 1 --dataset diablo --mode full-mesh --size 1 --link hop --check 0 --dynamic 0 --switch 0 --latency 0`

This checks repository structure and selected inputs without building images, deploying services, or launching workloads.
