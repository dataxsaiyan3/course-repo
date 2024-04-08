
PROJECT = testing
REGISTRY = ghcr.io
ACCOUNT = dataxsaiyan3
VERSION = latest

ifndef VERSION
  VERSION := $(shell git describe --tags --always)
endif


.PHONY: build-local-docker
build-local-docker:
	docker build . -t $(REGISTRY)/$(ACCOUNT)/$(PROJECT):$(VERSION)

.PHONY: build-docker-no-cache
build-docker-no-cache:
	docker build .  --no-cache -t $(REGISTRY)/$(ACCOUNT)/$(PROJECT):$(VERSION)

.PHONY: push-docker
push-docker:
	docker push ${REGISTRY}/$(ACCOUNT)/${PROJECT}:${VERSION}