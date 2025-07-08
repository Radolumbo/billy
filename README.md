# Billy

Hi, I'm Billy! I understand bills using AI 'cause ain't nobody got time to read all that.

## Local Environment Setup

1. Install VS Code/Cursor extensions:
   - Python extension (`ms-python.python`)
   - Black Formatter (`ms-python.black-formatter`)
   - Ruff (`charliermarsh.ruff`)
   - REST Client (`humao.rest-client`)

1. Install dependencies with dev extras:
    ```bash
    pip install -e .[dev]
    ```

1. Copy `server/.env.template` to `server/.env` and fill in the values. Ask Nick or get `GEMINI_API_KEY` from [Google AI Studio](https://aistudio.google.com/app/apikey) and `CONGRESS_API_KEY` from [the Congress's API](https://api.congress.gov/sign-up/).

## Run Server

Run the server with hot reload:
```bash
uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload
```

You can now hit http://localhost:8000 for the API. Examples with REST Client extension (I just save this in an `http.rest` file):

```
### List bills

GET http://localhost:8000/bill

### Ask bill

POST http://localhost:8000/bill/ask
Content-Type: application/json

{
    "congress": "117",
    "type": "HR",
    "number": "3076",
    "query": "What is the bill about?"
}
```
