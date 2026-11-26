
import streamlit as st
import random

# -----------------------------
# 1. 기본 설정
# -----------------------------
st.set_page_config(
    page_title="RETRO STRIKE",
    page_icon="🎮",
    layout="wide"
)

# -----------------------------
# 2. 게임 데이터 초기화
# -----------------------------
def new_game():
    st.session_state.hp = 100
    st.session_state.score = 0
    st.session_state.stage = 1
    st.session_state.kills = 0
    st.session_state.direction = 0
    st.session_state.player_x = 4
    st.session_state.player_y = 4
    st.session_state.game_over = False
    st.session_state.enemies = []
    st.session_state.started = True
    create_enemies()

# 적 생성 함수
def create_enemies():
    st.session_state.enemies = []

    # 스테이지가 높아질수록 적 증가
    enemy_count = 2 + st.session_state.stage

    while len(st.session_state.enemies) < enemy_count:
        x = random.randint(0, 8)
        y = random.randint(0, 8)

        if (x, y) != (
            st.session_state.player_x,
            st.session_state.player_y
        ) and (x, y) not in st.session_state.enemies:
            st.session_state.enemies.append((x, y))

# -----------------------------
# 3. 방향 및 이동 함수
# -----------------------------
# 북쪽, 동쪽, 남쪽, 서쪽
directions = [
    (0, -1),
    (1, 0),
    (0, 1),
    (-1, 0)
]

def turn_left():
    st.session_state.direction = (
        st.session_state.direction - 1
    ) % 4

def turn_right():
    st.session_state.direction = (
        st.session_state.direction + 1
    ) % 4

def move_player(distance):
    dx, dy = directions[st.session_state.direction]

    new_x = st.session_state.player_x + dx * distance
    new_y = st.session_state.player_y + dy * distance

    if 0 <= new_x <= 8 and 0 <= new_y <= 8:
        st.session_state.player_x = new_x
        st.session_state.player_y = new_y

    enemy_turn()

# -----------------------------
# 4. 적의 행동
# -----------------------------
def enemy_turn():

    if st.session_state.game_over:
        return

    new_enemies = []

    for enemy in st.session_state.enemies:

        x, y = enemy

        # 플레이어와 인접하면 공격
        px = st.session_state.player_x
        py = st.session_state.player_y

        distance = abs(px - x) + abs(py - y)

        if distance <= 1:
            st.session_state.hp -= 10
            new_enemies.append(enemy)

        else:
            # 적이 무작위로 이동
            dx, dy = random.choice(directions)

            nx = x + dx
            ny = y + dy

            if (
                0 <= nx <= 8
                and 0 <= ny <= 8
                and (nx, ny) != (px, py)
                and (nx, ny) not in new_enemies
            ):
                new_enemies.append((nx, ny))
            else:
                new_enemies.append(enemy)

    st.session_state.enemies = new_enemies

    if st.session_state.hp <= 0:
        st.session_state.hp = 0
        st.session_state.game_over = True

# -----------------------------
# 5. 공격 함수
# -----------------------------
def shoot():

    if st.session_state.game_over:
        return

    dx, dy = directions[st.session_state.direction]

    px = st.session_state.player_x
    py = st.session_state.player_y

    target = None

    # 정면 최대 4칸까지 공격
    for distance in range(1, 5):

        tx = px + dx * distance
        ty = py + dy * distance

        if (tx, ty) in st.session_state.enemies:
            target = (tx, ty)
            break

    if target is not None:

        st.session_state.enemies.remove(target)
        st.session_state.score += 100
        st.session_state.kills += 1

        st.session_state.message = "🎯 TARGET DESTROYED! +100"

    else:
        st.session_state.message = "❌ MISS! TARGET NOT FOUND"

    enemy_turn()

# -----------------------------
# 6. 다음 스테이지
# -----------------------------
def next_stage():

    st.session_state.stage += 1
    st.session_state.hp = min(
        100,
        st.session_state.hp + 20
    )

    create_enemies()

    st.session_state.message = "🚀 NEXT STAGE START!"

# -----------------------------
# 7. 게임 제목
# -----------------------------
st.markdown("""
# 🎮 RETRO STRIKE
### ⚡ SPACE ARENA : FPS SURVIVAL
적 드론을 찾아 공격하고 모든 스테이지를 클리어하라!
""")

# -----------------------------
# 8. 게임 시작
# -----------------------------
if "started" not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    st.info("게임을 시작하려면 아래 버튼을 눌러 주세요.")

    if st.button("▶ START GAME", use_container_width=True):
        new_game()
        st.rerun()

    st.stop()

# -----------------------------
# 9. 상태 표시
# -----------------------------
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

col1.metric("❤️ HP", st.session_state.hp)
col2.metric("🏆 SCORE", st.session_state.score)
col3.metric("🚀 STAGE", st.session_state.stage)
col4.metric("🎯 KILLS", st.session_state.kills)

st.markdown("---")

# -----------------------------
# 10. 게임 화면
# -----------------------------
st.subheader("🖥️ FIRST PERSON VIEW")

# 방향에 따른 시야 표현
view_names = ["NORTH ⬆️", "EAST ➡️", "SOUTH ⬇️", "WEST ⬅️"]

st.markdown(
    f"**현재 방향: {view_names[st.session_state.direction]}**"
)

# 앞에 적이 있는지 확인
dx, dy = directions[st.session_state.direction]

px = st.session_state.player_x
py = st.session_state.player_y

visible_enemy = None

for distance in range(1, 5):
    check = (
        px + dx * distance,
        py + dy * distance
    )

    if check in st.session_state.enemies:
        visible_enemy = distance
        break

if visible_enemy is not None:
    st.error(f"⚠️ 적 발견! 정면 {visible_enemy}칸 거리에 적이 있습니다!")
else:
    st.success("주변을 탐색 중입니다. 적을 찾아보세요.")

# FPS 스타일 화면
if visible_enemy is not None:
    st.markdown("""
    <div style="
    background:linear-gradient(#101629,#273d50);
    border:3px solid #31d9ef;
    border-radius:10px;
    padding:45px;
    text-align:center;
    color:white;
    ">
    <h2>⚠️ ENEMY DETECTED</h2>
    <div style="font-size:90px;">🤖</div>
    <h3>HOSTILE DRONE</h3>
    <p>READY TO FIRE</p>
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="
    background:linear-gradient(#101629,#273d50);
    border:3px solid #31d9ef;
    border-radius:10px;
    padding:45px;
    text-align:center;
    color:white;
    ">
    <h2>SPACE ARENA</h2>
    <div style="font-size:90px;">🔭</div>
    <h3>SCANNING AREA...</h3>
    <p>SEARCHING FOR ENEMIES</p>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# 11. 조작 버튼
# -----------------------------
st.subheader("🎮 CONTROL PANEL")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⬅️ TURN LEFT", use_container_width=True):
        turn_left()
        st.rerun()

with col2:
    if st.button("⬆️ MOVE FORWARD", use_container_width=True):
        move_player(1)
        st.rerun()

with col3:
    if st.button("➡️ TURN RIGHT", use_container_width=True):
        turn_right()
        st.rerun()

col4, col5 = st.columns(2)

with col4:
    if st.button("⬇️ MOVE BACKWARD", use_container_width=True):
        move_player(-1)
        st.rerun()

with col5:
    if st.button("⚡ FIRE / SPACE", use_container_width=True):
        shoot()
        st.rerun()

# -----------------------------
# 12. 게임 결과
# -----------------------------
if "message" in st.session_state:
    st.info(st.session_state.message)

if st.session_state.game_over:

    st.error("💀 GAME OVER")

    st.write(f"최종 점수: {st.session_state.score}")
    st.write(f"처치한 적: {st.session_state.kills}")

    if st.button("🔄 RESTART GAME"):
        new_game()
        st.rerun()

elif len(st.session_state.enemies) == 0:

    st.success("🏆 STAGE CLEAR!")

    if st.button("NEXT STAGE 🚀"):
        next_stage()
        st.rerun()

# -----------------------------
# 13. 미니맵
# -----------------------------
st.markdown("---")
st.subheader("🗺️ RADAR MAP")

for y in range(9):

    line = ""

    for x in range(9):

        if (x, y) == (
            st.session_state.player_x,
            st.session_state.player_y
        ):
            line += "🟢 "

        elif (x, y) in st.session_state.enemies:
            line += "🔴 "

        else:
            line += "⬛ "

    st.markdown(line)

st.caption("🟢 PLAYER  🔴 ENEMY  ⬛ EMPTY")
