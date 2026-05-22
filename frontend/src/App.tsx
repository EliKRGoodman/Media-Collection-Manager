import "./App.css";

import { useEffect, useState } from "react";

import { getCollectionItems } from "./services/api";

import type { CollectionItem } from "./types/collectionItem";


/*
Main application component.

Current frontend goal:
- fetch collection items from FastAPI
- display each owned album copy as a visual card
*/
function App() {
  const [items, setItems] = useState<CollectionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /*
  Load collection items once when the app first renders.
  */
  useEffect(() => {
    async function loadCollection() {
      try {
        const data = await getCollectionItems();
        setItems(data);
      } catch (err) {
        setError("Failed to load collection.");
      } finally {
        setLoading(false);
      }
    }

    loadCollection();
  }, []);

  if (loading) {
    return <div className="page">Loading collection...</div>;
  }

  if (error) {
    return <div className="page error">{error}</div>;
  }

  return (
    <main className="page">
      <header className="page-header">
        <h1>Media Collection Manager</h1>
        <p>{items.length} collection items</p>
      </header>

      {items.length === 0 ? (
        <p>No collection items found.</p>
      ) : (
        <section className="album-grid">
          {items.map((item) => (
            <article className="album-card" key={item.id}>
              <div className="album-cover">
                {item.image_url ? (
                  <img
                    src={item.image_url}
                    alt={`${item.album_title} cover`}
                  />
                ) : (
                  <div className="album-cover-placeholder">
                    No Image
                  </div>
                )}
              </div>

              <div className="album-card-body">
                <h2>{item.album_title}</h2>
                <p className="artist-name">{item.artist_name}</p>

                <p className="album-meta">
                  {item.release_year ?? "Unknown year"}
                  {item.genre ? ` • ${item.genre}` : ""}
                </p>

                {item.album_rating && (
                  <p className="rating">
                    Rating: {item.album_rating}/10
                  </p>
                )}

                {item.location_name && (
                  <p className="location">
                    Location: {item.location_name}
                  </p>
                )}

                {item.tags.length > 0 && (
                  <div className="tag-list">
                    {item.tags.map((tag) => (
                      <span className="tag" key={tag}>
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </article>
          ))}
        </section>
      )}
    </main>
  );
}

export default App;
