# SSL Certificate Setup for Homelab

This document outlines the process for setting up and renewing self-signed SSL certificates for the homelab services.

## Current Certificate Details

- **Domain**: `home.local`
- **Certificate Type**: Self-signed
- **Created**: May 15, 2024
- **Expires**: May 15, 2034 (10 years from creation)
- **Certificate Location**: `/Users/zach/src/homelab/certs/home.local.crt`
- **Key Location**: `/Users/zach/src/homelab/certs/home.local.key`

## Why Self-Signed?

Let's Encrypt cannot issue certificates for `.local` domains as they are reserved for local networks and not publicly accessible. This results in the error:

```
Cannot issue for "home.local": Domain name does not end with a valid public suffix (TLD)
```

## Certificate Renewal Process

When the certificate expires, follow these steps to create a new one:

### 1. Generate a New Self-Signed Certificate

```bash
cd /Users/zach/src/homelab
mkdir -p certs
openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
  -keyout certs/home.local.key \
  -out certs/home.local.crt \
  -subj "/CN=home.local" \
  -addext "subjectAltName = DNS:home.local"
```

### 2. Convert the Certificate to PEM Format

```bash
openssl x509 -in certs/home.local.crt -out certs/home.local.pem -outform PEM
```

### 3. Update the Kubernetes Secrets

```bash
# Update secret in the home-assistant namespace
kubectl create secret tls home-local-tls \
  --key certs/home.local.key \
  --cert certs/home.local.crt \
  -n home-assistant \
  --dry-run=client -o yaml | kubectl apply -f -

# Update secret in the node-red namespace
kubectl create secret tls home-local-tls \
  --key certs/home.local.key \
  --cert certs/home.local.crt \
  -n node-red \
  --dry-run=client -o yaml | kubectl apply -f -
```

### 4. Restart Traefik to Pick Up the New Certificate

```bash
kubectl rollout restart deploy traefik -n kube-system
kubectl rollout status deploy traefik -n kube-system
```

### 5. Trust the New Certificate on Your System

```bash
# For macOS:
sudo security add-trusted-cert -d -r trustRoot \
  -k /Library/Keychains/System.keychain \
  /Users/zach/src/homelab/certs/home.local.pem
```

## Verify Everything is Working

After following these steps, access your applications via HTTPS and confirm there are no certificate warnings:

- Home Assistant: https://home.local
- Node-RED: https://home.local/node-red

## Troubleshooting

### Check Traefik Logs for Certificate Issues

```bash
# Get the Traefik pod name
kubectl get pods -n kube-system -l app.kubernetes.io/name=traefik -o name

# Check the logs for TLS-related errors
kubectl logs -n kube-system pod/traefik-XXXXX-XXXXX | grep -i "tls\|cert\|secret"
```

### Verify the Secrets Exist in Each Namespace

```bash
kubectl get secret home-local-tls -n home-assistant
kubectl get secret home-local-tls -n node-red
```

## Configuration Files

### Traefik Configuration (apps/infra/traefik/traefik-config.yaml)

```yaml
apiVersion: helm.cattle.io/v1
kind: HelmChartConfig
metadata:
  name: traefik
  namespace: kube-system
spec:
  valuesContent: |-
    additionalArguments:
      - "--entrypoints.websecure.http.tls=true"
```

### Home Assistant IngressRoute (apps/home-assistant/ingress.yaml)

```yaml
# HTTPS IngressRoute section
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: home-assistant-https
  namespace: home-assistant
spec:
  entryPoints:
    - websecure
  routes:
    - kind: Rule
      match: Host(`home.local`)
      services:
        - name: home-assistant
          port: 8123
  tls:
    secretName: home-local-tls
```

### Node-RED IngressRoute (apps/node-red/ingress.yaml)

```yaml
# HTTPS IngressRoute section
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: node-red-https
  namespace: node-red
spec:
  entryPoints:
    - websecure
  routes:
    - kind: Rule
      match: Host(`home.local`) && PathPrefix(`/node-red`)
      middlewares:
        - name: node-red-stripprefix
      services:
        - name: node-red
          port: 1880
  tls:
    secretName: home-local-tls
``` 