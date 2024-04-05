import asyncio
from typing import Sequence

import aiohttp

from methods import _APIMethod
from responses import FindUsersResult, GetUserResult, GetAnalyticsReportResult, FindTeamsResult, \
    FindActivityTypesResult, _APIResponse, FindStagesetsResult, FindMilestonesResult, FindLeadsResult


class NutshellAPI:
    """Class to handle multiple API calls to the Nutshell API"""
    URL = "https://app.nutshell.com/api/v1/json"

    def __init__(self, username: str, password: str):
        self.auth = aiohttp.BasicAuth(username, password=password)
        self._api_calls = []

    @property
    def api_calls(self):
        return self._api_calls

    @api_calls.setter
    def api_calls(self, calls: Sequence[_APIMethod] | _APIMethod):
        if isinstance(calls, _APIMethod):
            self._api_calls = [calls]
        else:
            self._api_calls = calls

    async def call_api(self):
        tasks = []
        async with aiohttp.ClientSession() as session:
            for call in self._api_calls:
                tasks.append(self._fetch_report(session, call))
            responses = await asyncio.gather(*tasks)

            return self._map_results(responses)

    async def _fetch_report(self, session: aiohttp.ClientSession, call: _APIMethod) -> dict:
        payload = {"id": "apeye",
                   "jsonrpc": "2.0",
                   "method": call.api_method,
                   "params": call.params}
        async with session.post(self.URL, auth=self.auth, json=payload, ) as resp:
            info = await resp.json()
            return info

    def _map_results(self, results: list[dict]) -> list[tuple[_APIMethod, _APIResponse]]:
        call_response = []
        for idx, call in enumerate(self._api_calls):
            match call.api_method:
                case "findUsers":
                    call_response.append((call, FindUsersResult(**results[idx])))
                case "getUser":
                    call_response.append((call, GetUserResult(**results[idx])))
                case "findTeams":
                    call_response.append((call, FindTeamsResult(**results[idx])))
                case "findActivityTypes":
                    call_response.append((call, FindActivityTypesResult(**results[idx])))
                case "getAnalyticsReport":
                    call_response.append((call, GetAnalyticsReportResult(**results[idx])))
                case "findStagesets":
                    call_response.append((call, FindStagesetsResult(**results[idx])))
                case "findMilestones":
                    call_response.append((call, FindMilestonesResult(**results[idx])))
                case "findLeads":
                    call_response.append((call, FindLeadsResult(**results[idx])))

        return call_response
