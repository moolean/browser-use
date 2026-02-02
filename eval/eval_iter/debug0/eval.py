# -*- coding: utf-8 -*-
import json
import os
import asyncio
from browser_use.tools.service import Tools
from browser_use.llm.openrouter.chat import ChatOpenRouter
from browser_use import Agent, Browser, ChatBrowserUse, BrowserSession, BrowserProfile, ActionResult
import logging
import sys
sys.path.append("/home/fallengold/Documents/browser-use")
logger = logging.getLogger(__name__)
os.environ["BROWSER_USE_API_KEY"] = "bu_cj6ZpLpUDP8-QmcoAllBR9EK8IfAdROWhHp3moFnIaE"
os.environ["BROWSER_USE_DISABLE_EXTENSIONS"] = 'false'
user_data_dir = "/home/fallengold/Documents/browser-use/eval/eval_iter/browse_user_dir"


ACCOUNT = "stefanoricci旗舰店:凯淳AI"
PASSWORD = "kc13581897578"


def format_query(query: str, domain: str = None) -> str:
    canmo_url = "https://sycm.taobao.com/"
    qianniu_url = "https://myseller.taobao.com/"
    wanxiang_url = "https://one.alimama.com/"

    formatted_query = f"""
请你扮演一个资深的电商运营专家，帮助我完成以下任务：
任务：{query}

你有两个可以查询的网页，除了这三个网页之外，不能访问其他网页。
    - 账号：凯淳
    - 密码：qbt123
1.  淘宝商家中心 生意参谋，网址是：{canmo_url} （适用于淘宝店铺运营）
2.  天猫商家中心 千牛，网址是：{qianniu_url} （适用于天猫店铺运营）
3.  阿里妈妈推广管理后台 万象，网址是：{wanxiang_url} （适用于淘宝天猫店铺的推广运营）

如果你发现已经登陆成功了, 请直接完成任务, 不要再尝试重新登陆
**重要**
1. 当你通过截图发现页面没加载完, **不要尝试重复点击任何按钮导致页面重新刷新**, 这会导致死锁. 请继续等待页面加载完成后再进行下一步操作, 当你重复进行操作发现一直失败的时候,请等待
2. **禁止写todo.md**, 你并没有权限去这么做

注意：登录时请使用以下账号和密码：
账号：{ACCOUNT}
密码：{PASSWORD}

Notes:
1. 搜索输入框可能没有确认按钮，需要在选中输入框时输入回车才能搜索。搜索之后需要进行等待，然后检查是否出现新tab，如果出现新tab，需要切换到新tab，并等待页面加载完成。
2. 在搜索操作之后，必须先检查是否出现新tab，如果出现新tab，需要切换到新tab，并等待页面加载完成。
3. 如果有滑块验证码，使用drag_drop工具来完成滑块验证。
4. 搜索具体活动时，需要在活动名称而不是大促中搜索
5. 对于一些时间选择任务，需要先点击到对应的时间选择按钮，例如‘日’，‘月’。如果选择的是任意时间段，考虑‘自定义’按钮。之后请等待一段时间，等待其加载出来, 日期选择可能不太好用，每次选完日期需要仔细检查一下是否选对了
选择按钮时，如果按钮如下所示，选择11235按钮会按下‘日’按钮
[11235]<button />
    日
[11236]<button />

6. 在点击对应按钮并等待之后，需要直接进行选择时间操作，在现实出正确的时间选择界面之前，不要进行其他操作。
7. 选择年月时如下所示：

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

其中[13932]和[13938]是上个月和下个月的按钮，[13930]和[13940]是上一年和下一年的按钮。
请点击按钮切换时间界面，在点击按钮之后，需要等待一段时间，等待其加载出来。如果点击切换年的按钮没有反应，尝试只是用切换月按钮操作。

8. 日期选择时如果出来是单个日历说明只能选一个固定时间。如果出来两个日历，前面索引数字较小的日历是选择起始时间，后面索引数字较大的日历是终止时间。
当你需要选择两个时间时，必须先在前一个日历中选择起始时间，然后等待页面加载。等新的页面出现之后，再在后一个选择终止时间，等待页面加载。在确认时间之后点击确认。

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

"""
    return formatted_query


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

    # llm = ChatAnthropic(
    #     base_url='https://api.ppchat.vip',
    #     api_key="sk-0rEu2P0yo7YR8tMTIwAK36ornv2HeF99VcmMWhadwRM4tViX",
    #     model='claude-sonnet-4-20250514',
    # )

    llm = ChatBrowserUse()  # browser-use/bu-30b-a3b-preview

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
    history = await agent.run()
    # save trace file ====================
    save_trace_file = f"{save_path}/debug_trace.json"
    history.save_to_file(save_trace_file)

    return history.final_result()


class EvalLoader:

    def __init__(self, path):
        self.path = path
        with open(self.path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        self.item = []
        for domain, value in raw_data.items():
            for idx, item in value.items():
                test_cases = item.get("test_cases", [])
                query_template = item.get("updated_query_template", None) or item.get(
                    "query_template", None)
                for case_num, case in enumerate(test_cases):
                    input_field = case["输入"]
                    query = query_template
                    for name, value in input_field.items():
                        query = query.replace(f"<<{name}>>", str(value))
                    item = {
                        "idx": idx,
                        "domain": domain,
                        "input": case["输入"],
                        "query_template": query_template,
                        "query": query,
                        "gt": case["输出"],
                        "case_num": case_num
                    }
                    self.item.append(item)
        print(f"Loaded {len(self.item)} eval items from {self.path}")

    def __len__(self):
        return len(self.item)

    def __getitem__(self, index):
        return self.item[index]


def batch_test(test_path, test_res_dir):
    data_loader = EvalLoader(test_path)

    with open(f"{test_res_dir}/test_output.jsonl", "a", encoding="utf-8") as output_f:

        for test_item in data_loader.item:
            save_path = f"{test_res_dir}/debug_{test_item['domain']}_{test_item['idx']}_case{test_item['case_num']}"
            os.makedirs(save_path, exist_ok=True)
            test_output = test_item.copy()
            test_query = test_item["query"]
            query = format_query(test_query, "")

            res = asyncio.run(
                example(
                    query,
                    save_path=save_path
                )
            )

            print("Final Answer:", res)
            test_output["answer"] = res
            print(test_output)
            output_f.write(json.dumps(test_output, ensure_ascii=False) + "\n")


if __name__ == "__main__":

    test_path = "/home/fallengold/tmp/browser-use/eval/query_all.json"
    test_res_dir = "/home/fallengold/tmp/browser-use/output/test_all_claudesonnet_debug"
    os.makedirs(test_res_dir, exist_ok=True)
    batch_test(test_path, test_res_dir)
