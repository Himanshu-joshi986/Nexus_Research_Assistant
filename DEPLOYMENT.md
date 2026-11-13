# Deploy with GitHub Pages and Render

GitHub Pages hosts the static frontend, and Render runs the FastAPI backend as a native Python web service. No Docker is needed.

## 1. Prepare the repository

1. Revoke and replace any API keys that have been exposed. Add the new keys only in Render's environment settings.
2. The root `.gitignore` excludes `.env` files and runtime data files. Before pushing, check `git status --short --untracked-files=all`, `git ls-files backend/.env backend/data/users.json backend/data/reports.json`, and `git check-ignore -v backend/.env backend/data/users.json backend/data/reports.json`. If a secret file was already tracked, `.gitignore` alone will not untrack it; remove it from Git's index with `git rm --cached <file>`, rotate its credentials, and remember that this does not remove it from previous commits.
3. Push the project to a GitHub repository on the `main` branch. Do not commit `backend/.env`.

## 2. Deploy the backend to Render

1. In Render, choose **New â†’ Web Service** and connect the GitHub repository.
2. Set:
   - **Root Directory:** `backend`
   - **Runtime:** Python (version pinned to 3.11.9 by the repository's `.python-version` file)
   - **Build Command:** `pip install -r requirements.txt && python -m spacy download en_core_web_sm && python -c "import nltk; [nltk.download(pkg, quiet=True) for pkg in ['punkt', 'punkt_tab', 'stopwords', 'wordnet', 'averaged_perceptron_tagger']]"`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path:** `/health`
3. In **Environment**, add these variables using the newly rotated API keys and a unique admin password:
   - `TAVILY_API_KEY`
   - `OPENROUTER_API_KEY`
   - `ADMIN_USERNAME`
   - `ADMIN_PASSWORD`
   - `ADMIN_NAME` (optional; defaults to `Research Admin`)
4. Choose a plan and deploy. The first build may take a while because it installs NLP packages and downloads the spaCy model.
5. Once deployed, visit `https://YOUR-SERVICE.onrender.com/health`. It should return `{"status":"ok"}`.

When no `backend/data/users.json` exists, the backend creates the initial admin account from `ADMIN_USERNAME`, `ADMIN_PASSWORD`, and `ADMIN_NAME`. When no runtime `reports.json` exists, it starts with the safe, tracked sample report in `backend/data/demo_reports.json`. Locally, existing `users.json` and `reports.json` files continue to take precedence.

## 3. Point the frontend to Render

Edit `frontend/components/config.js` and replace the local URL with your Render URL (no trailing slash):

```js
window.RESEARCH_API_URL = 'https://YOUR-SERVICE.onrender.com';
```

Commit and push this change to `main`.

## 4. Publish the frontend on GitHub Pages

1. In the GitHub repository, open **Settings â†’ Pages** and set the source to **GitHub Actions**.
2. The included `.github/workflows/pages.yml` publishes the `frontend/` directory when changes are pushed to `main`.
3. Wait for the **Deploy frontend to GitHub Pages** workflow to complete, then open the Pages URL.
4. Sign in with the admin username and password configured in Render.

## Optional: reduce idle sleeping

Render Free services can sleep after inactivity. An uptime monitor can request `https://YOUR-SERVICE.onrender.com/health` every 10 minutes to reduce idle sleeping. This is not a guarantee of always-on service and does not make local data persistent.

## Free-plan limitations

Render Free may sleep after inactivity and has an ephemeral filesystem. Generated reports and ChromaDB data can be lost after a sleep, restart, or deploy; runtime-created account files can be lost too. The configured admin is recreated if its file is missing, and the sample report is restored if the runtime reports file is missing, but newly generated reports and vectors are not durable. To keep them, use persistent storage and update the app to use it. The service uses model-heavy NLP and embeddings; if it exceeds the free instance's resources, use a larger plan or different inference/storage service. This simple login system is for a demo, not real user accounts or sensitive data.

