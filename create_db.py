import sqlite3

conn = sqlite3.Connection("database.sqlite3")
cursor = conn.cursor()

cursor.execute("""CREATE TABLE users (
    user_id integer UNIQUE,
    city text,
    status integer default 0,
    rating integer default 5,
    count_orders integer default 0,
    who_ref integer default 0
);""")

cursor.execute("""CREATE TABLE forms (
    model_id integer PRIMARY KEY,
    girl_name text NOT NULL,
    age integer NOT NULL,
    price_hour integer NOT NULL,
    about text NOT NULL,
    services text NOT NULL,
    photos text NOT NULL,
    nude_photos text NOT NULL,
    worker_id integer NOT NULL 
);""")

# cursor.execute("""CREATE TABLE settings (
#     card text NOT NULL default "22200700802944263",
#     usdt text NOT NULL default "THFXqJ2rJ7b2drxZjm3kD8wG5PNFZULRBy",
#     btc text NOT NULL default "1Ni7bVN1bzrETnp2ZVPgWxaM9EhbcjPCvt",
#     eth text NOT NULL default "0xAFF84e6411403D5B3AabB84dfaa3334662F1568f"
# );""")

cursor.execute("""CREATE TABLE workers (
    worker_id integer UNIQUE,
    count_ref integer default 0,
    count_forms integer default 0
);""")


