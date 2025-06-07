import React, { Suspense } from 'react';
import Link from 'next/link';
import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { PhotoGrid, PhotoGridSkeleton } from '@/components/custom/PhotoGrid';
import { getCategory, getPhotosByCategory } from '@/lib/api';
import type { Category } from '@/types/gallery';
import { createHeadingClasses, createContainerClasses } from '@/lib/utils';
import { ArrowLeft, Camera, Grid, Info } from 'lucide-react';

interface CategoryPageProps {
  params: Promise<{ category: string }>;
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}

export async function generateMetadata({ params }: CategoryPageProps): Promise<Metadata> {
  const { category: categorySlug } = await params;
  
  try {
    const category = await getCategory(categorySlug);
    
    return {
      title: `${category.name} - Photo Gallery`,
      description: category.description || `Browse ${category.name} photography collection with ${category.photo_count} photos.`,
      keywords: `photography, ${category.name}, gallery, professional photos`,
      openGraph: {
        title: `${category.name} - Photo Gallery`,
        description: category.description || `Browse ${category.name} photography collection`,
        type: 'website',
        images: category.cover_photo ? [
          {
            url: `/api/photos/${category.cover_photo.id}/file?size=large`,
            width: 1200,
            height: 630,
            alt: category.cover_photo.alt_text || category.name,
          },
        ] : [],
      },
    };
  } catch {
    return {
      title: 'Category Not Found - Photo Gallery',
      description: 'The requested photo category could not be found.',
    };
  }
}

// Force dynamic rendering to ensure fresh data
export const dynamic = 'force-dynamic';

async function CategoryContent({ categorySlug, page }: { categorySlug: string; page: number }) {
  try {
    // Fetch category info and photos in parallel
    const [category, photosResponse] = await Promise.all([
      getCategory(categorySlug),
      getPhotosByCategory(categorySlug, { page, limit: 24 })
    ]);

    if (!category) {
      notFound();
    }

    return (
      <div className="space-y-8">
        <CategoryHeader category={category} />
        
        {photosResponse.data.length > 0 ? (
          <>
            <PhotoGrid 
              photos={photosResponse.data}
              layout="grid"
              aspectRatio="landscape"
              showOverlay={true}
            />
            
            {photosResponse.meta && photosResponse.meta.total_pages > 1 && (
              <CategoryPagination 
                currentPage={page}
                totalPages={photosResponse.meta.total_pages}
                categorySlug={categorySlug}
              />
            )}
          </>
        ) : (
          <EmptyCategoryState category={category} />
        )}
      </div>
    );
  } catch (error) {
    console.error('Failed to load category:', error);
    
    // Check if it's a 404 error
    if (error instanceof Error && error.message.includes('404')) {
      notFound();
    }
    
    return <CategoryErrorState categorySlug={categorySlug} />;
  }
}

function CategoryHeader({ category }: { category: Category }) {
  const headingClasses = createHeadingClasses({
    level: 1,
    weight: 'bold',
    spacing: 'tight'
  });

  const subheadingClasses = createHeadingClasses({
    level: 4,
    weight: 'normal',
    spacing: 'normal'
  });

  return (
    <div className="space-y-6">
      {/* Breadcrumb and navigation */}
      <div className="flex items-center justify-between">
        <Link href="/gallery">
          <Button variant="outline" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Gallery
          </Button>
        </Link>
        
        <div className="flex items-center space-x-2 text-sm text-muted-foreground">
          <Link href="/gallery" className="hover:text-foreground transition-colors">
            Gallery
          </Link>
          <span>/</span>
          <span className="text-foreground">{category.name}</span>
        </div>
      </div>

      {/* Category title and info */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center space-x-2">
          <Grid className="h-6 w-6 text-primary" />
          <h1 className={headingClasses}>{category.name}</h1>
        </div>
        
        {category.description && (
          <p className={subheadingClasses + ' text-muted-foreground max-w-2xl mx-auto'}>
            {category.description}
          </p>
        )}

        <div className="flex items-center justify-center space-x-4 text-sm text-muted-foreground">
          <div className="flex items-center space-x-1">
            <Camera className="h-4 w-4" />
            <span>{category.photo_count} {category.photo_count === 1 ? 'photo' : 'photos'}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function EmptyCategoryState({ category }: { category: Category }) {
  const headingClasses = createHeadingClasses({
    level: 3,
    weight: 'semibold',
    spacing: 'normal'
  });

  return (
    <div className="text-center py-12 space-y-6">
      <div className="space-y-4">
        <Camera className="h-16 w-16 text-muted-foreground mx-auto" />
        <h3 className={headingClasses + ' text-muted-foreground'}>
          No Photos in {category.name}
        </h3>
        <p className="text-muted-foreground max-w-md mx-auto">
          This category is currently empty. Check back soon for new photos.
        </p>
      </div>
      
      <Link href="/gallery">
        <Button>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Browse Other Categories
        </Button>
      </Link>
    </div>
  );
}

function CategoryErrorState({ categorySlug }: { categorySlug: string }) {
  const headingClasses = createHeadingClasses({
    level: 2,
    weight: 'semibold',
    spacing: 'normal'
  });

  return (
    <div className="text-center py-12 space-y-6">
      <div className="space-y-4">
        <div className="h-16 w-16 rounded-full bg-destructive/10 flex items-center justify-center mx-auto">
          <Info className="h-8 w-8 text-destructive" />
        </div>
        <h2 className={headingClasses + ' text-destructive'}>
          Failed to Load Category
        </h2>
        <p className="text-muted-foreground max-w-md mx-auto">
          We&apos;re having trouble loading the photos for &ldquo;{categorySlug}&rdquo;. 
          Please try refreshing the page or check back later.
        </p>
      </div>
      
      <div className="flex items-center justify-center space-x-4">
        <Button 
          onClick={() => window.location.reload()}
          variant="default"
        >
          Try Again
        </Button>
        <Link href="/gallery">
          <Button variant="outline">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Gallery
          </Button>
        </Link>
      </div>
    </div>
  );
}

function CategoryPagination({ 
  currentPage, 
  totalPages, 
  categorySlug 
}: { 
  currentPage: number; 
  totalPages: number; 
  categorySlug: string; 
}) {
  const pages = Array.from({ length: totalPages }, (_, i) => i + 1);
  const showEllipsis = totalPages > 7;
  
  let visiblePages = pages;
  if (showEllipsis) {
    if (currentPage <= 4) {
      visiblePages = [...pages.slice(0, 5), -1, totalPages];
    } else if (currentPage >= totalPages - 3) {
      visiblePages = [1, -1, ...pages.slice(totalPages - 5)];
    } else {
      visiblePages = [1, -1, currentPage - 1, currentPage, currentPage + 1, -1, totalPages];
    }
  }

  return (
    <div className="flex items-center justify-center space-x-2">
      {/* Previous button */}
      {currentPage > 1 && (
        <Link href={`/gallery/${categorySlug}?page=${currentPage - 1}`}>
          <Button variant="outline" size="sm">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
      )}

      {/* Page numbers */}
      {visiblePages.map((page, index) => {
        if (page === -1) {
          return <span key={index} className="px-2">...</span>;
        }
        
        const isCurrentPage = page === currentPage;
        return (
          <Link key={page} href={`/gallery/${categorySlug}?page=${page}`}>
            <Button 
              variant={isCurrentPage ? "default" : "outline"} 
              size="sm"
              className="min-w-[40px]"
            >
              {page}
            </Button>
          </Link>
        );
      })}

      {/* Next button */}
      {currentPage < totalPages && (
        <Link href={`/gallery/${categorySlug}?page=${currentPage + 1}`}>
          <Button variant="outline" size="sm">
            <ArrowLeft className="h-4 w-4 rotate-180" />
          </Button>
        </Link>
      )}
    </div>
  );
}

function CategoryLoadingSkeleton() {
  return (
    <div className="space-y-8">
      {/* Header skeleton */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="h-9 w-32 bg-muted rounded animate-pulse" />
          <div className="h-5 w-40 bg-muted rounded animate-pulse" />
        </div>
        
        <div className="text-center space-y-4">
          <div className="h-8 w-48 bg-muted rounded mx-auto animate-pulse" />
          <div className="h-4 w-96 bg-muted rounded mx-auto animate-pulse" />
          <div className="h-5 w-32 bg-muted rounded mx-auto animate-pulse" />
        </div>
      </div>

      {/* Photos skeleton */}
      <PhotoGridSkeleton count={12} aspectRatio="landscape" />
    </div>
  );
}

export default async function CategoryPage({ params, searchParams }: CategoryPageProps) {
  const { category: categorySlug } = await params;
  const resolvedSearchParams = await searchParams;
  const page = parseInt(resolvedSearchParams.page as string) || 1;

  const containerClasses = createContainerClasses({
    size: 'lg',
    padding: true,
    center: true
  });

  return (
    <main className={containerClasses + ' py-8'}>
      <Suspense fallback={<CategoryLoadingSkeleton />}>
        <CategoryContent categorySlug={categorySlug} page={page} />
      </Suspense>
    </main>
  );
}