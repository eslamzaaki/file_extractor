# Deploying to Vercel

This Express.js server is configured to deploy easily to Vercel.

## Quick Deploy

### Option 1: Vercel CLI (Recommended)

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel
```

3. For production:
```bash
vercel --prod
```

### Option 2: GitHub Integration

1. Push your code to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Import your repository
4. Vercel will automatically detect the configuration and deploy

## Configuration

The project includes:
- `vercel.json` - Vercel configuration
- `api/index.ts` - Serverless function entry point
- `server.ts` - Express app (automatically detected)

## Important Notes

### Build Settings

Vercel will automatically:
- Detect TypeScript files
- Build using `@vercel/node`
- Set up serverless functions

### Environment Variables

If you need environment variables:
1. Go to your Vercel project settings
2. Add variables in the "Environment Variables" section
3. Redeploy

### Function Configuration

- **Max Duration**: 30 seconds (configured in `vercel.json`)
- **Memory**: 1024 MB (for PDF processing)
- **Runtime**: Node.js (automatic)

## Testing After Deployment

Once deployed, test your endpoints:

```bash
# Health check
curl https://your-app.vercel.app/health

# Extract file
curl -X POST https://your-app.vercel.app/api/extract \
  -H "Content-Type: application/json" \
  -d '{"fileUrl": "https://example.com/file.pdf"}'
```

## Troubleshooting

### Build Errors

If you encounter build errors:
1. Check that all dependencies are in `package.json`
2. Ensure TypeScript compiles locally (`npm run build`)
3. Check Vercel build logs for specific errors

### Runtime Errors

- Check function logs in Vercel dashboard
- Verify all imports are correct
- Ensure `pdf-parse` is properly configured (it should work on Vercel)

### Timeout Issues

If requests timeout:
- Increase `maxDuration` in `vercel.json`
- Optimize file processing logic
- Consider using Vercel Pro for longer timeouts

## Local Development

The server works normally in local development:

```bash
npm run dev
```

The `app.listen()` only runs locally, not on Vercel (handled automatically).
