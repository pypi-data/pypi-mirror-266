from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData


Base = declarative_base(metadata=MetaData(schema="public"))

data_to_insert = []

