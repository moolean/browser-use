# -*- coding: utf-8 -*-
import json
import os
import asyncio
import zipfile
import pandas as pd
import tempfile
import shutil
from browser_use.tools.service import Tools
from browser_use.llm.openrouter.chat import ChatOpenRouter
from browser_use import Agent, Browser, ChatBrowserUse, BrowserSession, BrowserProfile, ActionResult
from langchain_openai import ChatOpenAI
import logging
import sys

import pdb
sys.path.append("/Users/liuyichen/Documents/repo/browser-use")
logger = logging.getLogger(__name__)
os.environ["BROWSER_USE_API_KEY"] = "bu_cj6ZpLpUDP8-QmcoAllBR9EK8IfAdROWhHp3moFnIaE"
os.environ["BROWSER_USE_DISABLE_EXTENSIONS"] = 'false'
user_data_dir = "/Users/liuyichen/Documents/repo/browser-use/eval/eval_iter/browse_user_dir"


ACCOUNT_stefanoricci = "stefanoricci旗舰店:凯淳AI"
PASSWORD_stefanoricci = "kc13581897578"
ACCOUNT_shangxia = "上下官方旗舰店:凯淳AI"
PASSWORD_shangxia= "kc13581897578"

def format_query(query: str, domain: str) -> str:
    canmo_url = "https://sycm.taobao.com/"
    qianniu_url = "https://myseller.taobao.com/"
    wanxiang_url = "https://one.alimama.com/"

    formatted_query = f"""
请你扮演一个资深的电商运营专家，帮助我完成以下任务：
任务：{query}

你有三个可以查询的网页，除了这三个网页之外，不能访问其他网页。
1.  淘宝商家中心 生意参谋，网址是：{canmo_url} （适用于淘宝店铺运营）
2.  天猫商家中心 千牛，网址是：{qianniu_url} （适用于天猫店铺运营）
3.  阿里妈妈推广管理后台 万象，网址是：{wanxiang_url} （适用于淘宝天猫店铺的推广运营）

请登入店铺{domain}

如果你发现已经登陆成功了, 请直接完成任务, 不要再尝试重新登陆
**重要**
1. 当你通过截图发现页面没加载完, **不要尝试点击任何按钮导致页面重新刷新**, 这会导致死锁. 请继续等待页面加载完成后再进行下一步操作。
2. **跟随指令步骤进行操作**。如果没有出现预期界面，先进行等待，如果等待后依然没有出现预期界面，要重新尝试上一步指令步骤。
3. 当任务需要选择年月日的时候，**只使用点击切换按钮方式来选择年月**，
4. **禁止写todo.md**, 你并没有权限去这么做。

注意：登录时请使用以下账号和密码：
账号(stefanoricci旗舰店)：{ACCOUNT_stefanoricci}
密码(stefanoricci旗舰店)：{PASSWORD_stefanoricci}

账号(上下官方旗舰店)：{ACCOUNT_shangxia}
密码(上下官方旗舰店)：{PASSWORD_shangxia}

Notes:
1. 搜索输入框可能没有确认按钮，需要在选中输入框时输入回车才能搜索。搜索之后需要进行等待，然后检查是否出现新tab，如果出现新tab，需要切换到新tab，并等待页面加载完成。
2. 在搜索操作之后，必须先检查是否出现新tab，如果出现新tab，需要切换到新tab，并等待页面加载完成。
3. 如果有滑块验证码，使用drag_drop工具来完成滑块验证。
4. 搜索具体活动时，需要在活动名称而不是大促中搜索
5. 对于一些时间选择任务，需要先点击到对应的时间选择按钮，例如‘日’，‘月’。之后请等待一段时间，等待其加载出来, 日期选择可能不太好用，每次选完日期需要仔细检查一下是否选对了
选择按钮时，如果按钮如下所示，选择11235按钮会按下‘日’按钮
[11235]<button />
    日
[11236]<button />

6. 在点击对应按钮并等待之后，需要直接进行选择时间操作，在现实出正确的时间选择界面之前，不要进行其他操作。需要确保时间选择界面在网页中，如果没有时间选择界面，要重新点击或者将鼠标悬停在时间选择按钮
7. 选择年月时有如下例子：
案例一：
[13929]<span />
	[13930]<i />
[13931]<span />
	[13932]<i />
[13933]<span />
	2026
	年
[13936]<span />
	1月
[13937]<span />
	[13938]<i />
[13939]<span />
	[13940]<i />

其中[13932]和[13938]是切换到上个月和下个月的按钮，[13930]和[13940]是切换到上一年和下一年的按钮。在此情景下点击[13932]按钮会切换到上个月，也就是2025年12月。

案例二：
*[9588]<span />
	*[9589]<i />
*[9590]<span />
	*[9591]<i />
[9592]<span />
	2026
	年
[9595]<span />
	1月
*[9597]<span />
	*[9598]<i />
[9599]<span />
	一

其中[9591]和[9598]是切换到上个月和下个月的按钮，[9589]是切换到上一年的按钮。此处没有切换到下一年的按钮。

案例三：
[4400]<span />
	[4396]<i />
[4401]<span />
	[4397]<i />
[4402]<span />
	2026
	年
[4403]<span />
	2月
[4406]<th />
	一
其中[6944]是切换到上个月的按钮，[6943]是切换到上一年的按钮。此处没有切换到下一年的按钮。

案例四：
[30315]<span />
	[30316]<i />
		
	[30317]<i />
		
[30318]<span />
	
[30319]<span />
	2025年02月
[30320]<span />
	
[30321]<span />
	[30322]<i />
		
	[30323]<i />
		
其中[30318]和[30320]是切换到上个月和下个月的按钮，[30316]和[30323]是切换到上一年和下一年的按钮。


请点击按钮切换时间界面，在点击按钮之后，需要等待一段时间，等待其加载出来。如果没有反应，多几次进行点击尝试操作。先尝试只使用切换月按钮操作。

7. 对于万象台的时间选择任务，如果问题是时间段，**需不要在同一个日历里面选择两个时间！！！**例如：
*[29958]<div id=trigger_mx_15789 />
	*[29959]<div />
		*[29960]<i />
			
		*[29961]<span />
			2026-01-28
*[29962]<div id=trigger_mx_15790 />
	*[29963]<div />
		*[29964]<i />
			
		*[29965]<span />
			昨日
你需要点击[29960]，在其对应的日历中选择第一个时间，等待三秒钟等待页面刷新，然后点击[29964]，在其对应的日历中选择第二个时间。

8. 如果出来两个日历，前面索引数字较小的日历是选择起始时间，后面索引数字较大的日历是终止时间。当你需要选择两个时间时，必须先在前一个日历中选择起始时间，然后等待页面加载。等新的页面出现之后，再在后一个选择终止时间，等待页面加载。在确认时间之后点击确认。

例如
[7511]<td />
	11
[7512]<td />
	12
[7513]<td />
	13
...
[7573]<td />
	11
[7574]<td />
	12
[7575]<td />
	13
如果需要选择11日到13日，请先选择7511，对应的是11日，等待页面加载，然后选择7575，对应的是13日，等待页面加载，最后点击确认。
9.当你完成了任务, 请详细汇报你的操作步骤和最终结果 (如果有文件下载, 请给出文件路径), 以便我了解你是如何完成任务的。

"""
    return formatted_query


def parse_file(file_path):
    print(f">>Parsing file: {file_path}")
    if not os.path.exists(file_path):
        return f"File not found: {file_path}"

    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.zip':
        zip_results = []
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(tmpdir)
                    for root, dirs, files in os.walk(tmpdir):
                        for file in files:
                            full_path = os.path.join(root, file)
                            # Parse each file inside the zip
                            content = parse_file(full_path)
                            zip_results.append(content)
            except Exception as e:
                return f"Error opening ZIP {file_path}: {e}"
        return "\n\n".join(zip_results)

    elif ext in ['.csv']:
        try:
            try:
                df = pd.read_csv(file_path, encoding="gbk")
            except:
                df = pd.read_csv(file_path, encoding='utf-8')
            return f"File: {os.path.basename(file_path)}\nContent:\n{df.head(20).to_string()}"
        except Exception as e:
            return f"Error reading CSV {file_path}: {e}"

    elif ext in ['.xls', '.xlsx']:
        try:
            df = pd.read_excel(
                file_path, engine='openpyxl' if ext == '.xlsx' else 'xlrd')
            return f"FileName: {os.path.basename(file_path)}\nContent:\n{df.head(20).to_string()}"
        except Exception as e:
            return f"Error reading Excel {file_path}: {e}"

    return f"File: {os.path.basename(file_path)} (unsupported format or not a data file)"


def find_gt_file(domain, idx, filename):
    # Basic mapping: strip "旗舰店"

    mapping = {
        "stefanoricci旗舰店": "stefanoricci",
        "上下官方旗舰店": "上下官方"
    }
    folder = mapping[domain]
    gt_file_path = os.path.join(GT_PATH, folder, str(idx), filename)
    if os.path.exists(gt_file_path):
        return gt_file_path

    return None


async def example(query, save_path=None):
    # chrome profile configuration ====================
    profile = BrowserProfile(
        headless=False,
        user_data_dir=user_data_dir,
        keep_alive=False,
        cookie_whitelist_domains=["taobao.com", "tmall.com", "alimama.com"],
        downloads_path=f"{save_path}/browser_temp",
    )
    session = BrowserSession(
        browser_profile=profile,
        window_size={'width': 1920, 'height': 1080},
        viewport={'width': 1920, 'height': 1080}
    )
    # LLM configuration ====================

    from browser_use import Agent, ChatAnthropic

    llm = ChatAnthropic(
        # base_url='https://api.ppchat.vip',
        # api_key="sk-0rEu2P0yo7YR8tMTIwAK36ornv2HeF99VcmMWhadwRM4tViX",
        base_url='https://api.uniapi.io/claude',
        api_key="sk-fx7IRkc1izDuBZH_hi_0k8jVyAlJ9wqTpQcWW2FlbiPbEn9vO67P-iOwXaI",
        model='claude-sonnet-4-20250514',
    )

    # llm = ChatBrowserUse()  # browser-use/bu-30b-a3b-preview

    # Tools configuration ====================
    use_vision = False
    display_files_in_done_text = True
    exclude_actions = ['screenshot'] if use_vision != 'auto' else []
    tools = Tools(exclude_actions=exclude_actions,
                  display_files_in_done_text=display_files_in_done_text)

    # Agent configuration ====================
    agent = Agent(
        task=query,
        llm=llm,
        tools=tools,
        browser_session=session,
        save_conversation_path=save_path,
        browser_temp_dir=f"{save_path}/browser_temp",
        flash_mode=True
    )
    # RUN ! ====================
    history = await agent.run(max_steps=40)
    # save trace file ====================
    save_trace_file = f"{save_path}/debug_trace.json"
    history.save_to_file(save_trace_file)

    return history.model_dump()["history"][-1]["model_output"]


class EvalLoader:

    def __init__(self, path, output_path=None):
        self.path = path
        with open(self.path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        if output_path and os.path.exists(output_path):
            self.processed_unique_ids = set()
            with open(output_path, "r", encoding="utf-8") as f:
                # read jsonl
                for line in f:
                    data = json.loads(line)
                    print(data)
                    unique_id = data.get("unique_id", None)
                    if unique_id:
                        self.processed_unique_ids.add(unique_id)
            print(
                f"Loaded {len(self.processed_unique_ids)} processed unique ids from {output_path}, skipping them.")

        self.item = []
        count = 0
        for domain, value in raw_data.items():
            for idx, item in value.items():
                test_cases = item.get("test_cases", [])
                query_template = item.get("updated_query_template", None) or item.get(
                    "query_template", None)
                print(f"Processing {domain} {idx}. index from {count} to {count + len(test_cases) - 1}")
                count += len(test_cases)
                for case_num, case in enumerate(test_cases):
                    input_field = case["输入"]
                    query = query_template
                    for name, value in input_field.items():
                        query = query.replace(f"<<{name}>>", str(value))
                    unique_id = f"{domain}_{idx}_case{case_num}"
                    if output_path and os.path.exists(output_path) and unique_id in self.processed_unique_ids:
                        print(
                            f"Skipping already processed unique_id: {unique_id}")
                        continue

                    item = {
                        "idx": idx,
                        "domain": domain,
                        "input": case["输入"],
                        "query_template": query_template,
                        "query": query,
                        "gt": case["输出"],
                        "case_num": case_num,
                        "unique_id": unique_id
                    }

                    self.item.append(item)
        print(f"Loaded {len(self.item)} eval items from {self.path}")

    def __len__(self):
        return len(self.item)

    def __getitem__(self, index):
        return self.item[index]


class LLMJudge(ChatOpenAI):

    def evaluate(self, query, prediction: str, reference: str, pred_file_content: str = None, gt_file_content: str = None):
        file_info = ""
        if pred_file_content or gt_file_content:
            file_info = f"\n\n模型下载文件内容:\n{pred_file_content or '未下载或无法解析'}\n\n参考答案文件内容:\n{gt_file_content or '未提供'}"

        prompt = f"""
用户问题: {query}
Agent回答: {prediction}
问题参考答案: {reference}

**下载文件信息**
{file_info}\n\n

请你作为一个评测专家，评估下面的回答是否**正确完整地回答了问题**, 给出你的原因和结论，最终结论用<judge>True/False</judge>来表示.
"""

        response = self.invoke(
            input=prompt
        )
        print(">>原始prompt" + prompt)
        return response.content


async def batch_test(test_path, test_res_dir):
    data_loader = EvalLoader(test_path, test_res_dir + f"/test_output.jsonl")
    kwargs = {
        "model_name": "qwen3-max-2026-01-23",
        "base_url": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        "max_tokens": 16384,
        "temperature": 1.0,
        "api_key": "sk-f9665c2c4e144e63b9d79fb084737b6d",
        "extra_body": {
            "enable_thinking": False
        }
    }
    llm_judge = LLMJudge(**kwargs)
    # pdb.set_trace()
    # for test_item in data_loader.item[45:]:
    for test_item in data_loader.item[15:45]:
        save_path = f"{test_res_dir}/debug_{test_item['domain']}_{test_item['idx']}_case{test_item['case_num']}"
        # if os.path.exists(save_path):
        #     print(f"Skipping {save_path} because it already exists")
        #     continue
        os.makedirs(save_path, exist_ok=True)
        test_output = test_item.copy()
        test_query = test_item["query"]
        query = format_query( test_item["query"], test_item['domain'])

        res = await example(
            query, save_path=save_path
        )

        # 1. Process downloaded files
        downloads_dir = os.path.join(save_path, "browser_temp")
        pred_file_content = ""
        if os.path.exists(downloads_dir):
            downloaded_files = [f for f in os.listdir(
                downloads_dir) if os.path.isfile(os.path.join(downloads_dir, f))]
            print(f">>Downloaded files: {downloaded_files}")
            parsed_contents = []
            for df in downloaded_files:
                parsed_contents.append(parse_file(
                    os.path.join(downloads_dir, df)))
            pred_file_content = "\n\n".join(parsed_contents)

        # 2. Process GT file
        # gt_file_content = ""
        # gt_file_path = None
        # gt = test_item["gt"].copy()
        # if "文件路径" in gt:
        #     gt_filename = gt["文件路径"] if isinstance(
        #         gt["文件路径"], str) else gt["文件路径"][0]
        #     gt_file_path = find_gt_file(
        #         test_item["domain"], test_item["idx"], gt_filename)
        #     if gt_file_path:
        #         gt_file_content = parse_file(gt_file_path)
        #     else:
        #         gt_file_content = f"Ground truth file not found: {gt_filename} for domain {test_item['domain']} idx {test_item['idx']}"

        # print("Final Answer:", res)
        # test_output["answer"] = res
        # if "图片" in gt:
        #     gt.pop("图片")
        # test_output["gt_file_path"] = gt_file_path if gt_file_path else "N/A"
        # test_output["downloaded_file_name"] = downloaded_files
        # test_output["pred_file_content"] = pred_file_content
        # test_output["gt_file_content"] = gt_file_content
        # judgement_content = llm_judge.evaluate(
        #     test_query, res, gt, pred_file_content=pred_file_content, gt_file_content=gt_file_content
        # )
        # test_output["judgement"] = judgement_content
        # is_passed = "<judge>True</judge>" in judgement_content
        # test_output = {"score": is_passed, **test_output}
        # with open(f"{test_res_dir}/test_output.jsonl", "a", encoding="utf-8") as output_f:
        #     output_f.write(json.dumps(
        #         test_output, ensure_ascii=False) + "\n")

async def batch_eval(test_res_dir):
    kwargs = {
        "model_name": "qwen3-max-2026-01-23",
        "base_url": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        "max_tokens": 16384,
        "temperature": 1.0,
        "api_key": "sk-f9665c2c4e144e63b9d79fb084737b6d",
        "extra_body": {
            "enable_thinking": False
        }
    }
    llm_judge = LLMJudge(**kwargs)

    with open(f"{test_res_dir}/test_output.jsonl", "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i != 0:
                continue
            test_output = json.loads(line)
            judgement_content = llm_judge.evaluate(
                    test_output["query"], test_output["answer"], test_output["gt"]
                )
            is_passed = "<judge>True</judge>" in judgement_content
            test_output["score"] = is_passed
            print(judgement_content)
            print(f"Test {i}: {test_output["unique_id"]} is passed: {is_passed}")

if __name__ == "__main__":

    test_path = "/Users/liuyichen/Documents/repo/browser-use/eval/query_yichen.json"
    test_res_dir = "/Users/liuyichen/Documents/repo/browser-use//outputs/test_all_claudesonnet_10_21-debug"
    os.makedirs(test_res_dir, exist_ok=True)
    asyncio.run(batch_test(test_path, test_res_dir))
    # asyncio.run(batch_eval(test_res_dir))
