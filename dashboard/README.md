# Dashboard deployment entrypoint

Deploy `dashboard/streamlit_app.py` on Streamlit Community Cloud.

The app reads only versioned JSON reports from the repository. This folder has
a deliberately small `requirements.txt`, so the dashboard deployment does not
install Chroma, Torch, sentence-transformers or other evaluation-only packages.
Community Cloud starts the app from the repository root, and the wrapper runs
the canonical root `streamlit_app.py` so local and deployed behavior stay the
same.

No secrets are required for the saved-results view. The Blind review view is
included for local reproducibility, but edits made on Community Cloud's
ephemeral filesystem are not a permanent review workflow.
