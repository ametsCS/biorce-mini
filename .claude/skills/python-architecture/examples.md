# Python Backend Architecture Examples

This document contains detailed code examples for implementing Domain-Driven Design and Clean Architecture in Python AWS Lambda functions.

## Domain Layer Examples

### Entity Example

```python
# domain/models/claim.py
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, UTC
from decimal import Decimal

class Claim(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    
    id: UUID
    policy_id: UUID
    claimant_name: str
    incident_date: datetime
    status: str = "submitted"
    amount_claimed: Decimal
    amount_approved: Optional[Decimal] = None
    verification_notes: Optional[str] = None
    
    @staticmethod
    def create(
        policy_id: UUID,
        claimant_name: str,
        incident_date: datetime,
        amount_claimed: Decimal
    ) -> 'Claim':
        if amount_claimed <= 0:
            raise ValueError("Claim amount must be positive")
        
        return Claim(
            policy_id=policy_id,
            claimant_name=claimant_name,
            incident_date=incident_date,
            amount_claimed=amount_claimed
        )
    
    def verify(self, notes: str) -> None:
        if self.status != "submitted":
            raise ValueError("Only submitted claims can be verified")
        self.status = "verified"
        self.verification_notes = notes
    
    def approve(self, approved_amount: Decimal) -> None:
        if self.status != "verified":
            raise ValueError("Only verified claims can be approved")
        if approved_amount > self.amount_claimed:
            raise ValueError("Approved amount cannot exceed claimed amount")
        
        self.status = "approved"
        self.amount_approved = approved_amount
    
    def reject(self, reason: str) -> None:
        if self.status not in ["submitted", "verified"]:
            raise ValueError("Cannot reject claim in current status")
        self.status = "rejected"
        self.verification_notes = reason
```

### Value Object Example

```python
# domain/models/money.py
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, field_validator

class Money(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    amount: Decimal
    currency: str
    
    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v: str) -> str:
        if len(v) != 3:
            raise ValueError('Currency must be 3 characters')
        return v.upper()
    
    def add(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(amount=self.amount + other.amount, currency=self.currency)
```

### Enum Example

```python
# domain/claim_status.py
from enum import Enum

class ClaimStatus(str, Enum):
    SUBMITTED = "submitted"
    VERIFIED = "verified"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"
```

### Domain Service Example

```python
# domain/claim_validation_service.py
from decimal import Decimal

class ClaimValidationService:
    @staticmethod
    def validate_claim_amount(
        claimed_amount: Decimal,
        policy_limit: Decimal,
        deductible: Decimal
    ) -> tuple[bool, str]:
        if claimed_amount <= deductible:
            return False, "Claim amount is below deductible"
        
        if claimed_amount > policy_limit:
            return False, f"Claim exceeds policy limit of {policy_limit}"
        
        return True, "Valid"
    
    @staticmethod
    def calculate_payable(
        claimed: Decimal,
        deductible: Decimal,
        coverage_pct: Decimal
    ) -> Decimal:
        after_deductible = claimed - deductible
        if after_deductible <= 0:
            return Decimal('0')
        return after_deductible * (coverage_pct / Decimal('100'))
```

### Repository Ports Examples

```python
# domain/ports/storage.py
from typing import Any, Protocol

class IStorage(Protocol):
    async def save(self, request_id: str, content: dict[str, Any]) -> str:
        ...
```

```python
# domain/ports/claim_repository.py
from typing import Protocol, Optional
from uuid import UUID
from domain.models import Claim

class IClaimRepository(Protocol):
    async def save(self, claim: Claim) -> None: ...
    async def get_by_id(self, claim_id: UUID) -> Optional[Claim]: ...
    async def delete(self, claim_id: UUID) -> None: ...
```

```python
# domain/ports/notification_service.py
from typing import Protocol
from uuid import UUID
from decimal import Decimal

class INotificationService(Protocol):
    async def send_claim_verified(self, email: str, claim_id: UUID) -> None: ...
    async def send_claim_approved(self, email: str, claim_id: UUID, amount: Decimal) -> None: ...
```

## Application Layer Examples

### Verify Claim Use Case

```python
# application/claim/verify/models/request.py
from pydantic import BaseModel, ConfigDict, field_validator
from uuid import UUID

class VerifyClaimRequest(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    
    claim_id: UUID
    verification_notes: str
    
    @field_validator('verification_notes')
    @classmethod
    def validate_notes(cls, v: str) -> str:
        if len(v) < 10:
            raise ValueError('Notes must be at least 10 characters')
        return v
```

```python
# application/claim/verify/models/response.py
from pydantic import BaseModel, ConfigDict
from uuid import UUID

class VerifyClaimResponse(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    
    claim_id: UUID
    status: str
```

```python
# application/claim/verify/verify_claim_handler.py
import logging

from application.claim.verify.models import VerifyClaimRequest, VerifyClaimResponse
from domain.ports import IClaimRepository

class VerifyClaimHandler:
    def __init__(
        self,
        claim_repository: IClaimRepository,
        logger: logging.Logger
    ):
        self._claim_repository = claim_repository
        self._logger = logger
    
    async def handler(self, request: VerifyClaimRequest) -> VerifyClaimResponse:
        claim = await self._claim_repository.get_by_id(request.claim_id)
        if not claim:
            raise ValueError(f"Claim {request.claim_id} not found")
        
        claim.verify(notes=request.verification_notes)
        
        await self._claim_repository.save(claim)
        
        self._logger.info(
            "Claim verified",
            extra={"claim_id": str(claim.id), "status": claim.status}
        )
        
        return VerifyClaimResponse(
            claim_id=claim.id,
            status=claim.status
        )
```

### Approve Claim Use Case

```python
# application/claim/approve/models/request.py
from pydantic import BaseModel, ConfigDict, field_validator
from uuid import UUID
from decimal import Decimal

class ApproveClaimRequest(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    
    claim_id: UUID
    approved_amount: Decimal
    
    @field_validator('approved_amount')
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v
```

```python
# application/claim/approve/approve_claim_handler.py
import logging

from application.claim.approve.models import ApproveClaimRequest, ApproveClaimResponse
from domain.ports import IClaimRepository, INotificationService

class ApproveClaimHandler:
    def __init__(
        self,
        claim_repository: IClaimRepository,
        notification_service: INotificationService,
        logger: logging.Logger
    ):
        self._claim_repository = claim_repository
        self._notification_service = notification_service
        self._logger = logger
    
    async def handler(self, request: ApproveClaimRequest) -> ApproveClaimResponse:
        claim = await self._claim_repository.get_by_id(request.claim_id)
        if not claim:
            raise ValueError(f"Claim {request.claim_id} not found")
        
        claim.approve(approved_amount=request.approved_amount)
        
        await self._claim_repository.save(claim)
        
        await self._notification_service.send_claim_approved(
            email="claimant@example.com",
            claim_id=claim.id,
            amount=request.approved_amount
        )
        
        self._logger.info(
            "Claim approved",
            extra={"claim_id": str(claim.id), "amount": str(request.approved_amount)}
        )
        
        return ApproveClaimResponse(
            claim_id=claim.id,
            status=claim.status,
            approved_amount=request.approved_amount
        )
```

## Infrastructure Layer Examples

### S3 Storage Implementation

```python
# infrastructure/storage/s3_storage.py
import json
import logging
from typing import Any

import boto3
from botocore.exceptions import ClientError


class S3Storage:
    def __init__(
        self,
        bucket: str,
        logger: logging.Logger,
        region: str = "eu-west-1",
        endpoint_url: str | None = None,
    ):
        self._bucket = bucket
        self._logger = logger
        self._region = region
        self._endpoint_url = endpoint_url
        
        client_kwargs = {"region_name": region}
        if endpoint_url:
            client_kwargs["endpoint_url"] = endpoint_url
        
        self._client = boto3.client("s3", **client_kwargs)
    
    async def save(self, request_id: str, content: dict[str, Any]) -> str:
        key = f"incoming/{request_id}.json"
        body = json.dumps(content)
        
        self._logger.info(
            "Saving request to S3",
            extra={"request_id": request_id, "bucket": self._bucket, "key": key}
        )
        
        try:
            self._client.put_object(
                Bucket=self._bucket,
                Key=key,
                Body=body,
                ContentType="application/json",
            )
            
            if self._endpoint_url:
                s3_url = f"{self._endpoint_url}/{self._bucket}/{key}"
            else:
                s3_url = f"https://{self._bucket}.s3.{self._region}.amazonaws.com/{key}"
            
            return s3_url
            
        except ClientError as e:
            self._logger.error(
                "Failed to upload object to S3",
                extra={"bucket": self._bucket, "key": key, "error": str(e)}
            )
            raise
```

### SES Notification Service Implementation

```python
# infrastructure/ses_notification_service.py
import boto3
from uuid import UUID
from decimal import Decimal

class SESNotificationService:
    def __init__(self, from_email: str):
        self._ses = boto3.client('ses')
        self._from_email = from_email
    
    def send_claim_verified(self, email: str, claim_id: UUID) -> None:
        self._ses.send_email(
            Source=self._from_email,
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': 'Claim Verified'},
                'Body': {'Text': {'Data': f'Your claim {claim_id} has been verified.'}}
            }
        )
    
    def send_claim_approved(self, email: str, claim_id: UUID, amount: Decimal) -> None:
        self._ses.send_email(
            Source=self._from_email,
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': 'Claim Approved'},
                'Body': {'Text': {'Data': f'Your claim {claim_id} approved for ${amount}.'}}
            }
        )
```

## Presentation Layer Example

```python
# app/lambda_handler.py
import asyncio
import logging
from typing import Any

from aws_lambda_typing import context

from app.startup import ApplicationContainer
from application.invoice import ProcessInvoiceHandler
from application.invoice.models import ProcessInvoiceResponse, VetClaimRequest

container = ApplicationContainer()
container.wire(modules=[__name__])
logger = container.logger()
process_invoice = container.process_invoice_handler()


def lambda_handler(
    event: dict[str, Any], lambda_context: context.Context | None = None
) -> dict[str, Any]:
    """AWS Lambda handler function."""
    return asyncio.get_event_loop().run_until_complete(_async_handler(event))


async def _async_handler(event: dict[str, Any]) -> dict[str, Any]:
    """Async implementation of the Lambda handler."""
    logger.info("Starting Lambda handler", extra={"event": event})
    
    try:
        request = VetClaimRequest(**event)
        result = await process_invoice.handler(request)
        
        logger.info(
            "Lambda handler completed successfully",
            extra={"result": result.model_dump()}
        )
        
        return result.model_dump()
    
    except (ValueError, KeyError, TypeError) as e:
        logger.error(
            f"Error while processing message: {e}",
            extra={"exception": {"type": type(e).__name__, "message": str(e)}}
        )
        raise ValueError("error while processing") from e
```

## Testing Example

```python
import pytest
from unittest.mock import AsyncMock, Mock
from uuid import uuid4
from decimal import Decimal
from datetime import datetime, UTC
import logging

from application.claim.verify.verify_claim_handler import VerifyClaimHandler
from application.claim.verify.models import VerifyClaimRequest, VerifyClaimResponse
from domain.models import Claim
from domain.ports import IClaimRepository


@pytest.mark.asyncio
async def Should_VerifyClaim_When_ClaimIsSubmitted() -> None:
    # Arrange
    claim_repo = AsyncMock(spec=IClaimRepository)
    logger = Mock(spec=logging.Logger)
    
    claim_id = uuid4()
    claim = Claim(
        id=claim_id,
        policy_id=uuid4(),
        claimant_name="John Doe",
        incident_date=datetime.now(UTC),
        amount_claimed=Decimal('1000')
    )
    claim_repo.get_by_id.return_value = claim
    
    sut = VerifyClaimHandler(
        claim_repository=claim_repo,
        logger=logger
    )
    
    request = VerifyClaimRequest(
        claim_id=claim_id,
        verification_notes="Documents verified and valid"
    )
    
    # Act
    actual = await sut.handler(request)
    
    # Assert
    assert actual.status == "verified"
    claim_repo.save.assert_awaited_once()
```
