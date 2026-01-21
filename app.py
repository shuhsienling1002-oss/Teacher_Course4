import streamlit as st
import time
import os
import random  # 新增：隨機模組
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
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700;900&display=swap');

    .stApp { 
        background-color: #FFF8E1; 
        font-family: 'Noto Sans TC', sans-serif;
    }
    
    .block-container { padding-top: 2rem !important; padding-bottom: 5rem !important; }
    
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
    
    p, div, span, label, li {
        color: #4E342E !important;
    }

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
    
    .sentence-card {
        background-color: #FFFFFF;
        padding: 20px 25px;
        border-radius: 16px;
        margin-bottom: 15px;
        border-left: 5px solid #FF6F00;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    
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
    
    .action-tag {
        color: #E65100 !important;
        font-size: 13px;
        font-weight: 600;
        background: #FFCCBC;
        padding: 4px 12px;
        border-radius: 12px;
        display: inline-block;
    }

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

# 為了 Q2 填空題，建立「食物-味道」對應表
QA_PAIRS = [
    {"food": "mami'", "taste": "'acicim", "zh_food": "柑橘", "zh_taste": "酸"},
    {"food": "tefos", "taste": "micedem", "zh_food": "甘蔗", "zh_taste": "甜"},
    {"food": "kakorot", "taste": "'angrer", "zh_food": "苦瓜", "zh_taste": "苦"},
    {"food": "tamaniki", "taste": "kaedah", "zh_food": "洋蔥", "zh_taste": "辣"},
    {"food": "cilah", "taste": "kahcid", "zh_food": "鹽巴", "zh_taste": "鹹"},
]

# --- 1.5 智慧語音核心 ---
def play_audio(text, filename_base=None):
    # 優先嘗試播放上傳的檔案
    if filename_base:
        for ext in ['m4a', 'mp3']:
            path = f"audio/{filename_base}.{ext}"
            if os.path.exists(path):
                st.audio(path, format=f'audio/{ext}')
                return
    
    # 檔案不存在時使用 TTS
    try:
        tts = gTTS(text=text, lang='id')
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        st.audio(fp, format='audio/mp3')
    except:
        st.caption("🔇")

# --- 2. 隨機出題邏輯 (核心修改) ---

def init_quiz():
    """初始化或重置測驗題目"""
    st.session_state.score = 0
    st.session_state.current_q = 0
    
    # --- Q1: 聽力測驗 (隨機選一個單字) ---
    q1_target = random.choice(VOCABULARY)
    # 隨機選 2 個錯誤答案
    others = [v for v in VOCABULARY if v['amis'] != q1_target['amis']]
    q1_options = random.sample(others, 2) + [q1_target]
    random.shuffle(q1_options) # 打亂選項順序
    
    st.session_state.q1_data = {
        "target": q1_target,
        "options": q1_options
    }

    # --- Q2: 填空題 (隨機選一組 食物-味道) ---
    q2_target = random.choice(QA_PAIRS)
    # 隨機選 2 個錯誤的味道
    all_tastes = [p['taste'] for p in QA_PAIRS]
    wrong_tastes = [t for t in all_tastes if t != q2_target['taste']]
    # 為了顯示漂亮，選項要包含中文
    # 這裡稍微複雜一點，要找出錯誤味道對應的中文
    q2_options_raw = random.sample(wrong_tastes, 2)
    q2_options = []
    
    # 加入正確答案
    q2_options.append(f"{q2_target['taste']} ({q2_target['zh_taste']})")
    
    # 加入錯誤答案 (需找回對應中文)
    for wt in q2_options_raw:
        # 找到該味道對應的中文 (隨便找一個符合的即可)
        match = next((p for p in QA_PAIRS if p['taste'] == wt), None)
        if match:
            q2_options.append(f"{match['taste']} ({match['zh_taste']})")
            
    random.shuffle(q2_options)
    
    st.session_state.q2_data = {
        "target": q2_target,
        "options": q2_options,
        "correct_str": f"{q2_target['taste']} ({q2_target['zh_taste']})"
    }

    # --- Q3: 句子理解 (隨機選一個句子) ---
    q3_target = random.choice(SENTENCES)
    # 隨機選 2 個錯誤的中文意思
    other_sentences = [s['zh'] for s in SENTENCES if s['zh'] != q3_target['zh']]
    q3_options = random.sample(other_sentences, 2) + [q3_target['zh']]
    random.shuffle(q3_options)
    
    st.session_state.q3_data = {
        "target": q3_target,
        "options": q3_options
    }

# 如果是第一次執行，初始化題目
if 'q1_data' not in st.session_state:
    init_quiz()

# --- 3. 介面邏輯 ---

def show_learning_mode():
    st.markdown("""
        <div style='text-align: center; margin-bottom: 30px;'>
            <h2 style='color: #BF360C !important; font-size: 32px; margin: 0; font-weight:800;'>Sanek</h2>
            <div style='color: #FF6F00 !important; font-size: 18px; margin-top: 8px; font-weight:500;'>
                — O Maan a Sanek? (是什麼味道？) —
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
            <div style="font-size: 20px; font-weight:800; color:#BF360C !important; margin-bottom: 8px;">
                {s['amis']}
            </div>
            <div style="color:#5D4037 !important; font-size: 16px;">{s['zh']}</div>
        </div>
        """, unsafe_allow_html=True)
        play_audio(s['amis'], filename_base=s['file'])

def show_quiz_mode():
    st.markdown("<h3 style='text-align: center; color: #E65100 !important; margin-bottom: 20px;'>🏆 隨機挑戰賽</h3>", unsafe_allow_html=True)
    
    st.progress(st.session_state.current_q / 3)
    st.write("") 

    # --- Q1 顯示邏輯 ---
    if st.session_state.current_q == 0:
        data = st.session_state.q1_data
        target = data['target']
        
        st.markdown("**第 1 關：聽聽看，這是什麼味道？**")
        play_audio(target['amis'], filename_base=target['file'])
        
        st.write("")
        cols = st.columns(3)
        
        for idx, opt in enumerate(data['options']):
            with cols[idx]:
                # 按鈕顯示 Emoji + 中文
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

    # --- Q2 顯示邏輯 ---
    elif st.session_state.current_q == 1:
        data = st.session_state.q2_data
        target = data['target']
        
        st.markdown("**第 2 關：我是翻譯官**")
        st.markdown(f"當你吃到 **{target['zh_food']} ({target['food']})**，你會說：")
        
        st.markdown(f"""
        <div style="background:#FFFFFF; padding:20px; border-radius:15px; border-left: 6px solid #FF6F00; margin: 15px 0; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
            <span style="font-size:20px; color:#333 !important;">Tada <b>_______</b> ko {target['food']}!</span>
            <br><span style="color:#888; font-size:15px;">({target['zh_food']}好{target['zh_taste']}！)</span>
        </div>
        """, unsafe_allow_html=True)
        
        ans = st.radio("請選擇正確的單字：", data['options'])
        
        if st.button("確定送出"):
            if ans == data['correct_str']:
                st.balloons()
                st.success(f"太棒了！{target['food']} 真的很 {target['zh_taste']}！")
                time.sleep(1.5)
                st.session_state.score += 1
                st.session_state.current_q += 1
                st.rerun()
            else:
                st.error("再想一下，這個食物的味道是什麼？")

    # --- Q3 顯示邏輯 ---
    elif st.session_state.current_q == 2:
        data = st.session_state.q3_data
        target = data['target']
        
        st.markdown("**第 3 關：終極挑戰**")
        st.markdown("請聽這句話，選出正確的意思：")
        play_audio(target['amis'], filename_base=target['file'])
        
        # 顯示選項
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

    # --- 結算畫面 ---
    else:
        st.markdown(f"""
        <div style='text-align: center; padding: 40px; background-color: #FFFFFF; border-radius: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);'>
            <h1 style='color: #E65100 !important; margin-bottom:10px;'>🎉 挑戰成功！</h1>
            <p style='font-size: 20px; color: #5D4037 !important;'>你的聽力越來越好了！</p>
            <div style='font-size: 80px; margin: 20px 0;'>🥘</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 點擊這裡會重新隨機出題
        if st.button("🔄 再玩一次 (題目會變喔)"):
            init_quiz() # 重新抽題
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
