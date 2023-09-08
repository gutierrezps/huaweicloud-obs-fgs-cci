import os

from dotenv import load_dotenv
from obs import ObsClient


REQUIRED_ENV_VARS = {
    'ak': 'HWC Access Key (AK)',
    'sk': 'HWC Secret Access Key (SK)',
    'endpoint': 'OBS Endpoint (e.g. "obs.sa-brazil-1.myhuaweicloud.com")',
    'bucket': 'OBS bucket name',
    'object': 'OBS object key (e.g. "path%2Fto%2Ffile.txt")',
    'upload': 'OBS folder where output file will be uploaded'
}


def check_env_vars():
    for var, desc in REQUIRED_ENV_VARS.items():
        if var not in os.environ:
            print(f'error: missing env variable "{var}" ({desc})')
            exit(-1)


def create_obs_client():
    # https://support.huaweicloud.com/intl/en-us/sdk-python-devg-obs/obs_22_0500.html
    AK = os.environ['ak']
    SK = os.environ['sk']
    ENDPOINT = os.environ['endpoint']

    client = ObsClient(
        access_key_id=AK,
        secret_access_key=SK,
        server=ENDPOINT
    )

    return client


def download_file(obs_client: ObsClient) -> str:
    # https://support.huaweicloud.com/intl/en-us/sdk-python-devg-obs/obs_22_0911.html
    BUCKET = os.environ['bucket']
    object_key = os.environ['object']

    object_key = object_key.replace('%2F', '/')

    output_dir = os.path.dirname(os.path.realpath(__file__))
    output_dir = os.path.join(output_dir, 'work')
    os.makedirs(output_dir, exist_ok=True)

    output_file = object_key.split('/')[-1]
    output_file = os.path.join(output_dir, output_file)

    resp = obs_client.getObject(
        bucketName=BUCKET,
        objectKey=object_key,
        downloadPath=output_file
    )

    if resp.status < 300:
        print('requestId:', resp.requestId)
        print('url:', resp.body.url)
        return output_file

    print('error: getObject, code =', resp.errorCode, end='')
    print(', message =', resp.errorMessage)
    exit(-2)


def process_file(input_file_path: str) -> str:
    # add "_processed" to the end of the file name
    output_file_path, ext = input_file_path.rsplit('.', 1)
    output_file_path = f'{output_file_path}_processed.{ext}'

    with open(output_file_path, 'w') as output_file:
        # copy the input file contents to the output file
        with open(input_file_path) as input_file:
            output_file.write(input_file.read())

        # add a new line to the end
        output_file.write('\nprocessed')

    return output_file_path


def upload_file(obs_client: ObsClient, file_path: str):
    BUCKET = os.environ['bucket']
    UPLOAD_DIR = os.environ['upload']

    filename = os.path.split(file_path)[-1]

    object_key = f'{UPLOAD_DIR}/{filename}'

    resp = obs_client.putFile(
        bucketName=BUCKET,
        objectKey=object_key,
        file_path=file_path
    )

    if resp.status < 300:
        print('requestId:', resp.requestId)
        print('etag:', resp.body.etag)
        print('versionId:', resp.body.versionId)
        print('storageClass:', resp.body.storageClass)
    else:
        print('errorCode:', resp.errorCode)
        print('errorMessage:', resp.errorMessage)
        exit(-3)


def main():
    # for local tests, create a .env file and set environment variables
    load_dotenv()

    check_env_vars()

    obs_client = create_obs_client()

    input_file_path = download_file(obs_client)

    output_file_path = process_file(input_file_path)

    upload_file(obs_client, output_file_path)


if __name__ == '__main__':
    main()
