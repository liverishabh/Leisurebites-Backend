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
    profile_image      varchar(255),
    primary_category   varchar(50),
    starting_price     integer,
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
    id                  serial
        constraint category_pkey
            primary key,
    name                varchar(50)                            not null,
    tag_line            varchar(255),
    main_image_url      varchar(255),
    thumbnail_image_url varchar(255),
    is_active           boolean                  default true  not null,
    created_time        timestamp with time zone default now() not null,
    updated_time        timestamp with time zone default now() not null
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
    id                    bigserial
        constraint experience_slot_pkey
            primary key,
    experience_id         integer                                not null
        constraint experience_slot_experience_id_fkey
            references experience,
    start_time            timestamp with time zone               not null,
    end_time              timestamp with time zone               not null,
    remaining_guest_limit integer                                not null,
    is_active             boolean                  default true  not null,
    created_time          timestamp with time zone default now() not null,
    updated_time          timestamp with time zone default now() not null
);


-- Artist Slot
create table artist_slot
(
    id            serial
        primary key,
    artist_id     integer                                not null
        references supplier,
    price         numeric(10, 2)                         not null,
    start_time    timestamp with time zone               not null,
    end_time      timestamp with time zone               not null,
    venue_address text,
    venue_city    varchar(50),
    venue_state   varchar(50),
    venue_country varchar(50),
    is_booked     boolean                  default false not null,
    is_active     boolean                  default true  not null,
    created_time  timestamp with time zone default now() not null,
    updated_time  timestamp with time zone default now() not null
);


-- Promo Code
create type promocodetype as enum ('discount_flat', 'discount_percent');
create type promocodestatus as enum ('active', 'inactive', 'deleted');
create table promo_code
(
    id                   bigserial
        primary key,
    code                 varchar(100)                           not null,
    promo_code_type      promocodetype                          not null,
    description          text,
    min_purchase_amount  numeric(10, 2)                         not null,
    max_discount_amount  numeric(10, 2)                         not null,
    flat_discount_amount numeric(10, 2)                         not null,
    discount_percent     numeric(10, 2)                         not null,
    start_time           timestamp with time zone               not null,
    end_time             timestamp with time zone               not null,
    visible              boolean                                not null,
    status               promocodestatus                        not null,
    created_time         timestamp with time zone default now() not null,
    updated_time         timestamp with time zone default now() not null
);

create index ix_promo_code_code on promo_code (code);


-- Booking
create type bookingtype as enum ('experience', 'artist');
create type bookingstatus as enum ('pending_with_artist', 'pending', 'confirmed', 'cancelled', 'completed', 'failed');
create type bookingcancelledby as enum ('customer', 'supplier');
create table booking
(
    id                  bigserial
        primary key,
    booking_uuid        varchar(30)                            not null
        unique,
    booking_type        bookingtype                            not null,
    customer_id         bigint                                 not null
        references customer,
    supplier_id         integer                                not null
        references supplier,
    experience_slot_id  bigint
        references experience_slot,
    artist_slot_id      bigint
        references artist_slot,
    no_of_guests        integer                                not null,
    status              bookingstatus                          not null,
    sub_total           numeric(10, 2)                         not null,
    service_tax         numeric(10, 2)                         not null,
    promo_discount      numeric(10, 2),
    payable_amount      numeric(10, 2)                         not null,
    promo_code_id       bigint
        references promo_code,
    cancellation_time   timestamp with time zone,
    cancelled_by        bookingcancelledby,
    cancellation_reason text,
    confirmation_time   timestamp with time zone,
    created_time        timestamp with time zone default now() not null,
    updated_time        timestamp with time zone default now() not null
);


-- Payment
create type paymentstatus as enum ('pending', 'success', 'failed');
create type paymentmethod as enum ('cod', 'pg');
create table payment
(
    id               bigserial
        primary key,
    booking_id       bigint                                 not null
        references booking,
    amount           numeric(10, 2)                         not null,
    status           paymentstatus                          not null,
    transaction_code varchar(50)
        unique,
    payment_method   paymentmethod                          not null,
    pg_order_id      varchar(50),
    created_time     timestamp with time zone default now() not null,
    updated_time     timestamp with time zone default now() not null
);
