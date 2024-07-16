CREATE TABLE album (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    artist_id INT 
);

select * from artists