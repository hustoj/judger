all: build

build:
	@go build -o docker/runner runner.go
	@docker build -t runner:test ./docker

clean:
	@rm docker/runner