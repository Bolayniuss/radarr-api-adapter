.PHONY: all set-base build base login push run

#
# make build-base login push - will build and push the base image
# make build login push - will build and push the app image
#
TAG=$(shell git log -1 --pretty=%h)
NAME=radarr-api-adapter
VERSION:=${NAME}:${TAG}
LATEST:=${NAME}:latest

BUILD_REPO_ORIGIN=$(shell git config --get remote.origin.url)
BUILD_COMMIT_SHA1=$(shell git rev-parse --short HEAD)
BUILD_COMMIT_DATE=$(shell git log -1 --date=short --pretty=format:%ct)
BUILD_BRANCH=$(shell git symbolic-ref --short HEAD)
BUILD_DATE=$(shell date -u +"%Y-%m-%dT%H:%M:%SZ")

DOCKERFILE=Dockerfile
REGISTRY=michaelbolay

build:
	docker build --rm -t ${REGISTRY}/${LATEST} -t ${REGISTRY}/${VERSION} \
				 --build-arg BUILD_COMMIT_SHA1=${BUILD_COMMIT_SHA1} \
				 --build-arg BUILD_COMMIT_DATE=${BUILD_COMMIT_DATE} \
				 --build-arg BUILD_BRANCH=${BUILD_BRANCH} \
				 --build-arg BUILD_DATE=${BUILD_DATE} \
				 --build-arg BUILD_REPO_ORIGIN=${BUILD_REPO_ORIGIN} \
				 . --file docker/${DOCKERFILE}

buildx:
	docker buildx build --rm -t ${REGISTRY}/${LATEST} -t ${REGISTRY}/${VERSION} \
				 --build-arg BUILD_COMMIT_SHA1=${BUILD_COMMIT_SHA1} \
				 --build-arg BUILD_COMMIT_DATE=${BUILD_COMMIT_DATE} \
				 --build-arg BUILD_BRANCH=${BUILD_BRANCH} \
				 --build-arg BUILD_DATE=${BUILD_DATE} \
				 --build-arg BUILD_REPO_ORIGIN=${BUILD_REPO_ORIGIN} \
				 . --file docker/${DOCKERFILE}

login:
	docker login

push:
	docker push ${REGISTRY}/${VERSION}
	docker push ${REGISTRY}/${LATEST}


run:
	docker run --rm -p 8000:8000 ${LATEST}
