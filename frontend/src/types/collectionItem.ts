/*
Represents the API response shape returned by:
GET /collection-items/

This mirrors the backend CollectionItemRead schema.
*/

export interface Track {
  id: number;
  title: string;
  track_number: number | null;
  runtime_seconds: number | null;
  rating: number | null;
}

export interface CollectionItem {
  id: number;

  artist_name: string;
  album_title: string;

  release_year: number | null;
  genre: string | null;

  image_url: string | null;

  musicbrainz_id: string | null;
  discogs_id: string | null;

  condition: string | null;
  notes: string | null;

  location_name: string | null;

  price: number | null;
  album_rating: number | null;

  date_added: string;

  tags: string[];

  tracks: Track[];
}