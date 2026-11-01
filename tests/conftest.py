# Docker cases need the compiler and runner images. Collect them only when
# their directory is passed explicitly: pytest tests/docker
collect_ignore = ["docker"]
