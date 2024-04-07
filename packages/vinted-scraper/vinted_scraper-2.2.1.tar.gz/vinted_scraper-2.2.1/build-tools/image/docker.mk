# ====================================================================================
# Setup Project

ifeq ($(origin DOCKERFILE), undefined)
DOCKERFILE := $(ROOT)/Dockerfile
endif

ifeq ($(origin VOLUMES), undefined)
VOLUMES :=
endif

ifeq ($(origin TEST_VOLUMES), undefined)
TEST_VOLUMES :=
endif

# ====================================================================================
# Actions

.PHONY: img.build
img.build: #! Build the application container.
	docker build --no-cache -t $(PROJECT_NAME):$(VERSION) -f $(DOCKERFILE) .

.PHONY: img.test.build
img.test.build: #! Build the unit test container.
	export DOCKER_BUILDKIT=1
	docker build --no-cache -t test-base-image:tmp -f $(DOCKERFILE) .
	cp $(BUILD_TOOLS_FOLDER)/$(TECHNOLOGY)/test/Dockerfile $(ROOT)/test.Dockerfile
	docker build --no-cache -t $(PROJECT_NAME)-test-image:tmp -f $(ROOT)/test.Dockerfile .
	rm $(ROOT)/test.Dockerfile

.PHONY: img.run
img.run: #! Run the main program inside a container
	docker run  --rm --name=$(PROJECT_NAME)-$(VERSION) $(VOLUMES) $(PROJECT_NAME):$(VERSION)

.PHONY: img.test.run
img.test.run: #! Run all the unit test inside a container.
	docker run  --rm --name=$(PROJECT_NAME)-test-image -v $(ROOT):/tmp/test $(TEST_VOLUMES) $(PROJECT_NAME)-test-image:tmp

.PHONY: img.clean
img.clean: #! Clean up img from the created image
	docker rmi $$(docker images -f dangling=true -q) || true
	docker image rm -f $(PROJECT_NAME):$(VERSION) || true

.PHONY: img.test.clean
img.test.clean: #! Clean up img from the created image
	docker rmi $$(docker images -f dangling=true -q) || true
	docker image rm -f $(PROJECT_NAME)-test-image:tmp || true
	docker image rm -f test-base-image:tmp || true

.PHONY: img.prune
img.prune: #! Prune Docker images
	docker image prune -a

.PHONY: img.check
img.check:  ; @: #! Run the static analysis tool to scan the Dockerfile

