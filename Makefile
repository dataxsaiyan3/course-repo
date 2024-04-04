PROJECT = project-name
REGISTRY = ecr-name
TEAM = team-name
VERSION = latest

ifndef VERSION
  VERSION := $(shell git describe --tags --always)
endif

ifndef ENVIRONMENT
  $(info ENVIRONMENT is not set (value should be either dev, qa or prod (case sensitive)). Presuming dev.)
  ENVIRONMENT := dev
endif
ifeq ($(ENVIRONMENT),qa)
  VIRTUALVERSION := qa
else ifeq ($(ENVIRONMENT),prod)
  VIRTUALVERSION := prod
else
  VIRTUALVERSION := latest
endif


.PHONY: build-dev-docker
build-dev-docker:
	docker build . -t $(REGISTRY)/$(PROJECT):$(VERSION) -t $(REGISTRY)/$(PROJECT):$(VIRTUALVERSION)

.PHONY: build-docker
build-docker:
	docker build .  --no-cache -t $(REGISTRY)/$(PROJECT):$(VERSION) -t $(REGISTRY)/$(PROJECT):$(VIRTUALVERSION)

.PHONY: push-docker
push-docker:
	bash bin/push.sh $(REGISTRY) $(PROJECT) $(VERSION)
	bash bin/push.sh $(REGISTRY) $(PROJECT) $(VIRTUALVERSION)

.PHONY: deploy
deploy:
	bash bin/deploy.sh $(PROJECT) $(ENVIRONMENT) $(VERSION) $(TEAM)


.PHONY: cleanup
cleanup:
	@if [ "`docker ps -aq -f name=$(PROJECT)-$(VERSION)`" != "" ]; then docker rm -f $(PROJECT)-$(VERSION); fi

.PHONY: echo
echo:
	$(info test $(PROJECT))