import warnings
from typing import Any, Dict, List

import boto3

from sefazetllib.Builder import Builder, field
from sefazetllib.config.CustomLogging import logger
from sefazetllib.factory.platform.dataframe.Default import Default
from sefazetllib.factory.platform.Platform import Platform
from sefazetllib.load.Load import Load
from sefazetllib.utils.key import DefaultKey, Key


@Builder
class LoadS3(Load):
    warnings.warn(
        "The 'LoadS3' class is deprecated. Please use the 'LoadStorage' class with the protocol parameter (e.g., 's3a')."
    )
    platform: Platform = field(default=Default())
    file_format: str = field(default="")
    format_properties: Dict[str, Any] = field(default_factory=dict)
    reference: str = field(default="")
    url: str = field(default="")
    repository: str = field(default="")
    layer: str = field(default="")
    schema: str = field(default="")
    entity: str = field(default="")
    mode: str = field(default="")
    df_writer: Any = field(default="")
    duplicates: bool = field(default=False)
    key: Key = field(default=DefaultKey())
    columns: List = field(default_factory=list)
    load_date: bool = field(default=True)
    load_date_name: str = field(default="DAT_CARGA")
    load_date_timestamp: bool = field(default=False)
    load_date_timezone: str = field(default="UTC-3")

    def build_connection_string(self):
        self.url = f"s3a://{self.repository}/{self.layer}/{self.schema}/{self.entity}"
        return self.url

    def get_table_name(self):
        return self.entity.split("/")[-1] if "/" in self.entity else self.entity

    def delete_aws_glue_table(self, database, table):
        glue = boto3.client("glue")
        try:
            glue.delete_table(DatabaseName=database, Name=table)
        except glue.exceptions.EntityNotFoundException:
            logger.warning(
                "Attempted to delete table %s in AWS Glue's database %s, but the table does not exist. The deletion routine will be ignored.",
                table.upper(),
                database.upper(),
            )

    def execute(self, **kwargs):
        if isinstance(self.platform, Default):
            self.setPlatform(kwargs["platform"])

        local_repository = self.repository
        if local_repository == "":
            self.setRepository(kwargs["repository"])

        if kwargs:
            args = kwargs["args"]
            if args.loadRepository and local_repository == "":
                self.setRepository(args.loadRepository)

            if args.loadUrl:
                url = args.loadUrl
            else:
                url = self.build_connection_string()
        else:
            url = self.build_connection_string()

        sk_name = f"SK_{self.get_table_name()}"

        try:
            return (
                self.reference,
                self.platform.load(
                    df=self.df_writer,
                    sk_name=sk_name,
                    key=self.key,
                    columns=self.columns,
                    duplicates=self.duplicates,
                    file_format=self.file_format,
                    format_properties=self.format_properties,
                    url=url,
                    mode=self.mode,
                    load_date=self.load_date,
                    load_date_name=self.load_date_name,
                    load_date_timestamp=self.load_date_timestamp,
                    load_date_timezone=self.load_date_timezone,
                ),
            )
        except Exception as e:
            apache_hudi_type_conversion_exception = "org.apache.hudi.hive.HoodieHiveSyncException: Could not convert field Type"
            if (
                self.file_format == "hudi" or "org.apache.hudi"
            ) and apache_hudi_type_conversion_exception in str(e):
                database = self.format_properties[
                    "hoodie.datasource.hive_sync.database"
                ]
                table = self.get_table_name().lower()
                logger.info(
                    "Detected a change in data type. Deleting %s in AWS Glue's database %s to resolve the issue..",
                    table.upper(),
                    database.upper(),
                )
                self.delete_aws_glue_table(database, table)

            return (
                self.reference,
                self.platform.load(
                    df=self.df_writer,
                    sk_name=sk_name,
                    key=self.key,
                    columns=self.columns,
                    duplicates=self.duplicates,
                    file_format=self.file_format,
                    format_properties=self.format_properties,
                    url=url,
                    mode=self.mode,
                    load_date=self.load_date,
                    load_date_name=self.load_date_name,
                    load_date_timestamp=self.load_date_timestamp,
                    load_date_timezone=self.load_date_timezone,
                ),
            )
