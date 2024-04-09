from .utils.json_map import JsonMap
from .base import BaseModel


@JsonMap(
    {
        "data_limit_in_gb": "dataLimitInGB",
        "start_date": "startDate",
        "end_date": "endDate",
        "start_time": "startTime",
        "end_time": "endTime",
    }
)
class TopUpEsimRequest(BaseModel):
    """TopUpEsimRequest

    :param iccid: ID of the eSIM
    :type iccid: str
    :param data_limit_in_gb: Size of the package in GB. The available options are 1, 2, 3, 5, 8, 20GB
    :type data_limit_in_gb: float
    :param start_date: Start date of the package's validity in the format 'yyyy-MM-dd'. This date can be set to the current day or any day within the next 12 months.
    :type start_date: str
    :param end_date: End date of the package's validity in the format 'yyyy-MM-dd'. End date can be maximum 60 days after Start date.
    :type end_date: str
    :param email: Email address where the purchase confirmation email will be sent (excluding QR Code & activation steps), defaults to None
    :type email: str, optional
    :param start_time: Epoch value representing the start time of the package's validity. This timestamp can be set to the current time or any time within the next 12 months., defaults to None
    :type start_time: float, optional
    :param end_time: Epoch value representing the end time of the package's validity. End time can be maximum 60 days after Start time., defaults to None
    :type end_time: float, optional
    """

    def __init__(
        self,
        iccid: str,
        data_limit_in_gb: float,
        start_date: str,
        end_date: str,
        email: str = None,
        start_time: float = None,
        end_time: float = None,
    ):
        self.iccid = iccid
        self.data_limit_in_gb = data_limit_in_gb
        self.start_date = start_date
        self.end_date = end_date
        self.email = email
        self.start_time = start_time
        self.end_time = end_time
