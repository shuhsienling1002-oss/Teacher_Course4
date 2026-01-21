import streamlit as st
import time
import os
from gtts import gTTS
from io import BytesIO

# --- 0. 系統配置 ---
st.set_page_config(
    page_title="阿美語小教室 - Sanek", 
    page_icon="🍲", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# --- CSS 最佳視覺設計 (美食風格) ---
st.markdown("""
    <style>
    /* 全局字體導入 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700;900&display=swap');

    /* 全局背景：溫暖的奶油米色 */
    .stApp { 
        background-color: #FFF8E1; 
        font-family: 'Noto Sans TC', sans-serif;
    }
    
    /* 調整頂部留白 */
    .block-container { padding-top: 2rem !important; padding-bottom: 5rem !important; }
    
    /* 大標題：Sanek - 漸層美味色調 */
    h1 {
        font-family: 'Helvetica Neue', sans-serif;
        background: linear-gradient(120deg, #D84315, #FF8F00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900 !important;
        text-align: center;
        padding-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    /* 一般文字：使用深咖啡色 */
    p, div, span, label, li {
        color: #4E342E !important;
    }

    /* 按鈕：像是一道美味的料理 */
    .stButton>button {
        width: 100%;
        border-radius: 25px;
        font-size: 18px;
        font-weight: 700;
        background: linear-gradient(90deg, #FF6F00 0%, #FF8F00 100%);
        color: #FFFFFF !important;
        border: none;
        padding: 12px 0px;
        box-shadow: 0px 4px 10px rgba(255, 111, 0, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0px 6px 15px rgba(255, 111, 0, 0.5);
        background: linear-gradient(90deg, #EF6C00 0%, #FFA000 100%);
    }
    
    /* 單字卡片 */
    .card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 24px;
        text-align: center;
        margin-bottom: 20px;
        border: 1px solid #FFE0B2;
        box-shadow: 0 8px 20px rgba(78, 52, 46, 0.05);
        transition: transform 0.2s ease;
    }
    .card:hover {
        transform: translateY(-5px);
        border-color: #FFB74D;
    }
    
    /* 句子卡片 */
    .sentence-card {
        background-color: #FFFFFF;
        padding: 20px 25px;
        border-radius: 16px;
        margin-bottom: 15px;
        border-left: 5px solid #FF6F00;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    
    /* 字體樣式 */
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
    
    /* 動作標籤 */
    .action-tag {
        color: #E65100 !important;
        font-size: 13px;
        font-weight: 600;
        background: #FFCCBC;
        padding: 4px 12px;
        border-radius: 12px;
        display: inline-block;
    }

    /* Tab 樣式優化 */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255,255,255,0.6);
        border-radius: 10px;
        padding: 8px 16px;
        font-weight: 600;
        color: #5D4037 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF8F00 !important;
        color: #FFFFFF !important;
    }
    
    /* Radio 選項優化 */
    .stRadio label {
        font-size: 18px !important;
        padding: 10px;
        background: rgba(255,255,255,0.5);
        border-radius: 10px;
        margin-bottom: 5px;
        display: block;
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

# --- 2. 狀態管理 ---
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'current_q' not in st.session_state:
    st.session_state.current_q = 0

# --- 3. 介面邏輯 ---

def show_learning_mode():
    st.markdown("""
        <div style='text-align: center; margin-bottom: 30px;'>
            <h2 style='color: #BF360C !important; font-size: 32px; margin: 0; font-weight:800;'>Sanek</h2>
            <div style='color: #FF6F00 !important; font-size: 18px; margin-top: 8px; font-weight:500;'>
                — 是什麼味道？ —
            </div>
            <!-- 👇 講師資訊加在這裡 -->
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
            <div style="font-size: 20px; font-weight:800; color:#BF360C !important; margin-bottom: 8px;">
                {s['amis']}
            </div>
            <div style="color:#5D4037 !important; font-size: 16px;">{s['zh']}</div>
        </div>
        """, unsafe_allow_html=True)
        play_audio(s['amis'], filename_base=s['file'])

def show_quiz_mode():
    st.markdown("<h3 style='text-align: center; color: #E65100 !important; margin-bottom: 20px;'>🏆 味道挑戰賽</h3>", unsafe_allow_html=True)
    
    st.progress(st.session_state.current_q / 3)
    st.write("") 

    if st.session_state.current_q == 0:
        # Q1: 聽力測驗
        st.markdown("**第 1 關：聽聽看，這是什麼味道？**")
        play_audio("micedem", filename_base="v_micedem")
        
        st.write("")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🍋 好酸"): st.error("不對喔，酸是 'acicim")
        with col2:
            if st.button("🍬 好甜"): 
                st.balloons()
                st.success("答對了！Micedem 就是甜！")
                time.sleep(1.5)
                st.session_state.score += 1
                st.session_state.current_q += 1
                st.rerun()
        with col3:
            if st.button("🌶️ 好辣"): st.error("不對喔，辣是 kaedah")

    elif st.session_state.current_q == 1:
        # Q2: 填空題
        st.markdown("**第 2 關：我是翻譯官**")
        st.markdown("當你吃到 **洋蔥 (Tamaniki)**，你會說：")
        
        st.markdown("""
        <div style="background:#FFFFFF; padding:20px; border-radius:15px; border-left: 6px solid #FF6F00; margin: 15px 0; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
            <span style="font-size:20px; color:#333 !important;">Tada <b>_______</b> ko tamaniki!</span>
            <br><span style="color:#888; font-size:15px;">(洋蔥好辣！)</span>
        </div>
        """, unsafe_allow_html=True)
        
        options = ["micedem (甜)", "kaedah (辣)", "kahcid (鹹)"]
        ans = st.radio("請選擇正確的單字：", options)
        
        if st.button("確定送出"):
            if "kaedah" in ans:
                st.balloons()
                st.success("太棒了！Kaedah 就是辣！")
                time.sleep(1.5)
                st.session_state.score += 1
                st.session_state.current_q += 1
                st.rerun()
            else:
                st.error("再想一下，洋蔥會讓人流眼淚喔！")

    elif st.session_state.current_q == 2:
        # Q3: 句子理解
        st.markdown("**第 3 關：終極挑戰**")
        st.markdown("請聽這句話，選出正確的意思：")
        play_audio("'Angrer ko kakorot!", filename_base="s_angrer_kakorot")
        
        if st.button("苦瓜好苦！"):
            st.balloons()
            st.success("全對！你是阿美語美食家！👨‍🍳")
            time.sleep(1.5)
            st.session_state.score += 1
            st.session_state.current_q += 1
            st.rerun()
        if st.button("甘蔗好甜！"): st.error("不對喔，那是 tefos")
        if st.button("鹽巴好鹹！"): st.error("不對喔，那是 cilah")

    else:
        st.markdown(f"""
        <div style='text-align: center; padding: 40px; background-color: #FFFFFF; border-radius: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);'>
            <h1 style='color: #E65100 !important; margin-bottom:10px;'>🎉 挑戰成功！</h1>
            <p style='font-size: 20px; color: #5D4037 !important;'>你學會了所有的 Sanek (味道)！</p>
            <div style='font-size: 80px; margin: 20px 0;'>🥘</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("再玩一次"):
            st.session_state.current_q = 0
            st.session_state.score = 0
            st.rerun()

# --- 4. 主程式 ---
def main():
    st.title("阿美語小教室 🏫")
    
    tab1, tab2 = st.tabs(["📖 學習單詞", "🎮 練習挑戰"])
    
    with tab1:
        show_learning_mode()
    
    with tab2:
        show_quiz_mode()

if __name__ == "__main__":
    main()
