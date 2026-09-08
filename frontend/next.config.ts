import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow all typical local origins so HMR works for the frontend
  experimental: {
    serverActions: {
      allowedOrigins: ["localhost:3000", "127.0.0.1:3000", "10.124.135.77:3000"],
    },
  },
  // To fix the blocked cross-origin Next.js dev resources warning:
  allowedDevOrigins: ['127.0.0.1', 'localhost', '10.124.135.77'],
  async rewrites() {
    return [
      {
        source: '/outputs/:path*',
        destination: 'http://localhost:8000/outputs/:path*',
      },
      {
        source: '/download/:path*',
        destination: 'http://localhost:8000/download/:path*',
      },
    ];
  },
};

export default nextConfig;
