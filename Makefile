CONTAINER_NAME = fidelity_stats_dash

.phony: docker-build
docker-build:
	docker build -t $(CONTAINER_NAME) .


.phony: docker-run
docker-run: 
	docker run -p 8050:8050  \
		$(CONTAINER_NAME)