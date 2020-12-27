#!/bin/bash

export BUILDPLATFORM=linux/arm/v7
export TARGETPLATFORM=linux/arm/v7

export DOCKER_USER=klmcwhirter

rm -fr build

faas-cli build -f flooditapi.yml --build-arg BUILDPLATFORM=linux/arm/v7 --build-arg TARGETPLATFORM=linux/arm/v7

rc=$?
if [ $rc -eq 0 ]
then
    faas-cli push -f flooditapi.yml
    rc=$?
else
    exit $rc
fi

if [ $rc -eq 0 ]
then
    faas-cli remove -f flooditapi.yml

    echo give the push some time ...
    sleep 10

    faas-cli deploy -f flooditapi.yml
    rc=$?
fi

exit $rc
