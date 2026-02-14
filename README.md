# Graffiti Lookup NYC Web

An interactive web application to explore graffiti removal requests across New York City. Built with Astro and Vue, featuring a side-by-side list and map view.

## Features

- **Interactive Map** - View graffiti reports on a Leaflet map with CARTO Voyager basemaps
- **Search & Filter** - Search by ID or address, filter by status with dropdown
- **Click to Highlight** - Click markers or list items to sync selection between views
- **Live Map Updates** - Map markers update in real-time as you filter or scroll
- **Daily Updates** - Data refreshed automatically via GitHub Actions using [graffiti-lookup-nyc](https://pypi.org/project/graffiti-lookup-nyc/)
- **Geocoded Addresses** - Addresses automatically converted to map coordinates with caching
- **Mobile Responsive** - Optimized for mobile viewports with side-by-side filters

## Tech Stack

- [Astro](https://astro.build/) - Static site generator
- [Vue 3](https://vuejs.org/) - Interactive components with Composition API
- [Leaflet](https://leafletjs.com/) - Map library with [CARTO Voyager](https://carto.com/) tiles
- [geopy](https://geopy.readthedocs.io/) - Address geocoding via Nominatim
- [graffiti-lookup-nyc](https://pypi.org/project/graffiti-lookup-nyc/) - NYC 311 graffiti data CLI

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
pip install -r geocode/requirements.txt

# Generate graffiti data (replace with your IDs)
graffiti-lookup-nyc --ids "G258700,G258801,G258900" --file-path public/graffiti-lookups.json --file-type json

# Geocode addresses
python -m geocode
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
   - Add a variable named `GRAFFITI_IDS` with comma-separated graffiti lookup IDs (e.g., `G258700,G258801,G258900`)

### Manual Deployment

You can trigger a manual deployment from the Actions tab by running the "Build and Deploy" workflow.

## Project Structure

```
├── .github/
│   └── workflows/
│       ├── build-and-deploy.yml  # Daily data fetch & deploy
│       ├── codeql.yml            # Security analysis
│       ├── lint-js.yml           # ESLint for Vue/Astro
│       ├── lint-python.yml       # Black & flake8 for Python
│       └── test.yml              # Python tests with coverage
├── geocode/                      # Python geocoding package
│   ├── __init__.py
│   ├── __main__.py               # Entry point (python -m geocode)
│   ├── geocoder.py               # Geocoding logic with caching
│   ├── logger.py                 # Logging setup
│   ├── sanitize.py               # Address normalization
│   ├── requirements.txt          # Python dependencies
│   ├── requirements-dev.txt      # Dev dependencies (pytest)
│   └── tests/                    # Test suite
├── public/
│   ├── geocode-cache.json        # Cached geocoding results
│   └── graffiti-lookups.json     # Generated graffiti data
├── src/
│   ├── components/
│   │   ├── ListItem.vue          # Individual report card
│   │   ├── ListView.vue          # Scrollable list with search & filter
│   │   ├── MapView.vue           # Leaflet map with dynamic markers
│   │   ├── SearchBar.vue         # Reusable search input component
│   │   ├── StatusChip.vue        # Status badge with color coding
│   │   └── StatusFilter.vue      # Reusable status dropdown filter
│   ├── layouts/
│   │   └── Layout.astro          # Base HTML layout (100dvh viewport)
│   └── pages/
│       └── index.astro           # Main page with flex layout
├── astro.config.mjs              # Astro configuration
├── eslint.config.js              # ESLint configuration
├── setup.cfg                     # Python tool config (flake8, pytest)
└── package.json
```

## Architecture Diagram

Below is a high level architecture diagram showing the main data flow and core components:

```mermaid
flowchart TD
   subgraph Data_Pipeline
      GH[GitHub Actions]
      CLI[graffiti-lookup-nyc (Python)]
      GEOPY[geocode (Python)]
      GH --> CLI
      GH --> GEOPY
      CLI --> PUBLIC_JSON[graffiti-lookups.json]
      GEOPY --> GEOCACHE[geocode-cache.json]
   end

   PUBLIC_JSON & GEOCACHE --> Astro[Astro Build]
   Astro --> Frontend[Vue & Astro Frontend]
   Frontend --> User[User]
```

## License

MIT
