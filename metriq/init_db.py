from metriq.database import engine, Base
import metriq.models

print("Creating DB...")
Base.metadata.create_all(bind=engine)
print("Done")