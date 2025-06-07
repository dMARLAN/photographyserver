// API Integration Utilities for Photography Gallery

import type { 
  Photo, 
  Category, 
  ApiResponse, 
  ApiError
} from '@/types/gallery';

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
  const response = await apiRequest<{categories: Category[]}>('/categories');
  return response.categories;
}

export async function getCategory(slug: string): Promise<Category> {
  const response = await apiRequest<{category: string, photos: Photo[]}>(`/categories/${slug}`);
  // Transform API response to match Category interface
  return {
    name: response.category,
    photo_count: response.photos.length,
    latest_photo: response.photos[0]?.created_at || new Date().toISOString(),
    // Add missing optional fields
    slug: response.category
  };
}

// Photo API functions
export async function getPhotos(params?: {
  category?: string;
  page?: number;
  limit?: number;
}): Promise<{category: string, photos: Photo[]}> {
  // For now, use category-based endpoint since there's no general photos endpoint
  if (params?.category) {
    return await getCategory(params.category);
  }
  
  // If no category specified, throw error for now
  throw new Error('Category parameter is required');
}

export async function getPhoto(id: string): Promise<Photo> {
  const response = await apiRequest<Photo>(`/photos/${id}`);
  return response;
}

export async function getPhotosByCategory(
  categorySlug: string,
  params?: { page?: number; limit?: number }
): Promise<{data: Photo[], meta?: any}> {
  const response = await apiRequest<{category: string, photos: Photo[]}>(`/categories/${categorySlug}`);
  // Transform to match expected structure with pagination meta
  return {
    data: response.photos,
    meta: {
      total: response.photos.length,
      page: params?.page || 1,
      page_size: params?.limit || response.photos.length,
      total_pages: 1,
      has_next: false,
      has_previous: false
    }
  };
}

// Image URL utilities
export function getImageUrl(photoId: string, size?: 'thumbnail' | 'medium' | 'large' | 'original'): string {
  const baseUrl = size ? `/api/photos/${photoId}/file?size=${size}` : `/api/photos/${photoId}/file`;
  return baseUrl;
}

export function getOptimizedImageUrl(
  photoId: string, 
  width?: number, 
  height?: number,
  quality?: number
): string {
  const params = new URLSearchParams();
  if (width) params.set('width', width.toString());
  if (height) params.set('height', height.toString());
  if (quality) params.set('quality', quality.toString());
  
  const query = params.toString();
  return `/api/photos/${photoId}/file${query ? `?${query}` : ''}`;
}

// Helper function to generate placeholder blur data URL
export function generateBlurDataUrl(width: number = 10, height: number = 10): string {
  // Create a simple base64-encoded placeholder
  const canvas = typeof window !== 'undefined' 
    ? document.createElement('canvas') 
    : null;
    
  if (!canvas) {
    // Fallback blur data URL for SSR
    return 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAhEAACAQMDBQAAAAAAAAAAAAABAgMABAUGIWGRkbHB0eH/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/2gAMAwEAAhEDEQA/AJvBfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPf//Z';
  }
  
  canvas.width = width;
  canvas.height = height;
  
  const ctx = canvas.getContext('2d');
  if (!ctx) return '';
  
  // Create a simple gradient blur effect
  const gradient = ctx.createLinearGradient(0, 0, width, height);
  gradient.addColorStop(0, '#f3f4f6');
  gradient.addColorStop(1, '#e5e7eb');
  
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, width, height);
  
  return canvas.toDataURL('image/jpeg', 0.1);
}

// Error handling utilities
export class ApiRequestError extends Error {
  constructor(
    message: string, 
    public statusCode: number = 500,
    public endpoint?: string
  ) {
    super(message);
    this.name = 'ApiRequestError';
  }
}

export function isApiRequestError(error: unknown): error is ApiRequestError {
  return error instanceof ApiRequestError;
}

// Retry utility for failed requests
export async function withRetry<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> {
  let lastError: Error;
  
  for (let i = 0; i <= maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error('Unknown error');
      
      if (i === maxRetries) break;
      
      // Exponential backoff
      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
    }
  }
  
  throw lastError!;
}

// Cache utilities for client-side caching
const cache = new Map<string, { data: unknown; timestamp: number; ttl: number }>();

export async function getCachedData<T>(
  key: string,
  fetcher: () => Promise<T>,
  ttl: number = 5 * 60 * 1000 // 5 minutes default
): Promise<T> {
  const cached = cache.get(key);
  const now = Date.now();
  
  if (cached && now - cached.timestamp < cached.ttl) {
    return cached.data as T;
  }
  
  const data = await fetcher();
  cache.set(key, { data, timestamp: now, ttl });
  
  return data;
}

export function clearCache(key?: string): void {
  if (key) {
    cache.delete(key);
  } else {
    cache.clear();
  }
}