'use client';

import { Button } from '@/components/ui/button';

export function RefreshButton() {
  return (
    <Button 
      onClick={() => window.location.reload()}
      variant="default"
    >
      Try Again
    </Button>
  );
}