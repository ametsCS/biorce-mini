# mypy: ignore-errors
# Domain Entity Template
#
# Usage:
#     Copy this template and replace:
#     - EntityName with your entity name
#     - Add your specific properties
#     - Implement domain methods with business rules
from datetime import UTC, datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict


class EntityName(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    id: UUID
    # Add your properties here
    created_at: datetime
    updated_at: Optional[datetime] = None

    @staticmethod
    def create(
        # Add creation parameters here
    ) -> "EntityName":
        # Add validation logic here

        return EntityName(
            id=uuid4(),
            created_at=datetime.now(UTC),
            # Initialize other properties
        )

    def update(self, **kwargs) -> None:
        # Add update logic with business rules
        self.updated_at = datetime.now(UTC)
