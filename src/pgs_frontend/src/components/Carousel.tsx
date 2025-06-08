"use client";

interface CarouselProps {
  currentIndex: number;
  selectedCard: number;
}

export const TOTAL_CARDS = 8;
export const CARDS_PER_VIEW = 3.5;

export default function Carousel({ currentIndex, selectedCard }: CarouselProps) {
  const cardWidthPercent = 100 / CARDS_PER_VIEW;

  return (
    <div className="w-full">
      <div className="relative overflow-hidden mx-[-1rem] py-4">
        <div 
          className="flex transition-transform duration-300 ease-in-out"
          style={{ transform: `translateX(-${currentIndex * cardWidthPercent}%)` }}
        >
          {[...Array(TOTAL_CARDS)].map((_, index) => (
            <div
              key={index}
              className="flex-shrink-0 px-2 py-2"
              style={{ width: `${cardWidthPercent}%` }}
            >
              <div className="bg-gray-200 rounded-lg aspect-[4/6] shadow-lg relative overflow-hidden">
                <div className="absolute bottom-4 left-4 right-4">
                  <p className="text-xs text-gray-600">Lorem ipsum</p>
                  <h3 className="text-2xl font-bold text-gray-800 break-words w-2/3">Dolor Lorem</h3>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
