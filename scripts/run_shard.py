#!/usr/bin/env python3
"""
Run Lean 4 tests on a specific shard.

This script starts an instance from the prepared snapshot, clones the repository,
runs the specified shard of tests, and handles failures by creating snapshots.
"""

import argparse
import os
import sys
import time
from pathlib import Path
from morphcloud.api import MorphCloudClient


def read_snapshot_id():
    """Read the snapshot ID from the file created by build_snapshot.py."""
    try:
        with open("lean_snapshot_id.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("Error: lean_snapshot_id.txt not found. Run build_snapshot.py first.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Run Lean 4 tests on a shard")
    parser.add_argument("--shard", type=int, required=True, help="Shard index")
    parser.add_argument(
        "--shards", type=int, required=True, help="Total number of shards"
    )
    parser.add_argument("--repo", type=str, default=None, help="Repository URL to test")
    args = parser.parse_args()

    # Get Morph API key
    api_key = os.environ.get("MORPH_API_KEY")
    if not api_key:
        print("Error: MORPH_API_KEY environment variable not set")
        sys.exit(1)

    # Get snapshot ID
    snapshot_id = read_snapshot_id()

    # Initialize client
    client = MorphCloudClient(api_key=api_key)

    print(f"🚀 Starting instance for shard {args.shard}/{args.shards}")
    print(f"   Using snapshot: {snapshot_id}")

    # Start instance from snapshot
    instance = client.instances.start(
        snapshot_id=snapshot_id,
        name=f"lean-ci-shard-{args.shard}",
        ttl=3600,  # 1 hour TTL
    )

    print(f"⏳ Waiting for instance to be ready...")
    instance.wait_until_ready()

    print(f"✅ Instance ready: {instance.id}")

    # Determine repository to test
    repo_url = args.repo or os.environ.get("GITHUB_REPOSITORY_URL")
    if not repo_url:
        # Default to the current repository
        repo_url = f"https://github.com/{os.environ.get('GITHUB_REPOSITORY', 'SentinelOps-CI/morph-lean-ci')}.git"

    print(f"📥 Cloning repository: {repo_url}")

    # Clone and setup repository
    clone_cmd = f"git clone {repo_url} repo && cd repo"
    instance.exec(clone_cmd)

    # Run lake build
    print(f"🔨 Running lake build...")
    try:
        build_result = instance.exec("cd repo && lake build")
        print("✅ Build completed successfully")
    except Exception as e:
        print(f"❌ Build failed: {e}")
        # Create failure snapshot for debugging
        failure_snapshot = instance.snapshot(
            name=f"lean-ci-shard-{args.shard}-build-failure",
            metadata={
                "shard": args.shard,
                "total_shards": args.shards,
                "failure_type": "build",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            },
        )
        print(f"💾 Failure snapshot created: {failure_snapshot.id}")
        print(f"   Debug with: morphcloud instance start {failure_snapshot.id}")
        sys.exit(1)

    # Run tests for this shard
    print(f"🧪 Running tests for shard {args.shard}/{args.shards}")

    # Create a simple test script that runs tests for this shard
    test_script = f"""
    cd repo
    # Run tests and capture output
    lake test > test_output.log 2>&1
    test_exit_code=$?
    
    # Save test results
    echo "Test exit code: $test_exit_code" > shard_{args.shard}_results.txt
    echo "Shard: {args.shard}/{args.shards}" >> shard_{args.shard}_results.txt
    echo "Timestamp: $(date -u)" >> shard_{args.shard}_results.txt
    echo "--- Test Output ---" >> shard_{args.shard}_results.txt
    cat test_output.log >> shard_{args.shard}_results.txt
    
    exit $test_exit_code
    """

    try:
        test_result = instance.exec(test_script)
        print("✅ Tests completed successfully")
    except Exception as e:
        print(f"❌ Tests failed: {e}")
        # Create failure snapshot for debugging
        failure_snapshot = instance.snapshot(
            name=f"lean-ci-shard-{args.shard}-test-failure",
            metadata={
                "shard": args.shard,
                "total_shards": args.shards,
                "failure_type": "test",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            },
        )
        print(f"💾 Failure snapshot created: {failure_snapshot.id}")
        print(f"   Debug with: morphcloud instance start {failure_snapshot.id}")
        sys.exit(1)

    # Download test results
    print(f"📥 Downloading test results...")

    # Create output directory
    Path("out/logs").mkdir(parents=True, exist_ok=True)

    # Get test results
    results = instance.exec("cat repo/shard_{args.shard}_results.txt")
    with open(f"out/logs/{args.shard}.log", "w") as f:
        f.write(results)

    # Get test output log
    test_output = instance.exec("cat repo/test_output.log")
    with open(f"out/logs/{args.shard}_test_output.log", "w") as f:
        f.write(test_output)

    print(f"✅ Test results saved to out/logs/{args.shard}.log")
    print(f"✅ Test output saved to out/logs/{args.shard}_test_output.log")

    # Clean up instance
    print(f"🧹 Cleaning up instance...")
    instance.delete()

    print(f"🎉 Shard {args.shard} completed successfully!")


if __name__ == "__main__":
    main()
