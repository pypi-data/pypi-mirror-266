from annotated_types import Annotated
from pydantic import BeforeValidator
from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated

from supamodel.utils import check_int, title_case

CapitalStr = Annotated[str, AfterValidator(title_case)]
ForceInt = Annotated[int, BeforeValidator(check_int)]
