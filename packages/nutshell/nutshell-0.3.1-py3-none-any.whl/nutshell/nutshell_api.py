import asyncio
from typing import Sequence
from collections import namedtuple

import aiohttp

from nutshell.methods import _APIMethod
from nutshell.responses import FindUsersResult, GetUserResult, GetAnalyticsReportResult, FindTeamsResult, \
    FindActivityTypesResult, _APIResponse, FindStagesetsResult, FindMilestonesResult, FindLeadsResult

_MethodResponse = namedtuple("MethodResponse", ["method", "response"])


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

    def call_api(self):
        responses = asyncio.run(self._calling_api())

        return self._map_results(responses)

    async def _calling_api(self):
        tasks = []
        async with aiohttp.ClientSession() as session:
            for call in self._api_calls:
                tasks.append(self._fetch_report(session, call))
            responses = await asyncio.gather(*tasks)

        return responses

    async def _fetch_report(self, session: aiohttp.ClientSession, call: _APIMethod) -> dict:
        payload = {"id": "apeye",
                   "jsonrpc": "2.0",
                   "method": call.api_method,
                   "params": call.params}
        async with session.post(self.URL, auth=self.auth, json=payload, ) as resp:
            info = await resp.json()
            return info

    def _map_results(self, results: list[dict]) -> list[_MethodResponse[_APIMethod, _APIResponse]]:
        call_response = []
        for idx, call in enumerate(self._api_calls):
            match call.api_method:
                case "findUsers":
                    call_response.append(_MethodResponse(call, FindUsersResult(**results[idx])))
                case "getUser":
                    call_response.append(_MethodResponse(call, GetUserResult(**results[idx])))
                case "findTeams":
                    call_response.append(_MethodResponse(call, FindTeamsResult(**results[idx])))
                case "findActivityTypes":
                    call_response.append(_MethodResponse(call, FindActivityTypesResult(**results[idx])))
                case "getAnalyticsReport":
                    call_response.append(_MethodResponse(call, GetAnalyticsReportResult(**results[idx])))
                case "findStagesets":
                    call_response.append(_MethodResponse(call, FindStagesetsResult(**results[idx])))
                case "findMilestones":
                    call_response.append(_MethodResponse(call, FindMilestonesResult(**results[idx])))
                case "findLeads":
                    call_response.append(_MethodResponse(call, FindLeadsResult(**results[idx])))

        return call_response
