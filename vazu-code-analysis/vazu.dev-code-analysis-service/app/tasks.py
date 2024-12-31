import shutil

from celery import Celery
import os
import boto3

app = Celery('tasks')
app.config_from_object('celeryconfig')

BUCKET_NAME = "vazu-dev-codebase-storage"


class SysCommandError(Exception):
    pass


def run_sys_command(command):
    command_return_code = os.system(command)
    if command_return_code != 0:
        raise SysCommandError(f"{command} failed")


@app.task
def initiate_code_analysis(
    code_name,
    repo_url
):
    s3 = boto3.client("s3")
    file_path = f"app_codes/{code_name}.zip"
    download_path = f"/opt/{code_name}.zip"
    try:
        run_sys_command(f"mkdir app-codes/{code_name}")
        try:
            s3.download_file(BUCKET_NAME, file_path, download_path)
        except Exception as e:
            print("Error occured while downloadin the code", e)
            run_sys_command(f"git clone {repo_url} app-codes/{code_name}")
        else:
            run_sys_command(f"unzip -d app-codes/{code_name}/ /opt/{code_name}.zip")
            run_sys_command(f"rm /opt/{code_name}.zip")

        run_sys_command(
            f"cd app-codes/{code_name}/; sonar-scanner -Dsonar.projectKey={code_name} -Dsonar.sources=. -Dsonar.host.url=https://sonar.vazu-dev.dev -Dsonar.token=sqa_3cc13b1fd904aff1522c02eb701df11174b9e510"
        )
        run_sys_command(f"rm -rf app-codes/{code_name}")
        print("Analysis completed")
    except SysCommandError as e:
        os.system(f"rm -rf /opt/{code_name}.zip")
        os.system(f"rm -rf app-codes/{code_name}")
        print("Error:", e)
    return


@app.task
def code_upload_to_s3(repo_url, string_id):
    s3 = boto3.client("s3")
    pulled_path = f"/opt/{string_id}"
    zipped_path = f"/opt/{string_id}.zip"
    uploaded_file_path = f"app_codes/{string_id}.zip"
    try:
        run_sys_command(f"mkdir {pulled_path}")
        run_sys_command(f"git clone {repo_url} {pulled_path}")
        run_sys_command(f"cd {pulled_path}; zip -r {zipped_path} .")
        s3.upload_file(zipped_path, BUCKET_NAME, uploaded_file_path)
        run_sys_command(f"rm -rf {pulled_path}")
        run_sys_command(f"rm -rf {pulled_path}.zip")
        print("Code uploaded successfully")
    except Exception as e:
        print("Error:", e)
        run_sys_command(f"rm -rf {pulled_path}")
        run_sys_command(f"rm -rf {pulled_path}.zip")
    return



