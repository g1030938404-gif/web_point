import streamlit as st
import json
import os
from datetime import datetime, timedelta, timezone
from supabase import create_client, Client
import streamlit_cookies_manager as cm

# =====================================================
# Supabase 云数据库配置 (云端 Secrets 安全模式)
# =====================================================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase_client()

MAX_STUDY_HOURS = 12
DAILY_MAX_POINTS = 40
MAX_LOGS = 1000

SHOP_ITEMS = {
    "台球券": 20, "网吧券": 20, "KTV券": 20,
    "钓鱼券": 20, "麻将券": 30, "包夜券": 60
}

st.set_page_config(page_title="高羊积分系统", page_icon="💌", layout="wide")

# =====================================================
# 🍪 浏览器 Cookie 记住登录状态引擎 (免密直达)
# =====================================================
cookies = cm.CookieManager()
if not cookies.ready():
    st.stop() # 等待浏览器 Cookie 握手同步

# =====================================================
# 🧭 全球服务器无缝锁定北京时间 (UTC+8)
# =====================================================
def get_china_now():
    return datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=8)

# =====================================================
# 🌟 全设备完美适配 UI CSS (磨砂玻璃/流光/移动响应式)
# =====================================================
st.markdown("""
<style>
/* 隐藏默认元素 */
#MainMenu, footer, header {visibility: hidden;}

/* 全局布局最大宽度限制 */
.block-container {
    padding-top: 1rem !important; 
    padding-bottom: 2rem !important; 
    max-width: 850px !important;
    margin: 0 auto;
}

/* 全局背景：浪漫流光渐变 */
.stApp {
    background: linear-gradient(120deg, #fdfbfb 0%, #ebedee 100%);
    background-image: radial-gradient(at 0% 0%, hsla(353,100%,93%,1) 0, transparent 50%), 
                      radial-gradient(at 100% 100%, hsla(202,100%,92%,1) 0, transparent 50%);
    background-attachment: fixed;
    font-family: 'PingFang SC', 'Microsoft YaHei', -apple-system, sans-serif;
}

/* 磨砂玻璃通用卡片 */
.glass-card {
    background: rgba(255, 255, 255, 0.65);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.8);
    border-radius: 20px;
    padding: 24px;
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.05);
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    margin-bottom: 16px;
    width: 100%;
    box-sizing: border-box;
}
.glass-card:hover {
    box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.1);
    transform: translateY(-3px);
}

/* 浪漫 Banner 设计 */
.romantic-banner {
    text-align: center;
    padding: 30px 20px;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 245, 247, 0.8) 100%);
    border-radius: 24px;
    margin-bottom: 20px;
    box-shadow: 0 10px 30px rgba(255, 117, 140, 0.1);
    position: relative;
    overflow: hidden;
}
.banner-title {
    color: #2c3e50;
    font-weight: 800;
    font-size: 2.4rem;
    margin-bottom: 15px;
    letter-spacing: 2px;
}
.quote-en {
    font-size: 1rem;
    color: #95a5a6;
    font-style: italic;
    margin-bottom: 10px;
    letter-spacing: 0.5px;
    line-height: 1.4;
}
.quote-zh {
    font-size: 1.2rem;
    font-weight: 600;
    background: linear-gradient(120deg, #ff758c 0%, #ff7eb3 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 3px;
    margin-bottom: 15px;
}
.days-count {
    display: inline-block;
    padding: 6px 16px;
    background-color: #fff;
    border-radius: 20px;
    color: #ff758c;
    font-size: 0.9rem;
    font-weight: bold;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}

/* 登录框居中魔法 */
.login-container {
    max-width: 400px;
    margin: 10vh auto;
    padding: 40px 30px;
}

/* 优化输入框和下拉框 */
.stTextInput input, .stNumberInput input, .stSelectbox > div > div {
    border-radius: 12px !important;
    border: 1.5px solid #f1f2f6 !important;
    background-color: rgba(255, 255, 255, 0.9) !important;
    transition: 0.3s !important;
}

/* 优化所有的自带 st.button */
.stButton > button {
    width: 100%;
    border-radius: 12px !important;
    border: none !important;
    background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 99%, #fecfef 100%) !important;
    color: #4a4a4a !important;
    font-weight: bold !important;
    padding: 0.6rem 1rem !important;
    transition: all 0.3s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 5px 15px rgba(255,154,158, 0.4) !important;
    color: #fff !important;
}
button[kind="primary"] {
    background: linear-gradient(135deg, #ff758c 0%, #ff7eb3 100%) !important;
    color: white !important;
}

/* 优化标签页 Tab */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    padding: 5px;
    background-color: rgba(255, 255, 255, 0.5);
    border-radius: 16px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 12px !important;
    padding: 8px 16px !important;
    border: none !important;
    background-color: transparent;
}
.stTabs [aria-selected="true"] {
    background-color: #fff !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05) !important;
    color: #ff758c !important;
    font-weight: bold !important;
}

/* 日志气泡 */
.log-bubble {
    background: #ffffff;
    border-left: 4px solid #ff758c;
    padding: 12px 16px;
    border-radius: 0 12px 12px 0;
    margin-bottom: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    font-size: 0.95rem;
    color: #34495e;
    word-wrap: break-word;
}

@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    .banner-title { font-size: 1.8rem; }
    .glass-card { padding: 16px; }
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# 云端数据流底层通信
# =====================================================
def load_data():
    default_data = {
        "accounts": {
            "user1": {"login_id": "ziyang", "password": "123", "display_name": "高梓洋"},
            "user2": {"login_id": "yutong", "password": "123", "display_name": "杨雨桐"}
        },
        "points": {"user1": 0, "user2": 0},
        "logs": [], "record_history": [], "study_records": [], "daily_points": {}, "bounties": [],
        "tasks": [], 
        "study_status": {
            "user1": {"last_end_time": None, "accumulated_minutes": 0, "current_session_start": None, "current_session_type": None},
            "user2": {"last_end_time": None, "accumulated_minutes": 0, "current_session_start": None, "current_session_type": None}
        },
        "inventory": {"user1": {}, "user2": {}},
        "usage_limits": {"user1": {}, "user2": {}}
    }
    try:
        response = supabase.table("points_system").select("config_data").eq("id", 1).execute()
        if response.data and response.data[0]["config_data"]:
            saved_data = response.data[0]["config_data"]
            for key in default_data:
                if key not in saved_data:
                    saved_data[key] = default_data[key]
            return saved_data
        else:
            supabase.table("points_system").upsert({"id": 1, "config_data": default_data}).execute()
            return default_data
    except Exception as e:
        st.error(f"☁️ 云端数据拉取失败: {e}")
        return default_data

def save_data(updated_data):
    try:
        supabase.table("points_system").update({"config_data": updated_data}).eq("id", 1).execute()
    except Exception as e:
        st.error(f"☁️ 云端数据同步失败: {e}")

data = load_data()

# =====================================================
# 🔐 自动登录判定（内存没有就读取 Cookie）
# =====================================================
if "logged_in_uid" not in st.session_state:
    st.session_state.logged_in_uid = None

# 如果内存为空，但浏览器 Cookie 里存了 UID，执行无感自动登录
saved_uid = cookies.get("saved_login_uid")
if saved_uid and not st.session_state.logged_in_uid:
    st.session_state.logged_in_uid = saved_uid

# =====================================================
# 登录门户界面
# =====================================================
if not st.session_state.logged_in_uid:
    st.markdown("""
    <div class="login-container glass-card">
        <h2 style='text-align: center; color: #ff758c; margin-bottom: 10px;'>💌 积分系统</h2>
        <p style='text-align: center; color: #95a5a6; margin-bottom: 30px; font-size: 0.9rem;'>Love is going hand in hand and becoming a better person for each other.</p>
    """, unsafe_allow_html=True)

    login_id = st.text_input("账号 / User ID", placeholder="输入账号...")
    pwd = st.text_input("密码 / Password", type="password", placeholder="输入密码...")

    st.write("")
    if st.button("✨ 立即登录", type="primary"):
        matched_uid = None
        for uid, info in data["accounts"].items():
            if info["login_id"] == login_id and info["password"] == pwd:
                matched_uid = uid
                break
        if matched_uid:
            # 写入浏览器 Cookie 缓存，有效期自动设为长期
            cookies["saved_login_uid"] = matched_uid
            cookies.save()
            st.session_state.logged_in_uid = matched_uid
            st.rerun()
        else:
            st.error("账号或密码错误 🥺")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# =====================================================
# 🛡️ 退出登录逻辑（同步清除内存与 Cookie 锁）
# =====================================================
current_uid = st.session_state.logged_in_uid
global_current_name = data["accounts"][current_uid]["display_name"]

def execute_logout():
    cookies["saved_login_uid"] = ""
    cookies.save()
    st.session_state.logged_in_uid = None
    st.rerun()

st.sidebar.markdown(f"### 👋 欢迎，**{global_current_name}**")
st.sidebar.caption("于道各努力，千里自同风。")
if st.sidebar.button("🚪 安全退出系统"):
    execute_logout()

# =====================================================
# ⏱️ ✨ 核心高频引擎：定义 3秒级自动刷新片段
# =====================================================
@st.fragment(run_every="3s")
def render_live_system():
    global data
    data = load_data() 

    current_uid = st.session_state.logged_in_uid
    target_uid = "user2" if current_uid == "user1" else "user1"
    current_name = data["accounts"][current_uid]["display_name"]
    target_name = data["accounts"][target_uid]["display_name"]

    def get_today_key(): return get_china_now().strftime("%Y-%m-%d")

    def get_today_points(uid):
        today = get_today_key()
        if today not in data["daily_points"]: data["daily_points"][today] = {"user1": 0, "user2": 0}
        return data["daily_points"][today][uid]

    def add_today_points(uid, pts):
        today = get_today_key()
        if today not in data["daily_points"]: data["daily_points"][today] = {"user1": 0, "user2": 0}
        data["daily_points"][today][uid] += pts

    def add_log(uid, action, points_change):
        time_str = get_china_now().strftime('%m-%d %H:%M')
        if points_change != 0:
            if data["points"][uid] + points_change < 0: return False
            data["points"][uid] += points_change
        sign = "+" if points_change > 0 else ""
        user_name = data["accounts"][uid]["display_name"]
        log_text = f"**{time_str}** | **{user_name}** {action}" if points_change == 0 else f"**{time_str}** | **{user_name}** {action} <span style='color:#ff758c; font-weight:bold;'>({sign}{points_change}分)</span>"
        data["logs"].insert(0, log_text)
        data["logs"] = data["logs"][:MAX_LOGS]
        save_data(data)
        return True

    def calculate_study_points_smart(uid, new_start_dt, new_end_dt, study_type, is_makeup=False):
        new_minutes = (new_end_dt - new_start_dt).total_seconds() / 60.0
        if study_type == "课堂学习": return round((new_minutes / 60) * 5, 1), False
        if study_type == "碎片化学习": return round((new_minutes / 60) * 3, 1), False

        status = data["study_status"][uid]
        last_end_str = status.get("last_end_time")
        accumulated_mins = status.get("accumulated_minutes", 0)
        is_continuous = False

        if last_end_str:
            if 0 <= (new_start_dt - datetime.fromisoformat(last_end_str)).total_seconds() / 60.0 < 20:
                is_continuous = True
            else:
                accumulated_mins = 0
        else:
            accumulated_mins = 0

        points = sum([8 / 60 if (accumulated_mins + step) / 60 < 2 else 6 / 60 if (accumulated_mins + step) / 60 < 4 else 4 / 60 for step in range(int(new_minutes))])
        points = round(points, 1)

        remain_pts = DAILY_MAX_POINTS - get_today_points(uid)
        points = 0 if remain_pts <= 0 else min(points, remain_pts)

        if not is_makeup:
            data["study_status"][uid]["last_end_time"] = new_end_dt.isoformat()
            data["study_status"][uid]["accumulated_minutes"] = accumulated_mins + new_minutes
        return points, is_continuous

    def add_study_record(uid, minutes):
        data["study_records"].append({"uid": uid, "minutes": minutes, "time": get_china_now().isoformat()})
        save_data(data)

    def get_week_study_hours(uid):
        return round(sum(r["minutes"] for r in data["study_records"] if r["uid"] == uid and (get_china_now() - datetime.fromisoformat(r["time"])).days < 7) / 60, 1)

    def get_streak_days(uid):
        dates = {datetime.fromisoformat(r["time"]).strftime("%Y-%m-%d") for r in data["study_records"] if r["uid"] == uid}
        streak, current = 0, get_china_now()
        while current.strftime("%Y-%m-%d") in dates: streak += 1; current -= timedelta(days=1)
        return streak

    def get_month_points(uid):
        now_prefix = f"**{get_china_now().strftime('%m-')}"
        return sum(float(log.split("color:#ff758c; font-weight:bold;'>(+")[-1].split("分)")[0]) for log in data["logs"] if data["accounts"][uid]["display_name"] in log and now_prefix in log and "(+" in log)

    # 浪漫 Banner
    love_start = datetime(2022, 8, 13)
    love_days = (get_china_now() - love_start).days
    st.markdown(f"""
    <div class="romantic-banner">
        <div class="banner-title">💖 共同进步！</div>
        <div class="quote-en">"Love is going hand in hand and becoming a better person for each other."</div>
        <div class="quote-zh">朝暮与共，行至天光</div>
        <div class="days-count">我们已携手走过 {love_days} 天 ✨</div>
    </div>
    """, unsafe_allow_html=True)

    # 积分大看板
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <h3 style="color: #7f8c8d; margin-bottom: 0;">🌸 {current_name}</h3>
            <h1 style="color: #ff758c; font-size: 3rem; margin: 10px 0;">{round(data["points"][current_uid], 1)}</h1>
            <span style="color: #bdc3c7; font-size: 0.9rem;">我的金库</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <h3 style="color: #7f8c8d; margin-bottom: 0;">✨ {target_name}</h3>
            <h1 style="color: #3498db; font-size: 3rem; margin: 10px 0;">{round(data["points"][target_uid], 1)}</h1>
            <span style="color: #bdc3c7; font-size: 0.9rem;">对方金库</span>
        </div>
        """, unsafe_allow_html=True)

    # 学习成就榜
    c1, c2, c3 = st.columns(3)
    mvp_name = current_name if get_month_points(current_uid) >= get_month_points(target_uid) else target_name

    with c1: 
        st.markdown(f'<div class="glass-card" style="text-align:center; padding:15px; min-height:110px;">⏳ <b>本周时长</b><br><small style="color:#e74c3c;">{current_name}: {get_week_study_hours(current_uid)}h</small><br><small style="color:#2980b9;">{target_name}: {get_week_study_hours(target_uid)}h</small></div>', unsafe_allow_html=True)
    with c2: 
        st.markdown(f'<div class="glass-card" style="text-align:center; padding:15px; min-height:110px;">🔥 <b>连续打卡</b><br><small style="color:#e74c3c;">{current_name}: {get_streak_days(current_uid)}天</small><br><small style="color:#2980b9;">{target_name}: {get_streak_days(target_uid)}天</small></div>', unsafe_allow_html=True)
    with c3: 
        st.markdown(f'<div class="glass-card" style="text-align:center; padding:15px; min-height:110px;">🏆 <b>本月 MVP</b><br><h3 style="margin:8px 0 0 0; color:#f39c12; font-size:1.2rem;">{mvp_name}</h3></div>', unsafe_allow_html=True)

    # 选项卡功能区
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["⏱️ 学习", "📋 任务", "💰 悬赏", "🎁 商店", "🎒 背包", "⚙️ 设置"])

    # --- Tab 1 学习 ---
    with tab1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.info(f"💡 今日积分限额：{get_today_points(current_uid)} / {DAILY_MAX_POINTS}")
        status = data["study_status"][current_uid]

        st.subheader("🚀 实时记录")
        rt_start_str = status.get("current_session_start")
        if rt_start_str:
            rt_start_dt = datetime.fromisoformat(rt_start_str)
            elapsed_mins = int((get_china_now() - rt_start_dt).total_seconds() / 60)
            st.warning(f"正在进行【{status.get('current_session_type')}】，已持续 {elapsed_mins} 分钟 ⏳")
            if st.button("⏹️ 结束并结算", type="primary"):
                dt_end = get_china_now()
                total_minutes = (dt_end - rt_start_dt).total_seconds() / 60
                if total_minutes < 1:
                    st.error("不足 1 分钟，已取消记录。")
                else:
                    pts, is_cont = calculate_study_points_smart(current_uid, rt_start_dt, dt_end, status.get("current_session_type"))
                    add_today_points(current_uid, pts)
                    add_study_record(current_uid, total_minutes)
                    desc = f"{status.get('current_session_type')} [实时]" + (" [连战]" if is_cont else " [满血]")
                    add_log(current_uid, desc, pts)
                    st.success(f"太棒了！获得 {pts} 分 🎉")
                data["study_status"][current_uid]["current_session_start"] = None
                save_data(data)
                st.rerun()
        else:
            rt_type = st.selectbox("选择记录类型", ["自主学习", "课堂学习", "碎片化学习"], key="rt_type")
            if st.button("▶️ 专注开始", type="primary"):
                data["study_status"][current_uid].update({"current_session_start": get_china_now().isoformat(), "current_session_type": rt_type})
                save_data(data)
                st.rerun()

        st.divider()
        st.subheader("📝 历史补录")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            start_date = st.date_input("开始日期")
            start_time = st.time_input("开始时间", value=get_china_now().replace(hour=8, minute=0, second=0))
        with col_m2:
            end_date = st.date_input("结束日期", value=start_date)
            end_time = st.time_input("结束时间", value=get_china_now().replace(hour=10, minute=0, second=0))
        study_type = st.selectbox("补录类型", ["自主学习", "课堂学习", "碎片化学习"])
        dt_start = datetime.combine(start_date, start_time)
        dt_end = datetime.combine(end_date, end_time)
        
        if (dt_end - dt_start).total_seconds() > 0 and dt_end <= get_china_now():
            if st.button("提交补录"):
                key = f"{current_uid}_{dt_start}_{dt_end}_{study_type}"
                if key in data["record_history"]:
                    st.error("已存在相同记录！")
                else:
                    data["record_history"].append(key)
                    is_makeup = bool(status["last_end_time"] and dt_start < datetime.fromisoformat(status["last_end_time"]))
                    pts, is_cont = calculate_study_points_smart(current_uid, dt_start, dt_end, study_type, is_makeup)
                    add_today_points(current_uid, pts)
                    add_study_record(current_uid, (dt_end - dt_start).total_seconds() / 60)
                    desc = f"{study_type} ({start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')})" + (" [连战]" if is_cont and study_type == "自主学习" else " [满血]" if study_type == "自主学习" else "") + (" [补录]" if is_makeup else "")
                    add_log(current_uid, desc, pts)
                    st.success(f"补录成功，积分 +{pts}")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Tab 2 任务 ---
    with tab2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📋 申报完成事项")
        task_name = st.text_input("完成事项描述：", placeholder="比如：读几篇文献、跑通裂缝识别代码...", key="task_input_name")
        
        c1, c2, c3, c4 = st.columns(4)
        
        def submit_task_review(level, pts):
            if task_name:
                if "tasks" not in data: data["tasks"] = []
                new_id = len(data["tasks"]) + 1
                data["tasks"].append({
                    "id": new_id, "title": task_name, "level": level, "points": pts, "creator": current_uid, "status": "pending"
                })
                save_data(data)
                st.success(f"🚀 {level}级任务已提交！等待 {target_name} 审核确认。")
                st.rerun()
            else:
                st.error("请先输入完成事项描述哦 🥺")

        if c1.button("🟢 S级 (+2分)"): submit_task_review("S", 2)
        if c2.button("🔵 M级 (+5分)"): submit_task_review("M", 5)
        if c3.button("🟣 L级 (+10分)"): submit_task_review("L", 10)
        if c4.button("🟠 SSR (+20分)"): submit_task_review("SSR", 20)
        st.markdown('</div>', unsafe_allow_html=True)

        # 任务审批中心
        st.markdown('<div class="glass-card" style="max-height: 450px; overflow-y: auto;">', unsafe_allow_html=True)
        if "tasks" not in data: data["tasks"] = []
        
        my_audit_tasks = [t for t in data["tasks"] if t["creator"] == target_uid and t["status"] == "pending"]
        st.write(f"✍️ **待我审核（{target_name} 申报的）：**")
        if not my_audit_tasks:
            st.caption("暂无需要你审核的任务 🌟")
        for t in my_audit_tasks:
            st.markdown(f"【{t['level']}级】**{t['title']}** (🎁 +{t['points']}分)")
            t_col1, t_col2 = st.columns(2)
            with t_col1:
                if st.button("✅ 准予通过", key=f"t_pass_{t['id']}", type="primary"):
                    t["status"] = "approved"
                    add_log(t["creator"], f"完成任务[{t['level']}]：{t['title']}", t["points"])
                    st.rerun()
            with t_col2:
                if st.button("❌ 驳回申请", key=f"t_rej_{t['id']}"):
                    t["status"] = "rejected"
                    save_data(data)
                    st.rerun()
                    
        st.divider()
        my_pending_tasks = [t for t in data["tasks"] if t["creator"] == current_uid and t["status"] == "pending"]
        st.write("⏳ **我提交的待审核任务：**")
        if not my_pending_tasks: st.caption("暂无审核中的任务")
        for t in my_pending_tasks:
            st.markdown(f"【{t['level']}级】**{t['title']}** (💰 {t['points']}分) —— *等待对方审核中...*")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Tab 3 悬赏 ---
    with tab3:
        c_pub, c_list = st.columns([1, 1.2])
        with c_pub:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader(f"🎯 悬赏 {target_name}")
            b_title = st.text_input("指派任务：")
            b_points = st.number_input("赏金：", min_value=1, value=20)
            if st.button("发布悬赏", type="primary") and b_title:
                data["bounties"].append({"id": len(data["bounties"]) + 1, "title": b_title, "points": b_points, "creator": current_uid, "target": target_uid, "status": "open"})
                save_data(data)
                st.success("发布成功")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with c_list:
            st.markdown('<div class="glass-card" style="max-height: 400px; overflow-y: auto;">', unsafe_allow_html=True)
            my_b = [b for b in data["bounties"] if b["target"] == current_uid and b["status"] == "open"]
            st.write("📜 **待我完成：**")
            if not my_b: st.caption("暂时没有悬赏哦")
            for b in my_b:
                c_n, c_btn1, c_btn2 = st.columns([2.2, 1.5, 1.3])
                with c_n: st.markdown(f"**{b['title']}** (💰 {b['points']})")
                with c_btn1:
                    if st.button("申请领赏", key=f"ap_{b['id']}"): 
                        b["status"] = "pending"
                        save_data(data)
                        st.rerun()
                with c_btn2:
                    if st.button("拒绝", key=f"rej_b_{b['id']}"):
                        b["status"] = "rejected" 
                        add_log(current_uid, f"拒绝了 {target_name} 的悬赏：{b['title']}", 0) 
                        st.rerun()
            st.divider()
            
            pending = [b for b in data["bounties"] if b["creator"] == current_uid Barb["status"] == "pending"]
            st.write("✅ **待我审核：**")
            if not pending: st.caption("暂无待审核")
            for b in pending:
                st.markdown(f"**{b['title']}** (💰 {b['points']})")
                cp, cr = st.columns(2)
                with cp:
                    if st.button("通过", key=f"ok_{b['id']}", type="primary"): 
                        b["status"] = "closed"
                        add_log(b["target"], f"完成悬赏：{b['title']}", b["points"])
                        st.rerun()
                with cr:
                    if st.button("驳回", key=f"no_{b['id']}"): 
                        b["status"] = "open"
                        save_data(data)
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # --- Tab 4 商店 ---
    with tab4:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🛍️ 兑换中心")
        cols = st.columns(3)
        for idx, (item, cost) in enumerate(SHOP_ITEMS.items()):
            with cols[idx % 3]:
                if st.button(f"{item}\n💰 {cost}"):
                    if item == "包夜券" and data["inventory"][current_uid].get("包夜券", 0) >= 1:
                        st.error("背包已有，先用完哦！")
                    elif data["points"][current_uid] < cost:
                        st.error("余额不足")
                    elif add_log(current_uid, f"兑换了 {item}", -cost):
                        data["inventory"][current_uid][item] = data["inventory"][current_uid].get(item, 0) + 1
                        save_data(data)
                        st.success("兑换成功")
                        st.rerun()
        st.divider()
        col_c1, col_c2 = st.columns([2, 1])
        with col_c1: c_item = st.text_input("自定义愿望：", placeholder="比如：购买商品")
        with col_c2: c_cost = st.number_input("定价：", min_value=1, value=50)
        if st.button("兑换自定义愿望", type="primary") and c_item:
            if data["points"][current_uid] >= c_cost:
                add_log(current_uid, f"兑换自定义：{c_item}", -c_cost)
                data["inventory"][current_uid][c_item] = data["inventory"][current_uid].get(c_item, 0) + 1
                save_data(data)
                st.success("已收入背包")
                st.rerun()
            else:
                st.error("余额不足")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Tab 5 背包 ---
    with tab5:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        avail = {k: v for k, v in data["inventory"].get(current_uid, {}).items() if v > 0}
        if not avail: st.info("背包空空如也，快去兑换吧！")
        for item, count in avail.items():
            c1, c2 = st.columns([4, 1])
            with c1: st.markdown(f"#### 🎟️ {item} <span style='font-size:0.9rem; color:gray;'>(拥有 {count} 张)</span>", unsafe_allow_html=True)
            with c2:
                if st.button("使用", key=f"u_{item}"):
                    if item == "包夜券":
                        cur_m = get_china_now().strftime('%Y-%m')
                        if data["usage_limits"][current_uid].get("包夜券") == cur_m:
                            st.error("🚨 本月包夜限额已用完！")
                            continue
                        data["usage_limits"][current_uid]["包夜券"] = cur_m
                    data["inventory"][current_uid][item] -= 1
                    add_log(current_uid, f"使用了 {item}", 0)
                    st.success("使用成功！")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Tab 6 设置 ---
    with tab6:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        with st.form("set_f"):
            n_name = st.text_input("昵称 / Display Name", value=current_name)
            n_log = st.text_input("登录账号 / Login ID", value=data["accounts"][current_uid]["login_id"])
            n_pwd = st.text_input("密码 / Password", value=data["accounts"][current_uid]["password"], type="password")
            if st.form_submit_button("保存设置", type="primary"):
                if any(uid != current_uid and info["login_id"] == n_log for uid, info in data["accounts"].items()):
                    st.error("账号名冲突！")
                else:
                    data["accounts"][current_uid].update({"display_name": n_name, "login_id": n_log, "password": n_pwd})
                    save_data(data)
                    st.success("已生效！")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="glass-card" style="border: 1.5px solid rgba(255, 117, 140, 0.3); text-align: center;">', unsafe_allow_html=True)
        st.caption("📱 移动端快捷控制")
        if st.button("🚪 退出当前账号", key="mobile_logout_btn"):
            execute_logout()
        st.markdown('</div>', unsafe_allow_html=True)

    # 全局足迹动态
    st.markdown("<h3 style='margin-top: 30px; color: #2c3e50;'>📜 我们的足迹</h3>", unsafe_allow_html=True)
    for log in data["logs"][:20]:
        st.markdown(f'<div class="log-bubble">{log}</div>', unsafe_allow_html=True)

# =====================================================
# 🚀 启动秒级实时连线中心
# =====================================================
render_live_system()
