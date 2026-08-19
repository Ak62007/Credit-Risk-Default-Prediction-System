import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  agentRules: false,
  output: "standalone",
  basePath: "/try-the-model",
  trailingSlash: true,
};

export default nextConfig;
