# 🚀 Render Deployment Guide — Nexus AI

This guide walks you through deploying the **Nexus AI Inventory Management System** (both React Frontend & FastAPI Backend) to **Render** using either **Render Blueprints** (recommended) or **Manual Setup**.

---

## 🛠️ Option 1: One-Click Deploy using Render Blueprint (Recommended)

Render Blueprints allow you to deploy the full stack automatically using the `render.yaml` file located in the root of the repository.

### Steps:
1. Go to the [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** at the top right and select **Blueprint**.
3. Connect your GitHub repository: `https://github.com/Praveenofficial12/Inventary-Agent.git`.
4. Render will read the `render.yaml` file and prepare 2 services:
   - **nexus-ai-backend** (Python Web Service)
   - **nexus-ai-frontend** (Static Site)
5. Review the service configurations. Under `nexus-ai-backend` env variables, your **Groq API Key** is already populated.
6. Click **Approve**.
7. Once both services show `Live`, access the system via the **Static Site URL**.

---

## 🛠️ Option 2: Manual Deploy on Render Dashboard

If you prefer to configure the services manually on Render, follow these steps:

### 1. Backend Service (FastAPI)
1. Go to the Render Dashboard, click **New +** and select **Web Service**.
2. Connect your GitHub repository.
3. Configure the service settings:
   - **Name:** `nexus-ai-backend`
   - **Language/Environment:** `Python 3`
   - **Root Directory:** `backend` (if you want repository subfolder, or leave blank and adjust commands)
   - If Root Directory is blank:
     - **Build Command:** `pip install -r backend/requirements.txt`
     - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add the following **Environment Variables**:
   - `MONGO_URI` = `mongodb+srv://...` (or use a placeholder/MongoDB Atlas URI)
   - `MONGO_DB_NAME` = `inventory_db`
   - `SECRET_KEY` = `nexus_ai_inventory_secret_key_prod_2026`
   - `LLM_PROVIDER` = `groq`
   - `GROQ_API_KEY` = `<your_groq_api_key>`
   - `CORS_ORIGINS` = `*`
5. Click **Create Web Service**.
6. Copy the generated Web Service URL (e.g. `https://nexus-ai-backend.onrender.com`).

---

### 2. Frontend Service (React / Vite Static Site)
1. In the Render Dashboard, click **New +** and select **Static Site**.
2. Connect your GitHub repository.
3. Configure the build settings:
   - **Name:** `nexus-ai-frontend`
   - **Build Command:** `cd frontend && npm install && npm run build`
   - **Publish Directory:** `frontend/dist`
4. Add the following **Environment Variables**:
   - `VITE_API_URL` = `https://nexus-ai-backend.onrender.com` (use your actual deployed backend URL)
5. Set up **Rewrite Rules** (CRITICAL for React Router SPA pathing):
   - Under the service dashboard, navigate to **Redirects/Rewrites**.
   - Add a rule:
     - **Source:** `/*`
     - **Destination:** `/index.html`
     - **Action:** `Rewrite`
6. Click **Create Static Site**.

---

## 💾 SQLite Database Persistence Note (Free Tier Limitations)

Because the project leverages an intelligent mock database layer synced to a local file (`database.db`), deploying on Render's ephemeral instance means **database modifications will reset whenever the backend container restarts on free plans.**

### How to attain full persistence:
- **Option A (Premium Disk)**: In the backend service settings on Render, attach a **Persistent Disk** mounted at `/data/`, and update the path in `backend/app/db/mongo.py` to write `database.db` inside `/data/`.
- **Option B (MongoDB Atlas)**: Update `MONGO_URI` in the backend service variables to a live MongoDB Atlas cluster. The system will automatically skip SQLite local sync and read/write directly to your high-performance database instance!
