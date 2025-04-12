# Homelab

## Bootstrapping k3s

https://docs.k3s.io/quick-start

The same script is used to add nodes, but you need to set envvars on subsequent machines

## Uninstalling k3s (only to level everything)
`/usr/local/bin/k3s-uninstall.sh`

## Applying this repo

`kubectl apply -k .
