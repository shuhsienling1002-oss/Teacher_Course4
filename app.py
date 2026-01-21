import streamlit as st
import time
import os
import random
from gtts import gTTS
from io import BytesIO

# --- 0. 系統配置 ---
st.set_page_config(
    page_title="阿美語小教室 - Sanek", 
    page_icon="🍲", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# --- CSS 視覺設計 (方案 C：熱情饗宴風 🌶️ - 修正標題版) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700;900&display=swap');

    /* 全局背景：淡淡的暖粉白，像熱鬧的氛圍 */
    .stApp { 
        background-color: #FFF5F5; 
        font-family: 'Noto Sans TC', sans-serif;
    }
    
    .block-container { padding-top: 2rem !important; padding-bottom: 5rem !important; }
    
    /* 修正 h1：把漸層拿掉，改用 class 控制，避免 emoji 消失 */
    h1 {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 900 !important;
        text-align: center;
        padding-bottom: 10px;
        text-shadow: 0px 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 0px;
    }
    
    /* 專門給文字用的漸層 class */
    .spicy-text {
        background: linear-gradient(120deg, #C62828, #FF6F00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* 文字顏色：深褐色，對比清晰 */
    p, div, span, label, li {
        color: #4E342E !important;
    }

    /* 按鈕：辣椒紅漸層，非常吸睛 */
    .stButton>button {
        width: 100%;
        border-radius: 25px;
        font-size: 18px;
        font-weight: 700;
        background: linear-gradient(90deg, #D32F2F 0%, #FF5252 100%);
        color: #FFFFFF !important;
        border: none;
        padding: 12px 0px;
        box-shadow: 0px 4px 10px rgba(211, 47, 47, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0px 6px 15px rgba(211, 47, 47, 0.5);
        background: linear-gradient(90deg, #B71C1C 0%, #D32F2F 100%);
    }
    
    /* 卡片：白色背景，配上淡紅邊框 */
    .card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 24px;
        text-align: center;
        margin-bottom: 20px;
        border: 2px solid #FFCDD2; /* 淡紅邊框 */
        box-shadow: 0 8px 20px rgba(183, 28, 28, 0.05);
        transition: transform 0.2s ease;
    }
    .card:hover {
        transform: translateY(-5px);
        border-color: #EF5350;
    }
    
    /* 句子卡片：左側改為深紅色線條 */
    .sentence-card {
        background-color: #FFFFFF;
        padding: 20px 25px;
        border-radius: 16px;
        margin-bottom: 15px;
        border-left: 6px solid #C62828;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    
    /* 大字體：強調色改為深紅橘色 */
    .big-font {
        font-size: 26px !important;
        font-weight: 800;
        color: #BF360C !important; 
        margin: 8px 0;
        letter-spacing: 0.5px;
    }
    .med-font {
        font-size: 16px !important;
        color: #8D6E63 !important;
        font-weight: 500;
        margin-bottom: 12px;
    }
    .emoji-icon {
        font-size: 48px;
        margin-bottom: 5px;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
    }
    
    /* 動作標籤：淡紅色背景 */
    .action-tag {
        color: #B71C1C !important;
        font-size: 13px;
        font-weight: 600;
        background: #FFEBEE;
        padding: 4px 12px;
        border-radius: 12px;
        display: inline-block;
    }

    /* Tab 樣式 */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255,255,255,0.6);
        border-radius: 10px;
        padding: 8px 16px;
        font-weight: 600;
        color: #5D4037 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF5252 !important;
        color: #FFFFFF !important;
    }
    
    .stRadio label {
        font-size: 18px !important;
        padding: 10px;
        background: rgba(255,255,255,0.8);
        border-radius: 10px;
        margin-bottom: 5px;
        display: block;
        border: 1px solid #FFCDD2;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. 數據結構 ---

VOCABULARY = [
    {"amis": "'acicim",   "zh": "酸",     "emoji": "🍋", "action": "做出酸梅臉", "file": "v_acicim"},
    {"amis": "micedem",   "zh": "甜",     "emoji": "🍬", "action": "摸摸臉頰笑", "file": "v_micedem"},
    {"amis": "'angrer",   "zh": "苦",     "emoji": "🤢", "action": "吐舌頭皺眉", "file": "v_angrer"},
    {"amis": "kaedah",    "zh": "辣",     "emoji": "🌶️", "action": "用手搧舌頭", "file": "v_kaedah"},
    {"amis": "kahcid",    "zh": "鹹",     "emoji": "🧂", "action": "做出喝水動作", "file": "v_kahcid"},
    {"amis": "mami'",     "zh": "柑橘",   "emoji": "🍊", "action": "做出剝皮動作", "file": "v_mami"},
    {"amis": "tefos",     "zh": "甘蔗",   "emoji": "🎋", "action": "做出啃甘蔗動作", "file": "v_tefos"},
    {"amis": "kakorot",   "zh": "苦瓜",   "emoji": "🥒", "action": "搖搖頭", "file": "v_kakorot"},
    {"amis": "cilah",     "zh": "鹽巴",   "emoji": "🧂", "action": "手指搓一搓", "file": "v_cilah"},
    {"amis": "tamaniki",  "zh": "洋蔥",   "emoji": "🧅", "action": "假裝擦眼淚", "file": "v_tamaniki"},
]

SENTENCES = [
    {"amis": "Mama! O maan kora?",      "zh": "爸爸！那是什麼？", "file": "s_mama_omaan"},
    {"amis": "O mami' koni.",           "zh": "這是柑橘。",       "file": "s_o_mami"},
    {"amis": "'Acicim ko mami'.",       "zh": "柑橘好酸。",       "file": "s_acicim_mami"},
    {"amis": "O tefos koni.",           "zh": "這是甘蔗。",       "file": "s_o_tefos"},
    {"amis": "Tada micedem ko tefos.",  "zh": "甘蔗好甜！",       "file": "s_micedem_tefos"},
    {"amis": "O kakorot koni.",         "zh": "這是苦瓜。",       "file": "s_o_kakorot"},
    {"amis": "'Angrer ko kakorot!",     "zh": "苦瓜好苦！",       "file": "s_angrer_kakorot"},
    {"amis": "O tamaniki koni.",        "zh": "這是洋蔥。",       "file": "s_o_tamaniki"},
    {"amis": "Tada kaedah ko tamaniki!","zh": "洋蔥好辣！",       "file": "s_kaedah_tamaniki"},
    {"amis": "O cilah koni.",           "zh": "這是鹽巴。",       "file": "s_o_cilah"},
    {"amis": "Tada kahcid ko cilah.",   "zh": "鹽巴好鹹！",       "file": "s_kahcid_cilah"},
]

QA_PAIRS = [
    {"food": "mami'", "taste": "'acicim", "zh_food": "柑橘", "zh_taste": "酸"},
    {"food": "tefos", "taste": "micedem", "zh_food": "甘蔗", "zh_taste": "甜"},
    {"food": "kakorot", "taste": "'angrer", "zh_food": "苦瓜", "zh_taste": "苦"},
    {"food": "tamaniki", "taste": "kaedah", "zh_food": "洋蔥", "zh_taste": "辣"},
    {"food": "cilah", "taste": "kahcid", "zh_food": "鹽巴", "zh_taste": "鹹"},
]

# --- 1.5 智慧語音核心 ---
def play_audio(text, filename_base=None):
    if filename_base:
        for ext in ['m4a', 'mp3']:
            path = f"audio/{filename_base}.{ext}"
            if os.path.exists(path):
                st.audio(path, format=f'audio/{ext}')
                return
    
    try:
        tts = gTTS(text=text, lang='id')
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        st.audio(fp, format='audio/mp3')
    except:
        st.caption("🔇")

# --- 2. 隨機出題邏輯 ---

def init_quiz():
    st.session_state.score = 0
    st.session_state.current_q = 0
    
    # Q1
    q1_target = random.choice(VOCABULARY)
    others = [v for v in VOCABULARY if v['amis'] != q1_target['amis']]
    q1_options = random.sample(others, 2) + [q1_target]
    random.shuffle(q1_options)
    st.session_state.q1_data = {"target": q1_target, "options": q1_options}

    # Q2 (選項只留阿美語)
    q2_target = random.choice(QA_PAIRS)
    all_tastes_amis = [p['taste'] for p in QA_PAIRS]
    wrong_tastes = [t for t in all_tastes_amis if t != q2_target['taste']]
    q2_options = random.sample(wrong_tastes, 2)
    q2_options.append(q2_target['taste'])
    random.shuffle(q2_options)
    st.session_state.q2_data = {"target": q2_target, "options": q2_options, "correct_ans": q2_target['taste']}

    # Q3
    q3_target = random.choice(SENTENCES)
    other_sentences = [s['zh'] for s in SENTENCES if s['zh'] != q3_target['zh']]
    q3_options = random.sample(other_sentences, 2) + [q3_target['zh']]
    random.shuffle(q3_options)
    st.session_state.q3_data = {"target": q3_target, "options": q3_options}

if 'q1_data' not in st.session_state:
    init_quiz()

# --- 3. 介面邏輯 ---

def show_learning_mode():
    st.markdown("""
        <div style='text-align: center; margin-bottom: 30px;'>
            <h2 style='color: #C62828 !important; font-size: 32px; margin: 0; font-weight:800;'>Sanek</h2>
            <div style='color: #FF6F00 !important; font-size: 18px; margin-top: 8px; font-weight:500;'>
                — 是什麼味道？ —
            </div>
            <div style='color: #8D6E63 !important; font-size: 15px; margin-top: 15px; font-weight: 500;'>
                講師：高春美 &nbsp;&nbsp; 教材提供者：高春美
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.info("💡 點擊播放按鈕，感受這些味道！")
    
    st.markdown("### 🥘 味道與食材")
    col1, col2 = st.columns(2)
    
    for idx, item in enumerate(VOCABULARY):
        with (col1 if idx % 2 == 0 else col2):
            st.markdown(f"""
            <div class="card">
                <div class="emoji-icon">{item['emoji']}</div>
                <div class="big-font">{item['amis']}</div>
                <div class="med-font">{item['zh']}</div>
                <div class="action-tag">
                    {item['action']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            play_audio(item['amis'], filename_base=item['file'])

    st.markdown("---")
    
    st.markdown("### 🗣️ 美味對話")
    
    for s in SENTENCES:
        st.markdown(f"""
        <div class="sentence-card">
            <div style="font-size: 20px; font-weight:800; color:#C62828 !important; margin-bottom: 8px;">
                {s['amis']}
            </div>
            <div style="color:#4E342E !important; font-size: 16px;">{s['zh']}</div>
        </div>
        """, unsafe_allow_html=True)
        play_audio(s['amis'], filename_base=s['file'])

def show_quiz_mode():
    st.markdown("<h3 style='text-align: center; color: #D32F2F !important; margin-bottom: 20px;'>🏆 隨機挑戰賽</h3>", unsafe_allow_html=True)
    
    st.progress(st.session_state.current_q / 3)
    st.write("") 

    if st.session_state.current_q == 0:
        data = st.session_state.q1_data
        target = data['target']
        st.markdown("**第 1 關：聽聽看，這是什麼味道？**")
        play_audio(target['amis'], filename_base=target['file'])
        st.write("")
        cols = st.columns(3)
        for idx, opt in enumerate(data['options']):
            with cols[idx]:
                if st.button(f"{opt['emoji']} {opt['zh']}"):
                    if opt['amis'] == target['amis']:
                        st.balloons()
                        st.success(f"答對了！{target['amis']} 就是 {target['zh']}！")
                        time.sleep(1.5)
                        st.session_state.score += 1
                        st.session_state.current_q += 1
                        st.rerun()
                    else:
                        st.error(f"不對喔，{opt['zh']} 是 {opt['amis']}")

    elif st.session_state.current_q == 1:
        data = st.session_state.q2_data
        target = data['target']
        st.markdown("**第 2 關：我是翻譯官**")
        st.markdown(f"當你吃到 **{target['zh_food']} ({target['food']})**，你會說：")
        st.markdown(f"""
        <div style="background:#FFFFFF; padding:20px; border-radius:15px; border-left: 6px solid #D32F2F; margin: 15px 0; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
            <span style="font-size:20px; color:#333 !important;">Tada <b>_______</b> ko {target['food']}!</span>
            <br><span style="color:#888; font-size:15px;">({target['zh_food']}好{target['zh_taste']}！)</span>
        </div>
        """, unsafe_allow_html=True)
        ans = st.radio("請選擇正確的單字：", data['options'])
        if st.button("確定送出"):
            if ans == data['correct_ans']:
                st.balloons()
                st.success(f"太棒了！{ans} 就是 {target['zh_taste']}！")
                time.sleep(1.5)
                st.session_state.score += 1
                st.session_state.current_q += 1
                st.rerun()
            else:
                st.error("再想一下，這個單字的意思不對喔！")

    elif st.session_state.current_q == 2:
        data = st.session_state.q3_data
        target = data['target']
        st.markdown("**第 3 關：終極挑戰**")
        st.markdown("請聽這句話，選出正確的意思：")
        play_audio(target['amis'], filename_base=target['file'])
        for opt_text in data['options']:
            if st.button(opt_text):
                if opt_text == target['zh']:
                    st.balloons()
                    st.success("全對！你是阿美語美食家！👨‍🍳")
                    time.sleep(1.5)
                    st.session_state.score += 1
                    st.session_state.current_q += 1
                    st.rerun()
                else:
                    st.error("不對喔，再聽一次看看！")

    else:
        st.markdown(f"""
        <div style='text-align: center; padding: 40px; background-color: #FFFFFF; border-radius: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);'>
            <h1 style='color: #C62828 !important; margin-bottom:10px;'>🎉 挑戰成功！</h1>
            <p style='font-size: 20px; color: #4E342E !important;'>你的聽力越來越好了！</p>
            <div style='font-size: 80px; margin: 20px 0;'>🥘</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔄 再玩一次 (題目會變喔)"):
            init_quiz()
            st.rerun()

# --- 4. 主程式 ---
def main():
    # 修正這裡：使用 HTML 手動組合，把文字(漸層)和 Emoji(原色) 分開
    st.markdown("""
        <h1>
            <span class="spicy-text">阿美語小教室</span> 
            <span>🏫</span>
        </h1>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📖 學習單詞", "🎮 練習挑戰"])
    
    with tab1:
        show_learning_mode()
    
    with tab2:
        show_quiz_mode()

if __name__ == "__main__":
    main()
