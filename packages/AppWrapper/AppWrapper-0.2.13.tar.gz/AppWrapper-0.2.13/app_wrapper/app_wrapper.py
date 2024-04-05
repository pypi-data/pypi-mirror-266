import ast
import json
import os
import pathlib

import requests
import boto3
import logging
import traceback

from app_wrapper.task_status import Status

logger = logging.getLogger("app_wrapper")
logger.setLevel(logging.INFO)

# Create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter("[%(levelname)s] %(message)s")

# Add formatter to ch
ch.setFormatter(formatter)

# Add ch to logger
logger.addHandler(ch)


class S3DownloadLogger:
    def __init__(self, file_size, filename):
        self._filename = filename
        self._size = file_size
        self._seen_so_far = 0
        # 10% progress intervals
        self._seen_percentages = dict.fromkeys(
            [x for x in range(10, 100, 10)], False
        )

    def __call__(self, bytes_amount):
        self._seen_so_far += bytes_amount
        percentage = round((self._seen_so_far / self._size) * 100)
        if (
            percentage in self._seen_percentages.keys()
            and not self._seen_percentages[percentage]
        ):
            self._seen_percentages[percentage] = True
            logger.info(
                f"Download progress for '{self._filename}': {percentage}%"
            )


class AppWrapper:
    LOCAL_MODE = None
    AWS_ACCESS_KEY_ID = None
    AWS_SECRET_ACCESS_KEY = None
    AWS_DEFAULT_REGION = None

    def __init__(
        self,
        LOCAL_MODE=False,
        AWS_ACCESS_KEY_ID="",
        AWS_SECRET_ACCESS_KEY="",
        AWS_DEFAULT_REGION="ap-northeast-2",
    ):
        self.LOCAL_MODE = LOCAL_MODE
        AppWrapper.LOCAL_MODE = LOCAL_MODE
        AppWrapper.AWS_ACCESS_KEY_ID = AWS_ACCESS_KEY_ID
        AppWrapper.AWS_SECRET_ACCESS_KEY = AWS_SECRET_ACCESS_KEY
        AppWrapper.AWS_DEFAULT_REGION = AWS_DEFAULT_REGION

        if self.LOCAL_MODE:
            logger.warning("This app is running in a local environment.")
        else:
            try:
                self.TOAD_HOST = os.getenv("TOAD_HOST", None)
                self.tenant_id = os.getenv("TENANT_ID")
                self.task_id = os.environ["TASK_ID"]
                AppWrapper.TOAD_HOST = self.TOAD_HOST
                AppWrapper.task_id = self.task_id

                self.main_app_id = os.environ["MAIN_APP_ID"]
                self.file_folder = os.environ["POD_FILE_PATH"]
                self.app_input_files = ast.literal_eval(
                    os.environ["APP_INPUT_FILES"]
                )

                if len(self.app_input_files) != 0:
                    self.download_file_from_s3()
            except Exception as e:
                error_log = f"Initialization Failed: {str(e)}"
                self.update_status(Status.Failed.value, error_log)

    def send_pod_log_to_s3(self):
        pod_log_res = requests.get(
            f"{self.TOAD_HOST}/tasks/{self.task_id}/pod-log/"
        )
        pod_log = pod_log_res.json()

        # 로그를 파일로 저장
        with open(f"{self.task_id}.log", "w") as log_file:
            log_file.write(pod_log["log"])

        response = requests.get(
            f"{self.TOAD_HOST}/utils/presigned-upload-url/?app_id={self.main_app_id}&task_id=logs&file_name={self.task_id}.log"
        )

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        files = {"file": open(f"{self.task_id}.log", "rb")}
        requests.put(response.json()["url"], data=files, headers=headers)

    @classmethod
    def download_from_s3(cls, bucket: str, key: str, download_path: str):
        if AppWrapper.LOCAL_MODE:
            s3 = boto3.resource(
                "s3",
                aws_access_key_id=AppWrapper.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AppWrapper.AWS_SECRET_ACCESS_KEY,
                region_name=AppWrapper.AWS_DEFAULT_REGION,
            )

            remote_file = s3.Bucket(bucket).Object(key)
            logger.info(f"Starting download for '{remote_file.key}'")
            download_logger = S3DownloadLogger(
                remote_file.content_length, remote_file.key
            )

            remote_file.download_file(download_path, Callback=download_logger)
            logger.info(f"Finished download for '{remote_file.key}'")
        else:
            presigned_get_url = requests.get(
                f"{AppWrapper.TOAD_HOST}/utils/presigned-download-url-s3/?bucket={bucket}&key={key}"
            ).json()["url"]

            logger.info(f"Starting download for '{key}'")

            res = requests.get(presigned_get_url, stream=True)

            if res.status_code != 200:
                error_log = f"Failed: File download. \
                                    status code: {res.status_code} detail: {res.reason} \
                                    key: {key} presigned url: {presigned_get_url}"
                logger.error(error_log)
                AppWrapper.update_status(Status.Failed.value, error_log)

            total_size = int(res.headers.get("content-length", 0))
            chunk_size = int(total_size / 10)
            bytes_so_far = 0

            pathlib.Path(download_path).parents[0].mkdir(
                parents=True, exist_ok=True
            )
            with open(download_path, "wb") as f:
                for data in res.iter_content(chunk_size=chunk_size):
                    f.write(data)
                    bytes_so_far += len(data)
                    progress = (bytes_so_far / total_size) * 100
                    logger.info(f"Download progress: {progress:.2f}%")
            logger.info(f"Finished download for '{key}'")

    def download_file_from_s3(self):
        """
        DO NOT USE THIS METHOD IN APP.
        This method is only for apps backend(toad).
        """
        for _, s3_path in enumerate(self.app_input_files):
            file_key = s3_path.split("/")[2]

            presigned_get_url = requests.get(
                f"{self.TOAD_HOST}/utils/presigned-download-url/?app_id={self.main_app_id}&task_id={self.task_id}&file_name={file_key}"
            ).json()["url"]

            res = requests.get(presigned_get_url)

            if res.status_code != 200:
                error_log = f"Failed: File download. \
                                    status code: {res.status_code} detail: {res.reason} \
                                    file_key: {file_key} presigned url: {presigned_get_url}"
                self.update_status(Status.Failed.value, error_log)

            logger.info(f"Starting download for '{file_key}'")

            file_path = os.path.join(self.file_folder, file_key)
            pathlib.Path(file_path).parents[0].mkdir(
                parents=True, exist_ok=True
            )

            with open(file_path, "wb") as f:
                f.write(res.content)
            logger.info(f"Finished download for '{file_key}'")

    def upload_file_to_s3(self, result):
        file_path = result["file_path"]
        file_name = file_path.split("/")[-1]

        presigned_put_url = requests.get(
            f"{self.TOAD_HOST}/utils/presigned-upload-url/?app_id={self.main_app_id}&task_id={self.task_id}&file_name={file_name}"
        ).json()["url"]

        with open(file_path, "rb") as file:
            res = requests.put(presigned_put_url, data=file)

        if res.status_code != 200:
            error_log = f"Failed: File upload. \
                            status code: {res.status_code} detail: {res.reason} \
                            file_key: {file_name} presigned url: {presigned_put_url}"
            self.update_status(Status.Failed.value, error_log)

    def update_status(self, status: Status, log: str):
        if status == Status.Failed.value:
            logger.error(log)
            requests.put(
                f"{AppWrapper.TOAD_HOST}/tasks/{AppWrapper.task_id}/status/{status}/log/",
                data=json.dumps({"log": f"[AppWrapper] {log}"}),
            )
            # Temp: set status Failed to DB, but pod still exists
            # exit()

        logger.info(log)
        requests.put(
            f"{self.TOAD_HOST}/tasks/{self.task_id}/status/{status}/log/",
            data=json.dumps({"log": f"[AppWrapper] {log}"}),
        )

    def validate_result_format(self, result: dict):
        if not isinstance(result, dict) or "type" not in result:
            error_log = "App result should include 'type' key"
            self.update_status(Status.Failed.value, error_log)

        if result["type"] == "link" and "url" not in result:
            error_log = "App result should include 'url' key for link type"
            self.update_status(Status.Failed.value, error_log)

        if result["type"] == "download" and "file_path" not in result:
            error_log = (
                "App result should include 'file_path' key for download type"
            )
            self.update_status(Status.Failed.value, error_log)

    def __call__(self, func):
        def inner(*args, **kwargs):
            if self.LOCAL_MODE:
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    logger.error(e)
            else:
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    logger.error(traceback.format_exc())

                    task_data = requests.get(
                        f"{self.TOAD_HOST}/tasks/{self.task_id}"
                    ).json()

                    status = task_data["Task"]["status"]

                    if status != Status.Canceled.value:
                        self.send_pod_log_to_s3()
                        self.update_status(Status.Failed.value, str(e))

                try:
                    self.validate_result_format(result)

                    if result["type"] == "download":
                        self.upload_file_to_s3(result)

                    data = {"task_id": self.task_id, "result": result}

                    self.send_pod_log_to_s3()
                    requests.post(
                        f"{self.TOAD_HOST}/output/", data=json.dumps(data)
                    )

                    self.update_status(
                        Status.Complete.value, log="App completed"
                    )

                except Exception as e:
                    error_log = f"Post app failed: {e}"
                    self.update_status(Status.Failed.value, error_log)

        return inner
