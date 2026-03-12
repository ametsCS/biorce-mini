# mypy: ignore-errors
# Application Handler Template
#
# Usage:
#     Copy this template and replace:
#     - HandlerName with your handler name (e.g., VerifyClaimHandler)
#     - HandlerRequest with your request model
#     - HandlerResponse with your response model
#     - Add your specific dependencies
import logging
from typing import Protocol

from pydantic import BaseModel, ConfigDict


class HandlerRequest(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    # Add request fields here


class HandlerResponse(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    # Add response fields here


class HandlerName:
    def __init__(
        self,
        # repository: IRepository,  # Add your dependencies
        logger: logging.Logger,
    ):
        # self._repository = repository
        self._logger = logger

    async def handler(self, request: HandlerRequest) -> HandlerResponse:
        self._logger.info("Processing request", extra={"request": request.model_dump()})

        # 1. Load domain entity if needed
        # entity = await self._repository.get_by_id(request.id)

        # 2. Execute domain logic
        # entity.do_something()

        # 3. Persist changes
        # await self._repository.save(entity)

        # 4. Return response
        return HandlerResponse(
            # Map result to response
        )
