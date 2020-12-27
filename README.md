# flooditapi
provide api for flood_it as an openfaas function in python 3


## Requires the python3 template to be modified
Modify the top of the Dockerfile to contain these lines:

```Dockerfile
ARG TARGETPLATFORM
ARG BUILDPLATFORM

FROM --platform=${TARGETPLATFORM:-linux/arm/v7} ghcr.io/openfaas/classic-watchdog:0.1.4 as watchdog
FROM --platform=${TARGETPLATFORM:-linux/arm/v7} python:3-alpine
```
