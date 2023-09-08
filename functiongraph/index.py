# -*- coding:utf-8 -*-
import json
import time

import requests
import signer
from job_template import job_template


def create_signed_request(
        ak: str, sk: str,
        method: str, endpoint: str, body: str) -> signer.HttpRequest:
    """Creates a request, signed with AK and SK

    Args:
        ak (str): Access Key
        sk (str): Secret Access Key
        method (str): HTTP method (GET, POST etc.)
        endpoint (str): Endpoint URL
        body (str): Request body

    Returns:
        signer.HttpRequest: request object with Authorization header
    """
    sig = signer.Signer()
    sig.Key = ak
    sig.Secret = sk

    req = signer.HttpRequest(method, endpoint)
    req.headers = {"content-type": "application/json"}
    req.body = body
    sig.Sign(req)

    return req


def handler(event, context):
    # get OBS trigger event information
    # see "Object Storage Service (OBS)" test event
    bucket = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']

    # get environment variables from FunctionGraph configuration (context)
    # see <https://support.huaweicloud.com/intl/en-us/usermanual-functiongraph/functiongraph_01_0154.html>  # noqa
    container_env_vars = {
        'ak': context.getUserData('ak'),
        'sk': context.getUserData('sk'),
        'endpoint': context.getUserData('obs_endpoint'),
        'bucket': bucket,
        'object': object_key,
        'upload': context.getUserData('output_folder')
    }

    # convert env vars to K8S format (list of dicts with 'name' and 'value')
    k8s_env_vars = []
    for key, value in container_env_vars.items():
        var = {'name': key, 'value': value}
        k8s_env_vars.append(var)

    job_template['spec']['template']['spec']['containers'][0][
        'env'] = k8s_env_vars

    job_template['spec']['template']['spec']['containers'][0][
        'image'] = context.getUserData('swr_image')

    # configure job name (get job_name variable and append timestamp)
    job_name = context.getUserData('job_name')
    job_name += "-" + str(int(time.time()))
    job_template['metadata']['name'] = job_name
    job_template['spec']['template']['metadata']['name'] = job_name

    body = json.dumps(job_template)
    print(body)

    # API endpoint to create a CCI Job, without using kubectl and
    # cci-iam-authenticator. Source:
    # <https://support.huaweicloud.com/intl/en-us/api-cci/createBatchV1NamespacedJob.html>
    namespace = context.getUserData('cci_namespace')
    cci_endpoint = "https://" + context.getUserData('cci_endpoint')
    cci_endpoint += f"/apis/batch/v1/namespaces/{namespace}/jobs"

    req = create_signed_request(
        container_env_vars['ak'], container_env_vars['sk'],
        "POST", cci_endpoint, body)

    resp = requests.request(
        req.method,
        req.scheme + "://" + req.host + req.uri,
        headers=req.headers,
        data=req.body)

    return f"{resp.status_code} {resp.reason}"
