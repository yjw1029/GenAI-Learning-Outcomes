# GenAI Learning Outcomes

## Contents

* Overview
* Repo Contents
* System Requirements
* Installation Guide
* Demo
* Results
* License

## Overview

This repository contains the experimental platform and analysis code for the paper *Heterogeneous Impact of AI Assistance on Learning Outcomes*. The study ran structured learning experiments in two course contexts, Python and Game Theory, comparing students with GPT-assisted access against a no-LLM control group.

The codebase includes the NiceGUI-based experiment platform, course materials and problem sets, participant survey and scoring utilities, and Jupyter notebooks used for the quantitative analyses and figures reported in the main paper and appendix.

## Repo Contents

* `platform/`: Chinese-language experiment platform, including consent flow, learning pages, surveys, problem sets, GPT chat integration, and admin utilities.
* `platform_en/`: English-language version of the experiment platform with the same core structure.
* `platform/presets/` and `platform_en/presets/`: example platform configuration files and authentication rosters.
* `analyze/`: analysis notebooks and reusable analysis modules.
* `analyze/*.ipynb`: notebooks that reproduce the main-paper and appendix analyses for *Heterogeneous Impact of AI Assistance on Learning Outcomes*.

## System Requirements

### Hardware Requirements

A standard workstation is sufficient for the platform and most analyses. The random-forest and SHAP-based appendix analyses benefit from multiple CPU cores but do not require a GPU.

The package has been developed and tested on a macOS workstation. It should also run on Linux with Python and `uv` installed.

### Software Requirements

The repository uses Python and `uv` for dependency management.

Required software:

* Python: version `>=3.10,<3.13`
* `uv`: for creating the environment and running commands
* A modern browser: for using the NiceGUI platform

Important Python dependencies are specified in `pyproject.toml`, including:

* `nicegui==1.4.26`
* `pandas`
* `numpy`
* `matplotlib`
* `seaborn`
* `statsmodels`
* `scikit-learn`
* `shap`
* `openai`
* `jupyterlab`

If running the GPT-assisted platform, configure the relevant API credentials in the platform preset or environment files before launching the server.

## Installation Guide

Clone the repository and install dependencies:

```bash
git clone https://github.com/yjw1029/GenAI-Learning-Outcomes.git
cd GenAI-Learning-Outcomes
uv sync
```

## Data Preparation

The analysis notebooks expect processed data and annotations to be available locally, but these files are not publicly distributed with the repository because they contain private participant information and interaction records. Under the IRB approval and participant consent terms for this study, the raw data cannot be released publicly.

Researchers who need access to the data should contact the paper's corresponding author. Please explain the research purpose and your collaboration relationship with the study team. If the request is approved, the corresponding author or research team can provide data access authorization under the applicable IRB, consent, privacy, and data-use requirements.

Once access is authorized, place the required files in the local paths expected by the notebooks before running the analyses.

## Demo

### Run the Experiment Platform

Start the Chinese-language platform:

```bash
uv run python platform/src/main.py --port 8000 --config platform/presets/allinone.toml
```

Start the English-language platform:

```bash
uv run python platform_en/src/main.py --port 8000 --config platform_en/presets/allinone.toml
```

Then open `http://localhost:8000` in a browser.

### Run Analysis Notebooks

Launch JupyterLab with the repository Python environment:

```bash
uv run jupyter lab
```

Then open the notebooks under `analyze/` and run them in that environment. The notebooks assume the authorized local inputs are already available on disk.

## Results

The analysis notebooks correspond to the manuscript sections in *Heterogeneous Impact of AI Assistance on Learning Outcomes* as follows:

* `analyze/experimental_design_stats.ipynb`: participant statistics and baseline prior-knowledge balance checks for the Experimental Design section.
* `analyze/analysis_behavior_heterogeneity.ipynb`: AI-use learning behavior profiles and their association with exam scores.
* `analyze/analysis_inequality.ipynb`: background-stratified behavior and outcome analyses.
* `analyze/feedback_analysis_plots.ipynb`: participant feedback, willingness shifts, risk perception shifts, usage objectives, and integration patterns.
* `analyze/appendix_analysis.ipynb`: supplementary analyses, including assignment-score diagnostics, feature screening, test-quality ratings, and LLM accuracy diagnostics.

With the authorized local inputs, generated figures are saved as PDF files and match the filenames used by the manuscript where applicable.

## License

This project is licensed under the MIT License. See `LICENSE` for details.
