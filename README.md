# msai-poc

## Execution
``` bash
cd pro-gen
source .venv/bin/activate
uv sync
streamlit run app.py
```



``` bash
# make pjt
pip install uv
uv init pro-gen
cd pro-gen
uv venv --python=3.12
deactivate
source .venv/bin/activate
uv add openai python-dotenv streamlit azure-storage-blob pandas langchain-community azure-search-documents azure-identity
# uv.lock 파일이 있다면 uv sync
```