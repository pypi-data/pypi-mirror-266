from collections.abc import Callable
import asyncio
import aiohttp
import logging
import pandas as pd
from flowtask.conf import GOOGLE_API_KEY
from flowtask.components import DtComponent
from flowtask.exceptions import ComponentError


logging.getLogger("aiohttp").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

class GoogleGeoCoding(DtComponent):
    base_url: str = "https://maps.googleapis.com/maps/api/geocode/json"

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop = None,
        job: Callable = None,
        stat: Callable = None,
        **kwargs,
    ) -> None:
        super(GoogleGeoCoding, self).__init__(loop=loop, job=job, stat=stat, **kwargs)
        self.semaphore = asyncio.Semaphore(10)  # Adjust the limit as needed

    async def start(self, **kwargs):
        self._counter: int = 0
        if self.previous:
            self.data = self.input
        if not hasattr(self, 'columns'):
            raise RuntimeError(
                'GoogleGeoCoding requires a Column Attribute'
            )
        if not isinstance(self.columns, list):
            raise RuntimeError(
                'GoogleGeoCoding requires a Column Attribute as list'
            )
        if not isinstance(self.data, pd.DataFrame):
            raise ComponentError(
                "Incompatible Pandas Dataframe", code=404
            )
        if not GOOGLE_API_KEY:
            raise ComponentError(
                "Google API Key is missing", code=404
            )
        return True

    async def get_coordinates(self, idx, row):
        async with self.semaphore:  # Use the semaphore to limit concurrent requests
            # if pd.notnull(row.get('formatted_address', None)):
            #     # already calculated:
            #     return idx, None
            # pd.isnull(row['latitude'])
            street_address = self.columns[0]
            if pd.notnull(row[street_address]):
                try:
                    address = ', '.join(row[self.columns])
                except TypeError:
                    address = row[street_address]
                if not address:
                    return idx, None
                params = {
                    "address": address,
                    "key": GOOGLE_API_KEY
                }
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(self.base_url, params=params) as response:
                            if response.status == 200:
                                result = await response.json()
                                if result['status'] == 'OK':
                                    data = result['results'][0]
                                    return idx, {
                                        "latitude": data['geometry']['location']['lat'],
                                        "longitude": data['geometry']['location']['lng'],
                                        "formatted_address": data['formatted_address'],
                                        "place_id": str(data['place_id'])
                                    }
                except asyncio.TimeoutError as exc:
                    self._logger.error(f"TimeoutException: {exc}")
                    return idx, None
                except TypeError as exc:
                    self._logger.error(f"TypeError: {exc}")
                    return idx, None
            return idx, None

    def column_exists(self, column: str):
        if column not in self.data.columns:
            self._logger.warning(
                f"Column {column} does not exist in the dataframe"
            )
            self.data[column] = None
            return False
        return True

    async def run(self):
        # initialize columns:
        self.column_exists('place_id')
        self.column_exists('latitude')
        self.column_exists('longitude')
        tasks = [
            self.get_coordinates(idx, row) for idx, row in self.data.iterrows()
            if pd.isnull(row['formatted_address'])
        ]
        results = await asyncio.gather(*tasks)
        for idx, result in results:
            self._counter += 1
            if result:
                for key, value in result.items():
                    self.data.at[idx, key] = value
        self.add_metric("DOWNLOADED", self._counter)
        # if self._debug is True:
        print(self.data)
        print("::: Printing Column Information === ")
        for column, t in self.data.dtypes.items():
            print(column, "->", t, "->", self.data[column].iloc[0])
        self._result = self.data
        return self._result

    async def close(self):
        pass
