# Public Demo Deployment

The safest public-demo setup is Streamlit Community Cloud. It gives you a live link while keeping the DeepSeek API key server-side.

## Deploy on Streamlit Cloud

1. Push the repo to GitHub.
2. Go to `https://share.streamlit.io/`.
3. Create a new app from the GitHub repo.
4. Set:
   - Repository: `yq688m3JT/genAI_final`
   - Branch: `main`
   - Main file path: `app.py`
5. Open the app's Settings -> Secrets.
6. Add:

```toml
DEEPSEEK_API_KEY = "your_deepseek_key_here"
```

7. Deploy.

The app sidebar should show `LLM key detected on server`, and the LLM extraction toggle should be on by default.

## Why Not a Static Website With the Key?

A static website would expose the DeepSeek key in browser JavaScript. Anyone could inspect the page and copy the key. Streamlit avoids this because the API call happens on the server.

## Demo Script

Use the default warning text, leave provider as `deepseek`, and keep model as `deepseek-v4-pro`.

1. Show the scenario brief updating from the warning text.
2. Open the Synthetic Ledger tab to show labeled transactions.
3. Open Evaluation to show guided data beating the baseline.
4. Open Export Package to show the downloadable CSV/JSON outputs.
