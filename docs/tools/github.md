# GitHub

## CI/CD

_TODO: Improve this section_

The CI/CD pipelines are defined using the GitHub Actions syntax that can be found in the [.github](../../.github) directory. Currently, the following stages are defined:

- *lint*: runs `flake8` to check the code style
- *prepare*: run service specific script before the build, like downloading ML models
- *test*: run the unit testing
- *build*: create the docker image and push it in the registry
- ~~*deploy*: applies the changes on the Kubernetes cluster~~ _Not yet_

The CI/CD pipeline is triggered on each individual service only if a merge request modifies its content. Currently, we only have one running cluster, but a good practice would be to have multiple environments, like `dev`, `test` and `prod` which are deployed when according branches are modified.
