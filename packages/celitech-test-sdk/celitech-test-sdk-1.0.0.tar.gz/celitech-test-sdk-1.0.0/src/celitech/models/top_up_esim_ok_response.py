from .utils.json_map import JsonMap
from .base import BaseModel


@JsonMap(
    {
        "id_": "id",
        "package_id": "packageId",
        "start_date": "startDate",
        "end_date": "endDate",
        "created_date": "createdDate",
        "start_time": "startTime",
        "end_time": "endTime",
    }
)
class TopUpEsimOkResponsePurchase(BaseModel):
    """TopUpEsimOkResponsePurchase

    :param id_: ID of the purchase, defaults to None
    :type id_: str, optional
    :param package_id: ID of the package, defaults to None
    :type package_id: str, optional
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
    """

    def __init__(
        self,
        id_: str = None,
        package_id: str = None,
        start_date: str = None,
        end_date: str = None,
        created_date: str = None,
        start_time: float = None,
        end_time: float = None,
    ):
        self.id_ = id_
        self.package_id = package_id
        self.start_date = start_date
        self.end_date = end_date
        self.created_date = created_date
        self.start_time = start_time
        self.end_time = end_time


@JsonMap({})
class TopUpEsimOkResponseProfile(BaseModel):
    """TopUpEsimOkResponseProfile

    :param iccid: ID of the eSIM, defaults to None
    :type iccid: str, optional
    """

    def __init__(self, iccid: str = None):
        self.iccid = iccid


@JsonMap({})
class TopUpEsimOkResponse(BaseModel):
    """TopUpEsimOkResponse

    :param purchase: purchase, defaults to None
    :type purchase: TopUpEsimOkResponsePurchase, optional
    :param profile: profile, defaults to None
    :type profile: TopUpEsimOkResponseProfile, optional
    """

    def __init__(
        self,
        purchase: TopUpEsimOkResponsePurchase = None,
        profile: TopUpEsimOkResponseProfile = None,
    ):
        self.purchase = self._define_object(purchase, TopUpEsimOkResponsePurchase)
        self.profile = self._define_object(profile, TopUpEsimOkResponseProfile)
