import streamlit as st
import time
import os
from gtts import gTTS
from io import BytesIO

# --- 0. 系統配置 ---
st.set_page_config(
    page_title="阿美語小教室 - Unit 4", 
    page_icon="😋", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# --- CSS 極致美化 (含 iPhone 深色模式修正) ---
st.markdown("""
    <style>
    /* 全局背景：清爽的米黃色 */
    .stApp { 
        background-color: #FFFDE7; 
    }
    
    /* 🔥【關鍵修正】強制所有一般文字為深灰色，無視手機深色模式 */
    .stApp, .stMarkdown, p, div, span, label, li, h1, h2, h3, h4, h5, h6 {
        color: #333333 !important;
    }

    .block-container { padding-top: 2rem !important; padding-bottom: 5rem !important; }
    
    /* 標題漸層：橘紅配色，象徵酸甜苦辣 */
    h1 {
        font-family: 'Helvetica Neue', sans-serif;
        background: -webkit-linear-gradient(45deg, #FF6F00, #F57F17);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900 !important;
        text-align: center;
        padding-bottom: 10px;
    }
    
    /* 按鈕：橘色系 */
    .stButton>button {
        width: 100%;
        border-radius: 50px;
        font-size: 18px;
        font-weight: 700;
        background: linear-gradient(135deg, #FF8F00 0%, #EF6C00 100%);
        color: #FFFFFF !important;
        border: none;
        padding: 15px 0px;
        box-shadow: 0px 5px 15px rgba(239, 108, 0, 0.4);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0px 8px 20px rgba(239, 108, 0, 0.6);
    }
    
    /* 單字卡片 */
    .card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 15px;
        border: 2px solid #FFE0B2;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }
    
    /* 句子卡片 */
    .sentence-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #FFF3E0 100%);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 15px;
        border-left: 6px solid #FF6F00;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    
    .big-font {
        font-size: 24px !important;
        font-weight: 800;
        color: #E65100 !important;
        margin: 5px 0;
    }
    .med-font {
        font-size: 16px !important;
        color: #555 !important;
        font-weight: 500;
        margin-bottom: 10px;
    }
    .emoji-icon {
        font-size: 40px;
        margin-bottom: 5px;
    }
    
    /* 修正 Radio 選項文字顏色 */
    .stRadio label {
        color: #333333 !important;
        font-size: 18px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. 數據結構 (自動適應數量) ---

# 我幫你加上了生動的動作提示！
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
    # 優先尋找預錄音檔
    if filename_base:
        for ext in ['m4a', 'mp3']:
            path = f"audio/{filename_base}.{ext}"
            if os.path.exists(path):
                st.audio(path, format=f'audio/{ext}')
                return
    
    # 沒有檔案時，使用 Google 小姐 (印尼語口音較接近)
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
        <div style='text-align: center; margin-bottom: 25px;'>
            <h2 style='color: #E65100 !important; font-size: 26px; margin: 0;'>Unit 4: 好多味道</h2>
            <div style='color: #FB8C00 !important; font-size: 16px; margin-top: 5px;'>
                — 酸甜苦辣鹹，你喜歡哪一個？ —
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.info("💡 點擊播放按鈕，跟著老師大聲唸！")
    
    st.markdown("### 🍋 味道與食物單字")
    col1, col2 = st.columns(2)
    
    for idx, item in enumerate(VOCABULARY):
        with (col1 if idx % 2 == 0 else col2):
            st.markdown(f"""
            <div class="card">
                <div class="emoji-icon">{item['emoji']}</div>
                <div class="big-font">{item['amis']}</div>
                <div class="med-font">{item['zh']}</div>
                <div style="color: #BF360C !important; font-size: 12px; background: #FFCCBC; padding: 2px 8px; border-radius: 10px; display:inline-block;">
                    {item['action']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            play_audio(item['amis'], filename_base=item['file'])

    st.markdown("---")
    
    st.markdown("### 🗣️ 生活對話練習")
    
    for s in SENTENCES:
        st.markdown(f"""
        <div class="sentence-card">
            <div style="font-size: 18px; font-weight:900; color:#E65100 !important; margin-bottom: 5px;">
                {s['amis']}
            </div>
            <div style="color:#5D4037 !important; font-size: 16px;">{s['zh']}</div>
        </div>
        """, unsafe_allow_html=True)
        play_audio(s['amis'], filename_base=s['file'])

def show_quiz_mode():
    st.markdown("<h3 style='text-align: center; color: #E65100 !important; margin-bottom: 20px;'>🏆 小小美食家挑戰</h3>", unsafe_allow_html=True)
    
    st.progress(st.session_state.current_q / 3)
    st.write("") 

    if st.session_state.current_q == 0:
        # Q1: 聽力測驗
        st.markdown("**第 1 關：聽聽看，這是什麼味道？**")
        play_audio("micedem", filename_base="v_micedem")
        
        st.write("")
        if st.button("🍋 好酸"): st.error("不對喔，酸是 'acicim")
        if st.button("🍬 好甜"): 
            st.balloons()
            st.success("答對了！Micedem 就是甜！")
            time.sleep(1.5)
            st.session_state.score += 1
            st.session_state.current_q += 1
            st.rerun()
        if st.button("🌶️ 好辣"): st.error("不對喔，辣是 kaedah")

    elif st.session_state.current_q == 1:
        # Q2: 填空題
        st.markdown("**第 2 關：我是翻譯官**")
        st.markdown("當你吃到 **洋蔥 (Tamaniki)**，你會說：")
        
        # 🔥 這裡加上了 color:#000000 修正 iPhone 白字問題
        st.markdown("""
        <div style="background:#fff; color:#000000; padding:15px; border-radius:10px; border-left: 5px solid #FF6F00; margin: 10px 0;">
            <span style="font-size:18px;">Tada <b>_______</b> ko tamaniki!</span>
            <br><span style="color:#999; font-size:14px;">(洋蔥好辣！)</span>
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
            st.success("全對！你是阿美語小廚神！👨‍🍳")
            time.sleep(1.5)
            st.session_state.score += 1
            st.session_state.current_q += 1
            st.rerun()
        if st.button("甘蔗好甜！"): st.error("不對喔，那是 tefos")
        if st.button("鹽巴好鹹！"): st.error("不對喔，那是 cilah")

    else:
        st.markdown(f"""
        <div style='text-align: center; padding: 30px; background-color: #FFF3E0; border-radius: 20px;'>
            <h1 style='color: #E65100 !important;'>🎉 挑戰成功！</h1>
            <p style='font-size: 20px;'>你學會了所有的味道！</p>
            <p style='font-size: 60px;'>🥘</p>
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
