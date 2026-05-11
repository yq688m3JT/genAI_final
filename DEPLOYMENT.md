# Public Browser Demo

The presentation demo is designed to work from a plain browser link with no Streamlit account, no API key, and no local setup.

## Click-ready Demo Link

Use this link in Google Slides or PowerPoint:

```text
https://rawcdn.githack.com/yq688m3JT/genAI_final/fa4ed4cc3ab6dd13d10fa40e40ec5e6036816755/docs/demo.html
```

The committed demo file is:

```text
docs/demo.html
```

## Optional GitHub Pages Setup

If GitHub Pages is enabled for the repository and configured to serve the `/docs` folder, the cleaner URL is:

```text
https://yq688m3jt.github.io/genAI_final/
```

This is optional. The HTMLPreview link above works directly from the public GitHub repository.

## Why the Demo Is Static

Putting a DeepSeek API key in browser JavaScript would expose it to anyone who opens the page. The browser demo therefore uses the committed sample run and evaluation artifacts.

The full Streamlit app is still included for local runs where an API key can stay in an environment variable or server-side secret.
