import { minify } from '@swc/core'
import { VueLoaderPlugin } from "vue-loader";
import fs from "fs"
import { fileURLToPath } from "url"
import path from "path"

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const distPath = path.resolve(__dirname, "./dist")

// cleanup
if (fs.existsSync(distPath)) {
  fs.rmSync(distPath, { recursive: true, force: true })
}

class VendorOnlyMinifyPlugin {
  apply(compiler) {
    compiler.hooks.thisCompilation.tap('VendorOnlyMinifyPlugin', compilation => {
      compilation.hooks.processAssets.tapPromise(
        {
          name: 'VendorOnlyMinifyPlugin',
          stage: compiler.webpack.Compilation.PROCESS_ASSETS_STAGE_OPTIMIZE,
        },
        async assets => {
          for (const filename of Object.keys(assets)) {
            if (filename.includes('main') || !filename.endsWith('.js')) {
              continue
            }
            const source = assets[filename].source()
            const result = await minify(source, { compress: true, mangle: true })
            compilation.updateAsset(filename,
              new compiler.webpack.sources.RawSource(result.code))
          }
        },
      )
    })
  }
}

export default {
  entry: "./src/main.ts",
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
    new VueLoaderPlugin(),
    new VendorOnlyMinifyPlugin(),
  ],
  optimization: {
    minimize: false,
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendor',
          chunks: 'all',
        }
      },
    },
  },
};
