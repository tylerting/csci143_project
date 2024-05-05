SET max_parallel_maintenance_workers TO 80;
SET maintenance_work_mem TO '16 GB';

CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    age INTEGER
);

CREATE TABLE tweet_urls (
    id_tweets BIGINT,
    id_urls BIGINT,
    PRIMARY KEY (id_tweets, id_urls),
);

CREATE TABLE messages (
    id BIGSERIAL primary key,
    sender_id integer not null REFERENCES users(id),
    message text not null,
    created_at timestamp not null default current_timestamp,
    id_urls INTEGER REFERENCES urls(id_urls)
);


CREATE EXTENSION IF NOT EXISTS RUM;
CREATE EXTENSION IF NOT EXISTS pg_trgm;


