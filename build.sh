#!/bin/bash

export BUILDPLATFORM=linux/arm/v7
export TARGETPLATFORM=linux/arm/v7

export DOCKER_USER=klmcwhirter

faas-cli build -f flooditapi.yml --build-arg BUILDPLATFORM=linux/arm/v7 --build-arg TARGETPLATFORM=linux/arm/v7
