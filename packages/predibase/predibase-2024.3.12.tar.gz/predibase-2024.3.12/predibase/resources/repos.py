from __future__ import annotations

from predibase.pql import Session
from predibase.resource.model import create_model_repo, ModelRepo, get_model_repo


class Repos:
    def __init__(self, session: Session):
        self._session = session

    def create(self, name: str, description: str | None = None, exists_ok: bool = False) -> ModelRepo:
        return create_model_repo(
            self._session,
            name,
            description,
            engine=None,
            exists_ok=exists_ok,
        )

    def get(self, resource_id: str) -> ModelRepo:
        if resource_id.startswith("pb://repos/"):
            resource_id = resource_id[: len("pb://repos/")]

        return get_model_repo(self._session, resource_id)

    def delete(self, resource_id: str):
        repo = self.get(resource_id)
        endpoint = f"/models/repo/{repo.id}"
        return self._session.delete_json(endpoint)
