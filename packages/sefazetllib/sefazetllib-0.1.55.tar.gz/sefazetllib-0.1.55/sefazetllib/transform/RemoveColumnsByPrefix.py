from typing import Optional, Tuple

from pyspark.sql import DataFrame

from sefazetllib import Builder, field
from sefazetllib.transform.Transform import Transform


@Builder
class RemoveColumnsByPrefix(Transform):
    df: Optional[DataFrame] = None
    reference: str = field(default="")
    output: str = field(default="")
    column_prefix: str = field(default="")

    def execute(self) -> Tuple[str, DataFrame]:
        if not self.output:
            raise ValueError("Output cannot be None or empty.")

        if not self.column_prefix:
            raise ValueError("Column prefix cannot be None or empty.")

        filtered_columns = [
            col for col in self.df.columns if not col.startswith(self.column_prefix)
        ]

        if not filtered_columns:
            raise ValueError("No columns left after removing specified prefix.")

        return (self.output, self.df.select(*filtered_columns))
