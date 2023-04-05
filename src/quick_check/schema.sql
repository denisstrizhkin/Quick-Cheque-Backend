drop table if exists user;

create table user (
  id        serial       primary key,
  name      varchar(50)  not null,
  email     varchar(50)  unique not null,
  password  varchar(16)  not null,
  photo_url varchar(100)
)
