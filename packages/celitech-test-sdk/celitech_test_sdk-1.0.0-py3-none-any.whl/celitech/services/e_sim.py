from .utils.validator import Validator
from .utils.base_service import BaseService
from ..net.transport.serializer import Serializer
from ..models.utils.cast_models import cast_models
from ..models.get_esim_ok_response import GetEsimOkResponse
from ..models.get_esim_mac_ok_response import GetEsimMacOkResponse
from ..models.get_esim_history_ok_response import GetEsimHistoryOkResponse
from ..models.get_esim_device_ok_response import GetEsimDeviceOkResponse


class ESimService(BaseService):

    @cast_models
    def get_esim(self, iccid: str) -> GetEsimOkResponse:
        """Get status from eSIM

        :param iccid: iccid
        :type iccid: str
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: Successful Response
        :rtype: GetEsimOkResponse
        """

        Validator(str).validate(iccid)

        serialized_request = (
            Serializer(f"{self.base_url}/esim", self.get_default_headers())
            .add_query("iccid", iccid)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)

        return GetEsimOkResponse._unmap(response)

    @cast_models
    def get_esim_device(self, iccid: str) -> GetEsimDeviceOkResponse:
        """Get device info from an installed eSIM

        :param iccid: iccid
        :type iccid: str
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: Successful Response
        :rtype: GetEsimDeviceOkResponse
        """

        Validator(str).validate(iccid)

        serialized_request = (
            Serializer(
                f"{self.base_url}/esim/{{iccid}}/device", self.get_default_headers()
            )
            .add_path("iccid", iccid)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)

        return GetEsimDeviceOkResponse._unmap(response)

    @cast_models
    def get_esim_history(self, iccid: str) -> GetEsimHistoryOkResponse:
        """Get history from an eSIM

        :param iccid: iccid
        :type iccid: str
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: Successful Response
        :rtype: GetEsimHistoryOkResponse
        """

        Validator(str).validate(iccid)

        serialized_request = (
            Serializer(
                f"{self.base_url}/esim/{{iccid}}/history", self.get_default_headers()
            )
            .add_path("iccid", iccid)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)

        return GetEsimHistoryOkResponse._unmap(response)

    @cast_models
    def get_esim_mac(self, iccid: str) -> GetEsimMacOkResponse:
        """Get MAC from eSIM

        :param iccid: iccid
        :type iccid: str
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: Successful Response
        :rtype: GetEsimMacOkResponse
        """

        Validator(str).validate(iccid)

        serialized_request = (
            Serializer(
                f"{self.base_url}/esim/{{iccid}}/mac", self.get_default_headers()
            )
            .add_path("iccid", iccid)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)

        return GetEsimMacOkResponse._unmap(response)
