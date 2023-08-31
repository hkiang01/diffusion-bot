#!/usr/bin/env bash

source kubernetes/ci/.env

REGISTRY=${REGISTRY:-localhost:32000}
PUSH_REGISTRY=${PUSH_REGISTRY:-${REGISTRY}}
NAMESPACE=${NAMESPACE}

function build_push() {
    docker compose build
    tag=$(_tag)
    docker tag diffusion-bot-api:latest ${PUSH_REGISTRY}/diffusion-bot-api:${tag}
    docker tag diffusion-bot-bot:latest ${PUSH_REGISTRY}/diffusion-bot-bot:${tag}
    docker push ${PUSH_REGISTRY}/diffusion-bot-api:${tag}
    docker push ${PUSH_REGISTRY}/diffusion-bot-bot:${tag}
}

function deploy() {
    tag=$(_tag)
    helm -n ${NAMESPACE} upgrade --install diffusion-bot \
      kubernetes/helm/charts/diffusion-bot \
      --set api.image.repository="${REGISTRY}/diffusion-bot-api" \
      --set api.image.tag="${tag}"
}

function _tag() {
    echo $(git rev-parse --short HEAD)
}

build_push
deploy
