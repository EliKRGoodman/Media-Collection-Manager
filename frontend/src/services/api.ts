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

export interface CreateCollectionItemData {
  artist_name: string;
  album_title: string;

  release_year?: number;
  genre?: string;

  image_url?: string;

  condition?: string;
  location_name?: string;

  price?: number;
  album_rating?: number;

  tags?: string[];
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

/*
Create a new collection item.
*/
export async function createCollectionItem(
  data: CreateCollectionItemData
): Promise<CollectionItem> {

  const response = await fetch(
    `${API_BASE_URL}/collection-items/`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify(data),
    }
  );

  if (!response.ok) {
    throw new Error("Failed to create collection item.");
  }

  return response.json();
}