from sqlalchemy import create_engine,Column, String,Integer,DATE, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from pydantic import BaseModel

class RestaurantsInfoSchema(BaseModel):
    id : int
    restaurants_id: int
    restaurant_name: str
    address: str
    quantity_free_tables: int
    quantity_of_tables: int

    class Config:
        orm_mode = True


class RegistrationSchema(BaseModel):
    username: str
    number_phone: str
    password: str

    class Config:
        orm_mode = True


class Authorization(BaseModel):
    username: str
    password: str


class TableReservationSchema(BaseModel):
    restaurants_id : int
    username : str
    number_phone : str
    count_people : int
    time_reservation : str
    period_booking : str
    date : str

    class Config:
        orm_mode = True


DATABASE_URL = ("postgresql+psycopg2://postgres:9785@127.0.0.1:5432/postgres")

engine = create_engine(DATABASE_URL)

Base = declarative_base()
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

session = SessionLocal()


class UserRegistration(Base): # Таблица зарегистрированных пользователей
    __tablename__ = 'user_registration'
    id = Column(Integer, primary_key=True)
    username = Column(String) # Имя пользователя
    number_phone = Column(String) # Номер телефона пользователя
    password = Column(String) # Пароль пользователя


class Restaurants(Base): # Список ресторанов
    __tablename__ = 'restaurants'
    id = Column(Integer, primary_key=True)
    restaurant_name = Column(String) # Название ресторана
    address = Column(String) # Адрес ресторана

    restaurants_info = relationship("RestaurantsInfo", back_populates="restaurant", uselist=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class RestaurantsInfo(Base): # Информация о ресторанах
    __tablename__ = 'restaurants_info'
    id = Column(Integer, primary_key=True)
    restaurants_id = Column(Integer,ForeignKey('restaurants.id', ondelete='CASCADE'),index=True) # Ссылка на id таблицы Restaurants
    quantity_free_tables = Column(Integer) # Кол-во свободных столов в ресторане
    quantity_of_tables = Column(Integer) # Общее кол-во столов в ресторане

    restaurant = relationship("Restaurants", back_populates="restaurants_info")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}



class TableReservation(Base): # Таблица брони
    __tablename__ = 'table_reservation'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user_registration.id', ondelete='CASCADE'),index=True)
    restaurants_id = Column(Integer, ForeignKey('restaurants.id', ondelete='CASCADE'),index=True) # Ссылка на id таблицы Restaurants
    username = Column(String) # Имя пользователя
    number_phone = Column(String) # Номер телефона пользователя
    count_people = Column(Integer) # Кол-во людей в брони
    time_reservation = Column(String) # Время брони
    period_booking = Column(String) # Время продолжительности брони
    date = Column(DATE)


r1 = Restaurants(
    restaurant_name='Restaurante mexicano',
    address='Маяковская 31'
)

r2 = Restaurants(
    restaurant_name='Restaurante mexicano',
    address='Хамовники 18'
)

r3 = Restaurants(
    restaurant_name='Restaurante mexicano',
    address='Лубянка 12'
)

r4 = Restaurants(
    restaurant_name='Restaurante mexicano',
    address='Чертаново 7'
)
r5 =  Restaurants(
    restaurant_name='Restaurante mexicano',
    address='Якиманка 28'
)

ri1 = RestaurantsInfo(
    restaurants_id = 1 ,
	quantity_free_tables = 10,
    quantity_of_tables = 10
)

ri2 = RestaurantsInfo(
    restaurants_id = 2,
	quantity_free_tables = 15,
    quantity_of_tables = 15
)

ri3 = RestaurantsInfo(
    restaurants_id = 3,
	quantity_free_tables = 20,
    quantity_of_tables = 20
)

ri4 = RestaurantsInfo(
    restaurants_id = 4,
	quantity_free_tables = 17,
    quantity_of_tables = 17
)

ri5 = RestaurantsInfo(
    restaurants_id = 5,
	quantity_free_tables = 8,
    quantity_of_tables = 8
)

def init_models():
    """Инициализация создания таблиц базы данных"""
    Base.metadata.create_all(bind=engine)



if __name__ == "__main__":
    session.bulk_save_objects([r1, r2, r3, r4, r5, ri1, ri2, ri3, ri4, ri5])
    session.commit()
    session.close()










