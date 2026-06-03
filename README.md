# Information Integration of Four Music Datasets

**Large Scale Data Management — Course Project**

*Gabriele Matini & Alessio Maiola*

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Source Datasets](#2-source-datasets)
3. [Source Schema Formalization](#3-source-schema-formalization)
4. [Global Schema Design](#4-global-schema-design)
5. [Mapping Assertions](#5-mapping-assertions)
6. [Materialization with Pentaho](#6-materialization-with-pentaho)
7. [Queries on the Global Schema](#7-queries-on-the-global-schema)
8. [Virtualization of a Query](#8-virtualization-of-a-query)
9. [Repository Structure](#9-repository-structure)

---

## 1. Introduction

This project defines a complete **Information Integration System (IIS)** over four heterogeneous CSV datasets containing music-related data. The central objective is to reconcile overlapping and complementary information from the four sources into a single, coherent **global schema**, and to demonstrate two classical approaches to information integration:

| Approach | Description |
|---|---|
| **Materialization** | Data from every source is extracted, transformed, and physically loaded (ETL) into a unified relational database via Pentaho Data Integration (Kettle). |
| **Virtualization** | A query posed over the global schema is rewritten into an equivalent query over the original sources, and the equivalence is formally proved. |

The system follows the **Global-as-View (GAV)** paradigm: each relation of the global schema is defined as a view over the source relations through a set of mapping assertions expressed in first-order logic (FOL).

---

## 2. Source Datasets

Four CSV files serve as the heterogeneous data sources.

### 2.1 T1 — Top 100 Spotify Tracks (2010–2019)

A dataset of the top 100 tracks on Spotify from 2010 to 2019, including audio features and artist metadata.

| Column | Description |
|---|---|
| `title` | Song title |
| `artist` | Song artist |
| `genre` | Genre of the song |
| `year_released` | Year the song was released |
| `added` | Date the song was added to Spotify's Top Hits playlist |
| `bpm` | Beats Per Minute (tempo) |
| `nrgy` | Energy — how energetic the song is |
| `dnce` | Danceability — how easy it is to dance to |
| `dB` | Decibel — how loud the song is |
| `live` | Likelihood the song is a live recording |
| `val` | Valence — positivity of the song's mood |
| `dur` | Duration of the song |
| `acous` | Acousticness |
| `spch` | Speechiness — focus on spoken word |
| `pop` | Popularity score (not a ranking) |
| `top_year` | Year the song was a top hit |
| `artist_type` | Solo, duo, trio, or band |

### 2.2 T2 — Artists (MusicBrainz & Last.fm)

Rich artist metadata cross-referencing MusicBrainz and Last.fm identifiers.

| Column | Description |
|---|---|
| `mbid` | MusicBrainz ID |
| `artist_mb` | Artist name (MusicBrainz) |
| `artist_lastfm` | Artist name (Last.fm) |
| `country_mb` | Country (MusicBrainz) |
| `country_lastfm` | Country (Last.fm tags) |
| `tags_mb` | Tags on MusicBrainz (`;`-separated) |
| `tags_lastfm` | Tags on Last.fm (`;`-separated, frequency-sorted) |
| `listeners_lastfm` | Number of listeners on Last.fm |
| `scrobbles_lastfm` | Number of scrobbles on Last.fm |
| `ambiguous_artist` | `TRUE` if multiple artists share the same Last.fm page |

### 2.3 T3 — Spotify Tracks

A broader Spotify tracks dataset with identifiers, genre, album, popularity, and explicit-content flags.

| Column | Description |
|---|---|
| `id` | Unique Spotify track identifier |
| `name` | Track name |
| `genre` | Genre |
| `artists` | Artist name(s), comma-separated |
| `album` | Album name |
| `popularity` | Popularity score (0–100) |
| `duration_ms` | Duration in milliseconds |
| `explicit` | Explicit content flag |

> **Note:** The `artists` field is multi-valued. During schema formalization it is denormalized into a separate relation `T3_artists(name, artist)` containing one tuple per artist–song pair.

### 2.4 T4 — Spotify & YouTube Tracks

A combined Spotify and YouTube dataset providing audio features, Spotify URIs, and YouTube video metadata.

| Column | Description |
|---|---|
| `Id` | Track identifier |
| `Track` | Song name (Spotify) |
| `Artist` | Artist name |
| `Url_spotify` | Spotify URL |
| `Album` | Album name |
| `Album_type` | `single` or `album` |
| `Uri` | Spotify API URI |
| `Danceability` | 0.0–1.0 danceability score |
| `Energy` | 0.0–1.0 energy score |
| `Key` | Musical key (Pitch Class notation, −1 if undetected) |
| `Loudness` | Loudness in dB (typically −60 to 0) |
| `Speechiness` | Spoken-word presence (0.0–1.0) |
| `Acousticness` | Acoustic confidence (0.0–1.0) |
| `Instrumentalness` | Vocal absence likelihood (0.0–1.0) |
| `Liveness` | Live-performance probability (0.0–1.0) |
| `Valence` | Musical positiveness (0.0–1.0) |
| `Tempo` | Estimated BPM |
| `Duration_ms` | Duration in milliseconds |
| `Stream` | Number of Spotify streams |
| `Url_youtube` | YouTube video URL |
| `Title` | YouTube video title |
| `Channel` | YouTube channel name |
| `Views` | YouTube views |
| `Likes` | YouTube likes |
| `Comments` | YouTube comments |
| `Description` | YouTube video description |
| `Licensed` | Licensed content flag |
| `official_video` | Official video flag |

---

## 3. Source Schema Formalization

Each source is modeled as a relational predicate. For T3 the multi-valued `artists` column is split out:

```
T1(a_vec)                              — Top 100 tracks
T2(b_vec)                              — Artist metadata
T3(c1, c2, c3, c5, c6, c7, c8)        — Spotify tracks (without artists)
T3_artists(c2, c4)                     — Denormalized artist-song pairs from T3
T4(d_vec)                              — Spotify + YouTube tracks
```

This decomposition is essential because T3's `artists` field contains a serialized list; extracting it into `T3_artists` yields a clean first-normal-form relation suitable for join-based integration.

---

## 4. Global Schema Design

The global schema defines the target integrated database. It introduces surrogate identifiers (`SERIAL` primary keys) and decomposes the domain into seven relations capturing three core semantic objects — **Song**, **Artist**, and **Album** — plus their relationships and platform-specific metadata.

### 4.1 Relations

```sql
Album(id_album: SERIAL PK, name: VARCHAR)

Artist(id_artist: SERIAL PK, name: VARCHAR, type: VARCHAR,
       country: VARCHAR, num_listeners: INTEGER,
       num_scrobbles: INTEGER, is_ambiguous: BOOLEAN)

AlbumArtist(id_album: FK → Album, id_artist: FK → Artist)   — PK: (id_album, id_artist)

Song(id_song: SERIAL PK, title: VARCHAR, genre: VARCHAR,
     year: INTEGER, id_album: FK → Album)

SongArtist(id_song: FK → Song, id_artist: FK → Artist)      — PK: (id_song, id_artist)

SongSpotify(id_song: FK → Song, uri: VARCHAR, bpm: NUMERIC,
            danceability: NUMERIC, loudness: NUMERIC,
            liveness: NUMERIC, acousticness: NUMERIC,
            speechiness: NUMERIC, instrumentalness: NUMERIC,
            key: INTEGER, duration: BIGINT, popularity: INTEGER,
            explicit: BOOLEAN, added: DATE, top_year: INTEGER,
            streams: BIGINT)

SongYoutube(id_song: FK → Song, url: VARCHAR, channel: VARCHAR,
            views: BIGINT, likes: BIGINT, comments: BIGINT,
            description: TEXT, licensed: BOOLEAN,
            official_video: BOOLEAN)
```

### 4.2 Integrity Constraints

**Foreign key constraints** enforce referential integrity across the schema:

```
Song[id_album]        ⊆ Album[id_album]
AlbumArtist[id_album] ⊆ Album[id_album]
AlbumArtist[id_artist] ⊆ Artist[id_artist]
SongArtist[id_artist]  ⊆ Artist[id_artist]
SongArtist[id_song]    ⊆ Song[id_song]
SongSpotify[id_song]   ⊆ Song[id_song]
SongYoutube[id_song]   ⊆ Song[id_song]
```

Because duplicate elimination is performed *before* surrogate IDs are assigned, all non-ID fields in `Song`, `Album`, and `Artist` are functionally unique. Similarly, `SongSpotify` and `SongYoutube` hold at most one tuple per song, making `id_song` a primary key in both.

The physical DDL is in [`tables.sql`](tables.sql).

---

## 5. Mapping Assertions

The mapping follows a **Global-as-View (GAV)** approach expressed as first-order logic (FOL) implications. A key design decision is the **information hierarchy**: when multiple sources provide semantically identical attributes for the same song, a priority ordering determines which value is retained:

> **T3 > T4 > T1**

That is, T3 data takes precedence over T4, and T4 over T1. This ensures deterministic conflict resolution during materialization.

### 5.1 T3 Mapping — Highest Priority Source

All information from T3 is used. A single mapping assertion splits T3 tuples into the global schema tables:

```
Forall y, a. (T3(y) AND T3_artists(y2, a)) ->
    Exists id_album, id_song, id_artist. (
        Album(id_album, y5)
      AND Exists v. Artist(id_artist, a, v)
      AND AlbumArtist(id_album, id_artist)
      AND Exists year. Song(id_song, y2, y3, year, id_album)
      AND Exists uri, bpm, dan, liv, lou, ac, spe, ins, key, added, tyear, streams.
          SongSpotify(id_song, uri, bpm, dan, liv, lou, ac, spe, ins, key, y7, y6, y8, added, tyear, streams)
      AND SongArtist(id_song, id_artist)
    )
```

This guarantees the existence of corresponding Album, Artist, Song, SongSpotify, SongArtist, and AlbumArtist tuples for every track–artist pair in T3.

### 5.2 T4 Mapping — Second Priority

#### 5.2.1 Album and Artist Collection

T4 contributes additional Album and AlbumArtist information beyond T3, but only when the `Album_type` is `"album"`:

```
Forall z. (T4(z) AND z6 = "album") ->
    Exists id_album, id_song, id_artist. (
        Album(id_album, z5)
      AND Exists v. Artist(id_artist, z3, v)
      AND AlbumArtist(id_album, id_artist)
      AND Exists genre, year. Song(id_song, z2, genre, year, id_album)
    )
```

#### 5.2.2 Songs Present in Both T3 and T4

When the same song (matched by track name and artist) appears in both T3 and T4, a **mixed tuple** is produced that merges attributes from both sources according to the priority hierarchy (T3 attributes for genre, duration, popularity, explicit; T4 attributes for URI, audio features, streams, YouTube metadata):

```
Forall y, z, a. (T4(z) AND T3(y) AND T3_artists(y2, a) AND y2 = z2 AND a = z3) ->
    Exists id_song, id_album. (
        Exists year. Song(id_song, z2, y3, year, id_album)
      AND Exists added, tyear. SongSpotify(id_song, z7, z17, z8, z11, z15, z13, z12, z14, z10, y7, y6, y8, added, tyear, z19)
      AND SongYoutube(id_song, z20, z22, z23, z24, z25, z26, z27, z28)
    )
```

#### 5.2.3 Songs Only in T4

Songs in T4 with no counterpart in T3 are handled by a separate assertion with existentially quantified variables for the attributes that T3 would have provided:

```
Forall z. (T4(z) AND NOT Exists y, a. (T3(y) AND T3_artists(y2, a) AND y2 = z2 AND a = z3)) ->
    Exists id_song, id_artist, id_album. (
        Exists v. Artist(id_artist, z3, v)
      AND Exists genre, year. Song(id_song, z2, genre, year, id_album)
      AND SongArtist(id_song, id_artist)
      AND Exists dur, pop, exp, added, tyear.
          SongSpotify(id_song, z7, z17, z8, z11, z15, z13, z12, z14, z10, dur, pop, exp, added, tyear, z19)
      AND SongYoutube(id_song, z20, z22, z23, z24, z25, z26, z27, z28)
    )
```

### 5.3 T1 Mapping — Lowest Priority

T1 is integrated last. Four sub-cases cover all possible overlaps with T3 and T4:

| Case | Sources Present | Mapping |
|---|---|---|
| 5.3.1 | T1 ∩ T4 ∩ T3 | Most complete tuples; T1 contributes `year`, `added`, `top_year` |
| 5.3.2 | T1 ∩ T4 \ T3 | Genre from T1; explicit left existential |
| 5.3.3 | T1 ∩ T3 \ T4 | Audio features partially from T1 (bpm, danceability, liveness, acousticness, speechiness); URI, loudness, instrumentalness, key, streams existential |
| 5.3.4 | T1 only | All audio features from T1; creates Artist tuple with `type`; URI, loudness, instrumentalness, key, explicit, streams existential |

### 5.4 Artist Mapping

Artist information is scattered across all four sources with varying richness:

- **T3, T4**: provide only artist *names*
- **T1**: provides names and `artist_type` (solo/duo/trio/band)
- **T2**: provides names, country, listener counts, scrobble counts, ambiguity flag

Nine mapping assertions (numbered 9–17 in the paper) cover all combinations of source overlap (T2 only, T1∧T2, T1 only, T2∧T4, T1∧T4, T1∧T2∧T4, T1∧T3, T2∧T3, T1∧T2∧T3), each producing the most specific Artist tuple possible given the available attributes.

---

## 6. Materialization with Pentaho

The materialization is implemented as a **Pentaho Data Integration (Kettle)** transformation (`materialization.ktr`). The ETL pipeline performs the following high-level steps:

```mermaid
graph LR
    subgraph Sources
        CSV1[T1.csv]
        CSV2[T2.csv]
        CSV3[T3.csv]
        CSV4[T4.csv]
    end

    subgraph Pentaho ETL Pipeline
        A[CSV Input ×4] --> B[Select / Rename Fields]
        B --> C[Sort Rows]
        C --> D[Merge Join on title+artist]
        D --> E[Filter Rows — overlap cases]
        E --> F[Unique Rows — deduplication ×13]
        F --> G[Select Values — project to global schema columns]
    end

    subgraph Target DB — PostgreSQL
        G --> H[Table Output: album]
        G --> I[Table Output: artist]
        G --> J[Table Output: song]
        G --> K[Table Output: songSpotify]
        G --> L[Table Output: songYouTube]
        G --> M[Table Output: songArtist]
        G --> N[Table Output: albumArtist]
    end
```

### Key ETL Steps

| Pentaho Step Type | Count | Purpose |
|---|---|---|
| `CsvInput` | 4 | Ingest source CSV files |
| `SelectValues` | 8 | Column selection, renaming, type casting |
| `SortRows` | multiple | Pre-sort for merge joins |
| `MergeJoin` | 3 | Join sources on song title + artist name |
| `FilterRows` | 5 | Route rows based on overlap cases (T3∩T4, T4-only, T1∩T3∩T4, etc.) |
| `Unique rows` | 13 | Duplicate elimination before ID assignment |
| `TableOutput` | 4 | Load into PostgreSQL tables (`album`, `artist`, `song`, etc.) |

The target database is **PostgreSQL** (connection named `PostgresDB` in the Kettle file). Surrogate IDs are generated by PostgreSQL `SERIAL` columns upon insertion, replacing the existentially quantified ID variables from the formal mapping.

> **Important:** The materialization produces a *non-universal solution*: serial IDs replace labeled nulls, and standard SQL `NULL` values represent genuinely missing information.

---

## 7. Queries on the Global Schema

Five queries are defined both in **first-order logic (FOL)** and in **SQL** (see [`queries.sql`](queries.sql)).

### 7.1 Top 10 Songs by Popularity

**FOL (informal):** Return `(songname, artistname, popularity)` for the 10 songs with the highest Spotify popularity, expressed via a counting sub-formula that asserts there are *not* 10 distinct songs with strictly greater popularity.

**SQL:**
```sql
SELECT s.title AS song_name, a.name AS artist_name, ss.popularity AS pop
FROM song s
JOIN songartist sa ON s.id_song = sa.id_song
JOIN artist a ON sa.id_artist = a.id_artist
JOIN songSpotify ss ON s.id_song = ss.id_song
WHERE ss.popularity IS NOT NULL
  AND s.title IS NOT NULL
  AND a.name IS NOT NULL
ORDER BY ss.popularity DESC
LIMIT 10;
```

### 7.2 All Artists with Their Albums

**FOL:**
```
{(artistname, albumname) | Exists id_artist, id_album, v.
    AlbumArtist(id_artist, id_album) AND Artist(id_artist, artistname, v) AND Album(id_album, albumname)}
```

**SQL:**
```sql
SELECT a.name AS artist_name, al.name AS album_name
FROM artist a
JOIN albumartist aa ON a.id_artist = aa.id_artist
JOIN album al ON aa.id_album = al.id_album
WHERE a.name IS NOT NULL AND al.name IS NOT NULL;
```

### 7.3 Artists with More Than Three Songs

**FOL:** Assert the existence of four distinct song IDs in `SongArtist` for the same artist.

**SQL:**
```sql
SELECT a.name AS artist_name
FROM artist a
JOIN songartist sa ON a.id_artist = sa.id_artist
WHERE a.name IS NOT NULL
GROUP BY a.name
HAVING COUNT(sa.id_song) > 3;
```

### 7.4 Songs Belonging to an Album

**FOL:**
```
{(songname, albumname) | ∃id_song, id_album.
    Song(id_song, songname, ..., id_album) ∧ Album(id_album, albumname)}
```

**SQL:**
```sql
SELECT s.title AS song_name, al.name AS album_name
FROM song s
JOIN album al ON s.id_album = al.id_album
WHERE s.title IS NOT NULL AND al.name IS NOT NULL;
```

### 7.5 Songs with Both a Spotify URI and a YouTube URL

**FOL:**
```
{(songname, uri, url) | ∃id_song.
    Song(id_song, songname, ...) ∧ SongSpotify(id_song, uri, ...) ∧ SongYoutube(id_song, url, ...)}
```

**SQL:**
```sql
SELECT DISTINCT s.title AS song_title, ss.uri AS spotify_uri, sy.url AS youtube_url
FROM song s
JOIN songSpotify ss ON s.id_song = ss.id_song
JOIN songYouTube sy ON s.id_song = sy.id_song
WHERE s.title IS NOT NULL AND ss.uri IS NOT NULL AND sy.url IS NOT NULL;
```

---

## 8. Virtualization of a Query

As a complement to the materialization approach, we demonstrate **virtualization** (query rewriting) for a simple query: *find all album names*.

### 8.1 Query on the Global Schema

```
q_g = {(albumname) | ∃id_album. Album(id_album, albumname)}
```

### 8.2 Relevant Mapping Assertions

Only two mapping assertions populate the `Album` table:

```
(24)  Forall y. T3(y) -> Exists id_album. Album(id_album, y5)
(25)  Forall z. (T4(z) AND z6 = "album") -> Exists id_album. Album(id_album, z5)
```

Taking contrapositives:

```
(26)  Forall y. NOT Exists id_album. Album(id_album, y5)  ->  NOT T3(y)
(27)  Forall z. NOT Exists id_album. Album(id_album, z5)  ->  NOT T4(z) OR z6 != "album"
```

These contrapositives reveal that every Album tuple originates *exclusively* from T3 or T4. Therefore the certain answers of `q_g` must be exactly the album names extractable from T3 and T4.

### 8.3 Perfect Rewriting on the Source Schema

```
q_s = {(albumname) | Exists y. T3(y1, y2, y3, y4, albumname, ...)
                    OR Exists z. (T4(z1, z2, z3, z4, albumname, ...) AND z6 = "album")}
```

### 8.4 Proof of Equivalence (Perfect Rewriting)

We prove `cert(q_g, I) = cert(q_s, I)` for every source instance `I`:

**Direction 1 — `cert(q_s, I) ⊆ cert(q_g, I)`:**
Let `t ∈ cert(q_s, I)`. Suppose for contradiction that `t ∉ cert(q_g, I)`. Then no legal database `B` satisfying the mapping contains `Album(_, t)`. But by mapping assertions (24) and (25), every legal `B` *must* contain `Album(_, t)` because `t` appears as an album name in T3 or in T4 with `Album_type = "album"`. Contradiction.

**Direction 2 — `cert(q_g, I) ⊆ cert(q_s, I)`:**
Let `t' ∈ cert(q_g, I)`. Suppose `t' ∉ cert(q_s, I)`. Then `t'` does not appear as an album in any T3 tuple, nor in any T4 tuple with `Album_type = "album"`. But then both antecedents of mapping assertions (24) and (25) are vacuously false for `t'`, meaning no mapping assertion forces `Album(_, t')` into any legal database. Hence `t'` cannot be a certain answer of `q_g`, contradicting the hypothesis. ∎

### 8.5 Empirical Verification

The script [`virtualized_query.py`](virtualized_query.py) provides an empirical check of the proof above. It:

1. Reads album names from `T3.csv` (field: `album`).
2. Reads album names from `T4.csv` where `Album_type` contains `"album"`.
3. Fetches all album names from the materialized PostgreSQL database (`SELECT name FROM album`).
4. Computes the symmetric difference between `T3 U T4` and the database contents.

A symmetric difference of zero confirms that the materialization is consistent with the perfect rewriting — that is, the set of album names produced by the ETL matches exactly the set predicted by the source-level query `q_s`.

---

## 9. Repository Structure

| File | Description |
|---|---|
| [`tables.sql`](tables.sql) | DDL for the global schema (PostgreSQL): table creation and foreign key constraints |
| [`materialization.ktr`](materialization.ktr) | Pentaho Kettle transformation implementing the full ETL pipeline |
| [`queries.sql`](queries.sql) | Five SQL queries over the materialized global schema |
| [`virtualized_query.py`](virtualized_query.py) | Python script for empirical verification of the virtualized query |
| `README.md` | This documentation |

---

## License

This project was developed as part of the *Large Scale Data Management* course curriculum. All datasets used are publicly available.
