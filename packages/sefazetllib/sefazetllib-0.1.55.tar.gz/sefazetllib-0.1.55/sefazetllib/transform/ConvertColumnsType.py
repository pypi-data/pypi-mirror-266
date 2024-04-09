from typing import List, Optional, Tuple

from pyspark.sql import DataFrame
from pyspark.sql.functions import col
from pyspark.sql.types import DataType

from sefazetllib import Builder
from sefazetllib.transform.Transform import Transform


@Builder
class ConvertColumnsType(Transform):
    df: Optional[DataFrame] = None
    reference: Optional[str] = None
    output: Optional[str] = None
    columns: Optional[List[str]] = None
    data_type: Optional[DataType] = None

    def execute(self) -> Tuple[str, DataFrame]:
        exceeded_columns = set(self.columns) - set(self.df.columns)

        if exceeded_columns:
            raise Exception(
                f"The following columns do not exist in {self.reference}: {str(exceeded_columns)}"
            )

        converted_columns = [
            column if column not in self.columns else col(column).cast(self.data_type)
            for column in self.df.columns
        ]
        return (
            self.output,
            (self.df.select(converted_columns)),
        )
