"use client";

import { useState } from "react";
import Carousel, { TOTAL_CARDS, CARDS_PER_VIEW } from "@/components/Carousel";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight } from "lucide-react";

export default function Home() {
  const [selectedCard, setSelectedCard] = useState(0);
  
  // Calculate which position to scroll to based on selected card
  const scrollIndex = Math.max(0, Math.min(selectedCard - 1, TOTAL_CARDS - Math.floor(CARDS_PER_VIEW)));

  const nextCard = () => {
    setSelectedCard((prev) => Math.min(prev + 1, TOTAL_CARDS - 1));
  };

  const prevCard = () => {
    setSelectedCard((prev) => Math.max(prev - 1, 0));
  };

  return (
    <div className="min-h-screen flex flex-col justify-center py-12">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-6">
            <p className="text-xl text-gray-600 leading-relaxed">
              Every photograph tells a story.
            </p>
            <h1 className="text-5xl font-bold tracking-tight">
              Capturing Moments
            </h1>
            <p className="text-sm text-gray-500">
              From landscapes to portraits, discover the art of visual storytelling.
            </p>
          </div>
          <div>
            <Carousel currentIndex={scrollIndex} selectedCard={selectedCard} />
          </div>
        </div>
        
        <div className="relative flex items-center mt-12">
          <div className="absolute left-1/2 -translate-x-1/2 flex items-center gap-6">
            <Button
              variant="outline"
              size="lg"
              className="rounded-full w-16 h-16"
              onClick={prevCard}
              disabled={selectedCard === 0}
            >
              <ChevronLeft className="h-8 w-8" />
            </Button>

            <Button
              variant="outline"
              size="lg"
              className="rounded-full w-16 h-16"
              onClick={nextCard}
              disabled={selectedCard === TOTAL_CARDS - 1}
            >
              <ChevronRight className="h-8 w-8" />
            </Button>
          </div>
          
          <div className="w-full flex items-center justify-end">
            <div className="w-1/2 flex items-center pl-24">
              <div className="flex-1 h-2 bg-gray-300 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gray-800 transition-all duration-300 ease-out"
                  style={{ 
                    width: `${((selectedCard + 1) / TOTAL_CARDS) * 100}%` 
                  }}
                />
              </div>
              
              <div className="ml-8 text-2xl font-bold text-gray-800">
                {String(selectedCard + 1).padStart(2, '0')}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
