from requests import post

from galileo_core.constants.routes import Routes
from galileo_core.helpers.config import GalileoConfig
from galileo_core.schemas.core.project import CreateProjectRequest, ProjectResponse


def create_project(request: CreateProjectRequest, config: GalileoConfig) -> ProjectResponse:
    return ProjectResponse.model_validate(
        config.api_client.request(post, Routes.projects, json=request.model_dump(mode="json"))
    )
