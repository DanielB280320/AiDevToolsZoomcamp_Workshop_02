from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app import schemas
from app.sources import DataSource, get_data_source

router = APIRouter(prefix="/api")

SourceDep = Annotated[DataSource, Depends(get_data_source)]


def _errors(not_found: str) -> dict:
    return {
        404: {"model": schemas.Error, "description": not_found},
        503: {"model": schemas.Error, "description": "The sports data provider failed and no cached copy is available."},
    }


@router.get("/leagues", tags=["leagues"], operation_id="listLeagues", summary="List all competitions")
def list_leagues(source: SourceDep) -> list[schemas.League]:
    return source.list_leagues()


@router.get(
    "/leagues/{leagueId}/standings",
    tags=["leagues"],
    operation_id="getLeagueStandings",
    summary="Get a league's standings table",
    response_model_exclude_none=True,
    responses=_errors("No league with this id."),
)
def get_league_standings(league_id: Annotated[str, Path(alias="leagueId")], source: SourceDep) -> schemas.Standings:
    return source.get_standings(league_id)


@router.get(
    "/teams/{teamId}",
    tags=["teams"],
    operation_id="getTeamDetail",
    summary="Get team detail",
    response_model_exclude_none=True,
    responses=_errors("No team with this id."),
)
def get_team_detail(team_id: Annotated[str, Path(alias="teamId")], source: SourceDep) -> schemas.TeamDetail:
    return source.get_team_detail(team_id)
