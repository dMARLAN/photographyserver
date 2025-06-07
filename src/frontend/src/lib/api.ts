// API Integration Utilities for Photography Gallery

import type {ApiError, Category, Photo} from '@/types/gallery';

// Base API configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

// Helper function to handle API responses
async function apiRequest<T>(
  endpoint: string, 
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const errorData: ApiError = await response.json().catch(() => ({
        detail: `HTTP ${response.status}: ${response.statusText}`,
        status_code: response.status
      }));
      throw new Error(errorData.detail);
    }
    
    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('An unexpected error occurred');
  }
}

// Category API functions
export async function getCategories(): Promise<Category[]> {
  return await apiRequest<Category[]>('/categories');
}

export async function getCategory(slug: string): Promise<Category> {
  const response = await apiRequest<Photo[]>(`/categories/${slug}`);
  // Transform API response to match Category interface
  return {
    name: slug,
    photo_count: response.length,
    latest_photo: response[0]?.created_at || new Date().toISOString(),
    // Add missing optional fields
    slug: slug
  };
}

export async function getPhotosByCategory(
  categorySlug: string,
  params?: { page?: number; limit?: number }
): Promise<{data: Photo[], meta?: any}> {
  const response = await apiRequest<Photo[]>(`/categories/${categorySlug}`);
  // Transform to match expected structure with pagination meta
  return {
    data: response,
    meta: {
      total: response.length,
      page: params?.page || 1,
      page_size: params?.limit || response.length,
      total_pages: 1,
      has_next: false,
      has_previous: false
    }
  };
}

// Image URL utilities
export function getImageUrl(photoId: string, size?: 'thumbnail' | 'medium' | 'large' | 'original'): string {
  return size ? `/api/photos/${photoId}/file?size=${size}` : `/api/photos/${photoId}/file`;
}
