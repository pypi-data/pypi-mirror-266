import subprocess

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    current_timestamp,
    from_utc_timestamp,
    lit,
    monotonically_increasing_id,
    to_date,
    xxhash64,
)
from pyspark.sql.types import StructType

from sefazetllib.config.CustomLogging import logger
from sefazetllib.factory.platform.Platform import Platform


class Spark(Platform):
    def __init__(self, name="Spark Job", configs=[]) -> None:
        self.name = name
        session = SparkSession.builder.appName(name)
        if configs != []:
            for config in configs:
                session = session.config(*config)
        self.session = session.getOrCreate()
        self.checkpoint_dir = f"/tmp/checkpoint/{name}"
        self.session.sparkContext.setCheckpointDir(self.checkpoint_dir)

    def __get_key_method(self, name):
        return {
            "SurrogateKey": xxhash64,
            "IncrementalKey": monotonically_increasing_id,
        }[name]

    def __define_properties(self, df, type_format, url, properties):
        if type_format == "jdbc":
            properties.pop("operation", None)
            properties["url"] = url

        return df.options(**properties)

    def __define_load(self, df, type_format, url):
        if type_format == "jdbc":
            return df.load()
        return df.load(url)

    def __define_save(self, df, type_format, url):
        if type_format == "jdbc":
            return df.save()
        return df.save(url)

    def columns_to_upper(self, df):
        return df.select([col(c).alias(c.upper()) for c in df.columns])

    def checkpoint(self, df):
        return df.checkpoint()

    def clean_checkpoint(self):
        try:
            cmd = ["hadoop", "fs", "-rm", "-r", self.checkpoint_dir]
            subprocess.check_call(
                cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        except subprocess.CalledProcessError:
            logger.error("Error deleting %s from HDFS", self.checkpoint_dir)
        except Exception as e:
            logger.error("Unexpected error: %s", str(e))

    def select_columns(self, df, columns):
        return df.select(*columns)

    def join(self, left, right, keys, how):
        if isinstance(keys, list):
            left_key, right_key = keys
        else:
            left_key = right_key = keys

        return left.join(right, left[left_key] == right[right_key], how)

    def union_by_name(self, left, right):
        return left.unionByName(right)

    def create_df(self, columns):
        schema = StructType([])
        df = self.session.createDataFrame([], schema)
        for cols in columns:
            df = df.withColumn(cols, lit(None))
        return df

    def read(self, **kwargs):
        type_format = kwargs["file_format"]
        url = kwargs["url"]
        format_properties = kwargs["format_properties"]
        optional = kwargs["optional"]
        columns = kwargs["columns"]
        duplicates = kwargs["duplicates"]

        df = self.session.read.format(type_format)

        if bool(format_properties):
            df = self.__define_properties(df, type_format, url, format_properties)

        try:
            df = self.__define_load(df, type_format, url)

            if bool(columns):
                df = df.select(columns)

            if duplicates:
                df = df.dropDuplicates()
            return df

        except Exception as e:
            if not optional:
                logger.error("The 'optional' attribute is set to False. Error: %s", e)
                raise Exception("erro dentro do SPARK", str(e))
            schema = StructType([])
            df = self.session.createDataFrame([], schema)
            for cols in columns:
                df = df.withColumn(cols, lit(None))
            return df

    def load(self, **kwargs):
        df = kwargs["df"]
        sk_name = kwargs["sk_name"]
        key = kwargs["key"]
        columns = kwargs["columns"]
        duplicates = kwargs["duplicates"]
        type_format = kwargs["file_format"]
        format_properties = kwargs["format_properties"]
        url = kwargs["url"]
        mode = kwargs["mode"]
        load_date = kwargs["load_date"]
        load_date_name = kwargs["load_date_name"]
        load_date_timestamp = kwargs["load_date_timestamp"]
        load_date_timezone = kwargs["load_date_timezone"]

        df_writer = df

        if load_date:
            timestamp_in_timezone = from_utc_timestamp(
                current_timestamp(), load_date_timezone
            )
            df_writer = df.withColumn(
                load_date_name,
                timestamp_in_timezone
                if load_date_timestamp
                else to_date(timestamp_in_timezone),
            )

        if hasattr(key, "name"):
            if key.name is not None:
                sk_name = key.name

            key.setMethod(self.__get_key_method(type(key).__name__))
            df_writer = df_writer.withColumn(sk_name, key.get())

        if bool(columns):
            df_writer = df_writer.select(
                list(dict.fromkeys([sk_name, *columns, load_date_name]))
            )

        if duplicates:
            df_writer = df_writer.dropDuplicates()

        writer_format = df_writer.write.format(type_format)

        if bool(format_properties):
            writer_format = self.__define_properties(
                writer_format, type_format, url, format_properties
            )

        if mode is not None:
            writer_format = writer_format.mode(mode)

        self.__define_save(writer_format, type_format, url)

        return df_writer
    
    def close_session(self):
        self.session.stop()
        return
