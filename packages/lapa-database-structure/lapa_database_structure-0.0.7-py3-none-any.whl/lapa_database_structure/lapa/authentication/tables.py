from sqlalchemy import Column, Integer, String, MetaData, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base(metadata=MetaData(schema="authentication"))

data_to_insert = []


class User(Base):
    __tablename__ = 'user'

    u_id = Column(Integer, primary_key=True, nullable=False)
    uas_id = Column(Integer, nullable=True)
    u_unique_identifier = Column(Integer, unique=True, nullable=True)


class AuthenticationUsername(Base):
    __tablename__ = 'authentication_username'

    au_id = Column(Integer, primary_key=True, nullable=False)
    u_id = Column(Integer, nullable=True)
    au_username = Column(String(255), unique=True, nullable=False)
    au_hashed_password = Column(String(255), nullable=False)
    au_password_salt = Column(String(255), nullable=False)
    au_access_token = Column(String(255), nullable=False)
    au_refresh_token = Column(String(255), nullable=False)


class UserProfile(Base):
    __tablename__ = 'user_profile'

    up_id = Column(Integer, primary_key=True, nullable=False)
    u_id = Column(Integer,  nullable=True)


class UserAuthenticationRelationship(Base):
    __tablename__ = 'user_authentication_relationship'

    uar_id = Column(Integer, primary_key=True, nullable=False)
    u_id = Column(Integer, nullable=False)
    urt_id = Column(Integer, nullable=False)


class AuthenticationType(Base):
    __tablename__ = 'authentication_type'

    at_id = Column(Integer, primary_key=True, nullable=False)
    at_name = Column(String(45), nullable=True, unique=True)


class UserAccountStatus(Base):
    __tablename__ = 'user_account_status'

    uas_id = Column(Integer, primary_key=True, nullable=False)
    uas_name = Column(String(45), nullable=True, unique=True)


class UserLog(Base):
    __tablename__ = 'user_log'

    ul_id = Column(Integer, primary_key=True, nullable=False)
    u_id = Column(Integer, nullable=False)
    ul_datetime = Column(DateTime, nullable=True)
    uls_id = Column(Integer, nullable=False)


class UserLogStatus(Base):
    __tablename__ = 'user_log_status'

    uls_id = Column(Integer, primary_key=True, nullable=False)
    uls_name = Column(String(45), nullable=True, unique=True)


    # data_to_insert.extend([
    #     UserValidationStatus(status_description="pending"),
    #     UserValidationStatus(status_description="verified")
    # ])

