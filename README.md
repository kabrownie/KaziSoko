# Kazi Soko

Kazi Soko is a static Kenyan job aggregator. A daily GitHub Actions job collects
public adverts into flat JSON files, and the browser provides search and
filtering without a backend or database.

## Local development

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m scraper.run --output site/public/data/jobs.json
npm --prefix site install
npm --prefix site run build
```

The generated site is in `site/dist`. To preview it, run
`npm --prefix site run dev`.

Scrapers must respect each source's `robots.txt`, terms of use, and rate
limits. Add sources as adapters in `scraper/adapters/`.

## Deployment

`.github/workflows/crawl.yml` runs daily at 18:00 EAT (`15:00 UTC`) and can
also be started manually. It crawls sources, builds the static site, and
publishes `site/dist` to GitHub Pages.

Kazi Soko aggregates publicly available job adverts and is not affiliated with
any government body or employer. Always verify details on the original source.
