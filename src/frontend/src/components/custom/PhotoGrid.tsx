'use client';

import React, { useState, useCallback } from 'react';
import Image from 'next/image';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import type { Photo } from '@/types/gallery';
import { getImageUrl } from '@/lib/api';
import { 
  cn, 
  createImageClasses,
  createGalleryClasses,
  createGalleryItemClasses,
  createTextOverlayClasses,
  createOptimizedImageProps,
  AspectRatio
} from '@/lib/utils';
import { ChevronLeft, ChevronRight, X, Download } from 'lucide-react';

interface PhotoGridProps {
  photos: Photo[];
  layout?: 'grid' | 'masonry';
  aspectRatio?: AspectRatio;
  showOverlay?: boolean;
  className?: string;
  onPhotoClick?: (photo: Photo, index: number) => void;
}

export function PhotoGrid({ 
  photos, 
  layout = 'grid',
  aspectRatio = 'landscape',
  showOverlay = true,
  className,
  onPhotoClick
}: PhotoGridProps) {
  const [lightboxPhoto, setLightboxPhoto] = useState<{ photo: Photo; index: number } | null>(null);

  const galleryClasses = createGalleryClasses(layout, {
    responsive: true,
    padding: true,
    maxWidth: true
  });

  const handlePhotoClick = useCallback((photo: Photo, index: number) => {
    if (onPhotoClick) {
      onPhotoClick(photo, index);
    } else {
      setLightboxPhoto({ photo, index });
    }
  }, [onPhotoClick]);

  const handleCloseLightbox = useCallback(() => {
    setLightboxPhoto(null);
  }, []);

  const handlePrevious = useCallback(() => {
    if (!lightboxPhoto) return;
    const newIndex = lightboxPhoto.index > 0 ? lightboxPhoto.index - 1 : photos.length - 1;
    setLightboxPhoto({ photo: photos[newIndex], index: newIndex });
  }, [lightboxPhoto, photos]);

  const handleNext = useCallback(() => {
    if (!lightboxPhoto) return;
    const newIndex = lightboxPhoto.index < photos.length - 1 ? lightboxPhoto.index + 1 : 0;
    setLightboxPhoto({ photo: photos[newIndex], index: newIndex });
  }, [lightboxPhoto, photos]);

  // Handle keyboard navigation
  React.useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (!lightboxPhoto) return;

      switch (event.key) {
        case 'Escape':
          handleCloseLightbox();
          break;
        case 'ArrowLeft':
          handlePrevious();
          break;
        case 'ArrowRight':
          handleNext();
          break;
      }
    };

    if (lightboxPhoto) {
      document.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [lightboxPhoto, handleCloseLightbox, handlePrevious, handleNext]);

  if (photos.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">No photos found in this category.</p>
      </div>
    );
  }

  return (
    <>
      <div className={cn(galleryClasses, className)}>
        {photos.map((photo, index) => (
          <PhotoGridItem
            key={photo.id}
            photo={photo}
            index={index}
            aspectRatio={aspectRatio}
            showOverlay={showOverlay}
            onClick={handlePhotoClick}
            priority={index < 6} // Prioritize first 6 images
          />
        ))}
      </div>

      {/* Lightbox */}
      {lightboxPhoto && (
        <PhotoLightbox
          photo={lightboxPhoto.photo}
          index={lightboxPhoto.index}
          total={photos.length}
          onClose={handleCloseLightbox}
          onPrevious={handlePrevious}
          onNext={handleNext}
        />
      )}
    </>
  );
}

// Individual photo grid item
interface PhotoGridItemProps {
  photo: Photo;
  index: number;
  aspectRatio: AspectRatio;
  showOverlay: boolean;
  priority?: boolean;
  onClick: (photo: Photo, index: number) => void;
}

function PhotoGridItem({ 
  photo, 
  index, 
  aspectRatio, 
  showOverlay, 
  priority = false,
  onClick 
}: PhotoGridItemProps) {
  const imageClasses = createImageClasses({
    ratio: aspectRatio,
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

  const optimizedImageProps = createOptimizedImageProps({
    priority,
    quality: 85,
    format: 'webp'
  });

  const imageUrl = getImageUrl(photo.id, 'medium');
  const altText = photo.alt_text || photo.title || photo.filename;

  return (
    <Card 
      className={cn(galleryItemClasses, 'overflow-hidden cursor-pointer')}
      onClick={() => onClick(photo, index)}
      tabIndex={0}
      role="button"
      aria-label={`View ${altText}`}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick(photo, index);
        }
      }}
    >
      <CardContent className="p-0">
        <div className="relative group">
          <div className={imageClasses}>
            <Image
              src={imageUrl}
              alt={altText}
              fill
              sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
              className="transition-transform duration-300 group-hover:scale-105"
              {...optimizedImageProps}
            />
          </div>

          {showOverlay && (photo.title || photo.description) && (
            <div className={cn(
              overlayClasses,
              'opacity-0 group-hover:opacity-100 transition-opacity duration-300'
            )}>
              {photo.title && (
                <h4 className="font-medium text-sm text-white line-clamp-1">
                  {photo.title}
                </h4>
              )}
              {photo.description && (
                <p className="text-xs text-white/80 line-clamp-2 mt-1">
                  {photo.description}
                </p>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

// Lightbox component
interface PhotoLightboxProps {
  photo: Photo;
  index: number;
  total: number;
  onClose: () => void;
  onPrevious: () => void;
  onNext: () => void;
}

function PhotoLightbox({ 
  photo, 
  index, 
  total, 
  onClose, 
  onPrevious, 
  onNext 
}: PhotoLightboxProps) {
  const imageUrl = getImageUrl(photo.id, 'large');
  const altText = photo.alt_text || photo.title || photo.filename;

  return (
    <div className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center">
      {/* Close button */}
      <Button
        variant="ghost"
        size="icon"
        className="absolute top-4 right-4 text-white hover:bg-white/10 z-10"
        onClick={onClose}
        aria-label="Close lightbox"
      >
        <X className="h-6 w-6" />
      </Button>

      {/* Navigation buttons */}
      {total > 1 && (
        <>
          <Button
            variant="ghost"
            size="icon"
            className="absolute left-4 top-1/2 -translate-y-1/2 text-white hover:bg-white/10 z-10"
            onClick={onPrevious}
            aria-label="Previous photo"
          >
            <ChevronLeft className="h-8 w-8" />
          </Button>

          <Button
            variant="ghost"
            size="icon"
            className="absolute right-4 top-1/2 -translate-y-1/2 text-white hover:bg-white/10 z-10"
            onClick={onNext}
            aria-label="Next photo"
          >
            <ChevronRight className="h-8 w-8" />
          </Button>
        </>
      )}

      {/* Image counter */}
      <div className="absolute top-4 left-4 text-white text-sm font-medium bg-black/50 px-3 py-1 rounded">
        {index + 1} / {total}
      </div>

      {/* Main image */}
      <div className="relative max-w-[90vw] max-h-[90vh] w-full h-full flex items-center justify-center">
        <Image
          src={imageUrl}
          alt={altText}
          fill
          className="object-contain"
          priority
          quality={95}
        />
      </div>

      {/* Photo info */}
      {(photo.title || photo.description) && (
        <div className="absolute bottom-4 left-4 right-4 text-white bg-black/50 p-4 rounded">
          {photo.title && (
            <h3 className="font-semibold text-lg mb-1">{photo.title}</h3>
          )}
          {photo.description && (
            <p className="text-sm text-white/90">{photo.description}</p>
          )}
        </div>
      )}

      {/* Download button */}
      <Button
        variant="ghost"
        size="icon"
        className="absolute bottom-4 right-4 text-white hover:bg-white/10"
        onClick={() => {
          const downloadUrl = getImageUrl(photo.id, 'original');
          window.open(downloadUrl, '_blank');
        }}
        aria-label="Download photo"
      >
        <Download className="h-5 w-5" />
      </Button>
    </div>
  );
}

// Loading skeleton for photo grid
export function PhotoGridSkeleton({ 
  count = 12, 
  aspectRatio = 'landscape' 
}: { 
  count?: number; 
  aspectRatio?: AspectRatio; 
}) {
  const imageClasses = createImageClasses({
    ratio: aspectRatio,
    rounded: true
  });

  return (
    <div className={createGalleryClasses('grid')}>
      {Array.from({ length: count }, (_, i) => (
        <Card key={i} className="overflow-hidden">
          <CardContent className="p-0">
            <Skeleton className={cn(imageClasses, 'animate-pulse')} />
          </CardContent>
        </Card>
      ))}
    </div>
  );
}