import shlex
import subprocess

from lunar.config import Config
from lunar.data import BatchClient
from lunar.lunar_client import LunarError

BATCH_JOB_CHECK_STATUS_LIST = ["SUBMITTED", "PENDING", "RUNNABLE", "STARTING", "RUNNING"]


class AIDPService:
    def __init__(self, config: Config):
        if config.RUNTIME_ENV != "AIDP":
            raise LunarError(code=400, msg="AIDPService is only available on AIDP runtime")

        self.config = config
        self.batch_client = BatchClient(config=config)

    def copy_table_to_s3(
        self,
        database_name: str,
        table_name: str,
        db_type: str,
        operation: str,
        target_name: str = None,
        s3_dt: str = None,
        bq_table_partition: str = None,
        write_type: str = "json",
        max_num_files: int = 20,
    ):
        """
        Copy a table from AIDP BigQuery to BAP S3 and Database.

        ## Args

        - database_name: (str) Database name of Bigquery
        - table_name: (str) Name of a table on Bigquery
        - db_type: (str) Type of database to be loaded on BAP ('dynamodb' | 'es' | 's3')
        - operation: (str) Type of operation ('put' (db_type 's3' is only available on 'put') | 'update' | 'upsert' (only for db_type 'dynamodb') | 'delete')
        - target_name: (optional) (str) Target name on database to be loaded (Default: Value of `table_name`)
        - bq_table_partition: (optional) (str) Partition value of table on BigQuery
        - write_type: (optional) Write type ((default) 'json' | 'parquet')
        - max_num_files: (optional) (int) Maximum number of files to be saved on AWS S3 (default: 10)

        ## Returns
        dict

        ## Example

        ```python
        response = copy_table_to_s3(
            database_name="apollo",
            table_name="test_table",
            db_type="dynamodb",
            operation="put",
            target_name="test_data",
            s3_dt="20211101",
            write_type="json"
            bq_table_partition="2021-09-01",
        )


        ```
        """

        from skt.gcp import bq_table_to_df
        from skt.ye import get_spark

        spark = get_spark()
        # spark dataframe을 fs로 write 시 _SUCCESS 파일을 자동으로 생성하는 것을 방지
        spark.conf.set("mapreduce.fileoutputcommitter.marksuccessfuljobs", "false")

        assert db_type in [
            "dynamodb",
            "es",
            "s3",
        ], "`db_type` must be one of `dynamodb` / `es` / `s3`"
        assert operation in [
            "put",
            "update",
            "upsert",
            "delete",
        ], "`operation` must be one of `put` / `update` / `upsert` / `delete`"
        assert write_type in ["json", "parquet"], "`write_type` must be one of `json`, `parquet`"

        if db_type != "dynamodb" and operation == "upsert":
            raise LunarError(code=400, msg="Operation 'upsert' is only available for db_type 'dynamodb'")
        if db_type == "s3" and operation != "put":
            raise LunarError(code=400, msg="db_type 's3' is only available on operation 'put'")

        target_name = target_name if target_name else table_name

        job_name = f"{target_name}-{operation}"
        job_list = self.batch_client.get_batch_list(job_status_list=BATCH_JOB_CHECK_STATUS_LIST)

        if job_name in job_list:
            raise LunarError(code=400, msg=f"Job {job_name} is already submitted to BAP S3")

        s3_dt_str = f"dt={s3_dt}/" if s3_dt else ""

        s3_bucket_name = f"s3a://lunar-loader-{self.config.ENV.lower()}"
        s3_path = f"{s3_bucket_name}/{db_type}/{target_name}/{s3_dt_str}op={operation}"

        # BigQuery to BAP S3
        # 1) BigQuery to spark dataframe
        try:
            bq_df = bq_table_to_df(
                database_name, table_name, col_list="*", partition=bq_table_partition, spark_session=spark
            )
        except Exception as e:
            raise LunarError(code=400, msg=f"Fail to get BigQuery to spark dataframe {str(e)}")

        # 2) spark dataframe to BAP S3
        num_rows = bq_df.count()
        num_files = min(max_num_files, int(num_rows / 10000) + 1)  # 10,000건 당 1개 worker로 처리
        try:
            print(f"Writing on {s3_path}, '{num_rows}' rows")
            if write_type == "parquet":
                bq_df.repartition(num_files).write.mode("overwrite").parquet(s3_path)
            else:
                bq_df.repartition(num_files).write.mode("overwrite").json(s3_path)
        except Exception as e:
            raise LunarError(code=400, msg=f"Fail to write spark dataframe to BAP S3, Error: {str(e)}")

        process_touch = subprocess.Popen(shlex.split(f"hdfs dfs -touchz {s3_path}/_SUCCESS"))
        process_touch.wait()
        if process_touch.returncode != 0:
            raise LunarError(code=400, msg="Fail to touch '_SUCCESS' file")

        print(f"SUCCESS to write files from BigQuery to BAP S3, counts: {num_rows}")

    def copy_table_to_s3_without_load(
        self,
        database_name: str,
        table_name: str,
        directory_name: str = None,
        bq_table_partition: str = None,
        write_type: str = "parquet",
        max_num_files: int = 20,
    ):
        """
        Copy a table from AIDP BigQuery to BAP S3. (Not database loading)

        ## Args

        - database_name: (str) Database name of Bigquery
        - table_name: (str) Name of a table on Bigquery
        - directory_name: (optional) (str) Name of directory to save on BAP S3
        - bq_table_partition: (optional) (str) Partition value of table on BigQuery
        - write_type: (optional) Write type ('json' | (default) 'parquet')
        - max_num_files: (optional) (int) Maximum number of files to be saved on AWS S3 (default: 10)

        ## Returns
        dict

        ## Example

        ```python
        response = copy_table_to_s3_without_load(
            database_name="apollo",
            table_name="test_table",
            directory_name="movie",
            write_type="parquet"
            bq_table_partition="2021-09-01",
        )

        ```
        """

        from skt.gcp import bq_table_to_df
        from skt.ye import get_spark

        spark = get_spark()
        # spark dataframe을 fs로 write 시 _SUCCESS 파일을 자동으로 생성하는 것을 방지
        spark.conf.set("mapreduce.fileoutputcommitter.marksuccessfuljobs", "false")

        s3_path = f"s3a://aide-bucket-{self.config.ENV.lower()}/{directory_name}"

        # BigQuery to BAP S3
        # 1) BigQuery to spark dataframe
        try:
            bq_df = bq_table_to_df(
                database_name, table_name, col_list="*", partition=bq_table_partition, spark_session=spark
            )
        except Exception as e:
            raise LunarError(code=400, msg=f"Fail to get BigQuery to spark dataframe {str(e)}")

        # 2) spark dataframe to BAP S3
        num_rows = bq_df.count()
        num_files = min(max_num_files, int(num_rows / 10000) + 1)  # 10,000건 당 1개 worker로 처리
        try:
            print(f"Writing on {s3_path}, '{num_rows}' rows")
            if write_type == "parquet":
                bq_df.repartition(num_files).write.mode("overwrite").parquet(s3_path)
            else:
                bq_df.repartition(num_files).write.mode("overwrite").json(s3_path)
        except Exception as e:
            raise LunarError(code=400, msg=f"Fail to write spark dataframe to BAP S3, Error: {str(e)}")

        process_touch = subprocess.Popen(shlex.split(f"hdfs dfs -touchz {s3_path}/_SUCCESS"))
        process_touch.wait()
        if process_touch.returncode != 0:
            raise LunarError(code=400, msg="Fail to touch '_SUCCESS' file")

        print(f"SUCCESS to write files from BigQuery to BAP S3, counts: {num_rows}")
