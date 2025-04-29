# Home

This container requires an acr secret to exist and reference an azure resource

```
kubectl create secret docker-registry acr-secret \
  --docker-server=homelabratory.azurecr.io \
  --docker-username=<your-acr-username> \
  --docker-password=<your-acr-password>
```