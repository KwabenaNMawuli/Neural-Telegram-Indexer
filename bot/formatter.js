// Telegram-flavored output formatting.
// We use parse_mode: "HTML" because it's far less footgun-y than MarkdownV2.

const escapeHtml = (s) =>
  String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

export function formatAnswer(answer, sources) {
  const body = escapeHtml(answer.trim());

  if (!sources || sources.length === 0) {
    return body;
  }

  const sourceLines = sources.map((s, i) => {
    const label = `[${i + 1}]`;
    const channel = escapeHtml(s.channel ?? "unknown");
    const url = encodeURI(s.url ?? "#");
    return `${label} <a href="${url}">${channel}/${s.message_id}</a>`;
  });

  return `${body}\n\n<b>Sources</b>\n${sourceLines.join("\n")}`;
}

export function formatNoResults() {
  return (
    "I couldn't find anything related to that in my index yet.\n\n" +
    "<i>The bot only knows about messages that have been scraped so far. " +
    "Try a different query, or wait until more data is indexed.</i>"
  );
}

export function formatError(err) {
  return (
    "Something went wrong while processing your question.\n\n" +
    `<code>${escapeHtml(err?.message ?? "unknown error")}</code>`
  );
}

export function formatWelcome() {
  return (
    "<b>Neural Telegram Indexer</b>\n\n" +
    "I search ML papers and resources shared in indexed Telegram channels, " +
    "then synthesize an answer from what I find.\n\n" +
    "<b>How to use:</b> just send me a question or topic — for example:\n" +
    "• <i>recent papers on retrieval-augmented generation</i>\n" +
    "• <i>graph neural networks for molecules</i>\n" +
    "• <i>diffusion models tutorial</i>\n\n" +
    "Use /help for more info."
  );
}

export function formatHelp() {
  return (
    "<b>Commands</b>\n" +
    "/start — show welcome\n" +
    "/help — show this message\n\n" +
    "<b>Anything else</b> you send is treated as a search query.\n\n" +
    "Replies always include source links so you can verify the answer " +
    "and read the original message in its channel."
  );
}
