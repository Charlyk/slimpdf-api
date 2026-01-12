# @slimpdf/client

TypeScript client SDK for the SlimPDF API. Works in both browser and Node.js (18+).

## Installation

```bash
npm install @slimpdf/client
```

## Quick Start

```typescript
import { SlimPdfClient } from '@slimpdf/client';

const client = new SlimPdfClient({
  baseUrl: 'https://api.slimpdf.io',
});

// Compress a PDF
const result = await client.compress.submitAndWait(file, { quality: 'high' });
const compressedPdf = await result.download();
```

## Features

- **Compress** - Reduce PDF file size with customizable quality
- **Merge** - Combine multiple PDFs into one
- **Image to PDF** - Convert images to PDF documents
- **Authentication** - Google OAuth and API key support
- **Billing** - Stripe integration for Pro subscriptions
- **API Keys** - Manage API keys for programmatic access (Pro)

## Usage

### Initialize Client

```typescript
import { SlimPdfClient } from '@slimpdf/client';

// Anonymous (free tier)
const client = new SlimPdfClient({
  baseUrl: 'https://api.slimpdf.io',
});

// With authentication
const client = new SlimPdfClient({
  baseUrl: 'https://api.slimpdf.io',
  accessToken: 'your-jwt-or-api-key',
});
```

### Compress PDF

```typescript
// Simple - submit and wait for completion
const result = await client.compress.submitAndWait(file, {
  quality: 'high', // 'low' | 'medium' | 'high' | 'maximum'
});
const blob = await result.download();

// Advanced - manual polling
const job = await client.compress.submit(file, { quality: 'medium' });
const status = await client.jobs.waitForCompletion(job.job_id, {
  onStatusChange: (status) => console.log('Status:', status.status),
});
const blob = await client.jobs.download(job.job_id);
```

### Merge PDFs

```typescript
const result = await client.merge.submitAndWait([pdf1, pdf2, pdf3]);
const mergedPdf = await result.download();
```

### Convert Images to PDF

```typescript
const result = await client.imageToPdf.submitAndWait(images, {
  pageSize: 'a4', // 'a4' | 'letter' | 'original'
});
const pdf = await result.download();
```

### Authentication

```typescript
// Login with Google
const auth = await client.auth.loginWithGoogle(googleIdToken);
client.setAccessToken(auth.access_token);

// Get current user info
const me = await client.auth.getCurrentUser();
console.log(me.user.plan); // 'free' or 'pro'
console.log(me.usage.compress.remaining); // remaining daily uses

// Verify token
const verified = await client.auth.verifyToken();
console.log(verified.authenticated);
```

### Billing (Pro)

```typescript
// Create checkout session
const checkout = await client.billing.createCheckout('month');
window.location.href = checkout.checkout_url;

// Manage subscription
const portal = await client.billing.createPortalSession();
window.location.href = portal.portal_url;
```

### API Keys (Pro)

```typescript
// List keys
const keys = await client.apiKeys.list();

// Create new key (key is shown only once!)
const newKey = await client.apiKeys.create('Production');
console.log(newKey.key); // sk_live_xxx...

// Revoke key
await client.apiKeys.revoke(keyId);
```

## Error Handling

```typescript
import {
  SlimPdfError,
  RateLimitError,
  FileSizeError,
  AuthenticationError,
  JobExpiredError,
} from '@slimpdf/client';

try {
  const result = await client.compress.submitAndWait(file);
} catch (error) {
  if (error instanceof RateLimitError) {
    console.log('Daily limit reached. Upgrade to Pro for unlimited access.');
  } else if (error instanceof FileSizeError) {
    console.log('File too large. Max size for free tier is 20MB.');
  } else if (error instanceof AuthenticationError) {
    console.log('Please log in to continue.');
  } else if (error instanceof JobExpiredError) {
    console.log('Download link expired. Please process the file again.');
  } else if (error instanceof SlimPdfError) {
    console.log(`API error: ${error.message}`);
  }
}
```

## Tier Limits

| Feature | Free | Pro |
|---------|------|-----|
| Compress rate | 2/day | Unlimited |
| Merge rate | 3/day | Unlimited |
| Image to PDF rate | 3/day | Unlimited |
| Max file size | 20MB | 100MB |
| Max merge files | 5 | 50 |
| Max images | 10 | 100 |
| Download expiry | 1 hour | 24 hours |

## TypeScript Support

All types are exported for TypeScript users:

```typescript
import type {
  CompressOptions,
  JobStatusResponse,
  User,
  CompressionQuality,
} from '@slimpdf/client';
```

## License

MIT
