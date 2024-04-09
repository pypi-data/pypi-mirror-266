from typing import Any, Optional, Tuple

from pyspark.sql.functions import col
from sefazetllib import Builder, field
from sefazetllib.transform.Transform import Transform


@Builder
class ColumnsToLowerCase(Transform):
    df: Optional[Any] = None
    reference: str = field(default="")
    output: str = field(default="")

    def execute(self) -> Tuple[str, Any]:
        if self.output is None:
            self.output = self.reference

        return self.output, self.df.select(
            [col(column).alias(column.lower()) for column in self.df.columns]
        )
