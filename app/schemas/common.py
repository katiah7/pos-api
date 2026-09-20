from decimal import Decimal
from typing import Annotated

from pydantic import Field

Money = Annotated[Decimal, Field(ge=0, max_digits=10, decimal_places=2)]
