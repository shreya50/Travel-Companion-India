# 📍 Travel Companion - India

A modern monorepo application designed to help travelers discover, explore, and map points of interest (POIs) across India. It integrates a **Next.js frontend** for interactive visualization with a **Python agent-based backend** (powered by the Google Antigravity SDK) that fetches and seeds real-time data from Wikipedia.

---

## 📁 Repository Structure

```filepath
├── client/          # Next.js web application (React, TypeScript, Tailwind, Leaflet)
├── database/        # SQLite Database and Python provisioning scripts
├── worker/          # Python worker utilizing the Google Antigravity SDK
├── .env.example     # Template for configuring environment variables
└── package.json     # Root npm package for monorepo configuration
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Node.js** (v18 or higher)
- **Python** (v3.9 or higher)
- **Gemini API Key** (Get yours at [Google AI Studio](https://aistudio.google.com/app/api-keys))

### 2. Environment Setup
Clone this repository and create a `.env` file at the root:

```bash
cp .env.example .env
```

Open `.env` and set your Gemini API Key:
```env
GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Install Dependencies
Install Node.js dependencies for the Next.js client:
```bash
npm install
```

Install Python dependencies for the worker and provisioner:
```bash
pip install -r worker/requirements.txt
```
*(Make sure `google-genai`, `google-antigravity`, and `python-dotenv` are installed in your Python environment).*

---

## 🗄️ Database Provisioning & Seeding

The application stores data locally in a SQLite database at `database/travel_companion.db`.

### Initialize the Schema
Run the database provision script to build the tables:
```bash
python database/provision.py --init
```

### Option A: Standard Wikipedia Seed
You can automatically fetch and seed points of interest around a city within a given radius using the CLI utility:
```bash
# Seed Mumbai with a 5km radius (lat: 18.9220, lon: 72.8347)
python database/provision.py --seed "Mumbai" 18.9220 72.8347 --radius 5000 --limit 10
```

### Option B: AI-Driven Agent Seed
You can use the smart travel agent to autonomously search, select, and store interesting points of interest for a given city:
```bash
python worker/populate_city_pois.py "New Delhi"
```
The agent will:
1. Lookup the coordinates of the city on Wikipedia.
2. Query nearby geographical POIs.
3. Intelligently select the most prominent POIs and store them in the SQLite database.

---

## 💻 Running the Web Application

To run the Next.js client application locally:

```bash
# From the root directory, start the Next.js dev server in the client workspace
npm run dev --workspace=client
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Features
* **Interactive Mapping**: Interactive Leaflet maps rendering points of interest with a CartoDB Dark Matter design.
* **Wikipedia Integration**: Read parsed Wikipedia articles directly on the app with a clean reading interface.
* **Server-Side Hydration**: Fast page loads and SEO optimized using Next.js App Router.
