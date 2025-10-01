+++
title = "Private Registries"
description = "Configure authentication for scanning container images from private registries using credentials, registry tokens, and credential helpers."
weight = 80
tags = ["syft", "grype", "docker", "container", "authentication", "ecr", "gcr", "acr"]
url = "docs/user-guides/private-registries"
+++

The Anchore OSS tools analyze container images from private registries using multiple authentication methods.
When a container runtime isn't available, the tools use the [go-containerregistry](https://github.com/google/go-containerregistry/tree/main/pkg/authn) library to handle authentication directly with registries.

When using a container runtime explicitly (for instance, with the `--from docker` flag) the tools defer to the runtime's authentication mechanisms.
However, if the `registry` source is used, the tools use the Docker configuration file and any configured credential helpers to authenticate with the registry.

## Registry tokens and personal access tokens

Many registries support personal access tokens (PATs) or registry tokens for authentication. Use `docker login` with your token, then the tools can use the cached credentials:

```bash
# GitHub Container Registry - create token at https://github.com/settings/tokens (needs read:packages scope)
docker login ghcr.io -u <username> -p <token>
syft ghcr.io/username/private-image:latest

# GitLab Container Registry - use deploy token or personal access token
docker login registry.gitlab.com -u <username> -p <token>
syft registry.gitlab.com/group/project/image:latest
```

The tools read credentials from `~/.docker/config.json`, the same file Docker uses when you run `docker login`. This file can contain either basic authentication credentials or credential helper configurations.

Here are examples of what the config looks like if you are crafting it manually:

**Basic authentication example:**

```json
{
  "auths": {
    "registry.example.com": {
      "username": "AzureDiamond",
      "password": "hunter2"
    }
  }
}
```

**Token authentication example:**

```json
// token auth, where credentials are base64-encoded
{
  "auths": {
    "ghcr.io": {
      "auth": "dXNlcm5hb...m5h=="
    }
  }
}
```

{{< alert color="warning" title="Security Warning" >}}
Storing plaintext passwords in `config.json` is insecure. Use credential helpers where possible.
{{< /alert >}}

By default, the tools look for credentials in `~/.docker/config.json`. You can override this location using the `DOCKER_CONFIG` environment variable:

```bash
export DOCKER_CONFIG=/path/to/custom/config
syft registry.example.com/private/image:latest
```

You can also use this in a container:

```bash
docker run -v ./config.json:/auth/config.json -e "DOCKER_CONFIG=/auth" anchore/syft:latest <private_image>
```

## Docker credential helpers

Docker credential helpers are specialized programs that securely store and retrieve registry credentials. They're particularly useful for cloud provider registries that use dynamic, short-lived tokens.

Instead of storing passwords as plaintext in `config.json`, you configure helpers that generate credentials on-demand. This is facilitated by the [google/go-containerregistry library](https://github.com/google/go-containerregistry/tree/main/pkg/authn#the-config-file).

### Configuring credential helpers

Add credential helpers to your `config.json`:

```json
{
  "credHelpers": {
    // using the docker-credential-gcr for Google Container Registry and Artifact Registry
    "gcr.io": "gcr",
    "us-docker.pkg.dev": "gcloud",

    // using the amazon-ecr-credential-helper for AWS Elastic Container Registry
    "123456789012.dkr.ecr.us-west-2.amazonaws.com": "ecr-login",

    // using the docker-credential-acr for Azure Container Registry
    "myregistry.azurecr.io": "acr"
  }
}
```

When the tools access these registries, they execute the corresponding helper program (for example, `docker-credential-gcr`, or more generically `docker-credential-NAME` where NAME is the config value) to obtain credentials.

{{< alert color="info" title="Note" >}}
If both `credHelpers` and `auths` are configured for the same registry, `credHelpers` takes precedence.
{{< /alert >}}

For more information about Docker credential helpers for various cloud providers:

- [ECR authentication documentation](https://docs.aws.amazon.com/AmazonECR/latest/userguide/registry_auth.html).
- [Artifact Registry authentication documentation](https://cloud.google.com/artifact-registry/docs/docker/authentication).
- [ACR authentication documentation](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-authentication).

## Within Kubernetes

When running the tools in Kubernetes and you need access to private registries, mount Docker credentials as a secret.

### Create secret

Create a Kubernetes secret containing your Docker credentials. The key `config.json` is important—it becomes the filename when mounted into the pod.
For more information about the credential file format, see the [go-containerregistry config docs](https://github.com/google/go-containerregistry/tree/main/pkg/authn#the-config-file).

```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: registry-config
  namespace: syft
data:
  config.json: <base64-encoded-config.json>
```

Create the secret:

```bash
# Base64 encode your config.json
cat ~/.docker/config.json | base64

# Apply the secret
kubectl apply -f secret.yaml
```

### Configure pod

Configure your pod to use the credential secret. The `DOCKER_CONFIG` environment variable tells the tools where to look for credentials.
Setting `DOCKER_CONFIG=/config` means the tools look for credentials at `/config/config.json`.
This matches the secret key `config.json` we created above—when Kubernetes mounts secrets, each key becomes a file with that name.

The `volumeMounts` section mounts the secret to `/config`, and the `volumes` section references the secret created in the previous step.

```yaml
# pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: syft-k8s-usage
spec:
  containers:
    - image: anchore/syft:latest
      name: syft-private-registry-demo
      env:
        - name: DOCKER_CONFIG
          value: /config
      volumeMounts:
        - mountPath: /config
          name: registry-config
          readOnly: true
      args:
        - <private-image>
  volumes:
    - name: registry-config
      secret:
        secretName: registry-config
```

Apply and check logs:

```bash
kubectl apply -f pod.yaml
kubectl logs syft-private-registry-demo
```
