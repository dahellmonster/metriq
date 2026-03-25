from sqlalchemy import Column, Integer, Float, String, DateTime, Date, UniqueConstraint
from metriq.database import Base


class HealthSample(Base):
    __tablename__ = "health_samples"

    id = Column(Integer, primary_key=True)

    timestamp = Column(DateTime, index=True, nullable=False)
    date = Column(Date, index=True, nullable=False)

    metric = Column(String, index=True, nullable=False)
    value = Column(Float, nullable=False)

    source = Column(String, default="apple_health")

    __table_args__ = (
        UniqueConstraint("timestamp", "metric", name="uq_sample"),
    )


class DailyMetrics(Base):
    __tablename__ = "daily_metrics"

    id = Column(Integer, primary_key=True)

    date = Column(Date, unique=True, index=True)

    # activity
    steps = Column(Integer, default=0)
    distance = Column(Float, default=0)
    flights_climbed = Column(Integer, default=0)

    # energy
    active_energy = Column(Float, default=0)
    basal_energy = Column(Float, default=0)

    # heart
    avg_heart_rate = Column(Float, nullable=True)

    # sleep (placeholder for now)
    sleep_hours = Column(Float, default=0)
    sleep_score = Column(Float, nullable=True)

    # nutrition
    calories_in = Column(Float, default=0)
    protein = Column(Float, default=0)
    carbs = Column(Float, default=0)
    fat = Column(Float, default=0)