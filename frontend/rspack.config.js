import { minify } from "@swc/core";
import { DefinePlugin } from "@rspack/core";
import { VueLoaderPlugin } from "vue-loader";
import fs from "fs";
import { fileURLToPath } from "url";
import path from "path";
import { defineConfig } from "@rspack/cli";
import { rspack } from "@rspack/core";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const distPath = path.resolve(__dirname, "./dist");

// cleanup
if (fs.existsSync(distPath)) {
  for (const child of fs.readdirSync(distPath)) {
    fs.rmSync(path.join(distPath, child), { recursive: true, force: true });
  }
}

class VendorOnlyMinifyPlugin {
  apply(compiler) {
    compiler.hooks.thisCompilation.tap(
      "VendorOnlyMinifyPlugin",
      (compilation) => {
        compilation.hooks.processAssets.tapPromise(
          {
            name: "VendorOnlyMinifyPlugin",
            stage: compiler.webpack.Compilation.PROCESS_ASSETS_STAGE_OPTIMIZE,
          },
          async (assets) => {
            for (const filename of Object.keys(assets)) {
              if (filename.includes("main") || !filename.endsWith(".js")) {
                continue;
              }
              const source = assets[filename].source();
              const result = await minify(source, {
                compress: true,
                mangle: true,
              });
              compilation.updateAsset(
                filename,
                new compiler.webpack.sources.RawSource(result.code),
              );
            }
          },
        );
      },
    );
  }
}

export default defineConfig({
  context: __dirname,
  entry: path.resolve(__dirname, "src/main.ts"),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
    extensions: [".ts", ".js", ".vue"],
  },
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        loader: "builtin:swc-loader",
        options: {
          jsc: {
            parser: {
              syntax: "typescript",
              tsx: false,
            },
          },
        },
      },
      {
        test: /\.vue$/,
        loader: "vue-loader",
      },
    ],
  },
  plugins: [
    new DefinePlugin({
      __VUE_OPTIONS_API__: JSON.stringify(true),
      __VUE_PROD_DEVTOOLS__: JSON.stringify(true),
      __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: JSON.stringify(false),
    }),
    new rspack.HtmlRspackPlugin({
      template: path.resolve(__dirname, "index.html"),
      minify: false,
      inject: "body",
    }),
    new VueLoaderPlugin(),
    new VendorOnlyMinifyPlugin(),
  ],
  optimization: {
    minimize: false,
    splitChunks: {
      chunks: "all",
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: "vendor",
          chunks: "all",
        },
      },
    },
  },
  performance: {
    maxEntrypointSize: 512000,
    maxAssetSize: 512000,
  },
});
