from typing import Any, List, Optional, Tuple
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, round

from sefazetllib import Builder, field
from sefazetllib.transform.Transform import Transform

@Builder
class RoundColumns(Transform):
    df: Optional[DataFrame] = None
    reference: Optional[str] = None
    output: Optional[str] = None
    columns: Optional[List[str]] = None
    precision: int = field(default=2)

    def execute(self) -> Tuple[str, DataFrame]:
        exceeded_columns = set(self.columns) - set(self.df.columns)

        if exceeded_columns:
            raise Exception(
                f"The following columns do not exist in {self.reference}: {str(exceeded_columns)}"
            )

        rounded_columns = [
            column
            if column not in self.columns
            else round(col(column), self.precision).alias(column)
            for column in self.df.columns
        ]
        return (
            self.output,
            (self.df.select(rounded_columns)),
        )
        
