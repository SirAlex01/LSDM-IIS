SELECT s.title AS song_name,a.name AS artist_name, ss.popularity AS pop
FROM song s JOIN songartist sa ON s.id_song = sa.id_song
			JOIN artist a ON sa.id_artist = a.id_artist
			JOIN songSpotify ss ON s.id_song = ss.id_song
WHERE ss.popularity IS NOT NULL AND s.title IS NOT NULL AND a.name IS NOT NULL
ORDER BY ss.popularity DESC
LIMIT 10;

SELECT a.name AS artist_name, al.name AS album_name
FROM artist a JOIN albumartist aa ON a.id_artist = aa.id_artist
			JOIN album al ON aa.id_album = al.id_album
WHERE a.name IS NOT NULL AND al.name IS NOT NULL;

SELECT a.name AS artist_name
FROM artist a JOIN  songartist sa ON a.id_artist = sa.id_artist
WHERE a.name IS NOT NULL
GROUP BY a.name
HAVING COUNT(sa.id_song) > 3;

SELECT s.title AS song_name, al.name AS album_name
FROM song s JOIN album al ON s.id_album = al.id_album
WHERE s.title IS NOT NULL AND al.name IS NOT NULL;

SELECT DISTINCT s.title AS song_title, ss.uri AS spotify_uri, sy.url AS youtube_url
FROM song s JOIN songSpotify ss ON s.id_song = ss.id_song JOIN songYouTube sy ON s.id_song = sy.id_song
WHERE s.title IS NOT NULL AND ss.uri IS NOT NULL AND sy.url IS NOT NULL; 