from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import Integer, String, Float, DateTime, UniqueConstraint, Index
from engine import get_engine

# پایه‌ی مدل‌ها
# Base = declarative_base()
class Base(DeclarativeBase):
    pass

class Earthquake(Base):
    __tablename__ = "Earthquakes"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    source = mapped_column(String(20), nullable=False)
    time = mapped_column(DateTime, nullable=False)
    latitude = mapped_column(Float, nullable=False)
    longitude = mapped_column(Float, nullable=False)
    depth = mapped_column(Float)
    magnitude = mapped_column(Float)
    region = mapped_column(String(100))
    place_raw = mapped_column(String(255))

    __table_args__ = (
        UniqueConstraint("source", "time", name = "uq_source_time"),
        Index("ix_time", "time"),
        Index("ix_region", "region"),
        Index("ix_magnitude", "magnitude"),
    )

    def __repr__(self):
        return f"<EQ {self.source} mag={self.magnitude} at {self.time}>"

def create_tables():
    """
    creates database tables using models.
    """
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("Database is ready.")

if __name__ == "__main__":
    create_tables()