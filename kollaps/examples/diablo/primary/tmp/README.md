# Primary container runtime assets

This directory contains helper files copied into the Lilith primary container under `/tmp` during the Docker image build.

Despite the directory name, tracked files here are not ordinary local temporary files. They are runtime helper assets used by the Lilith/Kollaps/Diablo integration.

Tracked files currently include:

- `export.sh`
- `out.py`
- `latencies.sh`
- `start_measurements.sh`
- `kollaps-p2p-latencies.py`

Workload definitions do not belong here. They are stored in:

`kollaps/examples/diablo/primary/fixes/`

Generated local files must not be committed. In particular:

- `id_ed25519`
- `aws.csv`
- `run.tmp`
- `*.tmp`
- `*.log`

These generated files are ignored by the repository `.gitignore`.
