// news-image-20261120 entrypoint (Node 22, standard library only).
// The front page is fully rendered by build-image.py into entry.png
// (a deterministic PIL drawing of the 52 verified 20-Nov-2026 stories);
// this program only checks the bytes and copies them to /output/entry.png.
import { createHash } from "node:crypto";
import { copyFileSync, existsSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const PNG_MAGIC = "89504e470d0a1a0a";

function fail(message: string): never {
  throw new Error(`entry: ${message}`);
}

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, "entry.png");
if (!existsSync(source)) fail("entry.png is missing next to main.ts");

const bytes = readFileSync(source);
if (bytes.subarray(0, 8).toString("hex") !== PNG_MAGIC) {
  fail("entry.png does not start with the PNG signature");
}
const digest = createHash("sha256").update(bytes).digest("hex");

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });
const target = join(outDir, "entry.png");
copyFileSync(source, target);
if (statSync(target).size !== bytes.length) fail("copied entry.png has the wrong size");
console.log(`wrote ${target} (${bytes.length} bytes, sha256 ${digest})`);
