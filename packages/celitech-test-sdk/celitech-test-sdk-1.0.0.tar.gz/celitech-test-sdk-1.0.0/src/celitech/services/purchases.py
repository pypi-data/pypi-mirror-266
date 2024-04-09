from .utils.validator import Validator
from .utils.base_service import BaseService
from ..net.transport.serializer import Serializer
from ..models.utils.cast_models import cast_models
from ..models.top_up_esim_request import TopUpEsimRequest
from ..models.top_up_esim_ok_response import TopUpEsimOkResponse
from ..models.list_purchases_ok_response import ListPurchasesOkResponse
from ..models.get_purchase_consumption_ok_response import (
    GetPurchaseConsumptionOkResponse,
)
from ..models.edit_purchase_request import EditPurchaseRequest
from ..models.edit_purchase_ok_response import EditPurchaseOkResponse
from ..models.create_purchase_request import CreatePurchaseRequest
from ..models.create_purchase_ok_response import CreatePurchaseOkResponse


class PurchasesService(BaseService):

    @cast_models
    def list_purchases(
        self,
        iccid: str = None,
        after_date: str = None,
        before_date: str = None,
        after_cursor: str = None,
        limit: float = None,
        after: float = None,
        before: float = None,
    ) -> ListPurchasesOkResponse:
        """This endpoint can be used to list all the successful purchases made between a given interval.

        :param iccid: iccid, defaults to None
        :type iccid: str, optional
        :param after_date: Start date of the interval for filtering purchases in the format 'yyyy-MM-dd', defaults to None
        :type after_date: str, optional
        :param before_date: End date of the interval for filtering purchases in the format 'yyyy-MM-dd', defaults to None
        :type before_date: str, optional
        :param after_cursor: after_cursor, defaults to None
        :type after_cursor: str, optional
        :param limit: limit, defaults to None
        :type limit: float, optional
        :param after: Epoch value representing the start of the time interval for filtering purchases, defaults to None
        :type after: float, optional
        :param before: Epoch value representing the end of the time interval for filtering purchases, defaults to None
        :type before: float, optional
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: Successful Response
        :rtype: ListPurchasesOkResponse
        """

        Validator(str).is_optional().validate(iccid)
        Validator(str).is_optional().validate(after_date)
        Validator(str).is_optional().validate(before_date)
        Validator(str).is_optional().validate(after_cursor)
        Validator(float).is_optional().validate(limit)
        Validator(float).is_optional().validate(after)
        Validator(float).is_optional().validate(before)

        serialized_request = (
            Serializer(f"{self.base_url}/purchases", self.get_default_headers())
            .add_query("iccid", iccid)
            .add_query("afterDate", after_date)
            .add_query("beforeDate", before_date)
            .add_query("afterCursor", after_cursor)
            .add_query("limit", limit)
            .add_query("after", after)
            .add_query("before", before)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)

        return ListPurchasesOkResponse._unmap(response)

    @cast_models
    def create_purchase(
        self, request_body: CreatePurchaseRequest = None
    ) -> CreatePurchaseOkResponse:
        """This endpoint is used to purchase a new eSIM by providing the package details.

        :param request_body: The request body., defaults to None
        :type request_body: CreatePurchaseRequest, optional
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: Successful Response
        :rtype: CreatePurchaseOkResponse
        """

        Validator(CreatePurchaseRequest).is_optional().validate(request_body)

        serialized_request = (
            Serializer(f"{self.base_url}/purchases", self.get_default_headers())
            .serialize()
            .set_method("POST")
            .set_body(request_body)
        )

        response = self.send_request(serialized_request)

        return CreatePurchaseOkResponse._unmap(response)

    @cast_models
    def top_up_esim(self, request_body: TopUpEsimRequest = None) -> TopUpEsimOkResponse:
        """This endpoint is used to top-up an eSIM with the previously associated destination by providing an existing ICCID and the package details. The top-up is not feasible for eSIMs in "DELETED" or "ERROR" state.

        :param request_body: The request body., defaults to None
        :type request_body: TopUpEsimRequest, optional
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: Successful Response
        :rtype: TopUpEsimOkResponse
        """

        Validator(TopUpEsimRequest).is_optional().validate(request_body)

        serialized_request = (
            Serializer(f"{self.base_url}/purchases/topup", self.get_default_headers())
            .serialize()
            .set_method("POST")
            .set_body(request_body)
        )

        response = self.send_request(serialized_request)

        return TopUpEsimOkResponse._unmap(response)

    @cast_models
    def edit_purchase(
        self, request_body: EditPurchaseRequest = None
    ) -> EditPurchaseOkResponse:
        """This endpoint allows you to modify the dates of an existing package with a future activation start time. Editing can only be performed for packages that have not been activated, and it cannot change the package size. The modification must not change the package duration category to ensure pricing consistency.

        :param request_body: The request body., defaults to None
        :type request_body: EditPurchaseRequest, optional
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: Successful Response
        :rtype: EditPurchaseOkResponse
        """

        Validator(EditPurchaseRequest).is_optional().validate(request_body)

        serialized_request = (
            Serializer(f"{self.base_url}/purchases/edit", self.get_default_headers())
            .serialize()
            .set_method("POST")
            .set_body(request_body)
        )

        response = self.send_request(serialized_request)

        return EditPurchaseOkResponse._unmap(response)

    @cast_models
    def get_purchase_consumption(
        self, purchase_id: str
    ) -> GetPurchaseConsumptionOkResponse:
        """This endpoint can be called for consumption notifications (e.g. every 1 hour or when the user clicks a button). It returns the data balance (consumption) of purchased packages.

        :param purchase_id: purchase_id
        :type purchase_id: str
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: Successful Response
        :rtype: GetPurchaseConsumptionOkResponse
        """

        Validator(str).validate(purchase_id)

        serialized_request = (
            Serializer(
                f"{self.base_url}/purchases/{{purchaseId}}/consumption",
                self.get_default_headers(),
            )
            .add_path("purchaseId", purchase_id)
            .serialize()
            .set_method("GET")
        )

        response = self.send_request(serialized_request)

        return GetPurchaseConsumptionOkResponse._unmap(response)
