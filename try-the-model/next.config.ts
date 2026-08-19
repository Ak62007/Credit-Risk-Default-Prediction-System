import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  agentRules: false,
  output: "standalone",
  basePath: "/try-the-model",
};

export default nextConfig;
