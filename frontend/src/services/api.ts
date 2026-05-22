/*
Central API helper layer.

This keeps HTTP logic separated from React components.
Later:
- authentication,
- error handling,
- retries,
- caching,
- and API abstraction
can all live here.
*/

import type { CollectionItem } from "../types/collectionItem";

/*
Base backend URL.

Vite frontend runs separately from FastAPI,
so requests must target the backend server.
*/
const API_BASE_URL = "http://127.0.0.1:8000";

/*
Fetch all collection items from the backend.
*/
export async function getCollectionItems(): Promise<CollectionItem[]> {
  const response = await fetch(
    `${API_BASE_URL}/collection-items/`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch collection items.");
  }

  return response.json();
}