import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Camera, ArrowRight } from 'lucide-react';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center px-6 py-12">
      <div className="text-center space-y-8 max-w-4xl">
        <h1 className="text-4xl sm:text-6xl lg:text-7xl xl:text-8xl font-light tracking-wide text-foreground font-sans">
          MARLAN
        </h1>
        <h2 className="text-2xl sm:text-3xl lg:text-4xl xl:text-5xl font-light tracking-[0.2em] text-muted-foreground font-sans">
          PHOTOGRAPHY
        </h2>
        <p className="text-base sm:text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed font-light">
          Capturing life&apos;s most precious moments through authentic storytelling and timeless imagery
        </p>
        
        {/* Gallery CTA */}
        <div className="pt-8">
          <Link href="/gallery">
            <Button size="lg" className="group">
              <Camera className="h-5 w-5 mr-2 transition-transform group-hover:scale-110" />
              Explore Gallery
              <ArrowRight className="h-4 w-4 ml-2 transition-transform group-hover:translate-x-1" />
            </Button>
          </Link>
        </div>
        
        {/* Quick navigation */}
        <div className="pt-6 flex items-center justify-center space-x-6 text-sm text-muted-foreground">
          <Link href="/gallery" className="hover:text-foreground transition-colors">
            Portfolio
          </Link>
          <span>•</span>
          <span>About</span>
          <span>•</span>
          <span>Contact</span>
        </div>
      </div>
    </main>
  );
}
