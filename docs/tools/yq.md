# yq

[yq](https://github.com/mikefarah/yq) is _"a lightweight and portable command-line YAML, JSON and XML processor. yq uses [jq](https://github.com/stedolan/jq) like syntax but works with yaml files as well as json, xml, properties, csv and tsv"_.

## How do we use this tool

We use yq to edit [Kubernetes](./kubernetes.md) configuration files so they can be fed to [envsubst](./envsubst.md) through [GitHub Actions](./github-actions.md) workflows using secrets stored on [GitHub Secrets](./github-secrets.md) before deployment.

## Additional resources

- _None_
