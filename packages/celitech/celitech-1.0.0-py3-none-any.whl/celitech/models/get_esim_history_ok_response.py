from typing import List
from .utils.json_map import JsonMap
from .base import BaseModel


@JsonMap({"status_date": "statusDate", "date_": "date"})
class History(BaseModel):
    """History

    :param status: The status of the eSIM at a given time, possible values are 'RELEASED', 'DOWNLOADED', 'INSTALLED', 'ENABLED', 'DELETED', or 'ERROR', defaults to None
    :type status: str, optional
    :param status_date: The date when the eSIM status changed in the format 'yyyy-MM-ddThh:mm:ssZZ', defaults to None
    :type status_date: str, optional
    :param date_: Epoch value representing the date when the eSIM status changed, defaults to None
    :type date_: float, optional
    """

    def __init__(
        self, status: str = None, status_date: str = None, date_: float = None
    ):
        self.status = status
        self.status_date = status_date
        self.date_ = date_


@JsonMap({})
class GetEsimHistoryOkResponseEsim(BaseModel):
    """GetEsimHistoryOkResponseEsim

    :param iccid: ID of the eSIM, defaults to None
    :type iccid: str, optional
    :param history: history, defaults to None
    :type history: List[History], optional
    """

    def __init__(self, iccid: str = None, history: List[History] = None):
        self.iccid = iccid
        self.history = self._define_list(history, History)


@JsonMap({})
class GetEsimHistoryOkResponse(BaseModel):
    """GetEsimHistoryOkResponse

    :param esim: esim, defaults to None
    :type esim: GetEsimHistoryOkResponseEsim, optional
    """

    def __init__(self, esim: GetEsimHistoryOkResponseEsim = None):
        self.esim = self._define_object(esim, GetEsimHistoryOkResponseEsim)
