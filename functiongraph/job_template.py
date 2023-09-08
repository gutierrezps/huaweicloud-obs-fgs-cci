job_template = {
    "apiVersion": "batch/v1",
    "kind": "Job",
    "metadata": {
        "annotations": {
            "description": ""
        },
        "name": "placeholder, to be updated by FunctionGraph",
        "labels": {}
    },
    "spec": {
        "template": {
            "metadata": {
                "annotations": {
                    "log.stdoutcollection.kubernetes.io":
                        "{\"collectionContainers\": [\"container-0\"]}"
                },
                "name": "placeholder, to be updated by FunctionGraph"
            },
            "spec": {
                "containers": [
                    {
                        "image": "placeholder, to be updated by FunctionGraph",
                        "name": "container-0",
                        "env": "placeholder, to be updated by FunctionGraph",
                        "resources": {
                            "limits": {
                                "cpu": "500m",
                                "memory": "1024Mi"
                            },
                            "requests": {
                                "cpu": "500m",
                                "memory": "1024Mi"
                            }
                        },
                        "command": [],
                        "lifecycle": {}
                    }
                ],
                "imagePullSecrets": [
                    {
                        "name": "imagepull-secret"
                    }
                ],
                "restartPolicy": "Never"
            }
        }
    }
}
