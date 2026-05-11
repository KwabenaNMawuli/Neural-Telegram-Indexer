// Search the Qdrant index for messages relevant to a user query.
// Embeds the query with Gemini (task_type=RETRIEVAL_QUERY, 768 dims),
// then asks Qdrant for the top-N nearest payloads.

import "./env.js";  // ensures .env is loaded if this module is imported in isolation

import { GoogleGenAI } from "@google/genai";
import { QdrantClient } from "@qdrant/js-client-rest";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const qdrantConfig = JSON.parse(
  await readFile(resolve(__dirname, "../shared/qdrant.json"), "utf-8")
);

const COLLECTION = qdrantConfig.collection;
const VECTOR_SIZE = qdrantConfig.vector_size;
const EMBEDDING_MODEL = qdrantConfig.embedding_model;

const genai = new GoogleGenAI({ apiKey: process.env.Gemini_api_key });
const qdrant = new QdrantClient({
  url: process.env.Qdrant_url,
  apiKey: process.env.Qdrant_api_key,
});

async function embedQuery(text) {
  const result = await genai.models.embedContent({
    model: EMBEDDING_MODEL,
    contents: text,
    config: {
      taskType: "RETRIEVAL_QUERY",
      outputDimensionality: VECTOR_SIZE,
    },
  });
  return result.embeddings[0].values;
}

export async function searchMessages(query, { limit = 5, minScore = 0.5 } = {}) {
  const vector = await embedQuery(query);

  const result = await qdrant.query(COLLECTION, {
    query: vector,
    limit,
    with_payload: true,
  });

  const points = result.points ?? [];
  return points
    .filter((p) => p.score >= minScore)
    .map((p) => ({
      score: p.score,
      text: p.payload.text,
      channel: p.payload.channel,
      message_id: p.payload.message_id,
      url: p.payload.url,
      date: p.payload.date,
    }));
}
