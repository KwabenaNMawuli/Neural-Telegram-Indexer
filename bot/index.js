// Telegraf entry point. Wires user messages → search → synthesize → reply.

import "./env.js";  // MUST be first — loads .env before any module reads process.env

import { Telegraf } from "telegraf";
import { searchMessages } from "./search.js";
import { synthesize } from "./synthesize.js";
import {
  formatAnswer,
  formatNoResults,
  formatError,
  formatWelcome,
  formatHelp,
} from "./formatter.js";

const token = process.env.Bot_token?.trim();
if (!token) {
  console.error("Bot_token is not set in .env");
  process.exit(1);
}

const bot = new Telegraf(token);

bot.start(async (ctx) => {
  await ctx.reply(formatWelcome(), { parse_mode: "HTML" });
});

bot.help(async (ctx) => {
  await ctx.reply(formatHelp(), { parse_mode: "HTML" });
});

bot.on("text", async (ctx) => {
  const query = ctx.message.text.trim();
  if (!query || query.startsWith("/")) return;

  // Show a "typing..." indicator while we work.
  await ctx.sendChatAction("typing");

  try {
    const results = await searchMessages(query, { limit: 5, minScore: 0.5 });

    if (results.length === 0) {
      await ctx.reply(formatNoResults(), { parse_mode: "HTML" });
      return;
    }

    const answer = await synthesize(query, results);
    await ctx.reply(formatAnswer(answer, results), {
      parse_mode: "HTML",
      link_preview_options: { is_disabled: true },
    });
  } catch (err) {
    console.error("[bot] handler error:", err);
    await ctx.reply(formatError(err), { parse_mode: "HTML" });
  }
});

bot.catch((err) => {
  console.error("[telegraf] unhandled:", err);
});

await bot.launch();
console.log("Bot is online. Press Ctrl+C to stop.");

process.once("SIGINT", () => bot.stop("SIGINT"));
process.once("SIGTERM", () => bot.stop("SIGTERM"));
