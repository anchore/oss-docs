+++
title = "Private Registry Authentication"
description = "SBOM Generation Private Registry Authentication"
weight = 80
tags = ["syft", "sbom", "docker", "container", "authentication"]
url = "docs/userguides/sbom/authentication"

+++

## Private Registry Authentication

### Local Docker Credentials

When a container runtime is not present, Syft can still utilize credentials configured in common credential sources (such as `~/.docker/config.json`). It will pull images from private registries using these credentials. The config file is where your credentials are stored when authenticating with private registries via some command like `docker login`. For more information see the `go-containerregistry` [documentation](https://github.com/google/go-containerregistry/tree/main/pkg/authn).

An example `config.json` looks something like this:

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

You can run the following command as an example. It details the mount/environment configuration a container needs to access a private registry:

```
docker run -v ./config.json:/config/config.json -e "DOCKER_CONFIG=/config" anchore/syft:latest  <private_image>
```

### Docker Credentials in Kubernetes

Here's a simple workflow to mount this config file as a secret into a container on Kubernetes.

1. Create a secret. The value of `config.json` is important. It refers to the specification detailed [here](https://github.com/google/go-containerregistry/tree/main/pkg/authn#the-config-file). Below this section is the `secret.yaml` file that the pod configuration will consume as a volume. The key `config.json` is important. It will end up being the name of the file when mounted into the pod.

   ```yaml
   # secret.yaml

   apiVersion: v1
   kind: Secret
   metadata:
     name: registry-config
     namespace: syft
   data:
     config.json: <base64 encoded config.json>
   ```

   `kubectl apply -f secret.yaml`

2. Create your pod running syft. The env `DOCKER_CONFIG` is important because it advertises where to look for the credential file. In the below example, setting `DOCKER_CONFIG=/config` informs syft that credentials can be found at `/config/config.json`. This is why we used `config.json` as the key for our secret. When mounted into containers the secrets' key is used as the filename. The `volumeMounts` section mounts our secret to `/config`. The `volumes` section names our volume and leverages the secret we created in step one.

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
           - <private_image>
     volumes:
       - name: registry-config
         secret:
           secretName: registry-config
   ```

   `kubectl apply -f pod.yaml`

3. The user can now run `kubectl logs syft-private-registry-demo`. The logs should show the Syft analysis for the `<private_image>` provided in the pod configuration.

Using the above information, users should be able to configure private registry access without having to do so in the `grype` or `syft` configuration files. They will also not be dependent on a Docker daemon, (or some other runtime software) for registry configuration and access.
