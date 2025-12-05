# Railway Deployment Configuration

## Required Environment Variables

The following environment variables must be configured in Railway's service settings:

### Database Configuration
- **`DATABASE_URL`** (Required)
  - Supabase PostgreSQL connection string
  - Format: `postgresql://user:password@host:port/database`
  - Use Transaction Pooler (port 6543) for production
  - Example: `postgresql://postgres.xxx:password@aws-0-region.pooler.supabase.com:6543/postgres`

### QStash Configuration (for Worker service)
- **`QSTASH_URL`** (Required)
  - Upstash QStash API endpoint
  - Example: `https://qstash.upstash.io/v2/publish`

- **`QSTASH_TOKEN`** (Required)
  - Upstash QStash authentication token
  - Get from: https://console.upstash.com/qstash

### Optional Configuration
- **`PORT`** (Optional, defaults to 8080)
  - Port number for the service
  - Railway automatically sets this

## Setting Environment Variables in Railway

1. Go to your Railway project dashboard
2. Select the "web" service
3. Click on the "Variables" tab
4. Add each environment variable with its value
5. Click "Deploy" to apply changes

## Local Development

For local development, copy these variables to your `.env` file:

```bash
DATABASE_URL=postgresql://postgres:password@localhost:5432/tubewiki
QSTASH_URL=https://qstash.upstash.io/v2/publish
QSTASH_TOKEN=your_qstash_token_here
```

## Verification

After setting environment variables, the deployment should succeed. Check the logs for:

```
Starting worker service on port 8080
```

If you see errors about missing environment variables, verify they are correctly set in Railway's Variables tab.
