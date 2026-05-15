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

## Running the project

NTI ships as two services — a Python scraper (Telethon → embeddings → Qdrant) and a Node bot (Telegram queries → search → synthesis). Both are containerized with Docker Compose.

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/Mac) or Docker Engine + Compose (Linux)
- A Telegram API ID + hash from [my.telegram.org](https://my.telegram.org)
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- A free [Qdrant Cloud](https://cloud.qdrant.io) cluster
- A [Google AI Studio](https://aistudio.google.com/app/apikey) API key for Gemini

### One-time setup

1. Copy `.env.example` to `.env` and fill in every value.
2. Copy `shared/channels.example.json` to `shared/channels.json` and list the channels you have permission to index.
3. Build the images:
   ```bash
   docker compose build
   ```
4. **First-time Telegram login (interactive, once per machine).** Telethon needs the phone code Telegram sends to your account. Run the scraper's client smoke-test inside a one-shot container so the session file lands directly in the persistent Docker volume:
   ```bash
   docker compose run --rm scraper python client.py
   ```
   You'll be prompted for your phone number, the code Telegram texts you, and your 2FA password (if set). On success, the session is saved to the `scraper_sessions` volume and never needs to be entered again.

### Day-to-day

```bash
docker compose up -d            # start both services in the background
docker compose logs -f          # tail logs from both services
docker compose logs -f scraper  # tail just the scraper
docker compose down             # stop and remove containers (volumes survive)
docker compose up -d --build    # rebuild and restart after code changes
```

### Configuration files

| File                         | What it contains                                    | In git? |
|------------------------------|-----------------------------------------------------|---------|
| `.env`                       | API keys, tokens, phone number                      | No      |
| `shared/channels.json`       | List of channels to index                           | No      |
| `shared/qdrant.json`         | Collection name, vector size, distance metric       | Yes     |
| `scraper/state/state.json`   | Resume cursor (last-indexed message ID per channel) | No      |

### About the license

The code is released under the **GNU Affero General Public License v3.0 (AGPL-3.0)**. In plain terms:

- You may study, modify, and build on this code freely.
- If you distribute a modified version — **or run a modified version as a network service** (e.g. a hosted bot) — you must release the full corresponding source code under the same license.
- This blocks the most common form of "freeloading" on open-source work: taking it, modifying it, and offering it as a closed-source hosted service.

**The license governs only the code.** It does not grant any rights to Telegram's data or platform. Anyone using this code remains independently bound by [Telegram's Terms of Service](https://core.telegram.org/api/terms) and by the consent terms of the channels they choose to index.

See [LICENSE](LICENSE) for the full text.
