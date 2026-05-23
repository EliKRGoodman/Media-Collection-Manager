import "./App.css";

import { useEffect, useState } from "react";

import {
  getCollectionItems,
  createCollectionItem,
  updateCollectionItem,
} from "./services/api";

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

  const [selectedItem, setSelectedItem] = useState<CollectionItem | null>(null);

  /*
  Frontend search/filter/sort state.
  */

  const [search, setSearch] = useState("");

  const [genre, setGenre] = useState("");

  const [sortBy, setSortBy] = useState("");

  const [sortOrder, setSortOrder] = useState("asc");

  /*
Create collection item form state.
*/

  const [artistName, setArtistName] = useState("");

  const [albumTitle, setAlbumTitle] = useState("");

  const [releaseYear, setReleaseYear] = useState("");

  const [genreInput, setGenreInput] = useState("");

  const [imageUrl, setImageUrl] = useState("");

  const [condition, setCondition] = useState("");

  const [locationName, setLocationName] = useState("");

  const [price, setPrice] = useState("");

  const [albumRating, setAlbumRating] = useState("");

  const [tagsInput, setTagsInput] = useState("");

  const [createLoading, setCreateLoading] = useState(false);

  const [showCreateForm, setShowCreateForm] = useState(false);

  const [isEditing, setIsEditing] = useState(false);

  const [editCondition, setEditCondition] = useState("");
  const [editNotes, setEditNotes] = useState("");
  const [editLocationName, setEditLocationName] = useState("");
  const [editPrice, setEditPrice] = useState("");
  const [editAlbumRating, setEditAlbumRating] = useState("");
  const [editTagsInput, setEditTagsInput] = useState("");

  const [editLoading, setEditLoading] = useState(false);
  /*
  Create a new collection item from form input.
  */

  async function handleCreateCollectionItem(
    event: React.FormEvent
  ) {

    event.preventDefault();

    setCreateLoading(true);

    try {

      await createCollectionItem({
        artist_name: artistName,
        album_title: albumTitle,

        release_year: releaseYear
          ? Number(releaseYear)
          : undefined,

        genre: genreInput || undefined,

        image_url: imageUrl || undefined,

        condition: condition || undefined,

        location_name: locationName || undefined,

        price: price
          ? Number(price)
          : undefined,

        album_rating: albumRating
          ? Number(albumRating)
          : undefined,

        tags: tagsInput
          ? tagsInput
            .split(",")
            .map((tag) => tag.trim())
            .filter(Boolean)
          : [],
      });

      /*
      Reset form after successful creation.
      */

      setArtistName("");
      setAlbumTitle("");
      setReleaseYear("");
      setGenreInput("");
      setImageUrl("");
      setCondition("");
      setLocationName("");
      setPrice("");
      setAlbumRating("");
      setTagsInput("");

      /*
      Refresh collection.
      */

      const updatedItems = await getCollectionItems({
        search,
        genre,
        sort_by: sortBy,
        sort_order: sortOrder,
      });

      setItems(updatedItems);

    } catch (err) {

      setError("Failed to create collection item.");

    } finally {

      setCreateLoading(false);

    }
  }

  function startEditingItem(item: CollectionItem) {
    setEditCondition(item.condition ?? "");
    setEditNotes(item.notes ?? "");
    setEditLocationName(item.location_name ?? "");
    setEditPrice(item.price !== null ? String(item.price) : "");
    setEditAlbumRating(
      item.album_rating !== null ? String(item.album_rating) : ""
    );
    setEditTagsInput(item.tags.join(", "));

    setIsEditing(true);
  }

  function cancelEditingItem() {
    setIsEditing(false);
  }

  async function handleUpdateCollectionItem(
    event: React.FormEvent
  ) {
    event.preventDefault();

    if (!selectedItem) {
      return;
    }

    setEditLoading(true);

    try {
      const updatedItem = await updateCollectionItem(
        selectedItem.id,
        {
          condition: editCondition || undefined,
          notes: editNotes || undefined,
          location_name: editLocationName || undefined,

          price: editPrice
            ? Number(editPrice)
            : undefined,

          album_rating: editAlbumRating
            ? Number(editAlbumRating)
            : undefined,

          tags: editTagsInput
            ? editTagsInput
              .split(",")
              .map((tag) => tag.trim())
              .filter(Boolean)
            : [],
        }
      );

      setSelectedItem(updatedItem);
      setIsEditing(false);

      const updatedItems = await getCollectionItems({
        search,
        genre,
        sort_by: sortBy,
        sort_order: sortOrder,
      });

      setItems(updatedItems);

    } catch (err) {
      setError("Failed to update collection item.");
    } finally {
      setEditLoading(false);
    }
  }

  /*
  Load collection items once when the app first renders.
  */
  /*
  Reload collection whenever:
  - search changes
  - genre changes
  - sorting changes
  */
  useEffect(() => {

    async function loadCollection() {

      setLoading(true);

      try {

        const data = await getCollectionItems({
          search,
          genre,
          sort_by: sortBy,
          sort_order: sortOrder,
        });

        setItems(data);

      } catch (err) {

        setError("Failed to load collection.");

      } finally {

        setLoading(false);

      }
    }

    loadCollection();

  }, [search, genre, sortBy, sortOrder]);

  if (error) {
    return <div className="page error">{error}</div>;
  }

  return (
    <main className="page">
      <header className="page-header">
        <h1>Media Collection Manager</h1>
        <p>{items.length} collection items</p>
      </header>

      <section className="create-form-section">

        <button
          type="button"
          className="create-form-toggle"
          onClick={() => setShowCreateForm(!showCreateForm)}
        >
          {showCreateForm ? "Add Collection Item" : "Add Collection Item"}
        </button>

        {showCreateForm && (
          <form
            className="create-form"
            onSubmit={handleCreateCollectionItem}
          >

            <input
              type="text"
              placeholder="Artist Name"
              value={artistName}
              onChange={(event) =>
                setArtistName(event.target.value)
              }
              required
            />

            <input
              type="text"
              placeholder="Album Title"
              value={albumTitle}
              onChange={(event) =>
                setAlbumTitle(event.target.value)
              }
              required
            />

            <input
              type="number"
              placeholder="Release Year"
              value={releaseYear}
              onChange={(event) =>
                setReleaseYear(event.target.value)
              }
            />

            <input
              type="text"
              placeholder="Genre"
              value={genreInput}
              onChange={(event) =>
                setGenreInput(event.target.value)
              }
            />

            <input
              type="text"
              placeholder="Image URL"
              value={imageUrl}
              onChange={(event) =>
                setImageUrl(event.target.value)
              }
            />

            <input
              type="text"
              placeholder="Condition"
              value={condition}
              onChange={(event) =>
                setCondition(event.target.value)
              }
            />

            <input
              type="text"
              placeholder="Location"
              value={locationName}
              onChange={(event) =>
                setLocationName(event.target.value)
              }
            />

            <input
              type="number"
              step="0.01"
              placeholder="Price"
              value={price}
              onChange={(event) =>
                setPrice(event.target.value)
              }
            />

            <input
              type="number"
              placeholder="Rating"
              value={albumRating}
              onChange={(event) =>
                setAlbumRating(event.target.value)
              }
            />

            <input
              type="text"
              placeholder="Tags (comma separated)"
              value={tagsInput}
              onChange={(event) =>
                setTagsInput(event.target.value)
              }
            />

            <button
              type="submit"
              disabled={createLoading}
            >
              {createLoading
                ? "Creating..."
                : "Add Album"}
            </button>

          </form>
        )}

      </section>

      <section className="controls">

        {/* Search input */}

        <input
          type="text"
          placeholder="Search artist, album, or track..."
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />

        {/* Genre filter */}

        <input
          type="text"
          placeholder="Filter by genre..."
          value={genre}
          onChange={(event) => setGenre(event.target.value)}
        />

        {/* Sort field */}

        <select
          value={sortBy}
          onChange={(event) => setSortBy(event.target.value)}
        >
          <option value="">No Sorting</option>

          <option value="artist">Artist</option>

          <option value="album_title">Album Title</option>

          <option value="release_year">Release Year</option>

          <option value="genre">Genre</option>
        </select>

        {/* Sort direction */}

        <select
          value={sortOrder}
          onChange={(event) => setSortOrder(event.target.value)}
        >
          <option value="asc">Ascending</option>

          <option value="desc">Descending</option>
        </select>

      </section>

      {selectedItem && (
        <section className="detail-panel">
          <button
            className="detail-close-button"
            onClick={() => setSelectedItem(null)}
          >
            Close
          </button>

          <h2>{selectedItem.album_title}</h2>
          <p>{selectedItem.artist_name}</p>

          <p>
            {selectedItem.release_year ?? "Unknown year"}
            {selectedItem.genre ? ` • ${selectedItem.genre}` : ""}
          </p>

          {selectedItem.image_url && (
            <img
              className="detail-image"
              src={selectedItem.image_url}
              alt={`${selectedItem.album_title} cover`}
            />
          )}

          {isEditing ? (
            <form
              className="edit-form"
              onSubmit={handleUpdateCollectionItem}
            >
              <input
                type="text"
                placeholder="Condition"
                value={editCondition}
                onChange={(event) =>
                  setEditCondition(event.target.value)
                }
              />

              <textarea
                placeholder="Notes"
                value={editNotes}
                onChange={(event) =>
                  setEditNotes(event.target.value)
                }
              />

              <input
                type="text"
                placeholder="Location"
                value={editLocationName}
                onChange={(event) =>
                  setEditLocationName(event.target.value)
                }
              />

              <input
                type="number"
                step="0.01"
                placeholder="Price"
                value={editPrice}
                onChange={(event) =>
                  setEditPrice(event.target.value)
                }
              />

              <input
                type="number"
                placeholder="Rating"
                value={editAlbumRating}
                onChange={(event) =>
                  setEditAlbumRating(event.target.value)
                }
              />

              <input
                type="text"
                placeholder="Tags, comma separated"
                value={editTagsInput}
                onChange={(event) =>
                  setEditTagsInput(event.target.value)
                }
              />

              <div className="edit-form-actions">
                <button type="submit" disabled={editLoading}>
                  {editLoading ? "Saving..." : "Save Changes"}
                </button>

                <button
                  type="button"
                  onClick={cancelEditingItem}
                >
                  Cancel
                </button>
              </div>
            </form>
          ) : (
            <>
              <p>Condition: {selectedItem.condition ?? "Unknown"}</p>
              <p>Location: {selectedItem.location_name ?? "None"}</p>
              <p>Price: {selectedItem.price ?? "Unknown"}</p>
              <p>Rating: {selectedItem.album_rating ?? "Unrated"}</p>

              {selectedItem.notes && (
                <p>Notes: {selectedItem.notes}</p>
              )}

              {selectedItem.tags.length > 0 && (
                <div className="tag-list">
                  {selectedItem.tags.map((tag) => (
                    <span className="tag" key={tag}>
                      {tag}
                    </span>
                  ))}
                </div>
              )}

              <button
                type="button"
                className="edit-button"
                onClick={() => startEditingItem(selectedItem)}
              >
                Edit Collection Info
              </button>
            </>
          )}

          {selectedItem.tracks.length > 0 && (
            <>
              <h3>Tracks</h3>
              <ol>
                {selectedItem.tracks.map((track) => (
                  <li key={track.id}>
                    {track.title}
                    {track.rating ? ` — ${track.rating}/10` : ""}
                  </li>
                ))}
              </ol>
            </>
          )}
        </section>
      )}

      {/*{loading && (
        <p className="status-message">Loading collection...</p>
      )}

      {error && <p className="error">{error}</p>}*/}

      {!loading && !error && items.length === 0 ? (
        <p>No collection items found.</p>
      ) : (

        <section className="album-grid">
          {items.map((item) => (
            <article
              className="album-card"
              key={item.id}
              onClick={() => setSelectedItem(item)}
            >
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
