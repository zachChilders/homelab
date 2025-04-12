# Tailscale Exit Node

This directory contains the Kubernetes configuration for deploying a Tailscale exit node.

## Prerequisites

1. A Tailscale account
2. An auth key with the following permissions:
   - Reusable
   - Ephemeral
   - Pre-authorized

## Setup

1. Create a Kubernetes secret with your Tailscale auth key:
   ```bash
   kubectl create secret generic tailscale-auth \
     --namespace=tailscale \
     --from-literal=auth-key='your-auth-key-here'
   ```

2. Apply the configuration:
   ```bash
   kubectl apply -k apps/tailscale/base
   ```

## Configuration

The exit node is configured with the following settings:
- Hostname: `tailscale-exit-node`
- Accepts routes: Yes
- Advertises routes: `0.0.0.0/0`
- Runs with NET_ADMIN capability
- Uses persistent state directory

## Usage

Once deployed, you can use this exit node by:
1. Connecting to your Tailscale network
2. Selecting this node as your exit node in the Tailscale client

## Troubleshooting

To check the status of the Tailscale node:
```bash
kubectl -n tailscale logs -f deployment/tailscale-exit-node
```

To restart the node if needed:
```bash
kubectl -n tailscale rollout restart deployment/tailscale-exit-node
```