from entities import User, Team, ActivityTypes, AnalyticsReport, Stageset, Milestone, Lead

from pydantic import BaseModel


class _APIResponse(BaseModel):
    """Base class for all API responses."""
    result: list[BaseModel] | BaseModel


class FindUsersResult(_APIResponse):
    result: list[User]


class GetUserResult(_APIResponse):
    result: User


class FindTeamsResult(_APIResponse):
    result: list[Team]


class FindActivityTypesResult(_APIResponse):
    result: list[ActivityTypes]


class GetAnalyticsReportResult(_APIResponse):
    result: AnalyticsReport


class FindStagesetsResult(_APIResponse):
    result: list[Stageset]


class FindMilestonesResult(_APIResponse):
    result: list[Milestone]


class FindLeadsResult(_APIResponse):
    result: list[Lead]
