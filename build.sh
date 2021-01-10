#!/bin/bash

export BUILDPLATFORM=linux/arm/v7
export TARGETPLATFORM=linux/arm/v7

export DOCKER_USER=klmcwhirter

function echocmd
{
    echo $*
    $*
}

echocmd faas-cli remove -f flooditapi.yml &

echocmd rm -fr build

echocmd faas-cli build -f flooditapi.yml --build-arg BUILDPLATFORM=linux/arm/v7 --build-arg TARGETPLATFORM=linux/arm/v7

rc=$?
if [ $rc -eq 0 ]
then
    echocmd faas-cli push -f flooditapi.yml
    rc=$?
else
    exit $rc
fi

if [ $rc -eq 0 ]
then
    kubectl rollout status -n openfaas-fn deploy/flooditapi

    echocmd faas-cli deploy -f flooditapi.yml
    rc=$?


    while [[ "$(kubectl rollout status -n openfaas-fn deploy/flooditapi)" =~ "successfully|Depoyed" ]]
    do
        echo give the deploy some time ...
        sleep 10
    done
fi

exit $rc
