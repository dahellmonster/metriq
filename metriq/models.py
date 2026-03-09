from sqlalchemy import Column, Integer, String, Float, Date, DateTime, UniqueConstraint
from datetime import datetime

from metriq.database import Base


class NutritionLog(Base):
    __tablename__ = "nutrition_log"
    date = Column(Date, primary_key=True)
    calories = Column(Float)
    protein = Column(Float)
    carbs = Column(Float)
    fat = Column(Float)
    source = Column(String)

class ActivityLog(Base):
    __tablename__ = "activity_log"
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    activity_type = Column(String)
    category = Column(String)
    calories = Column(Float)
    duration = Column(Float)
    source = Column(String)

class BiometricsLog(Base):
    __tablename__ = "biometrics_log"
    date = Column(Date, primary_key=True)
    weight = Column(Float)
    bodyfat = Column(Float)
    source = Column(String)

class MetricsLog(Base):
    __tablename__ = "metrics_log"
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    metric = Column(String)
    value = Column(Float)
    unit = Column(String)
    source = Column(String)
    



class HealthRecord(Base):
    __tablename__ = "health_records"

    id = Column(Integer, primary_key=True)

    type = Column(String, index=True)
    value = Column(String)

    start_date = Column(DateTime, index=True)
    end_date = Column(DateTime)

    __table_args__ = (
        UniqueConstraint(
            "type",
            "start_date",
            "end_date",
            "value",
            name="unique_health_record"
        ),
    )
