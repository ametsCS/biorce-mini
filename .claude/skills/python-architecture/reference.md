# Python Backend Architecture Reference

This document contains advanced configuration patterns and detailed reference for Python serverless backends.

## Dependency Injection with python-dependency-injector

### Application Container

```python
# app/startup.py
import logging

from dependency_injector import containers, providers

from app.configurations.logger import PascalCaseJSONFormatter
from application.invoice import ProcessInvoiceHandler
from domain.configurations import AppSettings
from infrastructure.storage import S3Storage


class ApplicationContainer(containers.DeclarativeContainer):
    config = providers.Singleton(AppSettings.from_environment)
    
    logger = providers.Singleton(
        lambda settings: _configure_logger(settings),
        settings=config
    )
    
    s3_storage = providers.Singleton(
        S3Storage,
        bucket=config.provided.aws.bucket,
        logger=logger,
        region=config.provided.aws.region,
        endpoint_url=config.provided.aws.endpoint_url,
    )
    
    process_invoice_handler = providers.Singleton(
        ProcessInvoiceHandler,
        storage=s3_storage,
        logger=logger,
    )


def _configure_logger(settings: AppSettings) -> logging.Logger:
    logger = logging.getLogger("boehringer")
    logger.setLevel(settings.logging.level)
    logger.propagate = False
    logger.handlers.clear()
    
    handler = logging.StreamHandler()
    handler.setFormatter(PascalCaseJSONFormatter(settings.application.name))
    logger.addHandler(handler)
    
    return logger
```

## Domain Configuration Classes

### Application Settings

```python
# domain/configurations/app_settings.py
import logging
import os
from dataclasses import dataclass, field
from typing import Any

from .aws_config import AwsConfig
from .logging_config import LoggingConfig


@dataclass
class AppSettings:
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    aws: AwsConfig = field(default_factory=AwsConfig)
    
    @classmethod
    def from_environment(cls) -> "AppSettings":
        app_config = ApplicationConfig()
        logging_config = LoggingConfig()
        
        log_level_str = os.getenv("LOG_LEVEL", "INFO")
        logging_config.level = getattr(logging, log_level_str, logging.INFO)
        
        return cls(
            application=app_config,
            logging=logging_config,
            aws=AwsConfig(),
        )
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "application": {"name": self.application.name},
            "logging": {"level": self.logging.level},
            "aws": {
                "region": self.aws.region,
                "endpoint_url": self.aws.endpoint_url,
                "bucket": self.aws.bucket,
            },
        }
```

### AWS Configuration

```python
# domain/configurations/aws_config.py
import os
from dataclasses import dataclass

@dataclass
class AwsConfig:
    region: str = "eu-west-1"
    endpoint_url: str | None = None
    bucket: str = ""
    
    def __post_init__(self):
        self.region = os.getenv("AWS_REGION", self.region)
        self.endpoint_url = os.getenv("AWS_ENDPOINT_URL")
        self.bucket = os.getenv("S3_BUCKET", self.bucket)
```

### Logging Configuration

```python
# domain/configurations/logging_config.py
import logging
from dataclasses import dataclass

@dataclass
class LoggingConfig:
    level: int = logging.INFO
    format: str = "json"
```

## Custom JSON Logger Formatter

```python
# app/configurations/logger/json_formatter.py
import json
import logging
from datetime import datetime, UTC
from typing import Any


class PascalCaseJSONFormatter(logging.Formatter):
    def __init__(self, app_name: str):
        super().__init__()
        self._app_name = app_name
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "Timestamp": datetime.now(UTC).isoformat(),
            "Level": record.levelname,
            "Logger": record.name,
            "Message": record.getMessage(),
            "Application": self._app_name,
        }
        
        if hasattr(record, "extra") and record.extra:
            log_entry["Extra"] = record.extra
        
        if record.exc_info:
            log_entry["Exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, default=str)
```

## LocalStack Testing Configuration

### Integration Test with LocalStack

Uses the shared `LocalStackContainer` wrapper from `boehringer-shared-test-ai`.

```python
# tests/integration/test_s3_storage.py
import pytest
from shared.containers import LocalStackContainer

from infrastructure.storage import S3Storage


@pytest.fixture(scope="module")
def localstack():
    container = LocalStackContainer(services=["s3"])
    container.start()
    yield container
    container.stop()


@pytest.fixture
def s3_storage(localstack):
    s3 = localstack.get_s3_client()
    s3.create_bucket(
        Bucket="test-bucket",
        CreateBucketConfiguration={"LocationConstraint": "eu-west-1"}
    )

    return S3Storage(
        bucket="test-bucket",
        logger=logging.getLogger("test"),
        endpoint_url=localstack.get_endpoint_url()
    )


@pytest.mark.asyncio
async def Should_SaveToS3_When_ValidContent(s3_storage):
    # Arrange
    request_id = "test-123"
    content = {"key": "value"}

    # Act
    actual = await s3_storage.save(request_id, content)

    # Assert
    assert "test-bucket" in actual
    assert request_id in actual
```

## Layer Dependencies

```text
┌─────────────────────────────────────────────────────────┐
│                    app/ (Presentation)                   │
│  lambda_handler.py, startup.py, configurations/          │
└─────────────────────────────────────────────────────────┘
                          │ depends on
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  infrastructure/                         │
│  storage/, notifications/, repositories/                 │
└─────────────────────────────────────────────────────────┘
                          │ depends on
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    application/                          │
│  {use_case}/models/, {use_case}/{handler}.py            │
└─────────────────────────────────────────────────────────┘
                          │ depends on
                          ▼
┌─────────────────────────────────────────────────────────┐
│                      domain/                             │
│  models/, ports/, configurations/, enums                 │
│              (NO EXTERNAL DEPENDENCIES)                  │
└─────────────────────────────────────────────────────────┘
```

## pyproject.toml Configuration

```toml
[project]
name = "my-lambda"
version = "1.0.0"
requires-python = ">=3.12"

dependencies = [
    "pydantic>=2.0",
    "boto3>=1.34",
    "aws-lambda-typing>=2.0",
    "dependency-injector>=4.41",
]

[project.optional-dependencies]
dev = [
    "pytest>=9.0",
    "pytest-asyncio>=0.23",
    "boehringer-shared-test-ai",
]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["Should_*"]
asyncio_mode = "auto"
```
