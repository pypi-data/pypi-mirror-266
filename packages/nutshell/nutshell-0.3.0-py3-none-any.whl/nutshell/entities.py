from enum import StrEnum, IntEnum
from typing import Optional

from pydantic import BaseModel, computed_field, Field


# TODO: Add more entities as needed
class ReportType(StrEnum):
    EFFORT = "Effort"
    PIPELINE = "Pipeline"


class FilterEntity(StrEnum):
    USERS = "Users"
    TEAMS = "Teams"
    ACTIVITY_TYPES = "Activity_Types"


class LeadStatus(IntEnum):
    OPEN = 0
    CANCELLED = 12
    LOST = 11
    WON = 10


class LeadQueryFilter(IntEnum):
    MY_LEADS = 0
    MY_TEAM_LEADS = 1
    ALL_LEADS = 2


class User(BaseModel):
    stub: bool = None
    id: int
    entity_type: str = Field(..., alias="entityType", pattern=r"Users")
    rev: str
    name: str
    first_name: str = Field(None, alias="firstName")
    last_name: str = Field(None, alias="lastName")
    is_enabled: bool = Field(..., alias="isEnabled")
    is_administrator: bool = Field(..., alias="isAdministrator")
    emails: list[str]
    modified_time: str = Field(..., alias="modifiedTime")
    created_time: str = Field(..., alias="createdTime")


class Team(BaseModel):
    stub: bool
    id: int
    name: str
    rev: str
    entity_type: str = Field(..., alias="entityType", pattern=r"Teams")
    modified_time: str = Field(..., alias="modifiedTime")
    created_time: str = Field(..., alias="createdTime")


class ActivityTypes(BaseModel):
    stub: bool
    id: int
    rev: str
    entity_type: str = Field(..., alias="entityType", pattern=r"Activity_Types")
    name: str


class SeriesData(BaseModel):
    total_effort: list[list[int]]
    successful_effort: list[list[int]]


class SummaryData(BaseModel):
    sum: float
    avg: float
    min: float
    max: float
    sum_delta: float
    avg_delta: float
    min_delta: float
    max_delta: float


class AnalyticsReport(BaseModel):
    series_data: SeriesData = Field(..., alias="seriesData")
    summary_data: dict[str, SummaryData] = Field(..., alias="summaryData")
    period_description: str = Field(..., alias="periodDescription")
    delta_period_description: str = Field(..., alias="deltaPeriodDescription")


class Stageset(BaseModel):
    id: int
    entity_type: str = Field(..., alias="entityType", pattern=r"Stagesets")
    name: str
    default: Optional[int] = None
    position: Optional[int] = None


class Milestone(BaseModel):
    id: int
    entity_type: str = Field(..., alias="entityType", pattern=r"Milestones")
    rev: str
    name: str
    position: Optional[int] = None
    stageset_id: Optional[int] = Field(None, alias="stagesetId")


class Lead(BaseModel):
    stub: Optional[bool] = None
    id: int
    entity_type: str = Field(..., alias="entityType", pattern=r"Leads")
    rev: str
    name: str
    html_url: Optional[str] = Field(None, alias="htmlUrl")
    tags: Optional[list[str]] = None
    description: str
    created_time: Optional[str] = Field(None, alias="createdTime")
    creator: Optional[User] = None
    milestone: Optional[Milestone] = None
    stageset: Optional[Stageset] = None
    status: int
    confidence: Optional[int] = None
    assignee: Optional[User | Team] = None
    due_time: str = Field(..., alias="dueTime")
    value: dict[str, float | str]
    normalized_value: Optional[dict[str, float | str]] = Field(None, alias="normalizedValue")


class FindLeadQuery(BaseModel):
    """For building a valid query for the findLeads method."""
    status: LeadStatus = LeadStatus.OPEN
    filter: LeadQueryFilter = LeadQueryFilter.ALL_LEADS
    milestone_id: Optional[int] = None
    milestone_ids: Optional[list[int]] = None
    stageset_id: Optional[int] = None
    stageset_ids: Optional[list[int]] = None
    due_time: Optional[str] = None
    assignee: Optional[list[User | Team]] = None
    number: Optional[int] = None

    @computed_field
    @property
    def query(self) -> dict:
        query_dict = {
            "status": self.status.value,
            "filter": self.filter.value
        }

        if self.milestone_id:
            query_dict["milestoneId"] = self.milestone_id
        if self.milestone_ids:
            query_dict["milestoneIds"] = self.milestone_ids
        if self.stageset_id:
            query_dict["stagesetId"] = self.stageset_id
        if self.stageset_ids:
            query_dict["stagesetIds"] = self.stageset_ids
        if self.due_time:
            query_dict["dueTime"] = self.due_time
        if self.assignee:
            query_dict["assignee"] = [
                {"entityType": entity.entity_type, "id": entity.id} for entity in self.assignee
            ]
        if self.number:
            query_dict["number"] = self.number

        return query_dict
