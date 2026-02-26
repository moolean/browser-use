# -*- coding: utf-8 -*-
import json
import os
import asyncio
import zipfile
import pandas as pd
import tempfile
import shutil
from langchain_anthropic import ChatAnthropic as ChatAnthropicLangchain
from langchain_core.messages import HumanMessage
import re
import urllib.request
import urllib.parse
from pathlib import Path
from browser_use.tools.service import Tools
from browser_use.llm.openrouter.chat import ChatOpenRouter
from browser_use import Agent, Browser, ChatBrowserUse, BrowserSession, BrowserProfile, ActionResult
from langchain_openai import ChatOpenAI
import base64
import logging
import sys

import pdb
# sys.path.append("/Users/liuyichen/Documents/repo/browser-use")
sys.path.append("D:\\repo\\browser-use")
logger = logging.getLogger(__name__)
os.environ["BROWSER_USE_API_KEY"] = "bu_cj6ZpLpUDP8-QmcoAllBR9EK8IfAdROWhHp3moFnIaE"
os.environ["BROWSER_USE_DISABLE_EXTENSIONS"] = 'false'
# user_data_dir = "/Users/liuyichen/Documents/repo/browser-use/eval/eval_iter/browse_user_dir"
user_data_dir = "D:\\repo\\browser-use\\eval\\eval_iter\\browse_user_dir"

# those 3 for login
# ACCOUNT_stefanoricci = "stefanoricci旗舰店:凯淳AI"
# PASSWORD_stefanoricci = "kc13581897578"
# ACCOUNT_shangxia = "上下官方旗舰店:凯淳AI"
# PASSWORD_shangxia= "kc13581897578"

# for jingdong
ACCOUNT_stefanoricci = "stefanoricci旗舰店凯淳AI"
PASSWORD_stefanoricci = "kc13581897578"
ACCOUNT_shangxia = "上下官方旗舰店凯淳AI"
PASSWORD_shangxia= "kc13581897578"

GT_PATH = "/Users/liuyichen/Documents/repo/browser-use/updated_data_files"


def format_query(query: str, domain: str = None) -> str:
    canmo_url = "https://sycm.taobao.com/"
    qianniu_url = "https://myseller.taobao.com/"
    wanxiang_url = "https://one.alimama.com/"

    formatted_query = f"""
请你扮演一个资深的电商运营专家，帮助我完成以下任务：
任务：{query}

你有三个可以查询的网页，除了这三个网页之外，你只能访问任务中提供的网页，不能访问其他网页。
1.  淘宝商家中心 生意参谋，网址是：{canmo_url} （适用于淘宝店铺运营）
2.  天猫商家中心 千牛，网址是：{qianniu_url} （适用于天猫店铺运营）
3.  阿里妈妈推广管理后台 万象，网址是：{wanxiang_url} （适用于淘宝天猫店铺的推广运营）

请登入店铺{domain}

如果你发现已经登陆成功了, 请直接完成任务, 不要再尝试重新登陆
**重要**
1. 当发现页面没加载完, **禁止尝试重复点击任何按钮导致页面重新刷新**, 这会导致死锁. 请继续等待页面加载完成后再进行下一步操作, 当你重复进行操作发现一直失败的时候,请一直等待, 这是强制要求, 永远保持耐心
2. **禁止写todo.md**, 你并没有权限去这么做
3. 当你发现需要输入手机验证码, 请耐心等待等我操作
4. 如果在点击关闭按钮后有新的弹窗出现，需要点击新弹窗中的“拒绝“、”关闭“等按钮。

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
7. 对于日期选择任务，可能需要点击年月切换按钮。如果<span类型下面有<i>标签，选择点击<i>标签，不要选择span标签。按钮可能没有反应，每次点击后需要确认是否出现预期的结果，如果没有需要再次点击。选择年月切换按钮时有如下例子：
案例一：
[13929]<span data-role="prev-year"/>
        [13930]<i />
[13931]<span data-role="prev-month"/>
        [13932]<i />
[13933]<span />
        2026
        年
[13936]<span />
        1月
[13937]<span data-role="next-month"/>
        [13938]<i />
[13939]<span data-role="next-year"/>
        [13940]<i />

其中[13932]和[13938]是切换到上个月和下个月的按钮，[13930]和[13940]是切换到上一年和下一年的按钮

案例二：
*[9588]<span data-role="prev-year"/>
	*[9589]<i />
*[9590]<span data-role="prev-month"/>
	*[9591]<i />
[9592]<span />
	2026
	年
[9595]<span />
	1月
*[9597]<span data-role="next-month"/>
	*[9598]<i />
[9599]<span />
	一

其中[9591]和[9598]是切换到上个月和下个月的按钮，[9589]是切换到上一年的按钮。此处没有切换到下一年的按钮。


案例三：
[30315]<span data-role="prev-year"/>
	[30316]<i />
		
	[30317]<i />
		
[30318]<span data-role="next-month"/>
	
[30319]<span />
	2025年02月
[30320]<span data-role="next-month"/>
	
[30321]<span data-role="next-year"/>
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

9.当你完成了任务, 请详细汇报你的操作步骤和最终结果 (如果有文件下载, 请给出**所有**文件路径)。
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
            return f"File: {os.path.basename(file_path)} (Suffix: {ext})\nContent:\n{df.head(20).to_string()}"
        except Exception as e:
            return f"Error reading CSV {file_path}: {e}"

    elif ext in ['.xls', '.xlsx']:
        try:
            df = pd.read_excel(
                file_path, engine='openpyxl' if ext == '.xlsx' else 'xlrd')
            return f"File: {os.path.basename(file_path)} (Suffix: {ext})\nContent:\n{df.head(20).to_string()}"
        except Exception as e:
            return f"Error reading Excel {file_path}: {e}"

    return f"File: {os.path.basename(file_path)} (unsupported format or not a data file)"


def find_gt_file(domain, idx, filename):
    # Basic mapping: strip "旗舰店"

    mapping = {
        "stefanoricci旗舰店": "stefanoricci",
        "上下官方旗舰店": "上下官方"
    }
    folder = mapping.get(domain, domain.replace("旗舰店", ""))
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
        base_url='https://api.ppchat.vip',
        api_key="sk-0rEu2P0yo7YR8tMTIwAK36ornv2HeF99VcmMWhadwRM4tViX",
        # base_url='https://api.uniapi.io/claude',
        # api_key="sk-fx7IRkc1izDuBZH_hi_0k8jVyAlJ9wqTpQcWW2FlbiPbEn9vO67P-iOwXaI",
        model='claude-sonnet-4-20250514',
    )

    # llm = ChatBrowserUse()  # browser-use/bu-30b-a3b-preview

    # Tools configuration ====================
    use_vision = True
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
    history = await agent.run(max_steps=60)
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
                if domain == "无需分店铺":
                    domain = "上下官方旗舰店"
                count += len(test_cases)
                for case_num, case in enumerate(test_cases):
                    input_field = case["输入"]
                    query = query_template
                    for name, value in input_field.items():
                        query = query.replace(f"<<{name}>>", str(value))
                    unique_id = f"{domain}_{idx}_case{case_num}"
                    # if output_path and os.path.exists(output_path) and unique_id in self.processed_unique_ids:
                    #     print(
                    #         f"Skipping already processed unique_id: {unique_id}")
                    #     continue

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

        prompt = f"""
你是一个电商数据专家，负责评测 AI Agent 执行网页操作任务的结果。

**输入信息：**
1. 用户问题: {query}
2. Agent 最终汇报内容: {prediction}
3. 问题参考答案 (Ground Truth): {reference}
4. 检测到模型下载的文件信息:
{pred_file_content if pred_file_content else "无"}

5. 参考答案的文件信息:
{gt_file_content if gt_file_content else "无"}

**评测规则：**
1. **结果导向判别**：如果用户要求下载/查询数据，请优先以“实际下载文件解析内容”为准。即使 Agent 在汇报内容中只提到了一个路径或漏掉了部分汇报，只要“模型下载文件内容”中包含了参考答案中要求的所有核心数据（内容一致），即判定为 True。
2. **处理文件名冲突**：Agent 在下载多个同名文件时，系统可能自动重命名为 `filename (1).csv`, `filename (2).csv` 等。请检查所有列出的文件内容，只要这些文件的内容总和涵盖了参考答案的要求，即为正确。
3. **宽容 Final Action 缺失**：如果用户核心任务是下载文件, 在这种情况下如果 Agent 没能准确输出最后的操作，但观察到其下载的文件数量和内容完全符合预期，应给予判定通过。
4. **忽略非关键差异**：
    - 忽略文件名格式的微小差异。
    - 忽略参考答案中可能存在的图片说明干扰。
    - 只要表格内容的核心数值、日期、和维度正确，即可判定为 True。

**输出要求：**
给出你的详细分析原因，最后结论必须用 <judge>True/False</judge> 括起来。
"""

        response = self.invoke(
            input=prompt
        )
        print(">>原始prompt" + prompt)
        return response.content


class VerificationJudge(ChatAnthropicLangchain):
    """Judge that verifies agent output against query requirements without ground truth."""

    def verify(self, query: str, prediction: str, pred_file_content: str = None, last_screenshot_content: str = None):
        """
        Verify if the agent output satisfies the query requirements.
        
        Args:
            query: The original query/task
            prediction: Agent's final output/response
            pred_file_content: Content of files downloaded by the agent
            
        Returns:
            str: Verification result with <judge>True/False</judge> tag
        """
        prompt = f"""
你是一个电商数据专家，负责验证 AI Agent 是否成功完成了用户的任务。

**输入信息：**
1. 用户任务/问题: {query}
2. Agent 最终汇报内容: {prediction}
3. Agent 下载的文件内容:
{pred_file_content if pred_file_content else "无"}
4. 来自Agent的最后一页截图

**验证规则：**
1. **任务完成度**：仔细分析用户任务的所有要求，检查 Agent 是否完成了所有关键点。任务可能包括：
   - 下载特定文件或数据
   - 查询特定信息
   - 执行特定操作
   - 生成特定格式的输出
   
2. **结果导向判别**：如果用户要求下载/查询数据，请优先以"实际下载文件解析内容"为准。即使 Agent 在汇报内容中只提到了一个路径或漏掉了部分汇报，只要"模型下载文件内容"中包含了用户任务要求的所有核心数据，即判定为 True。

3. **处理文件名冲突**：Agent 在下载多个同名文件时，系统可能自动重命名为 `filename (1).csv`, `filename (2).csv` 等。请检查所有列出的文件内容，只要这些文件的内容总和涵盖了任务要求，即为正确。

4. **完整性检查**：
   - 如果任务要求下载文件，检查文件是否已下载且内容符合要求
   - 如果任务要求查询信息，检查信息是否完整且准确
   - 如果任务要求执行操作，检查操作是否成功完成
   - 如果任务要求特定格式，检查格式是否正确

5. **准确性检查**：
   - 检查文件中的时间是否与任务要求的时间一致
   - 最后一页截图在有些任务中可以辅助验证时间是否正确

6. **忽略非关键差异**：
    - 只要表格内容的核心数值、日期、和维度正确，即可判定为 True
    - 允许汇报内容中的轻微不完整，只要实际结果（文件内容）符合要求

**输出要求：**
给出你的详细分析原因，最后结论必须用 <judge>True/False</judge> 括起来。
"""
        image_data = base64.b64encode(last_screenshot_content).decode("utf-8")
        messages = [
            HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {"type": "image", "base64": image_data, "mime_type": "image/jpeg"}
                ]
            )
        ]

        response = self.invoke(
            messages=messages
        )
        print(">>Verification prompt:\n" + prompt)
        return response.content


async def verify_agent_output(
    query: str,
    agent_output: str,
    save_path: str,
    llm_judge: VerificationJudge | None = None,
    max_retries: int = 3
) -> tuple[bool, str]:
    """
    Verify if agent output satisfies the query requirements.
    Downloads any files from URLs mentioned in the output if needed.
    
    Args:
        query: The original query/task
        agent_output: Agent's final output/response
        downloads_dir: Directory where agent downloaded files are stored
        save_path: Path to save verification results
        llm_judge: Optional VerificationJudge instance. If None, creates one with default config.
        max_retries: Maximum number of retries if verification fails
        
    Returns:
        Tuple of (is_valid: bool, verification_result: str)
    """
    # Initialize judge if not provided
    if llm_judge is None:
        kwargs = {
            "base_url": "https://api.ppchat.vip",
            "api_key": "sk-0rEu2P0yo7YR8tMTIwAK36ornv2HeF99VcmMWhadwRM4tViX",
            # "base_url": "https://api.uniapi.io/claude",
            # "api_key": "sk-fx7IRkc1izDuBZH_hi_0k8jVyAlJ9wqTpQcWW2FlbiPbEn9vO67P-iOwXaI",
            "model": "claude-sonnet-4-20250514",
        }
        llm_judge = VerificationJudge(**kwargs)
    
    # 1. Process downloaded files
    downloads_dir = os.path.join(save_path, "browser_temp")
    pred_file_content = ""
    downloaded_files = []
    if os.path.exists(downloads_dir):
        downloaded_files = [f for f in os.listdir(
            downloads_dir) if os.path.isfile(os.path.join(downloads_dir, f))]
        print(f">>Downloaded files: {downloaded_files}")
        parsed_contents = [parse_file(os.path.join(
            downloads_dir, df)) for df in downloaded_files]
        pred_file_content = "\n\n".join(parsed_contents)
    # Get the screenshot of the last page
    screenshot_path_dir = os.path.join(save_path, "browser_temp", "screenshots")
    all_screenshot_paths = [f for f in os.listdir(screenshot_path_dir) if f.endswith(".png")]
    all_screenshot_paths.sort(key=lambda x: int(x.split("_")[1].split(".")[0]))
    last_screenshot_path = os.path.join(screenshot_path_dir, all_screenshot_paths[-1])
    with open(last_screenshot_path, "rb") as f:
        last_screenshot_content = f.read()
    
    # 2. Verify using LLM judge
    verification_result = llm_judge.verify(
        query=query,
        prediction=agent_output,
        pred_file_content=pred_file_content,
        last_screenshot_content=last_screenshot_content
    )
    
    # 3. Extract verdict
    is_valid = "<judge>True</judge>" in verification_result or "<judge>true</judge>" in verification_result
    
    # 54 Save verification result
    verification_data = {
        "query": query,
        "agent_output": agent_output,
        "downloaded_files": downloaded_files,
        "verification_result": verification_result,
        "is_valid": is_valid
    }
    
    verification_path = os.path.join(save_path, "verification_result.json")
    with open(verification_path, "w", encoding="utf-8") as f:
        json.dump(verification_data, f, ensure_ascii=False, indent=2)
    
    print(f">>Verification result: {'PASSED' if is_valid else 'FAILED'}")
    print(f">>Verification saved to: {verification_path}")
    
    return is_valid, verification_result


async def batch_test(test_path, test_res_dir, max_retries: int = 3):
    """
    Run batch tests with verification and automatic retry on failure.
    
    Args:
        test_path: Path to test data JSON file
        test_res_dir: Directory to save test results
        max_retries: Maximum number of retries if verification fails
    """
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
    verification_judge = VerificationJudge(**kwargs)
    import pdb; pdb.set_trace()
    for test_item in data_loader.item[5:]:
    # for test_item in [data_loader.item[11], data_loader.item[14]]:
        save_path = f"{test_res_dir}/debug_{test_item['domain']}_{test_item['idx']}_case{test_item['case_num']}"
        print(f"Saving to {save_path}")
        # if os.path.exists(save_path):
        #     print(f"Skipping {save_path} because it already exists")
        #     continue
        os.makedirs(save_path, exist_ok=True)
        test_output = test_item.copy()
        test_query = test_item["query"]
        query = format_query(test_item["query"], test_item['domain'])

        # Run with retry logic
        res = None
        verification_passed = False
        verification_result = None
        attempt = 0
        
        while attempt < max_retries and not verification_passed:
            attempt += 1
            print(f"\n>>Attempt {attempt}/{max_retries}")
            
            # Run the agent
            res = await example(query, save_path=save_path)
            
            # Verify the output
            verification_passed, verification_result = await verify_agent_output(
                query=test_query,
                agent_output=res,
                save_path=save_path,
                llm_judge=verification_judge,
                max_retries=max_retries
            )
            
            if verification_passed:
                print(f">>Verification PASSED on attempt {attempt}")
            else:
                print(f">>Verification FAILED on attempt {attempt}")
                if attempt < max_retries:
                    # rename the save_path to save_path_failed
                    shutil.move(save_path, f"{save_path}_failed_{attempt}")
                    print(f">>Retrying...")
                else:
                    print(f">>Max retries reached. Keeping last attempt results.")

        # 1. Process downloaded files
        downloads_dir = os.path.join(save_path, "browser_temp")
        pred_file_content = ""
        downloaded_files = []
        if os.path.exists(downloads_dir):
            downloaded_files = [f for f in os.listdir(
                downloads_dir) if os.path.isfile(os.path.join(downloads_dir, f))]
            print(f">>Downloaded files: {downloaded_files}")
            parsed_contents = [parse_file(os.path.join(
                downloads_dir, df)) for df in downloaded_files]
            pred_file_content = "\n\n".join(parsed_contents)

        # 2. Process GT file (for comparison/evaluation)
        gt_file_content = ""
        gt_file_paths = []
        gt = test_item["gt"].copy()
        if isinstance(gt, dict) and "文件路径" in gt:
            gt_filenames = gt["文件路径"]
            if isinstance(gt_filenames, str):
                gt_filenames = [gt_filenames]

            parsed_list = []
            for fname in gt_filenames:
                path = find_gt_file(
                    test_item["domain"], test_item["idx"], fname)
                if path:
                    gt_file_paths.append(path)
                    parsed_list.append(parse_file(path))
                else:
                    parsed_list.append(f"Ground truth file not found: {fname}")
            gt_file_content = "\n\n".join(parsed_list)

        print("Final Answer:", res)
        test_output["answer"] = res
        test_output["verification_result"] = verification_result
        test_output["verification_passed"] = verification_passed
        test_output["attempts"] = attempt
        
        if isinstance(gt, dict) and "图片" in gt:
            gt.pop("图片")
        test_output["gt_file_path"] = gt_file_paths if gt_file_paths else "N/A"
        test_output["downloaded_file_name"] = downloaded_files
        test_output["pred_file_content"] = pred_file_content
        test_output["gt_file_content"] = gt_file_content
        
        # Also run LLMJudge for comparison (optional)
        judgement_content = llm_judge.evaluate(
            test_query, res, gt, pred_file_content=pred_file_content, gt_file_content=gt_file_content
        )
        test_output["judgement"] = judgement_content
        is_passed = "<judge>True</judge>" in judgement_content
        print(f">>Judgement content: {judgement_content}")
        test_output = {"score": is_passed, **test_output}
        
        with open(f"{test_res_dir}/test_output.jsonl", "a", encoding="utf-8") as output_f:
            output_f.write(json.dumps(
                test_output, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    test_path = "D:\\repo\\browser-use\\updated_data_files\\query_22-27-jingdong_updated.json"
    # test_path = "/Users/liuyichen/Documents/repo/browser-use/updated_data_files/query_1-9_shangxia_updated.json"
    test_res_dir = "D:\\repo\\browser-use\\outputs\\test_all_claude_sonnet_4_20250514_jingdong_22-27_updated_debugenMini"
    # test_res_dir = "/Users/liuyichen/Documents/repo/browser-use/outputs/debug"
    os.makedirs(test_res_dir, exist_ok=True)
    asyncio.run(batch_test(test_path, test_res_dir))
    # asyncio.run(batch_eval(test_res_dir))
