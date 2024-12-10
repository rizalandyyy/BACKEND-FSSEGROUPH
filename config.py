import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "mysql+mysqlconnector://{}:{}@{}:{}/{}".format(
        os.getenv("DB_USERNAME"),
        os.getenv("DB_PASSWORD"),
        os.getenv("DB_HOST"),
        os.getenv("DB_PORT"),
        os.getenv("DB_NAME")
    ))
    SQLALCHEMY_TRACK_MODIFICATIONS = False