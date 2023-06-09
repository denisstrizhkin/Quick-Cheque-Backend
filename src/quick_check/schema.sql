drop table if exists t_room_associative;
drop table if exists t_product_item;
drop table if exists t_room_user_assoc;
drop table if exists t_cheque;
drop table if exists t_room;
drop table if exists t_user;

create table t_user (
  id        serial        primary key,
  name      varchar(50)   not null,
  email     varchar(50)   unique not null,
  password  varchar(102)  not null,
  photo_url varchar(100)
);

create table t_room (
  id       serial      primary key,
  name     varchar(30) not null,
  owner_id int         not null references t_user(id)
);

create table t_room_user_assoc (
  room_id int not null references t_room(id),
  user_id int not null references t_user(id),

  primary key (room_id, user_id)
);

create table t_cheque (
  id       serial      primary key,
  room_id  int         not null references t_room(id),
  owner_id int         not null references t_user(id),
  name     varchar(30) not null
);

create table t_product_item (
  id      int         primary key,
  name    varchar(30) not null,
  price   int         not null,
  count   int         not null,
  room_id int         not null references t_room(id)
);

create table t_room_associative (
  room_id int not null references t_room(id) on delete cascade,
  user_id int not null references t_user(id) on delete cascade,

  primary key (user_id, room_id)
);

--ProductID (FK -> ProductItem, int)
--UserID (FK -> User, int)
