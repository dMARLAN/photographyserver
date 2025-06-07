'use client';

import Image from 'next/image';
import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/card';
import type { Category } from '@/types/gallery';
import { getImageUrl } from '@/lib/api';
import { 
  cn, 
  createImageClasses, 
  createGalleryItemClasses,
  createTextOverlayClasses,
  createHeadingClasses,
  createOptimizedImageProps
} from '@/lib/utils';

interface CategoryCardProps {
  category: Category;
  priority?: boolean;
  className?: string;
}

export function CategoryCard({ 
  category, 
  priority = false, 
  className 
}: CategoryCardProps) {
  const imageClasses = createImageClasses({
    ratio: 'landscape',
    objectFit: 'cover',
    priority,
    rounded: true
  });

  const galleryItemClasses = createGalleryItemClasses({
    interactive: true,
    hover: true,
    focus: true
  });

  const overlayClasses = createTextOverlayClasses({
    position: 'bottom',
    background: 'gradient',
    padding: 'normal'
  });

  const headingClasses = createHeadingClasses({
    level: 3,
    weight: 'semibold',
    spacing: 'tight'
  });

  // Get cover photo or use placeholder
  const coverPhotoUrl = category.cover_photo 
    ? getImageUrl(category.cover_photo.id, 'medium')
    : '/images/placeholder-category.svg';

  const altText = category.cover_photo?.alt_text || 
    category.cover_photo?.title ||
    `${category.name} category`;

  const optimizedImageProps = createOptimizedImageProps({
    priority,
    quality: 80,
    format: 'webp'
  });

  return (
    <Link href={`/gallery/${category.name}`}>
      <Card className={cn(galleryItemClasses, className)}>
        <CardContent className="p-0">
          <div className="relative">
            <div className={imageClasses}>
              <Image
                src={coverPhotoUrl}
                alt={altText}
                fill
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="transition-transform duration-300 group-hover:scale-105"
                {...optimizedImageProps}
              />
            </div>
            
            <div className={overlayClasses}>
              <div className="space-y-1">
                <h3 className={headingClasses}>
                  {category.name}
                </h3>
                
                <div className="flex items-center justify-between">
                  <p className="text-sm text-white/90">
                    {category.photo_count} {category.photo_count === 1 ? 'photo' : 'photos'}
                  </p>
                  
                  {category.description && (
                    <p className="text-xs text-white/75 line-clamp-1 max-w-[200px]">
                      {category.description}
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}

// Skeleton component for loading state
export function CategoryCardSkeleton({ className }: { className?: string }) {
  return (
    <Card className={cn('overflow-hidden', className)}>
      <CardContent className="p-0">
        <div className="relative">
          {/* Image skeleton */}
          <div className={cn(
            createImageClasses({ ratio: 'landscape' }),
            'bg-muted animate-pulse'
          )} />
          
          {/* Overlay skeleton */}
          <div className={createTextOverlayClasses()}>
            <div className="space-y-2">
              {/* Title skeleton */}
              <div className="h-6 bg-white/20 rounded w-3/4 animate-pulse" />
              
              {/* Photo count skeleton */}
              <div className="h-4 bg-white/15 rounded w-1/2 animate-pulse" />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Grid wrapper for category cards
interface CategoryGridProps {
  children: React.ReactNode;
  className?: string;
}

export function CategoryGrid({ children, className }: CategoryGridProps) {
  return (
    <div className={cn(
      'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6',
      'w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8',
      className
    )}>
      {children}
    </div>
  );
}