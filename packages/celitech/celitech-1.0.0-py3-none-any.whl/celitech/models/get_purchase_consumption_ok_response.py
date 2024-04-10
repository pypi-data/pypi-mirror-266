from .utils.json_map import JsonMap
from .base import BaseModel


@JsonMap({"data_usage_remaining_in_bytes": "dataUsageRemainingInBytes"})
class GetPurchaseConsumptionOkResponse(BaseModel):
    """GetPurchaseConsumptionOkResponse

    :param data_usage_remaining_in_bytes: Remaining balance of the package in bytes, defaults to None
    :type data_usage_remaining_in_bytes: float, optional
    :param status: Status of the connectivity, possible values are 'ACTIVE' or 'NOT_ACTIVE', defaults to None
    :type status: str, optional
    """

    def __init__(self, data_usage_remaining_in_bytes: float = None, status: str = None):
        self.data_usage_remaining_in_bytes = data_usage_remaining_in_bytes
        self.status = status
