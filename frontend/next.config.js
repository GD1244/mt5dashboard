/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    unoptimized: true,
  },
  // Allow client-side data fetching with Socket.io
  trailingSlash: true,
}

module.exports = nextConfig