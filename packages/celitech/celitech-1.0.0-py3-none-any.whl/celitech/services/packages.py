from .utils.validator import Validator
from .utils.base_service import BaseService
from ..net.transport.serializer import Serializer
from ..models.utils.cast_models import cast_models
from ..models.list_packages_ok_response import ListPackagesOkResponse


class PackagesService(BaseService):

    @cast_models
    def list_packages(
        self,
        destination: str = None,
        start_date: str = None,
        end_date: str = None,
        after_cursor: str = None,
        limit: float = None,
        start_time: int = None,
        end_time: int = None,
        duration: float = None,
    ) -> ListPackagesOkResponse:
        """List of available packages

        :param destination: destination, defaults to None
        :type destination: str, optional
        :param start_date: start_date, defaults to None
        :type start_date: str, optional
        :param end_date: end_date, defaults to None
        :type end_date: str, optional
        :param after_cursor: after_cursor, defaults to None
        :type after_cursor: str, optional
        :param limit: limit, defaults to None
        :type limit: float, optional
        :param start_time: start_time, defaults to None
        :type start_time: int, optional
        :param end_time: end_time, defaults to None
        :type end_time: int, optional
        :param duration: duration, defaults to None
        :type duration: float, optional
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: Successful Response
        :rtype: ListPackagesOkResponse
        """

        Validator(str).is_optional().validate(destination)
        Validator(str).is_optional().validate(start_date)
        Validator(str).is_optional().validate(end_date)
        Validator(str).is_optional().validate(after_cursor)
        Validator(float).is_optional().validate(limit)
        Validator(int).is_optional().validate(start_time)
        Validator(int).is_optional().validate(end_time)
        Validator(float).is_optional().validate(duration)

        serialized_request = (
            Serializer(f"{self.base_url}/packages", self.get_default_headers())
            .add_query("destination", destination)
            .add_query("startDate", start_date)
            .add_query("endDate", end_date)
            .add_query("afterCursor", after_cursor)
            .add_query("limit", limit)
            .add_query("startTime", start_time)
            .add_query("endTime", end_time)
            .add_query("duration", duration)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)

        return ListPackagesOkResponse._unmap(response)
