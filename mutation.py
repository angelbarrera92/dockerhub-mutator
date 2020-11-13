import base64

import jsonpatch
from docker_image.reference import Reference
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/")
def healthcheck():
    return "ok"


@app.route("/mutator/dockerhub", methods=['POST'])
def mutate_dockerhub():
    request_info = request.get_json()
    uid = request_info["request"]["uid"]
    obj = request_info["request"]["object"]
    kind = obj["kind"]
    patches = list()
    if kind == "Pod":
        patches = pod(obj)
    elif kind == "Deployment":
        patches = deployment(obj)
    elif kind == "Job":
        patches = job(obj)
    elif kind == "CronJob":
        patches = cronjob(obj)
    elif kind == "ReplicaSet":
        patches = replicaset(obj)
    elif kind == "ReplicationController":
        patches = replicationController(obj)
    elif kind == "DaemonSet":
        patches = daemonset(obj)
    elif kind == "StatefulSet":
        patches = statefulset(obj)
    elif kind == "PodTemplate":
        patches = podtemplate(obj)
    if len(patches) > 0:
        patches.append(
            {"op": "add", "path": "/metadata/labels/mutated", "value": "yes"})
    return admission_response_patch(uid, "Mutating containers images from dockerhub", json_patch=jsonpatch.JsonPatch(patches))


def is_dockerhub_image(image):
    ref = Reference.parse_normalized_named(image)
    hostname, name = ref.split_hostname()
    if "docker.io" in hostname:
        return True
    return False


def replace_docker_io(image):
    ref = Reference.parse_normalized_named(image)
    return ref.string().replace("docker.io", "mirror.gcr.io")


def pod(obj):
    patches = []
    index = 0
    containers = obj["spec"]["containers"]
    for container in containers:
        image = container["image"]
        if is_dockerhub_image(image):
            patches.append(
                {"op": "replace", "path": f"/spec/containers/{index}/image", "value": replace_docker_io(image)})
        index += 1
    return patches


def _generic_template(obj):
    patches = []
    index = 0
    containers = obj["spec"]["template"]["spec"]["containers"]
    for container in containers:
        image = container["image"]
        if is_dockerhub_image(image):
            patches.append(
                {"op": "replace", "path": f"/spec/template/spec/containers/{index}/image", "value": replace_docker_io(image)})
        index += 1
    return patches


def deployment(obj):
    return _generic_template(obj)


def job(obj):
    return _generic_template(obj)


def replicaset(obj):
    return _generic_template(obj)


def daemonset(obj):
    return _generic_template(obj)


def statefulset(obj):
    return _generic_template(obj)


def replicationController(obj):
    return _generic_template(obj)


def cronjob(obj):
    patches = []
    index = 0
    containers = obj["spec"]["jobTemplate"]["spec"]["template"]["spec"]["containers"]
    for container in containers:
        image = container["image"]
        if is_dockerhub_image(image):
            patches.append(
                {"op": "replace", "path": f"/spec/jobTemplate/spec/template/spec/containers/{index}/image", "value": replace_docker_io(image)})
        index += 1
    return patches


def podtemplate(obj):
    patches = []
    index = 0
    containers = obj["template"]["spec"]["containers"]
    for container in containers:
        image = container["image"]
        if is_dockerhub_image(image):
            patches.append(
                {"op": "replace", "path": f"/template/spec/containers/{index}/image", "value": replace_docker_io(image)})
        index += 1
    return patches


def admission_response_patch(uid, message, json_patch):
    base64_patch = base64.b64encode(
        json_patch.to_string().encode("utf-8")).decode("utf-8")
    return jsonify({
        "apiVersion": "admission.k8s.io/v1",
        "kind": "AdmissionReview",
        "response": {
            "allowed": True,
            "uid": uid,
            "status": {"message": message},
            "patchType": "JSONPatch",
            "patch": base64_patch,
        }})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=443, ssl_context=(
        "/certs/tls.crt", "/certs/tls.key"))
