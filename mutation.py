import base64

import jsonpatch
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/")
def healthcheck():
    return "ok"


@app.route("/mutator/deployment", methods=['POST'])
def mutate_deployment():
    request_info = request.get_json()
    uid = request_info["request"]["uid"]
    image_name = request_info["request"]["object"]["spec"]["template"]["spec"]["containers"][0]["image"]
    new_image = f"mirror.gcr.io/library/{image_name}"
    return admission_response_patch(uid, "Mutating container dockerhub image", json_patch=jsonpatch.JsonPatch([{"op": "replace", "path": "/spec/template/spec/containers/0/image", "value": new_image}, {"op": "add", "path": "/metadata/labels/mutated", "value": "yes"}]))


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
