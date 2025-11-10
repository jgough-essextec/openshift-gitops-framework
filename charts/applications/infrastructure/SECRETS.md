# Paperless Infisical Secrets Configuration

This document describes the Infisical secrets required for the Paperless services.

## Required Secrets

Add these secrets to your Infisical project:

### 1. PAPERLESS_SECRET_KEY

**Description:** Django secret key for Paperless-NGX and Paperless-AI
**Used by:** paperless-ngx, paperless-ai
**Format:** Random string (50+ characters recommended)
**Example:** `django-insecure-xyz123abc456def789ghi012jkl345mno678pqr901stu234vwx567yz`

**How to generate:**

```bash
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Or use OpenSSL:

```bash
openssl rand -base64 50
```

### 2. PAPERLESS_ADMIN_PASSWORD

**Description:** Admin user password for Paperless-NGX and Paperless-AI
**Used by:** paperless-ngx, paperless-ai
**Format:** Secure password string
**Example:** `MySecure!Password123`

**Note:** This is used to automatically create the admin user on first deployment. The username will be `admin` and email will be your cluster admin email.

### 3. OPENAI_API_KEY

**Description:** OpenAI API key for GPT-powered document processing
**Used by:** paperless-gpt
**Format:** OpenAI API key (starts with `sk-`)
**Example:** `sk-proj-abcdefghijklmnopqrstuvwxyz1234567890`

**How to get:**

1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key (it will only be shown once)

## Setting Up Secrets in Infisical

### Via Web UI:

1. Log in to your Infisical instance
2. Navigate to your project
3. Go to the appropriate environment (e.g., `test`, `sno`)
4. Click "Add Secret"
5. Add each of the secrets above with their respective values

### Via CLI:

```bash
# Install Infisical CLI if not already installed
# https://infisical.com/docs/cli/overview

# Authenticate
infisical login

# Set secrets (replace <value> with actual values)
infisical secrets set PAPERLESS_SECRET_KEY="<django-secret-key>" --env=test
infisical secrets set PAPERLESS_ADMIN_PASSWORD="<secure-password>" --env=test
infisical secrets set OPENAI_API_KEY="<your-openai-key>" --env=test
```

## Secret Usage Matrix

| Service       | PAPERLESS_SECRET_KEY | PAPERLESS_ADMIN_PASSWORD | OPENAI_API_KEY |
| ------------- | -------------------- | ------------------------ | -------------- |
| paperless-ngx | ✅                   | ✅                       | ❌             |
| paperless-ai  | ✅                   | ✅                       | ❌             |
| paperless-gpt | ❌                   | ❌                       | ✅             |
| glue-worker   | ❌                   | ❌                       | ❌             |

## Verification

After adding secrets to Infisical, verify External Secrets are syncing:

```bash
# Check ExternalSecret status
oc get externalsecret -n paperless-ngx
oc get externalsecret -n paperless-ai
oc get externalsecret -n paperless-gpt

# Verify secrets were created
oc get secret -n paperless-ngx paperless-ngx-secret
oc get secret -n paperless-ai paperless-ai-secret
oc get secret -n paperless-gpt paperless-gpt-secret

# Check secret contents (base64 encoded)
oc get secret -n paperless-ngx paperless-ngx-secret -o jsonpath='{.data}'
```

## Troubleshooting

### ExternalSecret not syncing

Check the ExternalSecret events:

```bash
oc describe externalsecret -n paperless-ngx paperless-ngx
```

Check ClusterSecretStore status:

```bash
oc get clustersecretstore external-secrets -o yaml
```

### Admin user not created

If the admin user isn't automatically created:

1. Check that `PAPERLESS_ADMIN_PASSWORD` secret exists
2. Verify the secret is properly mounted in the deployment
3. Delete the pod to force recreation:
   ```bash
   oc delete pod -n paperless-ngx -l app=paperless-ngx
   ```

### OpenAI API key not working

Verify the key in paperless-gpt:

```bash
oc exec -n paperless-gpt deployment/paperless-gpt -- env | grep OPENAI
```

Check paperless-gpt logs:

```bash
oc logs -n paperless-gpt -l app=paperless-gpt --tail=50
```

## Security Best Practices

1. **Rotate secrets regularly** - Update secrets in Infisical and restart pods
2. **Use strong passwords** - Minimum 16 characters with mixed case, numbers, and symbols
3. **Limit API key permissions** - Create OpenAI keys with minimum required permissions
4. **Monitor usage** - Check OpenAI usage dashboard to detect anomalies
5. **Backup secrets** - Keep encrypted backups of critical secrets

## Related Documentation

- [External Secrets Operator](../../security/external-secrets-operator/)
- [Infisical Documentation](https://infisical.com/docs)
- [Paperless-NGX Documentation](https://docs.paperless-ngx.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
