GITHUB_SHA := `git rev-parse HEAD`
GITHUB_REMOTE_URL := `git config --get remote.origin.url`
SERVICE := "ort-cbd-int-data-in"

aws-ecr-login:
    aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query 'Account' --output text).dkr.ecr.eu-west-1.amazonaws.com

build:
    docker buildx build \
        --platform linux/amd64 \
        --output type=docker \
        --build-arg SERVICE={{SERVICE}} \
        --build-arg ENV=production \
        --build-arg GITHUB_SHA={{GITHUB_SHA}} \
        --label org.opencontainers.image.source={{GITHUB_REMOTE_URL}} \
        --label org.opencontainers.image.revision={{GITHUB_SHA}} \
        --label org.opencontainers.image.created=$(date -u +%Y-%m-%dT%H:%M:%SZ) \
        --tag {{SERVICE}}:latest \
        --tag {{SERVICE}}:{{GITHUB_SHA}} \
        --file ./Dockerfile .

deploy-to-ecr:
    just build

    docker tag {{SERVICE}}:latest $(aws sts get-caller-identity --query 'Account' --output text).dkr.ecr.eu-west-1.amazonaws.com/{{SERVICE}}:latest
    docker tag {{SERVICE}}:{{GITHUB_SHA}} $(aws sts get-caller-identity --query 'Account' --output text).dkr.ecr.eu-west-1.amazonaws.com/{{SERVICE}}:{{GITHUB_SHA}}

    docker push $(aws sts get-caller-identity --query 'Account' --output text).dkr.ecr.eu-west-1.amazonaws.com/{{SERVICE}}:latest
    docker push $(aws sts get-caller-identity --query 'Account' --output text).dkr.ecr.eu-west-1.amazonaws.com/{{SERVICE}}:{{GITHUB_SHA}}

deploy-to-prefect:
    #!/usr/bin/env bash
    # we use a bash script here to have inline env variables
    # @see: https://just.systems/man/en/setting-variables-in-a-recipe.html
    set -euxo pipefail
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)
    DOCKER_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.eu-west-1.amazonaws.com"
    DOCKER_REGISTRY="${DOCKER_REGISTRY}" uv run python -m deploy-prefect
