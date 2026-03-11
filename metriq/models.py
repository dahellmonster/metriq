from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# --------------------------------------------------
# Nutrition (food intake)
# --------------------------------------------------

class NutritionLog(Base):

    __tablename__ = "nutrition_log"

    date = Column(Date, primary_key=True)

    calories = Column(Float)

    protein = Column(Float)

    carbs = Column(Float)

    fat = Column(Float)

    steps = Column(Float)

    weight = Column(Float)

    source = Column(String)


# --------------------------------------------------
# Activity tracking
# --------------------------------------------------

class ActivityLog(Base):

    __tablename__ = "activity_log"

    id = Column(Integer, primary_key=True)

    date = Column(Date)

    activity_type = Column(String)

    category = Column(String)

    calories = Column(Float)

    duration = Column(Float)

    source = Column(String)


# --------------------------------------------------
# Body metrics
# --------------------------------------------------

class BiometricsLog(Base):

    __tablename__ = "biometrics_log"

    date = Column(Date, primary_key=True)

    weight = Column(Float)

    bodyfat = Column(Float)

    source = Column(String)


# --------------------------------------------------
# Generic daily metrics
# --------------------------------------------------

class MetricsLog(Base):

    __tablename__ = "metrics_log"

    id = Column(Integer, primary_key=True)

    date = Column(Date)

    metric = Column(String)

    value = Column(Float)

    unit = Column(String)

    source = Column(String)


# --------------------------------------------------
# Raw health records ingestion
# --------------------------------------------------

class HealthRecord(Base):

    __tablename__ = "health_records"

    id = Column(Integer, primary_key=True)

    type = Column(String, index=True)

    value = Column(String)

    unit = Column(String)

    source = Column(String)

    start_date = Column(DateTime, index=True)

    end_date = Column(DateTime)


# --------------------------------------------------
# Sleep aggregation
# --------------------------------------------------

class SleepLog(Base):

    __tablename__ = "sleep_log"

    date = Column(Date, primary_key=True)

    hours = Column(Float)

    source = Column(String)