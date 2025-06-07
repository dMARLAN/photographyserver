export default function Loading() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center px-6 py-12">
      <div className="text-center space-y-6 max-w-4xl">
        <h1 className="text-3xl sm:text-5xl lg:text-6xl xl:text-7xl font-light tracking-wide text-foreground font-sans">
          MARLAN
        </h1>
        <div className="flex items-center justify-center space-x-2">
          <span className="text-lg sm:text-xl lg:text-2xl font-light tracking-[0.2em] text-muted-foreground font-sans">
            LOADING
          </span>
          <div className="flex space-x-1 ml-2">
            <div 
              className="w-1 h-1 bg-muted-foreground rounded-full animate-pulse"
              style={{ animationDelay: '0ms', animationDuration: '1.5s' }}
              aria-hidden="true"
            />
            <div 
              className="w-1 h-1 bg-muted-foreground rounded-full animate-pulse"
              style={{ animationDelay: '500ms', animationDuration: '1.5s' }}
              aria-hidden="true"
            />
            <div 
              className="w-1 h-1 bg-muted-foreground rounded-full animate-pulse"
              style={{ animationDelay: '1000ms', animationDuration: '1.5s' }}
              aria-hidden="true"
            />
          </div>
        </div>
        <p className="text-sm sm:text-base text-muted-foreground max-w-xl mx-auto leading-relaxed font-light opacity-75">
          Preparing your experience
        </p>
      </div>
      <span className="sr-only">Loading content, please wait</span>
    </main>
  );
}