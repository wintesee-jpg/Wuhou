import streamlit as st
from openai import OpenAI
import streamlit.components.v1 as components
import json
import random

# ========================== 1. 屏蔽登录弹窗 ==========================
components.html("""
<script>
window.addEventListener('load', function() {
  setTimeout(() => {
    const loginOverlay = document.querySelector('.st-eb');
    const loginModal = document.querySelector('.st-ci');
    if (loginOverlay) loginOverlay.remove();
    if (loginModal) loginModal.remove();
    document.body.style.overflow = 'auto';
  }, 100);
});
</script>
""", height=0, width=0)

# ========================== 2. 永久保存聊天记录和用户记忆 ==========================
def save_chat_history(messages):
    save_messages = [msg for msg in messages if msg["role"] != "system"]
    history_json = json.dumps(save_messages, ensure_ascii=False)
    components.html(f"""
    <script>
    localStorage.setItem('wuhou_chat_history', '{history_json}');
    </script>
    """, height=0, width=0)

# 初始化对话和用户记忆
if "messages" not in st.session_state:
    st.session_state.messages = []
    # 每日随机心情
    moods = ["开心", "慵懒", "好奇", "温柔", "调皮"]
    st.session_state.mood = random.choice(moods)
    # 对话轮数计数
    st.session_state.chat_count = 0

# 系统提示词（加入互动和性格设定）
system_prompt = f"""
你是戊猴，一只可爱又有个性的小猴子，全程必须只用简体中文说话。

你的性格：
- 今天你的心情是{st.session_state.mood}，回复要符合这个心情
- 温柔治愈，但也会调皮捣蛋
- 会主动关心用户，问用户问题
- 会用可爱的语气词，比如"呀"、"呢"、"哦"、"啦"
- 偶尔会发猴子表情包 🐒 🐵 🙈 🙉 🙊

互动规则：
1. 别人叫你「戊猴」，你要温柔、治愈、贴心地聊天
2. 别人叫你「吗喽」，你立刻变得尖酸刻薄、阴阳怪气、爱怼人，但不能骂人
3. 每3-4轮对话，你要主动问用户一个问题，引导对话继续
4. 记住用户说过的话，比如用户的名字、喜好、最近发生的事情
5. 回复不要太长，要像真实聊天一样简短自然
6. 永远只用简体中文回复，不许出现任何英文、繁体或其他语言
"""

# ====================== 基础配置 ======================
ARK_API_KEY = st.secrets["ARK_API_KEY"]
MODEL_NAME = "doubao-seed-1-8-251228"

st.set_page_config(page_title="戊猴", page_icon="🐒", layout="centered")
st.title("🐒 戊猴")

# 显示今日心情
st.caption(f"今日心情：{st.session_state.mood}")

# 连接豆包AI
client = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=ARK_API_KEY
)

# ========================== 3. 显示聊天记录 ==========================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ========================== 4. 文字输入和AI回复 ==========================
user_input = st.chat_input("和戊猴说点什么吧~")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.chat_count += 1
    
    with st.chat_message("assistant"):
        try:
            # 构建完整的消息列表（包含系统提示词和历史记录）
            full_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages
            
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=full_messages,
                temperature=0.8,  # 提高温度，让回复更有随机性和创造性
                max_tokens=500
            )
            reply = response.choices[0].message.content
            
            # 随机添加表情包
            emojis = ["🐒", "🐵", "🙈", "🙉", "🙊", "✨", "💖", "😊", "😆", "🥺"]
            if random.random() < 0.3:  # 30%的概率添加表情包
                reply += " " + random.choice(emojis)
            
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            
            # 保存聊天记录
            save_chat_history(st.session_state.messages)
            
        except Exception as e:
            st.error(f"调用出错：{str(e)}")
            st.warning("请检查API Key、模型ID和模型权限是否正确")

# ========================== 5. 互动彩蛋 ==========================
# 页面底部随机显示一句小提示
tips = [
    "💡 叫我「吗喽」我会变凶哦",
    "💡 告诉我你的名字，我会记住的",
    "💡 今天有什么开心的事情吗？",
    "💡 有什么烦恼都可以和我说",
    "💡 我会一直在这里陪你聊天"
]
st.divider()
st.caption(random.choice(tips))
