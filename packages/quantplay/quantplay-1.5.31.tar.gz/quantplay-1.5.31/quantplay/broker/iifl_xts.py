from quantplay.broker.xts import XTS
from quantplay.utils.constant import timeit


class IIFL(XTS):
    @timeit(MetricName="IIFL:__init__")
    def __init__(
        self,
        api_secret=None,
        api_key=None,
        md_api_key=None,
        md_api_secret=None,
        wrapper=None,
        md_wrapper=None,
        client_id=None,
        load_instrument=True,
    ):
        self.root_url = "https://ttblaze.iifl.com/"

        super().__init__(
            api_key=api_key,
            api_secret=api_secret,
            md_api_key=md_api_key,
            md_api_secret=md_api_secret,
            wrapper=wrapper,
            md_wrapper=md_wrapper,
            ClientID=client_id,
            load_instrument=load_instrument,
        )
