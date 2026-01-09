# FedGuard AI - Public Deployment Guide

This guide details how to deploy **FedGuard AI** to the public internet for free, using **Render** (for the Backend API) and **Vercel** (for the Frontend).

---

## 🚀 Phase 1: Deploy Backend (Render)
We will deploy the Python FastAPI backend first to get a public API URL.

### Prerequisites
- A GitHub account.
- A [Render](https://render.com) account (Free Tier).

### Steps
1.  **Push Code to GitHub**:
    - Ensure your `FedGuardAI` project is pushed to a GitHub repository.
    - Make sure the folder structure is:
        ```
        /backend
          /app
            main.py
          requirements.txt
          Procfile
          Dockerfile
        ```

2.  **Create New Web Service on Render**:
    - Go to [Render Dashboard](https://dashboard.render.com).
    - Click **New +** -> **Web Service**.
    - Connect your GitHub repository.

3.  **Configure Service**:
    - **Name**: `fedguard-backend` (or similar).
    - **Root Directory**: `backend` (Important!).
    - **Runtime**: `Python 3`.
    - **Build Command**: `pip install -r requirements.txt`.
    - **Start Command**: `gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`.
    - **Plan**: Free.

4.  **Deploy**:
    - Click **Create Web Service**.
    - Wait for the deployment to finish.
    - **Copy the URL**: You will get a URL like `https://fedguard-backend.onrender.com`.

5.  **Verify**:
    - Visit `https://fedguard-backend.onrender.com/docs` to see the Swagger API documentation.
    - Visit `https://fedguard-backend.onrender.com/health` to check health status.

---

## 🌐 Phase 2: Deploy Frontend (Vercel)
Now we deploy the static HTML frontend and connect it to the backend.

### Prerequisites
- A [Vercel](https://vercel.com) account.

### Steps
1.  **Configure Backend URL**:
    - Open `frontend/config.js` in your local project.
    - Update `API_BASE_URL` with your **Render Backend URL** from Phase 1.
    ```javascript
    const CONFIG = {
        API_BASE_URL: 'https://fedguard-backend.onrender.com/api/v1',
        // ...
    };
    ```
    - Commit and push this change to GitHub.

2.  **Import Project to Vercel**:
    - Go to [Vercel Dashboard](https://vercel.com/dashboard).
    - Click **Add New...** -> **Project**.
    - Import your GitHub repository.

3.  **Configure Build**:
    - **Framework Preset**: Other (or just leave default).
    - **Root Directory**: `frontend`.
    - **Build Command**: (Leave empty).
    - **Output Directory**: (Leave empty, or `.` if asked).
    
4.  **Deploy**:
    - Click **Deploy**.
    - Vercel will build and assign a public URL (e.g., `https://fedguard-ai.vercel.app`).

5.  **Verify**:
    - Open your Vercel URL.
    - Try logging in (Email: `admin@rbi.org.in`, Password: `password`).
    - It should successfully hit your Render backend.

---

## 🧪 Local Demo Setup (Offline Mode)
If internet access is not available, you can run the full stack locally using Docker.

1.  **Run Docker Compose**:
    ```bash
    docker-compose up --build
    ```
2.  **Access App**:
    - Frontend: `http://localhost`
    - Backend API: `http://localhost:8000/docs`

---

## 🔧 Troubleshooting

### Login Failed?
- **Check Backend Status**: Render free tier spins down after inactivity. The first request might take 50+ seconds. Wait and try again.
- **CORS Errors**: Open Browser Console (F12). If you see CORS errors, ensure `backend/app/main.py` has `allow_origins=["*"]`.

### Updates
- To update the app, just `git push` to your main branch. Render and Vercel will automatically redeploy.
