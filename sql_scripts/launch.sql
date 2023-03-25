-- Customer
create table customer
(
    id              bigserial
        constraint customer_pkey
            primary key,
    created_time    timestamp with time zone default now() not null,
    updated_time    timestamp with time zone default now() not null,
    name            varchar(100),
    email_id        varchar                                not null,
    phone_no        varchar                                not null,
    hashed_password varchar,
    is_active       boolean                  default true  not null
);

create unique index ix_customer_phone_no
    on customer (phone_no);

create unique index ix_customer_email_id
    on customer (email_id);


-- Supplier
create type suppliertype as enum ('host', 'artist');
create type suppliergender as enum ('male', 'female', 'others');
create type supplierstatus as enum ('created', 'approval_pending', 'approved', 'rejected');
create table supplier
(
    id                 serial
        constraint supplier_pkey
            primary key,
    type               suppliertype                                               not null,
    description        text,
    alternate_phone_no varchar(20),
    gender             suppliergender,
    address            text,
    aadhar_number      varchar(20),
    status             supplierstatus           default 'created'::supplierstatus not null,
    created_time       timestamp with time zone default now()                     not null,
    updated_time       timestamp with time zone default now()                     not null,
    name               varchar(100),
    email_id           varchar                                                    not null,
    phone_no           varchar                                                    not null,
    hashed_password    varchar,
    is_active          boolean                  default true                      not null
);

create unique index ix_supplier_email_id
    on supplier (email_id);

create unique index ix_supplier_phone_no
    on supplier (phone_no);


-- Category
create table category
(
    id           serial
        constraint category_pkey
            primary key,
    name         varchar(50)                            not null,
    icon_image   varchar(255),
    is_active    boolean                  default true  not null,
    created_time timestamp with time zone default now() not null,
    updated_time timestamp with time zone default now() not null
);


-- Experience
create type experiencemode as enum ('physical', 'virtual');
create type experiencestatus as enum ('approval_pending', 'approved', 'rejected');
create table experience
(
    id               serial
        constraint experience_pkey
            primary key,
    host_id          integer                                                               not null
        constraint experience_host_id_fkey
            references supplier,
    category_id      integer                                                               not null
        constraint experience_category_id_fkey
            references category,
    host_declaration text                                                                  not null,
    title            varchar(50)                                                           not null,
    description      text,
    activities       text,
    mode             experiencemode                                                        not null,
    min_age          integer                                                               not null,
    guest_limit      integer                                                               not null,
    price_per_guest  integer                                                               not null,
    venue_address    text,
    venue_city       varchar(50),
    venue_state      varchar(50),
    venue_country    varchar(50),
    created_time     timestamp with time zone default now()                                not null,
    updated_time     timestamp with time zone default now()                                not null,
    status           experiencestatus         default 'approval_pending'::experiencestatus not null
);


-- Experience Image
create table experience_image
(
    id            bigserial
        constraint experience_image_pkey
            primary key,
    experience_id integer                                not null
        constraint experience_image_experience_id_fkey
            references experience,
    url           varchar(255)                           not null,
    is_active     boolean                  default true  not null,
    created_time  timestamp with time zone default now() not null,
    updated_time  timestamp with time zone default now() not null
);


-- Experience Slot
create table experience_slot
(
    id            bigserial
        constraint experience_slot_pkey
            primary key,
    experience_id integer                                not null
        constraint experience_slot_experience_id_fkey
            references experience,
    start_time    timestamp with time zone               not null,
    end_time      timestamp with time zone               not null,
    is_booked     boolean                  default false not null,
    is_active     boolean                  default true  not null,
    created_time  timestamp with time zone default now() not null,
    updated_time  timestamp with time zone default now() not null
);
