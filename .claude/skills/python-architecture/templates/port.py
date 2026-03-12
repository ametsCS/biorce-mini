# mypy: ignore-errors
# Domain Port (Protocol Interface) Template
#
# Usage:
#     Copy this template and replace:
#     - IPortName with your interface name (always use I prefix)
#     - YourEntity with your actual domain entity type
#     - Add your specific methods
#     - Place in domain/ports/ folder, one interface per file
#     - Remove `# mypy: ignore-errors` after replacing placeholders
from typing import Optional, Protocol
from uuid import UUID


class YourEntity:
    # Replace with your actual domain entity import.


class IPortName(Protocol):
    async def get_by_id(self, id: UUID) -> Optional[YourEntity]: ...

    async def save(self, entity: YourEntity) -> None: ...

    async def delete(self, id: UUID) -> None: ...
