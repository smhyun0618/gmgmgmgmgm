
import streamlit as st
import random

# ==========================================
# RETRO STRIKE 2.0
# ==========================================

st.set_page_config(
    page_title="RETRO STRIKE 2.0",
    page_icon="🎮",
    layout="wide"
)

# ==========================================
# 1. 디자인 CSS
# ==========================================

st.markdown("""
<style>
.stApp {
    background: #080d18;
    color: #d9faff;
}
header {visibility: hidden;}

h1, h2, h3 {
    color: #54eaff !important;
    font-family: monospace;
}

div.stButton > button {
    background: #12283b;
    color: #61eaff;
    border: 1px solid #27c8e5;
    border-radius: 7px;
    font-weight: bold;
    min-height: 45px;
    transition: 0.15s;
}

div.stButton > button:hover {
    background: #176078;
    color: white;
    border-color: #a0faff;
}

.metric-box {
    background: linear-gradient(135deg,#102337,#172b42);
    border: 1px solid #2d9eae;
    border-radius: 9px;
    padding: 13px;
    text-align: center;
    margin-bottom: 8px;
}

.metric-label {
    color: #7bafc5;
    font-size: 12px;
}

.metric-value {
    color: #55efff;
    font-size: 27px;
    font-weight: bold;
    font-family: monospace;
}

.fps-screen {
    height: 350px;
    position: relative;
    overflow: hidden;
    border: 3px solid #2dd7ed;
    border-radius: 8px;
    background:
        linear-gradient(180deg,#10172e 0%,#26374a 62%,#101923 63%,#060a11 100%);
}

.fps-ceiling {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 60%;
    background: linear-gradient(#11172b,#26364a);
}

.fps-floor {
    position: absolute;
    bottom: 0;
    width: 100%;
    height: 38%;
    background: repeating-linear-gradient(
        0deg,#101923 0px,#101923 18px,#1a3440 19px
    );
    clip-path: polygon(35% 0,65% 0,100% 100%,0 100%);
}

.fps-tunnel {
    position: absolute;
    inset: 10% 13% 12%;
    border: 3px solid #26798b;
    box-shadow: 0 0 20px #12566c;
    clip-path: polygon(25% 0,75% 0,100% 100%,0 100%);
}

.fps-enemy {
    position: absolute;
    left: 50%;
    top: 43%;
    transform: translate(-50%,-50%);
    font-size: 85px;
    filter: drop-shadow(0 0 18px #00eaff);
    z-index: 4;
}

.fps-crosshair {
    position: absolute;
    left: 50%;
    top: 49%;
    color: #c9ffff;
    font-size: 25px;
    z-index: 5;
}

.fps-gun {
    position: absolute;
    bottom: -20px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 85px;
    z-index: 6;
    filter: drop-shadow(0 0 12px #00bfff);
}

.fps-info {
    position: absolute;
    top: 12px;
    left: 15px;
    z-index: 7;
    color: #71f6ff;
    font-family: monospace;
    font-size: 13px;
}

.map-cell {
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #142337;
    border: 1px solid #27445c;
    font-size: 16px;
}

.map-row {
    display: flex;
    justify-content: center;
}

.log-box {
    background: #101c2b;
    border-left: 3px solid #32cfe7;
    padding: 10px;
    margin: 5px 0;
    color: #b9d9e7;
    font-family: monospace;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. 게임 초기화
# ==========================================

def initialize():
    st.session_state.hp = 100
    st.session_state.armor = 50
    st.session_state.ammo = 20
    st.session_state.max_ammo = 20

    st.session_state.score = 0
    st.session_state.kills = 0
    st.session_state.stage = 1

    st.session_state.px = 4
    st.session_state.py = 4
    st.session_state.direction = 0

    st.session_state.enemies = []
    st.session_state.items = []

    st.session_state.started = True
    st.session_state.game_over = False
    st.session_state.message = "MISSION START!"
    st.session_state.log = ["SYSTEM ONLINE"]

    create_enemies()
    create_items()


# ==========================================
# 3. 적 생성
# ==========================================

def create_enemies():

    st.session_state.enemies = []

    count = 2 + st.session_state.stage

    enemy_types = [
        {"name": "SCOUT", "hp": 1, "damage": 5, "icon": "🤖"},
        {"name": "SOLDIER", "hp": 2, "damage": 10, "icon": "👾"},
        {"name": "ELITE", "hp": 3, "damage": 15, "icon": "💀"}
    ]

    for i in range(count):

        enemy = random.choice(enemy_types)

        x = random.randint(0, 8)
        y = random.randint(0, 8)

        attempts = 0

        while (
            (x, y) == (st.session_state.px, st.session_state.py)
            or any(
                e["x"] == x and e["y"] == y
                for e in st.session_state.enemies
            )
        ) and attempts < 100:

            x = random.randint(0, 8)
            y = random.randint(0, 8)
            attempts += 1

        if attempts < 100:
            st.session_state.enemies.append({
                "x": x,
                "y": y,
                "name": enemy["name"],
                "hp": enemy["hp"] + st.session_state.stage // 3,
                "damage": enemy["damage"],
                "icon": enemy["icon"]
            })


# ==========================================
# 4. 아이템 생성
# ==========================================

def create_items():

    st.session_state.items = []

    for i in range(3):

        x = random.randint(0, 8)
        y = random.randint(0, 8)

        item_type = random.choice([
            "MEDKIT", "AMMO", "ARMOR"
        ])

        st.session_state.items.append({
            "x": x,
            "y": y,
            "type": item_type
        })


# ==========================================
# 5. 방향 시스템
# ==========================================

directions = [
    (0, -1),
    (1, 0),
    (0, 1),
    (-1, 0)
]

direction_names = [
    "NORTH",
    "EAST",
    "SOUTH",
    "WEST"
]


def turn_left():

    st.session_state.direction = (
        st.session_state.direction - 1
    ) % 4

    enemy_turn()


def turn_right():

    st.session_state.direction = (
        st.session_state.direction + 1
    ) % 4

    enemy_turn()


# ==========================================
# 6. 아이템 획득
# ==========================================

def collect_item():

    px = st.session_state.px
    py = st.session_state.py

    for item in st.session_state.items[:]:

        if (item["x"], item["y"]) == (px, py):

            if item["type"] == "MEDKIT":
                st.session_state.hp = min(
                    100, st.session_state.hp + 30
                )
                st.session_state.message = "MEDKIT +30 HP"

            elif item["type"] == "AMMO":
                st.session_state.ammo += 10
                st.session_state.message = "AMMO +10"

            elif item["type"] == "ARMOR":
                st.session_state.armor = min(
                    100, st.session_state.armor + 25
                )
                st.session_state.message = "ARMOR +25"

            st.session_state.items.remove(item)


# ==========================================
# 7. 플레이어 이동
# ==========================================

def move_player(distance):

    if st.session_state.game_over:
        return

    dx, dy = directions[
        st.session_state.direction
    ]

    nx = st.session_state.px + dx * distance
    ny = st.session_state.py + dy * distance

    if 0 <= nx <= 8 and 0 <= ny <= 8:

        st.session_state.px = nx
        st.session_state.py = ny

        collect_item()

        enemy_turn()

    else:
        st.session_state.message = "BLOCKED!"


# ==========================================
# 8. 적 AI
# ==========================================

def enemy_turn():

    if st.session_state.game_over:
        return

    px = st.session_state.px
    py = st.session_state.py

    occupied = set()

    for enemy in st.session_state.enemies:

        x = enemy["x"]
        y = enemy["y"]

        distance = abs(px - x) + abs(py - y)

        if distance <= 1:

            damage = enemy["damage"]

            armor_damage = min(
                st.session_state.armor,
                damage
            )

            st.session_state.armor -= armor_damage

            remaining = damage - armor_damage

            st.session_state.hp -= remaining

            st.session_state.log.append(
                f"ENEMY ATTACK! -{damage} DAMAGE"
            )

        else:

            if random.random() < 0.7:

                if abs(px - x) > abs(py - y):
                    dx = 1 if px > x else -1
                    dy = 0
                else:
                    dx = 0
                    dy = 1 if py > y else -1

                if random.random() < 0.25:
                    dx, dy = random.choice(directions)

                nx = x + dx
                ny = y + dy

                if (
                    0 <= nx <= 8
                    and 0 <= ny <= 8
                    and (nx, ny) != (px, py)
                    and (nx, ny) not in occupied
                ):
                    x, y = nx, ny

        enemy["x"] = x
        enemy["y"] = y

        occupied.add((x, y))

    if st.session_state.hp <= 0:

        st.session_state.hp = 0
        st.session_state.game_over = True
        st.session_state.message = "MISSION FAILED!"


# ==========================================
# 9. 공격 시스템
# ==========================================

def shoot():

    if st.session_state.game_over:
        return

    if st.session_state.ammo <= 0:

        st.session_state.message = "OUT OF AMMO! RELOAD!"
        return

    st.session_state.ammo -= 1

    dx, dy = directions[
        st.session_state.direction
    ]

    px = st.session_state.px
    py = st.session_state.py

    target = None

    # 정면의 가장 가까운 적 탐색
    for distance in range(1, 7):

        tx = px + dx * distance
        ty = py + dy * distance

        for enemy in st.session_state.enemies:

            if enemy["x"] == tx and enemy["y"] == ty:
                target = enemy
                break

        if target is not None:
            break

    if target:

        target["hp"] -= 1

        if target["hp"] <= 0:

            st.session_state.enemies.remove(target)

            st.session_state.score += 100
            st.session_state.kills += 1

            st.session_state.message = (
                "TARGET DESTROYED! +100 SCORE"
            )

            st.session_state.log.append(
                "TARGET ELIMINATED!"
            )

        else:

            st.session_state.score += 25

            st.session_state.message = (
                "ENEMY HIT! -1 ENEMY HP"
            )

        if not st.session_state.enemies:
            st.session_state.message = "STAGE CLEAR!"

    else:

        st.session_state.message = "SHOT MISSED!"

    enemy_turn()


# ==========================================
# 10. 재장전
# ==========================================

def reload_weapon():

    if st.session_state.game_over:
        return

    need = (
        st.session_state.max_ammo
        - st.session_state.ammo
    )

    if need > 0:

        st.session_state.ammo += need

        st.session_state.message = "RELOADING COMPLETE!"

        enemy_turn()


# ==========================================
# 11. 다음 스테이지
# ==========================================

def next_stage():

    st.session_state.stage += 1

    st.session_state.hp = min(
        100, st.session_state.hp + 20
    )

    st.session_state.armor = min(
        100, st.session_state.armor + 10
    )

    st.session_state.ammo = st.session_state.max_ammo

    st.session_state.px = 4
    st.session_state.py = 4
    st.session_state.direction = 0

    create_enemies()
    create_items()

    st.session_state.message = "NEW STAGE START!"


# ==========================================
# 12. 화면에 보이는 적 탐색
# ==========================================

def find_visible_enemy():

    dx, dy = directions[
        st.session_state.direction
    ]

    px = st.session_state.px
    py = st.session_state.py

    for distance in range(1, 7):

        tx = px + dx * distance
        ty = py + dy * distance

        for enemy in st.session_state.enemies:

            if enemy["x"] == tx and enemy["y"] == ty:
                return enemy, distance

    return None, None


# ==========================================
# 13. 게임 타이틀
# ==========================================

st.markdown("""
# ⚡ RETRO STRIKE 2.0
### SPACE ARENA // SURVIVAL PROTOCOL

`SYSTEM ONLINE` | `MISSION: ELIMINATE ALL HOSTILES`
""")

st.markdown("---")


# ==========================================
# 14. 게임 시작 화면
# ==========================================

if "started" not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:

    st.markdown("""
    <div style="
    background:linear-gradient(120deg,#101b30,#173a4d);
    border:2px solid #38d9ed;
    border-radius:12px;
    padding:45px;
    text-align:center;
    ">
    <h1>⚡ RETRO STRIKE</h1>
    <h3>ENTER THE BATTLEFIELD</h3>
    <p>Destroy all hostile drones.</p>
    <p>Survive every stage.</p>
    <h2>MISSION START</h2>
    </div>
    """, unsafe_allow_html=True)

    if st.button("▶ START MISSION", use_container_width=True):
        initialize()
        st.rerun()

    st.stop()


# ==========================================
# 15. 게임 상태창
# ==========================================

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-box">
    <div class="metric-label">❤️ HEALTH</div>
    <div class="metric-value">{st.session_state.hp}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-box">
    <div class="metric-label">🛡️ ARMOR</div>
    <div class="metric-value">{st.session_state.armor}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-box">
    <div class="metric-label">🏆 SCORE</div>
    <div class="metric-value">{st.session_state.score}</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-box">
    <div class="metric-label">🚀 STAGE</div>
    <div class="metric-value">{st.session_state.stage}</div>
    </div>
    """, unsafe_allow_html=True)


st.progress(st.session_state.hp / 100)

st.caption(
    f"WEAPON: ENERGY RIFLE | "
    f"AMMO: {st.session_state.ammo} | "
    f"KILLS: {st.session_state.kills}"
)

st.markdown("---")


# ==========================================
# 16. FPS 시점 화면
# ==========================================

st.subheader("📡 FIRST PERSON VIEW")

enemy, distance = find_visible_enemy()

if enemy:

    enemy_view = f"""
    <div class="fps-enemy">{enemy['icon']}</div>
    <div style="
    position:absolute;
    top:68%;
    left:50%;
    transform:translateX(-50%);
    z-index:7;
    color:#ff5b67;
    font-weight:bold;
    text-align:center;
    ">
    {enemy['name']} | HP {enemy['hp']} | DISTANCE {distance}
    </div>
    """

else:

    enemy_view = """
    <div style="
    position:absolute;
    top:42%;
    left:50%;
    transform:translate(-50%,-50%);
    color:#54eaff;
    font-size:20px;
    z-index:4;
    text-align:center;
    ">
    SCANNING...
    </div>
    """

st.markdown(f"""
<div class="fps-screen">
    <div class="fps-ceiling"></div>
    <div class="fps-floor"></div>
    <div class="fps-tunnel"></div>

    <div class="fps-info">
        {direction_names[st.session_state.direction]}
        <br>
        HOSTILES: {len(st.session_state.enemies)}
    </div>

    {enemy_view}

    <div class="fps-crosshair">+</div>

    <div class="fps-gun">🔫</div>
</div>
""", unsafe_allow_html=True)

if enemy:
    st.error(f"⚠️ HOSTILE DETECTED: {enemy['name']}")
else:
    st.info("주변을 탐색하고 있습니다.")


# ==========================================
# 17. 컨트롤 패널
# ==========================================

st.markdown("---")
st.subheader("🎮 COMMAND CENTER")

left, center, right = st.columns(3)

with left:
    if st.button("↶ TURN LEFT", use_container_width=True):
        turn_left()
        st.rerun()

with center:
    if st.button("⬆ MOVE FORWARD", use_container_width=True):
        move_player(1)
        st.rerun()

with right:
    if st.button("TURN RIGHT ↷", use_container_width=True):
        turn_right()
        st.rerun()

left, center, right = st.columns(3)

with left:
    if st.button("⬇ MOVE BACK", use_container_width=True):
        move_player(-1)
        st.rerun()

with center:
    if st.button("⚡ FIRE", use_container_width=True):
        shoot()
        st.rerun()

with right:
    if st.button("🔄 RELOAD", use_container_width=True):
        reload_weapon()
        st.rerun()


# ==========================================
# 18. 미니맵
# ==========================================

st.markdown("---")
st.subheader("🗺️ TACTICAL RADAR")

grid = []

for y in range(9):

    row = []

    for x in range(9):

        symbol = "⬛"

        if (x, y) == (
            st.session_state.px,
            st.session_state.py
        ):
            symbol = "🟢"

        elif any(
            e["x"] == x and e["y"] == y
            for e in st.session_state.enemies
        ):
            symbol = "🔴"

        elif any(
            i["x"] == x and i["y"] == y
            for i in st.session_state.items
        ):
            symbol = "🟡"

        row.append(symbol)

    grid.append(row)

for row in grid:

    html = '<div class="map-row">'

    for cell in row:
        html += f'<div class="map-cell">{cell}</div>'

    html += '</div>'

    st.markdown(html, unsafe_allow_html=True)

st.caption("🟢 PLAYER | 🔴 ENEMY | 🟡 ITEM")


# ==========================================
# 19. 전투 기록
# ==========================================

st.markdown("---")
st.subheader("📋 MISSION LOG")

st.markdown(
    f'<div class="log-box">{st.session_state.message}</div>',
    unsafe_allow_html=True
)

for log in st.session_state.log[-5:]:
    st.markdown(
        f'<div class="log-box">{log}</div>',
        unsafe_allow_html=True
    )


# ==========================================
# 20. 스테이지 및 게임 종료
# ==========================================

if st.session_state.game_over:

    st.error("💀 MISSION FAILED")

    st.markdown(f"""
    ## FINAL RESULT

    - SCORE: {st.session_state.score}
    - TOTAL KILLS: {st.session_state.kills}
    - STAGE REACHED: {st.session_state.stage}
    """)

    if st.button("🔄 RESTART GAME", use_container_width=True):
        initialize()
        st.rerun()

elif len(st.session_state.enemies) == 0:

    st.success("🏆 STAGE CLEAR!")

    st.write(
        f"현재 스테이지 {st.session_state.stage} 클리어!"
    )

    if st.button("🚀 NEXT STAGE", use_container_width=True):
        next_stage()
        st.rerun()


# ==========================================
# 21. 게임 재시작
# ==========================================

st.markdown("---")

if st.button("⏹ RESET GAME", use_container_width=True):

    st.session_state.started = False
    st.rerun()

st.caption("RETRO STRIKE 2.0 | SURVIVAL SYSTEM")
