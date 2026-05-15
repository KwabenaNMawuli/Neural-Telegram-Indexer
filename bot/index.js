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

bot.use(async (ctx, next) => {
  console.log(
    `[update] type=${ctx.updateType}`,
    `from=${ctx.from?.username ?? ctx.from?.id ?? "?"}`,
    `text=${JSON.stringify(ctx.message?.text ?? "")}`
  );
  return next();
});

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

// Telegraf v4: bot.launch() returns a promise that resolves only when the bot
// stops, so we must NOT await it here — fire-and-forget, surface errors via .catch.
bot.launch({ dropPendingUpdates: true }).catch((err) => {
  console.error("[bot] launch failure:", err);
  process.exit(1);
});

// Confirm we got past launch initialization.
const me = await bot.telegram.getMe();
console.log(`Bot is online as @${me.username} (id=${me.id}). Press Ctrl+C to stop.`);

process.once("SIGINT", () => bot.stop("SIGINT"));
process.once("SIGTERM", () => bot.stop("SIGTERM"));
