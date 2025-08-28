# Deployment Guide for Lean 4 CI on Morph Cloud

This guide walks you through deploying the Lean 4 CI pipeline on your own repository.

## Prerequisites

1. **Morph Cloud Account**: Sign up at [cloud.morph.so](https://cloud.morph.so)
2. **GitHub Repository**: Fork or clone this repository
3. **Python 3.11+**: For local testing and development

## Step 1: Fork the Repository

1. Click the "Fork" button at the top-right of this repository
2. Clone your forked repository locally:
   ```bash
   git clone https://github.com/SentinelOps-CI/morph-lean-ci
   cd morph-lean-ci
   ```

## Step 2: Set Up Morph Cloud API Key

1. Go to [cloud.morph.so](https://cloud.morph.so) and sign in
2. Navigate to your account settings
3. Generate an API key
4. Copy the API key

## Step 3: Configure GitHub Secrets

1. Go to your forked repository on GitHub
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `MORPH_API_KEY`
5. Value: Paste your Morph Cloud API key
6. Click "Add secret"

## Step 4: Test Local Setup (Optional)

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set your API key:
   ```bash
   export MORPH_API_KEY="your_api_key_here"
   ```

3. Test the setup:
   ```bash
   python scripts/test_setup.py
   ```

## Step 5: Trigger the CI Pipeline

1. Go to the "Actions" tab in your repository
2. Select the "Lean 4 CI on Morph Cloud" workflow
3. Click "Run workflow"
4. Choose the number of shards (4 or 8)
5. Click "Run workflow"

## Step 6: Monitor and Debug

### Viewing Results
- Check the Actions tab for workflow progress
- Download artifacts to see logs and test results
- View the summary for performance metrics

### Debugging Failures
When a shard fails, the logs will contain a snapshot ID. You can debug it:

```bash
# Start an instance from the failure snapshot
morphcloud instance start <snapshot-id>

# SSH into the instance
morphcloud instance ssh <instance-id>

# Investigate the failure
cd repo
lake build
lake test
```

## Configuration Options

### Modifying Shard Count
Edit `.github/workflows/lean-ci.yml`:
```yaml
matrix:
  shard: ${{ fromJson(format('[0,1,2,3,4,5,6,7]')) }}
  shards: ${{ fromJson(format('[{0}]', github.event.inputs.shards || '4')) }}
```

### Resource Allocation
Modify `scripts/build_snapshot.py`:
```python
base_snapshot = client.snapshots.create(
    image_id="morphvm-minimal",
    vcpus=4,        # Adjust CPU cores
    memory=8192,    # Adjust memory (MB)
    disk_size=32768 # Adjust disk size (MB)
)
```

### Timeout Settings
Modify `scripts/run_shard.py`:
```python
instance = client.instances.start(
    snapshot_id=snapshot_id,
    name=f"lean-ci-shard-{args.shard}",
    ttl=3600  # Adjust TTL (seconds)
)
```

## Performance Optimization

### Caching Strategy
- The base snapshot includes pre-warmed mathlib cache
- Each shard runs from the same cached snapshot
- Failed shards create new snapshots for instant repro

### Scaling Considerations
- Start with 4 shards for testing
- Scale to 8 shards for larger projects
- Monitor Morph Cloud usage and costs

## Troubleshooting

### Common Issues

1. **API Key Error**
   - Verify `MORPH_API_KEY` is set in GitHub secrets
   - Check API key permissions in Morph Cloud

2. **Snapshot Creation Fails**
   - Verify Morph Cloud account has sufficient credits
   - Check image availability (`morphvm-minimal`)

3. **Lean Installation Fails**
   - Check network connectivity in Morph Cloud
   - Verify Lean 4 setup script is accessible

4. **Test Failures**
   - Check Lean syntax in your examples
   - Verify mathlib dependencies are correct

### Getting Help

- Check Morph Cloud documentation: [docs.morph.so](https://docs.morph.so)
- Review Morph Python SDK: [github.com/morph-labs/morph-python-sdk](https://github.com/morph-labs/morph-python-sdk)
- Open issues in this repository for CI-specific problems

## Next Steps

1. **Customize Examples**: Replace `examples/hello-lean` with your own Lean project
2. **Add Tests**: Create more comprehensive test suites
3. **Optimize Caching**: Add more sophisticated caching strategies
4. **Monitor Performance**: Track build times and optimize resource allocation

## Support

For issues with:
- **Morph Cloud**: Contact support@morph.so
- **Lean 4**: Check [leanprover-community.github.io](https://leanprover-community.github.io)
- **CI Pipeline**: Open an issue in this repository
