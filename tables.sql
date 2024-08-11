CREATE TABLE album (
    id_album SERIAL PRIMARY KEY,
    name VARCHAR(255)
);

CREATE TABLE artist (
    id_artist SERIAL PRIMARY KEY,
    name VARCHAR(500),
    type VARCHAR(255),
    country VARCHAR(500),
    num_listeners INTEGER,
    num_scrobbles INTEGER,
    is_ambiguous BOOLEAN
);

CREATE TABLE albumartist (
    id_album INTEGER NOT NULL,
    id_artist INTEGER NOT NULL,
    PRIMARY KEY (id_album, id_artist)
);

CREATE TABLE song (
    id_song SERIAL PRIMARY KEY,
    title VARCHAR(500),
    genre VARCHAR(255),
    year INTEGER,
    id_album INTEGER
);

CREATE TABLE songartist (
    id_song INTEGER NOT NULL,
    id_artist INTEGER NOT NULL,
    PRIMARY KEY (id_song, id_artist)
);


-- Aggiungi il vincolo di chiave esterna per id_album
ALTER TABLE albumartist
ADD CONSTRAINT fk_album
FOREIGN KEY (id_album) REFERENCES album(id_album);

-- Aggiungi il vincolo di chiave esterna per id_artist
ALTER TABLE albumartist
ADD CONSTRAINT fk_artist
FOREIGN KEY (id_artist) REFERENCES artist(id_artist);

-- Aggiungi il vincolo di chiave esterna per id_album
ALTER TABLE song
ADD CONSTRAINT fk_album
FOREIGN KEY (id_album) REFERENCES album(id_album);

-- 2. Aggiungi i vincoli di chiave esterna
ALTER TABLE songartist
ADD CONSTRAINT fk_song
FOREIGN KEY (id_song) REFERENCES song(id_song);

ALTER TABLE songartist
ADD CONSTRAINT fk_artist
FOREIGN KEY (id_artist) REFERENCES artist(id_artist);
