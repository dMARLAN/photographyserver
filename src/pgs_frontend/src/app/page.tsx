import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <div className="container mx-auto p-8">
      <h1 className="text-4xl font-bold mb-8">Photography Gallery</h1>
      <p className="text-muted-foreground mb-4">Welcome to the Photography Server frontend.</p>
      <Button>Get Started</Button>
    </div>
  );
}
