# Neural-Telegram-Indexer
A RAG-based search engine designed to turn unstructured Telegram channel data into a searchable, synthesized research library.

## Scope and Intended Use

This is a **personal, educational project** built by a student learning RAG systems, vector databases, and the Telegram API. It is not a product, not maintained for general use, and not intended to be deployed at scale.

### Before you use this code

If you fork or run this against any Telegram channel, you are responsible for ensuring you have the right to do so. In practice, that means:

- **Get explicit permission from each channel's administrator before indexing it.** Telegram's [API Terms of Service](https://core.telegram.org/api/terms) restrict the use of channel data in AI-related systems. Channel-admin consent does not override Telegram's terms, but it addresses the content-rights side of the equation and reflects good-faith engagement with the people whose work you're indexing.
- **Do not redistribute the scraped data.** No scraped messages, embeddings, or derived datasets are included in this repository, and none should ever be committed to a fork.
- **Do not use the indexed data to train, fine-tune, or otherwise build AI models.** This project uses messages as *retrieval context* for an LLM at query time only — it is not a dataset-construction tool, and using it that way would be both a ToS violation and outside the project's intent.

### What this project is not

- Not a commercial product.
- Not a way to anonymously scrape channels you have not joined or do not have permission to use.
- Not a substitute for legitimate research data sources (arXiv, OpenReview, journal APIs) when those are available.
- Not affiliated with or endorsed by Telegram.

### About the license

The code is released under the **GNU Affero General Public License v3.0 (AGPL-3.0)**. In plain terms:

- You may study, modify, and build on this code freely.
- If you distribute a modified version — **or run a modified version as a network service** (e.g. a hosted bot) — you must release the full corresponding source code under the same license.
- This blocks the most common form of "freeloading" on open-source work: taking it, modifying it, and offering it as a closed-source hosted service.

**The license governs only the code.** It does not grant any rights to Telegram's data or platform. Anyone using this code remains independently bound by [Telegram's Terms of Service](https://core.telegram.org/api/terms) and by the consent terms of the channels they choose to index.

See [LICENSE](LICENSE) for the full text.
