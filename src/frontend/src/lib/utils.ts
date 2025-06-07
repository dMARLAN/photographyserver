import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

// Core Shadcn utility function
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Image Handling Utilities
export type AspectRatio = 'square' | 'portrait' | 'landscape' | 'wide' | 'ultrawide' | 'tall'

export const aspectRatios: Record<AspectRatio, string> = {
  square: 'aspect-square',      // 1:1 - perfect for Instagram-style posts
  portrait: 'aspect-[3/4]',     // 3:4 - classic portrait orientation
  landscape: 'aspect-[4/3]',    // 4:3 - classic landscape orientation
  wide: 'aspect-[16/9]',        // 16:9 - wide cinematic format
  ultrawide: 'aspect-[21/9]',   // 21:9 - ultrawide cinematic
  tall: 'aspect-[9/16]'         // 9:16 - mobile/story format
}

export function getAspectRatioClass(ratio: AspectRatio): string {
  return aspectRatios[ratio]
}

export function createImageClasses({
  ratio,
  objectFit = 'cover',
  priority = false,
  rounded = false
}: {
  ratio?: AspectRatio
  objectFit?: 'cover' | 'contain' | 'fill' | 'none' | 'scale-down'
  priority?: boolean
  rounded?: boolean
}) {
  return cn(
    'relative overflow-hidden',
    ratio && aspectRatios[ratio],
    objectFit === 'cover' && 'object-cover',
    objectFit === 'contain' && 'object-contain',
    objectFit === 'fill' && 'object-fill',
    objectFit === 'none' && 'object-none',
    objectFit === 'scale-down' && 'object-scale-down',
    priority && 'will-change-transform',
    rounded && 'rounded-lg'
  )
}

// Gallery Layout Utilities
export type GalleryLayout = 'grid' | 'masonry' | 'flex' | 'carousel'

export const galleryLayouts: Record<GalleryLayout, string> = {
  grid: 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4',
  masonry: 'columns-1 sm:columns-2 lg:columns-3 gap-4 space-y-4',
  flex: 'flex flex-wrap gap-4',
  carousel: 'flex overflow-x-auto snap-x snap-mandatory gap-4 scrollbar-hide'
}

export function createGalleryClasses(layout: GalleryLayout, options?: {
  responsive?: boolean
  padding?: boolean
  maxWidth?: boolean
}) {
  const { responsive = true, padding = true, maxWidth = true } = options || {}
  
  return cn(
    galleryLayouts[layout],
    responsive && 'w-full',
    padding && 'p-4',
    maxWidth && 'max-w-7xl mx-auto'
  )
}

export function createGalleryItemClasses({
  interactive = true,
  hover = true,
  focus = true
}: {
  interactive?: boolean
  hover?: boolean
  focus?: boolean
} = {}) {
  return cn(
    'relative group cursor-pointer',
    interactive && 'transition-transform duration-300 ease-out',
    hover && 'hover:scale-[1.02] hover:shadow-xl',
    focus && 'focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2'
  )
}

// Typography Utilities
export function createHeadingClasses({
  level,
  serif = false,
  weight = 'normal',
  spacing = 'normal'
}: {
  level: 1 | 2 | 3 | 4 | 5 | 6
  serif?: boolean
  weight?: 'light' | 'normal' | 'medium' | 'semibold' | 'bold'
  spacing?: 'tight' | 'normal' | 'wide'
}) {
  const sizeClasses = {
    1: 'text-4xl md:text-6xl lg:text-7xl',
    2: 'text-3xl md:text-5xl lg:text-6xl',
    3: 'text-2xl md:text-4xl lg:text-5xl',
    4: 'text-xl md:text-3xl lg:text-4xl',
    5: 'text-lg md:text-2xl lg:text-3xl',
    6: 'text-base md:text-xl lg:text-2xl'
  }
  
  const weightClasses = {
    light: 'font-light',
    normal: 'font-normal',
    medium: 'font-medium',
    semibold: 'font-semibold',
    bold: 'font-bold'
  }
  
  const spacingClasses = {
    tight: 'tracking-tight',
    normal: 'tracking-normal',
    wide: 'tracking-wide'
  }
  
  return cn(
    sizeClasses[level],
    weightClasses[weight],
    spacingClasses[spacing],
    serif ? 'font-serif' : 'font-sans',
    'leading-tight text-balance'
  )
}

export function createTextOverlayClasses({
  position = 'bottom',
  background = 'gradient',
  padding = 'normal'
}: {
  position?: 'top' | 'bottom' | 'center' | 'full'
  background?: 'solid' | 'gradient' | 'blur' | 'none'
  padding?: 'sm' | 'normal' | 'lg'
} = {}) {
  const positionClasses = {
    top: 'absolute top-0 left-0 right-0',
    bottom: 'absolute bottom-0 left-0 right-0',
    center: 'absolute inset-0 flex items-center justify-center',
    full: 'absolute inset-0'
  }
  
  const backgroundClasses = {
    solid: 'bg-black/75',
    gradient: 'bg-gradient-to-t from-black/75 via-black/25 to-transparent',
    blur: 'backdrop-blur-sm bg-white/10',
    none: ''
  }
  
  const paddingClasses = {
    sm: 'p-2',
    normal: 'p-4',
    lg: 'p-6'
  }
  
  return cn(
    positionClasses[position],
    backgroundClasses[background],
    paddingClasses[padding],
    'text-white'
  )
}

// Animation and Transition Utilities
export function createTransitionClasses({
  type = 'all',
  duration = 'normal',
  easing = 'out'
}: {
  type?: 'all' | 'opacity' | 'transform' | 'colors'
  duration?: 'fast' | 'normal' | 'slow'
  easing?: 'linear' | 'in' | 'out' | 'in-out'
} = {}) {
  const typeClasses = {
    all: 'transition-all',
    opacity: 'transition-opacity',
    transform: 'transition-transform',
    colors: 'transition-colors'
  }
  
  const durationClasses = {
    fast: 'duration-150',
    normal: 'duration-300',
    slow: 'duration-500'
  }
  
  const easingClasses = {
    linear: 'ease-linear',
    in: 'ease-in',
    out: 'ease-out',
    'in-out': 'ease-in-out'
  }
  
  return cn(
    typeClasses[type],
    durationClasses[duration],
    easingClasses[easing]
  )
}

export function createHoverEffectClasses({
  effect = 'scale',
  intensity = 'subtle'
}: {
  effect?: 'scale' | 'opacity' | 'lift' | 'glow'
  intensity?: 'subtle' | 'medium' | 'strong'
} = {}) {
  const effectClasses = {
    scale: {
      subtle: 'hover:scale-[1.02]',
      medium: 'hover:scale-105',
      strong: 'hover:scale-110'
    },
    opacity: {
      subtle: 'hover:opacity-90',
      medium: 'hover:opacity-80',
      strong: 'hover:opacity-70'
    },
    lift: {
      subtle: 'hover:shadow-md hover:-translate-y-1',
      medium: 'hover:shadow-lg hover:-translate-y-2',
      strong: 'hover:shadow-xl hover:-translate-y-3'
    },
    glow: {
      subtle: 'hover:shadow-md hover:shadow-primary/20',
      medium: 'hover:shadow-lg hover:shadow-primary/30',
      strong: 'hover:shadow-xl hover:shadow-primary/40'
    }
  }
  
  return cn(
    createTransitionClasses(),
    effectClasses[effect][intensity]
  )
}

// Color Manipulation Utilities
export function createColorClasses({
  variant = 'primary',
  opacity = 100,
  hover = false
}: {
  variant?: 'primary' | 'secondary' | 'accent' | 'muted'
  opacity?: number
  hover?: boolean
} = {}) {
  const baseClasses = {
    primary: 'text-primary',
    secondary: 'text-secondary',
    accent: 'text-accent',
    muted: 'text-muted-foreground'
  }
  
  const opacityClass = opacity < 100 ? `opacity-${opacity}` : ''
  const hoverClass = hover ? 'hover:opacity-80' : ''
  
  return cn(
    baseClasses[variant],
    opacityClass,
    hoverClass,
    hover && createTransitionClasses({ type: 'opacity' })
  )
}

// Responsive Design Helpers
export type Breakpoint = 'sm' | 'md' | 'lg' | 'xl' | '2xl'

export function createResponsiveClasses({
  base,
  sm,
  md,
  lg,
  xl,
  '2xl': xl2
}: {
  base: string
  sm?: string
  md?: string
  lg?: string
  xl?: string
  '2xl'?: string
}) {
  return cn(
    base,
    sm && `sm:${sm}`,
    md && `md:${md}`,
    lg && `lg:${lg}`,
    xl && `xl:${xl}`,
    xl2 && `2xl:${xl2}`
  )
}

export function createContainerClasses({
  size = 'default',
  padding = true,
  center = true
}: {
  size?: 'sm' | 'default' | 'lg' | 'xl' | 'full'
  padding?: boolean
  center?: boolean
} = {}) {
  const sizeClasses = {
    sm: 'max-w-3xl',
    default: 'max-w-5xl',
    lg: 'max-w-7xl',
    xl: 'max-w-screen-2xl',
    full: 'max-w-full'
  }
  
  return cn(
    'w-full',
    sizeClasses[size],
    center && 'mx-auto',
    padding && 'px-4 sm:px-6 lg:px-8'
  )
}

// Accessibility Utilities
export function createSrOnlyClasses() {
  return 'sr-only'
}

export function createFocusClasses({
  style = 'ring',
  color = 'primary'
}: {
  style?: 'ring' | 'outline' | 'underline'
  color?: 'primary' | 'secondary' | 'accent'
} = {}) {
  const styleClasses = {
    ring: `focus:outline-none focus:ring-2 focus:ring-${color} focus:ring-offset-2`,
    outline: `focus:outline-2 focus:outline-${color}`,
    underline: `focus:underline focus:decoration-${color}`
  }
  
  return styleClasses[style]
}

export function createImageAltHelper(
  filename: string,
  context?: string
): string {
  const cleanName = filename
    .replace(/\.[^/.]+$/, '') // Remove file extension
    .replace(/[-_]/g, ' ')     // Replace hyphens and underscores with spaces
    .replace(/\b\w/g, l => l.toUpperCase()) // Title case
  
  return context ? `${context} - ${cleanName}` : cleanName
}

// Performance Utilities
export function createLoadingClasses({
  animate = true,
  skeleton = false
}: {
  animate?: boolean
  skeleton?: boolean
} = {}) {
  return cn(
    'bg-muted',
    animate && 'animate-pulse',
    skeleton && 'rounded-md'
  )
}

export function createOptimizedImageProps({
  priority = false,
  quality = 75,
  format = 'webp'
}: {
  priority?: boolean
  quality?: number
  format?: 'webp' | 'avif' | 'jpeg' | 'png'
} = {}) {
  return {
    priority,
    quality,
    format,
    placeholder: 'blur' as const,
    blurDataURL: 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAhEAACAQMDBQAAAAAAAAAAAAABAgMABAUGIWGRkbHB0eH/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/2gAMAwEAAhEDEQA/AJvBfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPfPf//Z'
  }
}
