import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // =============================================================================
  // IMAGE OPTIMIZATION - Photography Website Optimized
  // =============================================================================
  images: {
    // Domains allowed for image optimization
    domains: [
      'localhost',
      '127.0.0.1',
      'marlanphotography.com',
      'www.marlanphotography.com',
      // CDN domains for future use
      'cdn.marlanphotography.com',
      'images.marlanphotography.com',
      // Common CDN providers for future expansion
      'res.cloudinary.com',
      'images.unsplash.com',
      'd1example.cloudfront.net', // AWS CloudFront example
    ],
    
    // Remote patterns for more flexible domain matching
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '8000',
        pathname: '/api/v1/images/**',
      },
      {
        protocol: 'https',
        hostname: '*.marlanphotography.com',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'res.cloudinary.com',
        pathname: '/**',
      },
    ],
    
    // Photography-optimized formats and quality
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    minimumCacheTTL: 60 * 60 * 24 * 30, // 30 days cache for images
    dangerouslyAllowSVG: true,
    contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",
    
    // Note: Quality is configured per-image in components, not globally
  },

  // =============================================================================
  // API ROUTES & BACKEND INTEGRATION
  // =============================================================================
  async rewrites() {
    const apiUrl = process.env.API_URL || 'http://localhost:8000';
    const apiVersion = process.env.NEXT_PUBLIC_API_VERSION || 'v1';
    
    return [
      // Proxy API calls to FastAPI backend during development
      {
        source: '/api/:path*',
        destination: `${apiUrl}/api/${apiVersion}/:path*`,
      },
      // Direct backend health check
      {
        source: '/health',
        destination: `${apiUrl}/health`,
      },
      // Image serving from backend
      {
        source: '/images/:path*',
        destination: `${apiUrl}/api/${apiVersion}/images/:path*`,
      },
      // Gallery API endpoints - redirect to categories
      {
        source: '/gallery/api/:path*',
        destination: `${apiUrl}/api/${apiVersion}/categories/:path*`,
      },
    ];
  },

  // =============================================================================
  // PERFORMANCE OPTIMIZATION
  // =============================================================================
  
  // Experimental features for better performance
  experimental: {
    // Enable app router optimizations
    appDocumentPreloading: true,
    optimizePackageImports: ['lucide-react', '@radix-ui/react-slot'],
  },

  // Compiler optimizations
  compiler: {
    // Remove console.log in production
    removeConsole: process.env.NODE_ENV === 'production' ? {
      exclude: ['error']
    } : false,
  },

  // Bundle size optimization
  webpack: (config, { dev, isServer }) => {
    // Optimize for photography content
    if (!dev && !isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
          },
          images: {
            test: /\.(png|jpe?g|gif|svg|webp|avif)$/i,
            name: 'images',
            chunks: 'all',
          },
        },
      };
    }

    // Handle SVG imports
    config.module.rules.push({
      test: /\.svg$/,
      use: ['@svgr/webpack'],
    });

    return config;
  },

  // =============================================================================
  // SECURITY HEADERS
  // =============================================================================
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          // Security headers
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on'
          },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=63072000; includeSubDomains; preload'
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block'
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin'
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=()'
          },
        ],
      },
      {
        // Cache headers for static assets
        source: '/(_next/static|favicon.ico|robots.txt|sitemap.xml)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable'
          },
        ],
      },
      {
        // Cache headers for images
        source: '/images/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=2592000, stale-while-revalidate=86400'
          },
        ],
      },
    ];
  },

  // =============================================================================
  // ENVIRONMENT & BUILD CONFIGURATION
  // =============================================================================
  
  // Environment variables to expose to the client
  env: {
    NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL,
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_BUSINESS_NAME: process.env.NEXT_PUBLIC_BUSINESS_NAME,
    NEXT_PUBLIC_ENABLE_GALLERY: process.env.NEXT_PUBLIC_ENABLE_GALLERY,
  },

  // Output configuration
  output: (process.env.NEXT_OUTPUT as 'standalone' | 'export') || 'standalone',
  
  // Enable gzip compression
  compress: true,
  
  // Power optimization for production
  poweredByHeader: false,
  
  // Generate ETags for caching
  generateEtags: true,

  // =============================================================================
  // REDIRECTS & URL HANDLING
  // =============================================================================
  async redirects() {
    return [
      // Redirect old gallery URLs if migrating from another system
      {
        source: '/old-gallery/:path*',
        destination: '/gallery/:path*',
        permanent: true,
      },
      // SEO-friendly redirects
      {
        source: '/portfolio',
        destination: '/gallery',
        permanent: true,
      },
    ];
  },

  // =============================================================================
  // TYPESCRIPT & DEVELOPMENT
  // =============================================================================
  typescript: {
    // Type checking during build
    ignoreBuildErrors: false,
  },
  
  eslint: {
    // ESLint during build
    ignoreDuringBuilds: false,
  },

  // Development configuration
  // Note: Next.js 15 removed most devIndicators options

  // =============================================================================
  // STATIC EXPORT & DEPLOYMENT
  // =============================================================================
  trailingSlash: false,
  
  // Asset prefix for CDN deployment
  assetPrefix: process.env.CDN_URL || '',
  
  // Base path for subdirectory deployment
  basePath: process.env.BASE_PATH || '',

  // =============================================================================
  // ANALYTICS & MONITORING
  // =============================================================================
  
  // Note: Analytics are configured in components/layout, not in config
};

export default nextConfig;
