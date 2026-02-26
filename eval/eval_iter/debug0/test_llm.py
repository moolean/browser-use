from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
import base64
llm = ChatAnthropic(
    base_url='https://api.ppchat.vip',
    api_key="sk-0rEu2P0yo7YR8tMTIwAK36ornv2HeF99VcmMWhadwRM4tViX",
#     base_url='https://api.uniapi.io/claude',
#     api_key="sk-fx7IRkc1izDuBZH_hi_0k8jVyAlJ9wqTpQcWW2FlbiPbEn9vO67P-iOwXaI",
    model='claude-sonnet-4-20250514',
)

image_path = "/Users/liuyichen/Documents/repo/browser-use/outputs/test_all_claude_sonnet_4_20250514_shangxia_1-9_updated_debug-retest/debug_上下官方旗舰店_9_1_case0/browser_temp/browser_use_agent_0698cbdf-47e6-716b-8000-895235aa76fa_1770831348/screenshots/step_17.png"
with open(image_path, "rb") as f:
    image_content = f.read()



image_data = base64.b64encode(image_content).decode("utf-8")

messages = [HumanMessage(
    content=[
        {"type": "text", "text": "Describe the image."},
        { 
            "type": "image", 
            "base64": image_data, 
            "mime_type": "image/jpeg", 
        }, 
    ]
)]

# messages = [
#     SystemMessage(content="You are a helpful assistant that provides concise answers."),
#     HumanMessage(content="Translate the following text into English: 你好，世界！"
# )
# ]


# Get response and print it
response = llm.invoke(messages)
import pdb; pdb.set_trace()
print(response.content)