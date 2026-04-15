<div align="center">

# Lean 4 CI on Morph Cloud

A minimal, reusable CI template for running Lean 4 proofs on Morph Cloud's Infinibranch with intelligent caching and sharding.

</div>

---

## Quickstart

1. **Fork the Repository**: Click the 'Fork' button at the top-right of this page.

2. **Set Up Morph API Key**:
   - Navigate to your forked repository's settings.
   - Under 'Secrets and variables' > 'Actions', add a new repository secret named `MORPH_API_KEY` with your Morph Cloud API key.

3. **Trigger the Workflow**:
   - Go to the 'Actions' tab in your repository.
   - Select the 'lean-ci' workflow.
   - Click 'Run workflow' to start the CI process.

## Architecture

- **Base Snapshot**: Pre-built with Lean 4, Pantograph, and warmed mathlib cache
- **Sharding**: Configurable matrix of shards (default: 4) for parallel execution
- **Caching**: Mathlib and tactic states cached in snapshots for instant repro
- **Failure Handling**: Failing shards create snapshots for instant debugging

## Performance Targets

- **Cold Start**: ≤ p95 60s across 4 shards
- **Warm Cache**: ≤ p95 20s across 4 shards

## Repository Structure

```
/scripts
  build_snapshot.py    # Creates/refreshes base snapshot
  run_shard.py         # Runs tests on each shard
/examples/hello-lean   # Minimal Lean project with proofs
  lakefile.lean
  Main.lean
.github/workflows/lean-ci.yml  # GitHub Actions workflow
README.md
```

## Usage

The pipeline automatically:
1. Builds a cached Lean snapshot with mathlib
2. Fans out to N configurable shards
3. Runs `lake build` and `lake test` on each shard
4. Uploads logs and artifacts
5. Preserves failing shard snapshots for instant repro

## Debugging Failures

When a shard fails, the logs will contain a snapshot ID. You can instantly repro the failure:

```bash
morphcloud instance start <snapshot-id>
morphcloud instance ssh <instance-id>
```

## Configuration

Modify `.github/workflows/lean-ci.yml` to adjust:
- Number of shards (default: 4)
- Resource allocation (vcpus, memory, disk)
- Timeout settings
- Matrix strategy
