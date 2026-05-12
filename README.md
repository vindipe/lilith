# Lilith

Lilith is a topology-aware blockchain benchmarking tool developed during a PhD research project on blockchain performance, energy consumption, and experimental repeatability.

The tool integrates network topology generation, Kollaps-based network emulation, Diablo-based workload execution, and blockchain-specific runtime workers.

This repository is being cleaned and prepared for public release. The current version preserves the original experimental workflow while progressively improving safety, reproducibility, documentation, and repository structure.

## What Lilith does

Lilith helps run controlled blockchain benchmarking experiments where the network topology is part of the experimental configuration.

It can generate and deploy emulated network topologies, prepare Kollaps and Diablo runtime files, select blockchain-specific Lilith workers, execute workloads, collect results from containers, and export benchmark outputs.

Supported blockchain workers currently include:

- Algorand
- Diem
- Ethereum Clique / PoA
- Quorum IBFT
- Solana

Supported topology families include:

- full mesh
- scale-free
- torus
- fat-tree
- hypercube
- double-region variants

## Repository structure

Main files and directories:

- run.sh: main benchmark orchestration script
- multi-run.sh: helper script for running multiple benchmark configurations
- smart-handler.sh: helper script for synchronizing the repository to a remote handler and launching the workflow in tmux
- machines.example.txt: example cluster inventory file
- scripts/: topology generation, setup helpers, plotting, and analysis utilities
- misc/: input datasets, topology templates, and blockchain-specific Lilith workers
- kollaps/: Kollaps and Diablo integration files

Local files that are specific to a private cluster or runtime execution are intentionally ignored.

## Local cluster configuration

The repository does not version the local machines.txt file.

To configure a cluster, copy machines.example.txt to machines.txt and replace the example hosts with your SSH targets.

Each line in machines.txt should identify one machine that Lilith can reach through SSH.

## Setup

Install local dependencies with:

    ./scripts/requirements.sh

By default, this installs local dependencies, clones Kollaps when needed, creates runtime directories, and generates the container SSH key pair if missing.

SSH daemon tuning is optional and disabled by default. Use it only when you explicitly need it for your experimental environment:

    ./scripts/requirements.sh --with-ssh-server --tune-sshd

## Basic usage

A minimal run uses the default configuration:

    ./run.sh

Example with explicit options:

    ./run.sh --implementation poa --mode full-mesh --dataset diablo --size 1 --secondaries 10

A remote handler can be used with:

    ./smart-handler.sh --handler user@handler.example.com

The handler must already be reachable through SSH.

## Generated files

The following files are generated locally and are not versioned:

- machines.txt
- results/
- temp/
- misc/logs/
- kollaps/Kollaps/
- kollaps/examples/topology.xml
- kollaps/examples/diablo/primary/tmp/aws.csv
- kollaps/examples/diablo/primary/tmp/run.tmp
- kollaps/examples/diablo/primary/tmp/id_ed25519
- kollaps/examples/diablo/primary/fixes/lilith

The generated fixes/lilith file is created by run.sh from the blockchain-specific workers in misc/lilith/.

## Current release status

This repository is still being prepared for public release.

The original research workflow is preserved, but the repository is being cleaned to improve:

- safety of SSH and cleanup operations
- clarity of generated versus versioned files
- consistency of workload handling
- documentation quality
- reproducibility of setup steps

## Citation

Citation metadata will be added before the first public GitHub release.
