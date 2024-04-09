from .utils.json_map import JsonMap
from .base import BaseModel


@JsonMap(
    {"smdp_address": "smdpAddress", "manual_activation_code": "manualActivationCode"}
)
class GetEsimOkResponseEsim(BaseModel):
    """GetEsimOkResponseEsim

    :param iccid: ID of the eSIM, defaults to None
    :type iccid: str, optional
    :param smdp_address: SM-DP+ Address, defaults to None
    :type smdp_address: str, optional
    :param manual_activation_code: The manual activation code, defaults to None
    :type manual_activation_code: str, optional
    :param status: Status of the eSIM, possible values are 'RELEASED', 'DOWNLOADED', 'INSTALLED', 'ENABLED', 'DELETED', or 'ERROR', defaults to None
    :type status: str, optional
    """

    def __init__(
        self,
        iccid: str = None,
        smdp_address: str = None,
        manual_activation_code: str = None,
        status: str = None,
    ):
        self.iccid = iccid
        self.smdp_address = smdp_address
        self.manual_activation_code = manual_activation_code
        self.status = status


@JsonMap({})
class GetEsimOkResponse(BaseModel):
    """GetEsimOkResponse

    :param esim: esim, defaults to None
    :type esim: GetEsimOkResponseEsim, optional
    """

    def __init__(self, esim: GetEsimOkResponseEsim = None):
        self.esim = self._define_object(esim, GetEsimOkResponseEsim)
