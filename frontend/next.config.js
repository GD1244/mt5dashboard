/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  distDir: 'dist',
  images: {
    unoptimized: true,
  },
  // Allow static export to work with client-side data fetching
  trailingSlash: true,
}

module.exports = nextConfig