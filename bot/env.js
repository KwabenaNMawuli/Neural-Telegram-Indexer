// Load environment variables from the project root's .env.
// Import this first in any module that reads process.env at module load time.
// ESM resolves imports in order, so importing this module before any other
// project file ensures env vars are populated when downstream modules evaluate.

import { config } from "dotenv";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
config({ path: resolve(__dirname, "../.env") });
