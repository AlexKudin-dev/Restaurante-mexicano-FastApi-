import uuid
import hashlib
from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, status
from fastapi.responses import HTMLResponse
from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessBearer
from db import UserRegistration,Restaurants ,RestaurantsInfo,TableReservation, get_db_session,\
               RegistrationSchema,Authorization,TableReservationSchema, init_models


access_security = JwtAccessBearer(secret_key='secret',access_expires_delta=timedelta(minutes=60))

def get_me(token: JwtAuthorizationCredentials = Depends(access_security)):
    user_id = token.subject['user_id']
    return user_id


_DESCRIPTION = """
Для работы с бронированием столика можно:
* **Зарегистрироваться**.
* **Авторизоваться**.
* **Посмотреть доступные рестораны**.
* **Получить информацию о ресторане.**
* **Забронировать столик.** 
* **Получить информацию о брони.**
* **Поменять время брони.**
* **Удалить бронь.**

**Токен действует 60 минут, после этого необходимо заново авторизоваться!**
"""

init_models()
app = FastAPI(title="Инструкция пользования API.",
              description=_DESCRIPTION,
              version="1.0.0",
              redoc_url=None)

@app.get("/", response_class=HTMLResponse, tags=["Main"])
async def root():
    """Представление страницы приветствия."""
    html_content = """
    <html>
    <head>
        <title>Restaurante mexicano</title>
    </head>
    <body>
        <h1 style="color: green; display: inline-block;">Restaurante</h1>
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/Flag_of_Mexico.svg/800px-Flag_of_Mexico.svg.png" height="30px" width="45px" style="display: inline-block; margin-left: 5px;">
        <h1 style="color: red; display: inline-block;">mexicano</h1>
        <div>
             <a href="/docs">Документация приведена по данному адресу</a> 
        </div>
    </body>
</html>
    """
    return HTMLResponse(content=html_content)


@app.post("/user-registration/",tags=["Регистрация пользователя"])
def user_registration(data : RegistrationSchema,session: Session = Depends(get_db_session)):
    """**Регистрация пользователя с хэшированием пароля.**"""
    salt = uuid.uuid4().hex
    hashed_password = hashlib.sha256(salt.encode() + data.password.encode()).hexdigest() + ':' + salt
    user = UserRegistration(username=data.username,number_phone = data.number_phone,password=hashed_password)
    try:
        session.add(user)
        session.commit()
        return {"message": "Вы успешно зарегистрировались."}
    except Exception as e:
        session.rollback()
        return {"message": str(e)}


@app.post("/user-login/",tags=["Авторизация пользователя"])
async def user_authorization(data : Authorization,session: Session = Depends(get_db_session)):
    """**Авторизация пользователя с выдачей токена.**"""
    for user in session.query(UserRegistration).filter(UserRegistration.username == data.username):
        hashed_password = user.password
        password, salt = hashed_password.split(':')
        if password == hashlib.sha256(salt.encode() + data.password.encode()).hexdigest(): # сравнение паролей
            user_payload = {"user_id": f"{user.id}", "role": "user"}
            return {"access": access_security.create_access_token(user_payload)}
        else:
            return {"message": "Не совпадает пароль!!!"}


@app.get("/restaurants/",tags=["Просмотр доступных ресторанов"])
def restaurants(session: Session = Depends(get_db_session)):
    return session.query(Restaurants).all()


@app.get("/restaurants-info/",tags=["Информация о ресторанах"])
def info_restaurants(session: Session = Depends(get_db_session)):
    restaurants = session.query(Restaurants, RestaurantsInfo). \
        join(RestaurantsInfo, Restaurants.id == RestaurantsInfo.restaurants_id). \
        all()
    return [dict(restaurant.as_dict(), **restaurant_info.as_dict()) for restaurant, restaurant_info in restaurants]


@app.get("/table-reservation-info/", tags=["Информация о брони"])
def booking_information(session: Session = Depends(get_db_session),
                        token: JwtAuthorizationCredentials = Depends(access_security)):
        if session.query(TableReservation).all() == []:
            return status.HTTP_204_NO_CONTENT
        else:
            return session.query(TableReservation).get(get_me(token))


@app.post("/table-reservation/",tags=["Бронь столика"])
def reservation(data : TableReservationSchema,
                session: Session = Depends(get_db_session),
                token: JwtAuthorizationCredentials = Depends(access_security)):
    """**Дата передается в формате yyyy-mm-dd**"""
    if data.count_people > 8:
        return {"message": "Вместимость столика не больше 8 человек!"}
    else:
        booking = TableReservation(user_id=get_me(token), # данные добавляются в таблицу TableReservation
                                   restaurants_id=data.restaurants_id,
                                   username=data.username,
                                   number_phone=data.number_phone,
                                   count_people=data.count_people,
                                   time_reservation=data.time_reservation,
                                   period_booking=data.period_booking,
                                   date=data.date)
        products_update = session.query(RestaurantsInfo).get(data.restaurants_id)
        if products_update.quantity_free_tables == 0:
            return {"message": "Cвободных столов нет!"}
        else:
            try:
                session.add(booking)
                products_update.quantity_free_tables = products_update.quantity_free_tables - 1
                session.commit() # После брони  свободных столов в ресторане становится меньше на 1
                return {"message": "Вы успешно забронировали столик!"}
            except  Exception as e:
                session.rollback()
                return {"message": str(e)}


@app.patch("/booking-patch/{time}/",tags=["Изменить время в брони"])
def booking_patch(time: str,
                  session: Session = Depends(get_db_session),
                  token: JwtAuthorizationCredentials = Depends(access_security)):
    """**Передав в параметр время в формате (hh:mm) вы поменяете время брони.**"""
    for booking in session.query(TableReservation).filter(TableReservation.user_id == get_me(token)):
        try:
            booking.time_reservation = time # обновление времени брони
            session.commit()
            return {"message": f"Вы поменяли время брони на {time}."}
        except Exception as e:
            session.rollback()
            return {"message": str(e)}


@app.delete("/booking-delete/{restaurants_id}/",tags=["Отменить бронь"])
def booking_delete(session: Session = Depends(get_db_session),
                  token: JwtAuthorizationCredentials = Depends(access_security)):
    """**Отмена брони по restaurants_id.**"""
    # Удаляется бронь в таблице TableReservation по токен
    for booking_del in session.query(TableReservation).filter(TableReservation.user_id == get_me(token)):
        try:
            session.delete(booking_del)
            add_table = session.query(RestaurantsInfo).get(booking_del.restaurants_id) # поиск ресторана по restaurants_id
            add_table.quantity_free_tables = add_table.quantity_free_tables + 1 # +1 означает что столик снова свободный
            session.commit()
            return {"message": "Бронь отменена!"}
        except Exception as e:
            session.rollback()
            return {"message": str(e)}





























