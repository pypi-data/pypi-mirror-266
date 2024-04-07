from sqlalchemy import Boolean, Column, DateTime, Integer, String, text, MetaData
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base(metadata=MetaData(schema="file_storage"))

data_to_insert = []


class File(Base):
    __tablename__ = "file"

    file_id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    file_name_with_extension = Column(String, nullable=False)
    file_content_type = Column(String, nullable=False, index=True)
    file_date_created = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    file_last_modified = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    file_system_file_name_with_extension = Column(String, nullable=False)
    file_system_relative_path = Column(String, server_default="", nullable=False)
    file_storage_token = Column(String, nullable=False, unique=True, index=True)
    file_purpose = Column(String, nullable=True, unique=False, index=True)
    file_is_deleted = Column(
        Boolean, nullable=False, index=True, server_default=text("false")
    )
    file_date_deleted = Column(DateTime(timezone=True), nullable=True)
