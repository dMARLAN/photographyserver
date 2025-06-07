import React, { Suspense } from 'react';
import Link from 'next/link';
import { Metadata } from 'next';
import { Button } from '@/components/ui/button';
import { CategoryCard, CategoryCardSkeleton, CategoryGrid } from '@/components/custom/CategoryCard';
import { getCategories } from '@/lib/api';
import { createHeadingClasses, createContainerClasses } from '@/lib/utils';
import { ArrowLeft, Camera } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Photo Gallery - Browse by Category',
  description: 'Explore our photography collection organized by category. Professional photography showcasing various subjects and styles.',
  keywords: 'photography, gallery, categories, professional photos, portfolio',
  openGraph: {
    title: 'Photo Gallery - Browse by Category',
    description: 'Explore our photography collection organized by category',
    type: 'website',
    images: [
      {
        url: '/images/gallery-og.jpg',
        width: 1200,
        height: 630,
        alt: 'Photo Gallery',
      },
    ],
  },
};

// Force dynamic rendering to ensure fresh data
export const dynamic = 'force-dynamic';

async function GalleryContent() {
  try {
    const categories = await getCategories();
    
    if (categories.length === 0) {
      return <EmptyGalleryState />;
    }

    return (
      <div className="space-y-8">
        <GalleryHeader totalCategories={categories.length} />
        <CategoryGrid>
          {categories.map((category, index) => (
            <CategoryCard 
              key={category.name} 
              category={category}
              priority={index < 3} // Prioritize first 3 images
            />
          ))}
        </CategoryGrid>
      </div>
    );
  } catch (error) {
    console.error('Failed to load categories:', error);
    return <GalleryErrorState />;
  }
}

function GalleryHeader({ totalCategories }: { totalCategories: number }) {
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
    <div className="text-center space-y-4">
      <div className="flex items-center justify-center space-x-2 mb-4">
        <Camera className="h-8 w-8 text-primary" />
        <h1 className={headingClasses}>Photo Gallery</h1>
      </div>
      
      <p className={subheadingClasses + ' text-muted-foreground max-w-2xl mx-auto'}>
        Explore our photography collection organized by category. 
        {totalCategories > 0 && (
          <> Browse through {totalCategories} {totalCategories === 1 ? 'category' : 'categories'} of professional photography.</>
        )}
      </p>

      <div className="flex items-center justify-center space-x-4 pt-4">
        <Link href="/">
          <Button variant="outline" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Home
          </Button>
        </Link>
      </div>
    </div>
  );
}

function EmptyGalleryState() {
  const headingClasses = createHeadingClasses({
    level: 2,
    weight: 'semibold',
    spacing: 'normal'
  });

  return (
    <div className="text-center py-12 space-y-6">
      <div className="space-y-4">
        <Camera className="h-16 w-16 text-muted-foreground mx-auto" />
        <h2 className={headingClasses + ' text-muted-foreground'}>
          No Categories Found
        </h2>
        <p className="text-muted-foreground max-w-md mx-auto">
          The gallery is currently empty. Check back soon for new photography collections.
        </p>
      </div>
      
      <Link href="/">
        <Button>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Return to Home
        </Button>
      </Link>
    </div>
  );
}

function GalleryErrorState() {
  const headingClasses = createHeadingClasses({
    level: 2,
    weight: 'semibold',
    spacing: 'normal'
  });

  return (
    <div className="text-center py-12 space-y-6">
      <div className="space-y-4">
        <div className="h-16 w-16 rounded-full bg-destructive/10 flex items-center justify-center mx-auto">
          <Camera className="h-8 w-8 text-destructive" />
        </div>
        <h2 className={headingClasses + ' text-destructive'}>
          Failed to Load Gallery
        </h2>
        <p className="text-muted-foreground max-w-md mx-auto">
          We&apos;re having trouble loading the gallery. Please try refreshing the page or check back later.
        </p>
      </div>
      
      <div className="flex items-center justify-center space-x-4">
        <Button 
          onClick={() => window.location.reload()}
          variant="default"
        >
          Try Again
        </Button>
        <Link href="/">
          <Button variant="outline">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Return to Home
          </Button>
        </Link>
      </div>
    </div>
  );
}

function GalleryLoadingSkeleton() {
  const headingClasses = createHeadingClasses({
    level: 1,
    weight: 'bold',
    spacing: 'tight'
  });

  return (
    <div className="space-y-8">
      {/* Header skeleton */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center space-x-2 mb-4">
          <Camera className="h-8 w-8 text-primary" />
          <h1 className={headingClasses}>Photo Gallery</h1>
        </div>
        <div className="h-4 bg-muted rounded w-1/2 mx-auto animate-pulse" />
        <div className="h-4 bg-muted rounded w-1/3 mx-auto animate-pulse" />
      </div>

      {/* Categories skeleton */}
      <CategoryGrid>
        {Array.from({ length: 6 }, (_, i) => (
          <CategoryCardSkeleton key={i} />
        ))}
      </CategoryGrid>
    </div>
  );
}

export default function GalleryPage() {
  const containerClasses = createContainerClasses({
    size: 'lg',
    padding: true,
    center: true
  });

  return (
    <main className={containerClasses + ' py-8'}>
      <Suspense fallback={<GalleryLoadingSkeleton />}>
        <GalleryContent />
      </Suspense>
    </main>
  );
}