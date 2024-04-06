# CI Image
Docker image for CI / CD as published at [sampottingersketching/sketchingci](https://hub.docker.com/repository/docker/sampottingersketching/sketchingci/general). To release:

 - Build: `docker build -t cicd .`
 - Tag: `docker image tag cicd sampottingersketching/sketchingci:latest`
 - Release: `docker image push sampottingersketching/sketchingci:latest`

This is used in CI / CD pipeline automatically.
