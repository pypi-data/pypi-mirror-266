from typing import List
from .utils.json_map import JsonMap
from .base import BaseModel


@JsonMap(
    {
        "id_": "id",
        "data_limit_in_bytes": "dataLimitInBytes",
        "destination_name": "destinationName",
        "price_in_cents": "priceInCents",
    }
)
class Package(BaseModel):
    """Package

    :param id_: ID of the package, defaults to None
    :type id_: str, optional
    :param data_limit_in_bytes: Size of the package in Bytes, defaults to None
    :type data_limit_in_bytes: float, optional
    :param destination: ISO representation of the package's destination, defaults to None
    :type destination: str, optional
    :param destination_name: Name of the package's destination, defaults to None
    :type destination_name: str, optional
    :param price_in_cents: Price of the package in cents, defaults to None
    :type price_in_cents: float, optional
    """

    def __init__(
        self,
        id_: str = None,
        data_limit_in_bytes: float = None,
        destination: str = None,
        destination_name: str = None,
        price_in_cents: float = None,
    ):
        self.id_ = id_
        self.data_limit_in_bytes = data_limit_in_bytes
        self.destination = destination
        self.destination_name = destination_name
        self.price_in_cents = price_in_cents


@JsonMap({})
class PurchasesEsim(BaseModel):
    """PurchasesEsim

    :param iccid: ID of the eSIM, defaults to None
    :type iccid: str, optional
    """

    def __init__(self, iccid: str = None):
        self.iccid = iccid


@JsonMap(
    {
        "id_": "id",
        "start_date": "startDate",
        "end_date": "endDate",
        "created_date": "createdDate",
        "start_time": "startTime",
        "end_time": "endTime",
        "created_at": "createdAt",
    }
)
class Purchases(BaseModel):
    """Purchases

    :param id_: ID of the purchase, defaults to None
    :type id_: str, optional
    :param start_date: Start date of the package's validity in the format 'yyyy-MM-ddThh:mm:ssZZ', defaults to None
    :type start_date: str, optional
    :param end_date: End date of the package's validity in the format 'yyyy-MM-ddThh:mm:ssZZ', defaults to None
    :type end_date: str, optional
    :param created_date: Creation date of the purchase in the format 'yyyy-MM-ddThh:mm:ssZZ', defaults to None
    :type created_date: str, optional
    :param start_time: Epoch value representing the start time of the package's validity, defaults to None
    :type start_time: float, optional
    :param end_time: Epoch value representing the end time of the package's validity, defaults to None
    :type end_time: float, optional
    :param created_at: Epoch value representing the date of creation of the purchase, defaults to None
    :type created_at: float, optional
    :param package: package, defaults to None
    :type package: Package, optional
    :param esim: esim, defaults to None
    :type esim: PurchasesEsim, optional
    :param source: The source indicates where the eSIM was purchased, which can be from the API, dashboard, or landing-page. For purchases made before September 8, 2023, the value will be displayed as 'Not available'., defaults to None
    :type source: str, optional
    """

    def __init__(
        self,
        id_: str = None,
        start_date: str = None,
        end_date: str = None,
        created_date: str = None,
        start_time: float = None,
        end_time: float = None,
        created_at: float = None,
        package: Package = None,
        esim: PurchasesEsim = None,
        source: str = None,
    ):
        self.id_ = id_
        self.start_date = start_date
        self.end_date = end_date
        self.created_date = created_date
        self.start_time = start_time
        self.end_time = end_time
        self.created_at = created_at
        self.package = self._define_object(package, Package)
        self.esim = self._define_object(esim, PurchasesEsim)
        self.source = source


@JsonMap({"after_cursor": "afterCursor"})
class ListPurchasesOkResponse(BaseModel):
    """ListPurchasesOkResponse

    :param purchases: purchases, defaults to None
    :type purchases: List[Purchases], optional
    :param after_cursor: The cursor value representing the end of the current page of results. Use this cursor value as the "afterCursor" parameter in your next request to retrieve the subsequent page of results. It ensures that you continue fetching data from where you left off, facilitating smooth pagination., defaults to None
    :type after_cursor: str, optional
    """

    def __init__(self, purchases: List[Purchases] = None, after_cursor: str = None):
        self.purchases = self._define_list(purchases, Purchases)
        self.after_cursor = after_cursor
