# About yq

As the website of [yq](https://mikefarah.gitbook.io/yq) mentions:

!!! quote

    yq a lightweight and portable command-line YAML processor. yq uses [jq](https://github.com/stedolan/jq) like syntax but works with yaml files as well as json.

## How and why do we use yq

We use yq to edit [Kubernetes](./about-kubernetes.md) configuration files so they can be fed to [envsubst](./about-envsubst.md) through [GitHub Actions](./about-github-actions.md) workflows using secrets stored on [GitHub Secrets](./about-github-secrets.md) before deployment.

## Install yq

TODO

## Resources and alternatives

These resources and alternatives are related to the current item (in alphabetical order).

_None at the moment._
