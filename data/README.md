# Data Directory

- **`data/raw/`** — Not committed (see `.gitignore`). Populated by `src/data/download_cases.py`, which pulls specific RCAEval case folders from Hugging Face on demand.
- **`data/processed/`** — Not committed. Populated by `src/preprocessing/align.py`; holds reshaped, phase-labeled metrics/logs for whichever cases you've downloaded and processed locally.
- **`data/demo/`** — **Committed** (~18MB). A small, fixed 6-case subset (1 per fault type) of processed data, bundled specifically so the deployed API/UI work out of the box without requiring a fresh RCAEval download at deploy time.

To reproduce the full 30-case evaluation, run the pipeline in `src/data/` → `src/preprocessing/` → `src/evaluation/` as described in the main README.

Source dataset: [RCAEval](https://github.com/phamquiluan/RCAEval) (Pham et al., arXiv:2412.17015).