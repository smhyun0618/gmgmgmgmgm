import streamlit as st
import random
import time

st.set_page_config(
    page_title="TACTICAL STRIKE FPS",
    page_icon="🎯",
    layout="wide"
)

# =========================
# 게임 설정
# =========================

if "health" not in st.session_state:
    st.session_state.health = 100
    st.session_state.ammo = 30
    st.session_state.score = 0
    st.session_state.kills = 0
    st.session_state.wave = 1
    st.session_state.enemy_health = 100
    st.session_state.game_over = False
    st.session_state.reload = False
    st.session_state.log = ["작전 시작! 적을 제거하세요."]

# =========================
# 스타일
# =========================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #080d12, #101e25, #071016);
    color: #e5f4f2;
}
h1 {
    color: #00ffc3 !important;
    text-shadow: 0 0 15px #00ffc3;
}
h2, h3 {
    color: #b7fff0 !important;
}
[data-testid="stMetric"] {
    background: #14252b;
    border: 1px solid #00ffc355;
    border-radius: 12px;
    padding: 15px;
}
.stButton button {
    width: 100%;
    background: linear-gradient(90deg, #008f70, #00d6a5);
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: bold;
    min-height: 48px;
}
.stButton button:hover {
    background: #00ffc3;
    color: black;
    box-shadow: 0 0 20px #00ffc3;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 헤더
# =========================

st.title("🎯 TACTICAL STRIKE")
st.caption("ELITE FPS COMBAT SIMULATOR | VERSION 1.0")

if st.session_state.game_over:
    st.error("☠️ MISSION FAILED - 작전 실패")
    if st.button("🔄 다시 시작"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    st.stop()

# =========================
# 상태 표시
# =========================

c1, c2, c3, c4 = st.columns(4)

c1.metric("❤️ 체력", f"{st.session_state.health}%")
c2.metric("🔫 탄약", f"{st.session_state.ammo}/30")
c3.metric("💀 처치", st.session_state.kills)
c4.metric("🌊 웨이브", st.session_state.wave)

st.progress(st.session_state.health / 100)

st.divider()

# =========================
# 전장
# =========================

st.subheader("🏙️ BATTLEFIELD")

st.markdown("""
<div style="
background:linear-gradient(#182b34,#101820);
height:260px;
border:2px solid #00ffc355;
border-radius:15px;
display:flex;
flex-direction:column;
align-items:center;
justify-content:center;
position:relative;
overflow:hidden;
">
<div style="font-size:65px;">🏙️ 🌫️ 🏢</div>
<div style="font-size:50px;">🎯</div>
<div style="color:#00ffc3;font-size:20px;font-weight:bold;">
TACTICAL COMBAT ZONE
</div>
<div style="color:#8ba9a6;font-size:13px;">
ENEMY DETECTED
</div>
</div>
""", unsafe_allow_html=True)

st.subheader("👾 적군 정보")

st.write(f"적군 체력: {st.session_state.enemy_health}%")
st.progress(st.session_state.enemy_health / 100)

# =========================
# 게임 기능
# =========================

def attack():
    if st.session_state.ammo <= 0:
        st.session_state.log.insert(0, "⚠️ 탄약이 없습니다!")
        return

    st.session_state.ammo -= 1

    damage = random.randint(15, 35)
    st.session_state.enemy_health -= damage

    if st.session_state.enemy_health <= 0:
        st.session_state.enemy_health = 0
        st.session_state.kills += 1
        st.session_state.score += 100
        st.session_state.wave += 1
        st.session_state.enemy_health = random.randint(70, 130)
        st.session_state.ammo = min(30, st.session_state.ammo + 10)
        st.session_state.log.insert(0, "💀 적 처치! 다음 웨이브 시작!")
    else:
        st.session_state.log.insert(
            0, f"🎯 명중! {damage} 데미지!"
        )

    # 적의 반격
    if random.random() < 0.3:
        damage = random.randint(5, 15)
        st.session_state.health -= damage
        st.session_state.log.insert(
            0, f"💥 적의 공격! 체력 -{damage}"
        )

    if st.session_state.health <= 0:
        st.session_state.health = 0
        st.session_state.game_over = True


def reload_weapon():
    st.session_state.ammo = 30
    st.session_state.log.insert(0, "🔄 재장전 완료!")


def dodge():
    if random.random() < 0.75:
        st.session_state.log.insert(0, "💨 회피 성공!")
    else:
        damage = random.randint(5, 15)
        st.session_state.health -= damage
        st.session_state.log.insert(0, f"💥 회피 실패! 체력 -{damage}")

    if st.session_state.health <= 0:
        st.session_state.health = 0
        st.session_state.game_over = True


# =========================
# 조작 버튼
# =========================

st.subheader("🎮 COMBAT CONTROL")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔫 발사"):
        attack()
        st.rerun()

with col2:
    if st.button("🔄 재장전"):
        reload_weapon()
        st.rerun()

with col3:
    if st.button("💨 회피"):
        dodge()
        st.rerun()

# =========================
# 점수
# =========================

st.divider()

st.subheader("🏆 PLAYER SCORE")

st.markdown(f"""
<div style="
background:#14252b;
padding:20px;
border-radius:12px;
border:1px solid #00ffc355;
text-align:center;
">
<div style="color:#8ba9a6;">TOTAL SCORE</div>
<div style="font-size:42px;color:#00ffc3;font-weight:bold;">
{st.session_state.score:,}
</div>
</div>
""", unsafe_allow_html=True)

# =========================
# 전투 로그
# =========================

st.subheader("📡 COMBAT LOG")

for message in st.session_state.log[:8]:
    st.write(message)

# =========================
# 게임 종료
# =========================

st.divider()

if st.button("🏳️ 작전 포기"):
    st.session_state.game_over = True
    st.rerun()

st.caption("TACTICAL STRIKE © 2026 | TRAINING SIMULATOR")
