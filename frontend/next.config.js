/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'picsum.photos',
      },
    ],
  },
  env: {
    API_URL: process.env.API_URL || 'http://localhost:8000/api',
  },
}

module.exports = nextConfig
