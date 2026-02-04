from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import json
import os
from typing import List, Optional
import pandas as pd

import argparse

app = FastAPI()

# Get path from environment variable or command line
DEFAULT_RESULTS_PATH = os.environ.get(
    "RESULTS_PATH", "/home/fallengold/tmp/browser-use/output/test_all_claude_sonnet_4_20250514_stefanoricci_test1/test_output.jsonl")

templates = Jinja2Templates(directory=os.path.join(
    os.path.dirname(__file__), "templates"))


def load_data(file_path: str):
    if not os.path.exists(file_path):
        print(f"Warning: {file_path} not found")
        return []
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return data


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, score_filter: Optional[str] = None):
    data = load_data(DEFAULT_RESULTS_PATH)

    if score_filter == "passed":
        data = [i for i in data if i.get("score") is True]
    elif score_filter == "failed":
        data = [i for i in data if i.get("score") is False]

    # Calculate stats
    total = len(data)
    passed = sum(1 for i in data if i.get("score") is True)
    failed = total - passed
    pass_rate = (passed / total * 100) if total > 0 else 0

    return templates.TemplateResponse("index.html", {
        "request": request,
        "results": data,
        "stats": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": f"{pass_rate:.1f}%"
        },
        "score_filter": score_filter
    })


@app.get("/detail/{unique_id}", response_class=HTMLResponse)
async def get_detail(request: Request, unique_id: str):
    data = load_data(DEFAULT_RESULTS_PATH)
    item = next((i for i in data if i.get("unique_id") == unique_id), None)

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Pre-process JSON strings to ensure Chinese characters are decoded
    item_display = item.copy()
    item_display["input_json"] = json.dumps(item.get("input", {}), ensure_ascii=False, indent=2)
    item_display["gt_json"] = json.dumps(item.get("gt", {}), ensure_ascii=False, indent=2)

    return templates.TemplateResponse("detail.html", {"request": request, "item": item_display})

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default=DEFAULT_RESULTS_PATH,
                        help="Path to jsonl results")
    parser.add_argument("--port", type=int, default=8000,
                        help="Port to run on")
    args = parser.parse_args()

    DEFAULT_RESULTS_PATH = args.path

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=args.port)
