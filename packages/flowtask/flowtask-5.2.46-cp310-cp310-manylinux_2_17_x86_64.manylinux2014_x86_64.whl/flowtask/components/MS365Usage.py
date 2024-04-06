import pandas as pd
from flowtask.components.Azure import Azure
from flowtask.exceptions import ComponentError


class MS365Usage(Azure):
    async def start(self, **kwargs):
        super().start()

        self.method = "GET"
        self.download = False

        _base_url = "https://graph.microsoft.com/v1.0/reports/getM365App{usage_method}(period='{period}')?$format=text/csv"
        self.url = _base_url.format(
            usage_method=self.usage_method,
            period=self.period,
        )

        return True

    async def run(self):
        """Run Azure Connection for getting Users Info."""
        self._logger.info(f"<{__name__}>:")
        self.set_apikey()

        try:
            result, error = await self.async_request(self.url, self.method)

        except Exception as ex:
            raise ComponentError(f"Error getting {self.usage_method} from API") from ex
        df = pd.read_csv(result, encoding="utf-8", header=0)

        self._result = df
        return self._result
    

    async def close(self):
        pass

    def set_apikey(self):
        self.app = self.get_msal_app()
        token, self.token_type = self.get_token()
        self.auth["apikey"] = token
