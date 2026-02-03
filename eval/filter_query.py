import os
import json
with open("/Users/liuyichen/Documents/repo/browser-use/eval/query_all.json", "r") as f:
    data = json.load(f)

output_data = {}
for domain, value in data.items():
    output_data[domain] = {}
    for idx, item in value.items():
        test_cases = item.get("test_cases", [])
        query_template = item.get("updated_query_template", None) or item.get("query_template", None)
        if "生意参谋" in query_template or "千牛" in query_template or "万象" in query_template:
            output_data[domain][idx] = item

with open("/Users/liuyichen/Documents/repo/browser-use/eval/query_all_filtered.json", "w") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=4)