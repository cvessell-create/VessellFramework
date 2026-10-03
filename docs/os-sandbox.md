# Offline Linux OS sandbox

On macOS, the dedicated Colima profile runs a Linux VM. Tests then run in a
non-root Docker container inside that VM. This is stronger separation than the
Python replay environment, but is not a guarantee against hypervisor/kernel
vulnerabilities. Do not execute unknown malware or active exploit payloads.

Approved initial resources: 2 VM CPUs, 4 GiB VM memory, 30 GiB VM disk.
Container limits: 2 CPUs, 3 GiB memory, 256 processes and 256 MiB temporary
filesystem. New public data have a 10 GB acquisition budget; do not fill it with
irrelevant records. Acquisition and image construction require network access;
evaluation is offline.

## Build a source-only image

Install Docker CLI and Colima, then start the dedicated profile:

```sh
colima start --profile vf-replay --cpu 2 --memory 4 --disk 30 --runtime docker
```

Do not change another project's default Docker context. Use the dedicated
socket explicitly; obtain its path from `colima status --profile vf-replay`.
Build only committed files so credentials, virtual environments, caches and
untracked build copies are never sent as build context:

```sh
git archive HEAD | docker --host unix:///absolute/path/to/vf-replay/docker.sock \
  build --file sandbox/Dockerfile --tag vf-replay:local -
```

Record the resulting image ID and base image digest. Dependencies are captured
inside the image at `/opt/dependencies.txt`. Rebuild after source changes.

## Run with frozen data

Create a separate host output directory. Use your host's nonzero UID/GID to
allow writing only that directory. Do not mount the repository, home directory,
credentials, Docker socket or package cache.

```sh
docker --host unix:///absolute/path/to/vf-replay/docker.sock run --rm \
  --network none --read-only --cap-drop ALL \
  --security-opt no-new-privileges --pids-limit 256 --memory 3g --cpus 2 \
  --user "$(id -u):$(id -g)" \
  --tmpfs /tmp:rw,nosuid,nodev,noexec,size=256m,mode=1777 \
  --mount type=bind,src=/absolute/path/to/public_evaluation_data,dst=/data,readonly \
  --mount type=bind,src=/absolute/path/to/data_audit/evaluation.json,dst=/catalog.json,readonly \
  --mount type=bind,src=/absolute/path/to/sandbox_expansion,dst=/expansion,readonly \
  --mount type=bind,src=/absolute/path/to/sandbox-results,dst=/outputs \
  vf-replay:local
```

The entry point refuses replay unless effective capabilities are zero,
privilege escalation is disabled, root/data/catalog are read-only, source
writes are rejected, only loopback networking exists, and no Docker socket is
mounted. It writes isolation checks, test results, manifest verification output
and paired replay reports. A failure is explicit, not converted to success.

Downloads are staged outside the container. Review official source terms,
record URLs/retrieval date/query/license and hashes, validate contents, and
freeze a new catalog before evaluation. Keep additional domains separate from
the original replay population. ATT&CK is technique knowledge, EPSS is a
probability snapshot, and synthetic/lab cases are not field-efficacy outcomes.
No package/image/data is downloaded by the offline entry point.

The initial expansion contains an immutable-commit MITRE Enterprise ATT&CK
bundle (with its upstream license) and a September 1, 2025 EPSS snapshot.
Separate checks expose duplicate IDs, revoked/deprecated techniques and
dangling relationship references, and validate EPSS vintage/CVE/probability
fields. Missing exploitation labels remain missing; the lab does not call
those vulnerabilities safe or report unmeasured mitigation success.

Stop only this profile when finished:

```sh
colima stop --profile vf-replay
```
