# slc-hunger-risk
Repo to research the hunger risk in Suriname 2021-2022


## How to reproduce the results?

### Option 1 - Poetry (recommended)

1. Install Poetry: [instructions](https://python-poetry.org/docs/).
2. Clone the repo: `git clone https://github.com/CorrelAidxNL/slc-hunger-risk.git`.
3. Change the working directory into `slc-hunger-risk`: `cd slc-hunger-risk`.
4. Install Python dependencies using Poetry: `poetry install`.
5. Open the Poetry shell: `poetry shell`.
6. Run the scripts using Python, e.g.: `python scripts/download_data.py`.

### Option 2

1. Clone the repo: `git clone https://github.com/CorrelAidxNL/slc-hunger-risk.git`.
2. Change the working directory into `slc-hunger-risk`: `cd slc-hunger-risk`.
3. Install Python dependencies from `requirements.text` using Anaconda or pip (ideally in a virtual environment).
4. Add `src` directory to `PYTHONPATH`: `export PYTHONPATH="${PYTHONPATH}:<repo directory>/src"`. If you use a virtual environment you can permanently extend `PYTHONPATH` by running `pushd src; pwd >> $VIRTUAL_ENV/lib/python3.8/site-packages/slc-hunger-risk.pth; popd`.
5. Run the scripts using Python, e.g.: `python scripts/download_data.py`.
