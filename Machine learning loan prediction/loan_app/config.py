import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
    DATABASE_PATH = os.getenv("DATABASE_PATH", "users.db")
    MODEL_BUNDLE_PATH = os.getenv("MODEL_BUNDLE_PATH", "model_bundle.joblib")
    TRAINING_DATA_PATH = os.getenv("TRAINING_DATA_PATH", "mldatset.csv")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
