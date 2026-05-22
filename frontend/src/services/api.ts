/*
Central API helper layer.
*/

import type { CollectionItem } from "../types/collectionItem";

const API_BASE_URL = "http://127.0.0.1:8000";

/*
Optional collection query parameters.
*/
export interface CollectionQueryParams {
  search?: string;
  genre?: string;
  tag?: string;

  sort_by?: string;
  sort_order?: string;
}

/*
Fetch collection items with optional filters/sorting.
*/
export async function getCollectionItems(
  params: CollectionQueryParams = {}
): Promise<CollectionItem[]> {

  /*
  Build query string dynamically from provided params.
  */
  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value) {
      searchParams.append(key, value);
    }
  });

  const response = await fetch(
    `${API_BASE_URL}/collection-items/?${searchParams.toString()}`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch collection items.");
  }

  return response.json();
}