// TypeScript definitions for the photography gallery

export interface Photo {
  id: string;
  filename: string;
  title: string;
  category?: string;
  file_path?: string;
  width: number;
  height: number;
  aspect_ratio: number;
  orientation: string;
  megapixels?: number;
  file_size?: number;
  file_size_mb: number;
  file_extension?: string;
  url?: string;
  created_at: string;
  updated_at?: string;
  file_modified_at: string;
  description?: string;
  alt_text?: string;
  metadata?: PhotoMetadata;
}

export interface PhotoMetadata {
  camera?: string;
  lens?: string;
  focal_length?: string;
  aperture?: string;
  shutter_speed?: string;
  iso?: number;
  taken_at?: string;
  location?: string;
  tags?: string[];
}

export interface Category {
  name: string;
  photo_count: number;
  latest_photo: string;
  id?: string;
  description?: string;
  cover_photo?: Photo;
  slug?: string;
  created_at?: string;
  updated_at?: string;
  sort_order?: number;
}

export interface ApiResponse<T> {
  data: T;
  meta?: PaginationMeta;
  links?: ApiLinks;
}

export interface PaginationMeta {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface ApiLinks {
  self: string;
  first?: string;
  last?: string;
  next?: string;
  previous?: string;
}

export interface ApiError {
  detail: string;
  status_code: number;
  type?: string;
  field_errors?: Record<string, string[]>;
}

// Gallery component prop types
export interface GalleryProps {
  categories?: Category[];
  loading?: boolean;
  error?: string | null;
  className?: string;
}

export interface PhotoGridProps {
  photos: Photo[];
  layout?: GalleryLayout;
  aspectRatio?: AspectRatio;
  showOverlay?: boolean;
  className?: string;
  onPhotoClick?: (photo: Photo, index: number) => void;
  loading?: boolean;
}

export interface CategoryCardProps {
  category: Category;
  priority?: boolean;
  className?: string;
  onClick?: (category: Category) => void;
}

// Layout and design types
export type GalleryLayout = 'grid' | 'masonry' | 'flex' | 'carousel';

export type AspectRatio = 
  | 'square' 
  | 'portrait' 
  | 'landscape' 
  | 'wide' 
  | 'ultrawide' 
  | 'tall';

export type ImageSize = 
  | 'thumbnail' 
  | 'small' 
  | 'medium' 
  | 'large' 
  | 'original';

// API request parameters
export interface PhotosQueryParams {
  category?: string;
  page?: number;
  limit?: number;
  sort?: 'created_at' | 'updated_at' | 'title' | 'filename';
  order?: 'asc' | 'desc';
  search?: string;
  tags?: string[];
}

export interface CategoriesQueryParams {
  page?: number;
  limit?: number;
  sort?: 'name' | 'created_at' | 'photo_count' | 'sort_order';
  order?: 'asc' | 'desc';
  include_empty?: boolean;
}

// Image optimization parameters
export interface ImageOptimizationParams {
  width?: number;
  height?: number;
  quality?: number;
  format?: 'webp' | 'avif' | 'jpeg' | 'png';
  crop?: 'center' | 'top' | 'bottom' | 'left' | 'right';
  fit?: 'cover' | 'contain' | 'fill' | 'inside' | 'outside';
}

// Lightbox and viewer types
export interface LightboxState {
  isOpen: boolean;
  currentIndex: number;
  photos: Photo[];
}

export interface LightboxProps {
  photo: Photo;
  index: number;
  total: number;
  onClose: () => void;
  onPrevious: () => void;
  onNext: () => void;
  showDownload?: boolean;
  showInfo?: boolean;
}

// Search and filter types
export interface SearchFilters {
  category?: string;
  tags?: string[];
  dateRange?: {
    start: string;
    end: string;
  };
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface SearchResults {
  photos: Photo[];
  categories: Category[];
  total: number;
  query: string;
  filters: SearchFilters;
}

// Upload and management types (for future admin features)
export interface UploadFile {
  file: File;
  preview?: string;
  progress?: number;
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'error';
  error?: string;
}

export interface PhotoUploadData {
  title?: string;
  description?: string;
  category: string;
  alt_text?: string;
  tags?: string[];
  metadata?: Partial<PhotoMetadata>;
}

// Event types for gallery interactions
export interface PhotoClickEvent {
  photo: Photo;
  index: number;
  event: React.MouseEvent | React.KeyboardEvent;
}

export interface CategoryClickEvent {
  category: Category;
  event: React.MouseEvent | React.KeyboardEvent;
}

// Performance and optimization types
export interface LoadingState {
  categories: boolean;
  photos: boolean;
  photo: boolean;
}

export interface ErrorState {
  categories: string | null;
  photos: string | null;
  photo: string | null;
}

export interface CacheConfig {
  ttl: number; // Time to live in milliseconds
  maxSize: number; // Maximum number of cached items
  strategy: 'lru' | 'fifo' | 'none';
}

// SEO and metadata types
export interface PhotoSEO {
  title: string;
  description: string;
  keywords: string[];
  canonical?: string;
  openGraph: {
    title: string;
    description: string;
    images: Array<{
      url: string;
      width: number;
      height: number;
      alt: string;
    }>;
  };
}

export interface CategorySEO extends PhotoSEO {
  breadcrumbs: Array<{
    name: string;
    url: string;
  }>;
}

// Accessibility types
export interface A11yConfig {
  enableKeyboardNavigation: boolean;
  enableScreenReaderSupport: boolean;
  enableHighContrast: boolean;
  enableReducedMotion: boolean;
  ariaLabels: Record<string, string>;
}

// Theme and customization types
export interface GalleryTheme {
  colors: {
    primary: string;
    secondary: string;
    accent: string;
    background: string;
    surface: string;
    text: string;
    muted: string;
  };
  spacing: {
    grid: string;
    padding: string;
    margin: string;
  };
  typography: {
    headingFont: string;
    bodyFont: string;
    monoFont: string;
  };
  effects: {
    borderRadius: string;
    shadows: Record<string, string>;
    transitions: Record<string, string>;
  };
}

// Utility types
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;
export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;
export type PartialExcept<T, K extends keyof T> = Partial<T> & Pick<T, K>;

// React component helpers
export type PropsWithClassName<T = object> = T & {
  className?: string;
};

export type PropsWithChildren<T = object> = T & {
  children?: React.ReactNode;
};

export type ComponentWithForwardedRef<T, P = object> = React.ForwardRefExoticComponent<
  P & React.RefAttributes<T>
>;