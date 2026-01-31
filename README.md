# Graffiti Lookup NYC Web

An interactive web application to explore graffiti removal requests across New York City. Built with Astro and Vue, featuring a side-by-side list and map view.

## Features

- **Interactive Map** - View graffiti reports on a Leaflet map powered by OpenStreetMap
- **Searchable List** - Browse 100+ graffiti removal requests sorted by last updated
- **Daily Updates** - Data refreshed automatically via GitHub Actions using [graffiti-lookup-nyc](https://pypi.org/project/graffiti-lookup-nyc/)
- **Geocoded Addresses** - Addresses automatically converted to map coordinates

## Tech Stack

- [Astro](https://astro.build/) - Static site generator
- [Vue 3](https://vuejs.org/) - Interactive components
- [Leaflet](https://leafletjs.com/) - Map library
- [geopy](https://geopy.readthedocs.io/) - Address geocoding

## Local Development

### Prerequisites

- Node.js 20+ (see `.nvmrc`)
- Python 3.12+ (for geocoding script)

### Setup

```bash
# Install Node dependencies
npm install

# Start development server
npm run dev
```

The site will be available at `http://localhost:4321/graffiti-lookup-nyc-web/`

### Generating Data Locally

To generate graffiti data and geocode addresses locally:

```bash
# Install Python dependencies
pip install -r scripts/requirements.txt

# Generate graffiti data (replace with your IDs)
graffiti-lookup-nyc --ids "G261910,G261911" --file-path public/graffiti-lookups.json --file-type json

# Geocode addresses
python scripts/geocode.py
```

## Deployment

This project is configured for GitHub Pages deployment.

### Automatic Deployment

The GitHub Actions workflow (`.github/workflows/build-and-deploy.yml`) runs daily at 12am EST and:

1. Fetches latest graffiti data using the `graffiti-lookup-nyc` CLI
2. Geocodes new addresses
3. Builds the Astro site
4. Deploys to GitHub Pages

### Required Setup

1. **Enable GitHub Pages** in your repository settings:
   - Go to Settings → Pages
   - Set Source to "Deploy from a branch"
   - Select the `gh-pages` branch

2. **Add Repository Variable**:
   - Go to Settings → Secrets and variables → Actions → Variables
   - Add a variable named `GRAFFITI_IDS` with comma-separated graffiti lookup IDs (e.g., `G261910,G261911`)

### Manual Deployment

You can trigger a manual deployment from the Actions tab by running the "Build and Deploy" workflow.

## Project Structure

```
├── public/
│   └── graffiti-lookups.json  # Generated graffiti data
├── scripts/
│   ├── geocode.py             # Address geocoding script
│   └── requirements.txt       # Python dependencies
├── src/
│   ├── components/
│   │   ├── ListView.vue       # Scrollable list of reports
│   │   └── MapView.vue        # Leaflet map component
│   ├── layouts/
│   │   └── Layout.astro       # Base HTML layout
│   └── pages/
│       └── index.astro        # Main page
├── astro.config.mjs           # Astro configuration
└── package.json
```

## License

MIT
