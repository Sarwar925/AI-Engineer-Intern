import fs from "node:fs/promises";
import path from "node:path";
import os from "node:os";
import { fileURLToPath, pathToFileURL } from "node:url";

async function primeEsbuildBinary() {
  if (process.platform !== "win32") {
    return;
  }

  const here = path.dirname(fileURLToPath(import.meta.url));
  const source = path.resolve(
    here,
    "../node_modules/@esbuild/win32-x64/esbuild.exe",
  );
  const targetDir = path.join(os.tmpdir(), "woo-commerce-chat-ui", "esbuild");
  const target = path.join(targetDir, "esbuild.exe");

  await fs.mkdir(targetDir, { recursive: true });

  try {
    const [sourceStat, targetStat] = await Promise.all([
      fs.stat(source),
      fs.stat(target).catch(() => null),
    ]);

    if (!targetStat || targetStat.size !== sourceStat.size) {
      await fs.copyFile(source, target);
    }
  } catch {
    await fs.copyFile(source, target);
  }

  process.env.ESBUILD_BINARY_PATH = target;
}

await primeEsbuildBinary();
await import(pathToFileURL(path.resolve("node_modules/vite/bin/vite.js")).href);
