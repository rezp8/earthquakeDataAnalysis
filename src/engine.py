from sqlalchemy import create_engine
from sqlalchemy.engine import URL

def get_engine():
    """
    creates a connection (Engine) to the sqlite database.
    earthquakes.db is created alongside the project.    
    """

    user = "root" # نام کاربری MySQL
    password = "" # رمز عبور MySQL
    host = "localhost" # اگر سرور محلی داری
    port = 3306 # پورت MySQL
    database = "earthquakeDB" # نام دیتابیس

    # url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"
    url = URL.create(
        drivername="mysql+pymysql",
        username=user,
        password=password,   # handles special chars like '@'
        host=host,
        port=port,
        database=database,
        query={"charset": "utf8mb4"},
    )
    return create_engine(url, future=True, pool_pre_ping=True)




# from sqlalchemy import create_engine

# def get_engine():
#     """
#     creates a connection (Engine) to the sqlite database.
#     earthquakes.db is created alongside the project.
#     """
#     return create_engine("sqlite:///earthquakes.db", future = True)
