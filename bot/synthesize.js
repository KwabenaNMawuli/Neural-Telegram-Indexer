// Given a user query and a list of retrieved messages, ask Gemini to write
// a grounded answer. The model is instructed to only use the supplied context
// and to cite sources by their bracketed index.

import "./env.js";  // ensures .env is loaded if this module is imported in isolation

import { GoogleGenAI } from "@google/genai";

const MODEL = "gemini-3.5-flash";

const genai = new GoogleGenAI({ apiKey: process.env.Gemini_api_key });

const SYSTEM_PROMPT = `You are a research assistant that answers questions using ONLY the provided Telegram channel messages.

Rules:
- Base your answer strictly on the supplied context. If the context does not contain enough information to answer, say so plainly.
- Cite supporting messages using bracketed indices like [1], [2] that match the numbered context entries.
- Be concise. Prefer 2-4 short paragraphs over a long monologue.
- Do not fabricate sources, URLs, or paper names that are not in the context.
- If the user asks about something completely unrelated to the context, say you don't have data on it.`;

function buildContextBlock(items) {
  return items
    .map((it, i) => {
      const idx = i + 1;
      const text = (it.text ?? "").trim();
      const head = `[${idx}] (${it.channel}/${it.message_id}) ${it.url}`;
      return `${head}\n${text}`;
    })
    .join("\n\n---\n\n");
}

export async function synthesize(query, contextItems) {
  const contextBlock = buildContextBlock(contextItems);
  const userPrompt = `Question: ${query}\n\nContext messages:\n\n${contextBlock}\n\nAnswer the question using only the context above. Cite the [n] indices that support each claim.`;

  const result = await genai.models.generateContent({
    model: MODEL,
    contents: userPrompt,
    config: {
      systemInstruction: SYSTEM_PROMPT,
      temperature: 0.2,
    },
  });

  return result.text ?? "";
}
