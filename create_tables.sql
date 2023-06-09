create table if not exists user_registration
(   
    id serial primary key,
	username varchar(50),
	number_phone varchar(50),
    "password" varchar(100)
);
comment on table user_registration is 'Таблица регистрации пользователя';
comment on column user_registration.username is 'Логин пользователя';
comment on column user_registration.number_phone is 'Номер телефона пользователя';
comment on column user_registration."password" is 'Пароль пользователя';


create table if not exists restaurants
(
    id serial primary key ,
    restaurant_name varchar(100),
    address varchar(100)
    
);
comment on table restaurants is 'Таблица ресторанов с адресами';
comment on column restaurants.restaurant_name is 'Название ресторана';
comment on column restaurants.address is 'Адрес ресторана';


create table if not exists restaurants_info
(
    id serial primary key,
	restaurants_id int  references restaurants(id),
	quantity_free_tables int not null,
    quantity_of_tables int not null
);
comment on table restaurants_info is 'Таблица с информацией по ресторану';
comment on column restaurants_info.restaurants_id is 'Ссылка на id из таблицы restaurants';
comment on column restaurants_info.quantity_free_tables is 'Кол-во свободных столов';
comment on column restaurants_info.quantity_of_tables is 'Общее кол-во столов в ресторане';


create table if not exists table_reservation
(
    user_id int primary key references user_registration(id),
	restaurants_id int references restaurants(id),
	username varchar(50),
	number_phone varchar(50),
	count_people int not null,
	time_reservation varchar(10),
	period_booking varchar(10)
	"date" date
);
comment on table table_reservation is 'Таблица бронирования столика';
comment on column table_reservation.restaurants_id is 'Ссылка на id из таблицы restaurants';
comment on column table_reservation.user_id is 'Ссылка на id из таблицы user_registration';
comment on column table_reservation.username is 'Имя пользователя';
comment on column table_reservation.number_phone is 'Номер телефона пользователя';
comment on column table_reservation.count_people is 'Кол-во людей';
comment on column table_reservation.time_reservation is 'Время брони';
comment on column table_reservation.period_booking is 'Время продолжительности брони';




