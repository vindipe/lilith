# Primary container runtime assets

This directory contains runtime assets that are copied into the Lilith primary
container during the Docker image build.

Despite the directory name, these files are not ordinary local temporary files.
They are part of the current Lilith/Kollaps/Diablo integration contract.

Tracked files in this directory include helper scripts and workload definitions
used inside the primary container, for example:

- `export.sh`
- `out.py`
- `latencies.sh`
- `start_measurements.sh`
- `kollaps-p2p-latencies.py`
- `workload-dota.yaml`

Generated local files should not be committed. In particular:

- `id_ed25519`
- `aws.csv`
- `run.tmp`
- `*.tmp`
- `*.log`

These generated files are ignored by the repository `.gitignore`.
