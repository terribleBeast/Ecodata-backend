from datetime import datetime
from typing import Annotated

from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import mapped_column


@as_declarative()
class BaseSqlModel:
    __abstract__ = True

    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_`%(constraint_name)s`",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


intpk = Annotated[int, mapped_column(primary_key=True)]

created_at_utc = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.utcnow(),
        server_default=func.timezone("utc", func.now()),
    ),
]

updated_at_utc = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.utcnow(),
        server_default=func.timezone("utc", func.now()),
        onupdate=lambda: datetime.utcnow(),
        server_onupdate=func.timezone("utc", func.now()),
    ),
]
