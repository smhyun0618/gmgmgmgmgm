
import streamlit as st
import streamlit.components.v1 as components
import random
import json

st.set_page_config(
    page_title="RETRO STRIKE",
    page_icon="🎮",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: #080b12;
    color: white;
}
h1 {
    color: #42ff9e;
    text-align: center;
    font-family: monospace;
}
</style>
""", unsafe_allow_html=True)

st.title("⚔️ RETRO STRIKE")
st.caption("RETRO FPS MISSION | WASD MOVE | SPACE SHOOT")

# 적 종류
ENEMY_TYPES = [
    {
        "type": "alien",
        "name": "ALIEN",
        "color": "#39ff14",
        "hp": 1,
        "speed": 0.65,
        "size": 0.8
    },
    {
        "type": "robot",
        "name": "ROBOT",
        "color": "#ff3333",
        "hp": 3,
        "speed": 0.35,
        "size": 1.0
    },
    {
        "type": "ghost",
        "name": "GHOST",
        "color": "#bb66ff",
        "hp": 1,
        "speed": 1.0,
        "size": 0.7
    }
]

# Python 함수와 리스트 활용
def create_enemies(stage):
    enemies = []

    positions = [
        (3.5, 1.5),
        (5.5, 1.5),
        (8.5, 1.5),
        (3.5, 3.5),
        (8.5, 3.5),
        (3.5, 6.5),
        (8.5, 6.5),
        (5.5, 8.5),
        (8.5, 8.5)
    ]

    count = min(4 + stage * 2, len(positions))

    for i in range(count):
        enemy_type = random.choice(ENEMY_TYPES)
        x, y = positions[i]

        enemies.append({
            "type": enemy_type["type"],
            "name": enemy_type["name"],
            "color": enemy_type["color"],
            "hp": enemy_type["hp"],
            "maxHp": enemy_type["hp"],
            "speed": enemy_type["speed"],
            "size": enemy_type["size"],
            "x": x,
            "y": y
        })

    return enemies


initial_enemies = create_enemies(1)
enemy_json = json.dumps(initial_enemies)

html = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #05070c;
    color: white;
    font-family: monospace;
    overflow: hidden;
}

#hud {
    display: flex;
    justify-content: space-around;
    flex-wrap: wrap;
    gap: 8px;
    padding: 12px;
    background: #101722;
    color: #42ff9e;
    font-size: 16px;
}

#gameBox {
    position: relative;
    width: 100%;
}

canvas {
    display: block;
    width: 100%;
    background: black;
    image-rendering: pixelated;
    outline: none;
}

#help {
    text-align: center;
    padding: 10px;
    color: #42ff9e;
    background: #101722;
    font-size: 13px;
}

#overlay {
    position: absolute;
    inset: 0;
    background: rgba(0,0,0,0.9);
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    text-align: center;
    z-index: 10;
    padding: 20px;
}

#overlay h1 {
    color: #42ff9e;
    font-size: 36px;
}

#overlay p {
    line-height: 2;
    color: white;
}

#overlay button {
    background: #42ff9e;
    border: none;
    padding: 15px 30px;
    font-size: 18px;
    font-weight: bold;
    cursor: pointer;
}

</style>
</head>

<body>

<div id="hud">
    <span id="hp">HP: 100</span>
    <span id="ammo">AMMO: 20</span>
    <span id="score">SCORE: 0</span>
    <span id="stage">STAGE: 1</span>
    <span id="enemyCount">ENEMIES: 0</span>
</div>

<div id="gameBox">

<canvas id="game" width="800" height="450" tabindex="0"></canvas>

<div id="overlay">
    <h1>RETRO STRIKE</h1>
    <p>
        MISSION START<br>
        적을 모두 처치하고 다음 구역으로 이동하라.<br><br>
        WASD : 이동<br>
        ← → : 시야 회전<br>
        SPACE : 발사
    </p>
    <button id="startButton">START MISSION</button>
</div>

</div>

<div id="help">
    W/S 이동 · A/D 좌우 이동 · ←/→ 회전 · SPACE 발사 · R 재장전
</div>

<script>

const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

const W = canvas.width;
const H = canvas.height;

const initialEnemyData = __ENEMIES__;

const map = [
    "############",
    "#..........#",
    "#..##......#",
    "#..........#",
    "#.....#....#",
    "#.....#....#",
    "#..........#",
    "#..##......#",
    "#..........#",
    "############"
];

const FOV = Math.PI / 3;
const RAYS = 400;
const MAX_DEPTH = 12;

let player;
let enemies = [];
let keys = {};

let score = 0;
let stage = 1;
let hp = 100;
let ammo = 20;
let maxAmmo = 20;

let gameRunning = false;
let gameOver = false;
let stageCleared = false;

let muzzleFlash = 0;
let bulletFrames = 0;
let hitMarker = 0;
let damageFlash = 0;
let shootCooldown = 0;
let reloadTime = 0;

let lastTime = 0;
let animationId = null;
let zBuffer = [];

function startGame() {
    if (animationId) {
        cancelAnimationFrame(animationId);
    }

    player = {
        x: 1.5,
        y: 1.5,
        angle: 0
    };

    enemies = initialEnemyData.map(e => ({
        ...e,
        lastAttack: 0
    }));

    score = 0;
    stage = 1;
    hp = 100;
    ammo = maxAmmo;

    gameOver = false;
    stageCleared = false;
    gameRunning = true;

    muzzleFlash = 0;
    bulletFrames = 0;
    hitMarker = 0;
    damageFlash = 0;
    shootCooldown = 0;
    reloadTime = 0;
    lastTime = 0;

    keys = {};

    document.getElementById("overlay").style.display = "none";

    canvas.focus();

    updateHUD();
    animationId = requestAnimationFrame(loop);
}

document.getElementById("startButton").addEventListener(
    "click",
    startGame
);

function isWall(x, y) {
    const mx = Math.floor(x);
    const my = Math.floor(y);

    if (
        my < 0 ||
        my >= map.length ||
        mx < 0 ||
        mx >= map[0].length
    ) {
        return true;
    }

    return map[my][mx] === "#";
}

function canMove(x, y) {
    const r = 0.18;

    return (
        !isWall(x-r, y-r) &&
        !isWall(x+r, y-r) &&
        !isWall(x-r, y+r) &&
        !isWall(x+r, y+r)
    );
}

function normalizeAngle(a) {
    while (a > Math.PI) a -= Math.PI * 2;
    while (a < -Math.PI) a += Math.PI * 2;

    return a;
}

function castRay(angle) {
    for (let d = 0.02; d < MAX_DEPTH; d += 0.025) {
        const x = player.x + Math.cos(angle) * d;
        const y = player.y + Math.sin(angle) * d;

        if (isWall(x, y)) {
            return d;
        }
    }

    return MAX_DEPTH;
}

// 플레이어 이동
function movePlayer(dt) {
    const moveSpeed = 2.5 * dt;
    const turnSpeed = 2.0 * dt;

    if (keys["arrowleft"]) {
        player.angle -= turnSpeed;
    }

    if (keys["arrowright"]) {
        player.angle += turnSpeed;
    }

    const forward =
        (keys["w"] ? 1 : 0) -
        (keys["s"] ? 1 : 0);

    const side =
        (keys["d"] ? 1 : 0) -
        (keys["a"] ? 1 : 0);

    const dx = (
        Math.cos(player.angle) * forward -
        Math.sin(player.angle) * side
    ) * moveSpeed;

    const dy = (
        Math.sin(player.angle) * forward +
        Math.cos(player.angle) * side
    ) * moveSpeed;

    if (canMove(player.x + dx, player.y)) {
        player.x += dx;
    }

    if (canMove(player.x, player.y + dy)) {
        player.y += dy;
    }
}

// 배경과 벽
function drawWorld() {
    const sky = ctx.createLinearGradient(0, 0, 0, H/2);

    sky.addColorStop(0, "#080d20");
    sky.addColorStop(1, "#28334a");

    ctx.fillStyle = sky;
    ctx.fillRect(0, 0, W, H/2);

    const floor = ctx.createLinearGradient(0, H/2, 0, H);

    floor.addColorStop(0, "#24232b");
    floor.addColorStop(1, "#090909");

    ctx.fillStyle = floor;
    ctx.fillRect(0, H/2, W, H/2);

    zBuffer = [];

    for (let i = 0; i < RAYS; i++) {
        const angle =
            player.angle - FOV/2 + FOV * i/RAYS;

        const dist = castRay(angle);

        const corrected =
            dist * Math.cos(angle - player.angle);

        zBuffer[i] = corrected;

        const wallHeight =
            Math.min(H, H / Math.max(0.1, corrected));

        const y = (H-wallHeight)/2;

        const shade = Math.max(30, 210-corrected*20);

        ctx.fillStyle =
            `rgb(${shade*0.55},${shade*0.65},${shade})`;

        ctx.fillRect(
            i * W/RAYS,
            y,
            W/RAYS + 1,
            wallHeight
        );

        if (i % 8 === 0) {
            ctx.fillStyle = "rgba(0,0,0,0.15)";
            ctx.fillRect(
                i * W/RAYS,
                y,
                1,
                wallHeight
            );
        }
    }
}

// 적의 생김새
function drawEnemyShape(enemy, x, y, size) {
    ctx.save();
    ctx.translate(x, y);
    ctx.scale(size/55, size/55);

    if (enemy.type === "alien") {
        // 초록 외계인
        ctx.fillStyle = "#39ff14";

        ctx.beginPath();
        ctx.ellipse(0, -12, 22, 28, 0, 0, Math.PI*2);
        ctx.fill();

        ctx.fillStyle = "#07120a";
        ctx.fillRect(-14, -20, 10, 13);
        ctx.fillRect(5, -20, 10, 13);

        ctx.fillStyle = "white";
        ctx.fillRect(-12, -18, 5, 8);
        ctx.fillRect(7, -18, 5, 8);

        ctx.fillStyle = "#0a2c0c";
        ctx.fillRect(-12, 10, 24, 8);
        ctx.fillRect(-20, 20, 12, 20);
        ctx.fillRect(8, 20, 12, 20);

    } else if (enemy.type === "robot") {
        // 빨간 로봇
        ctx.fillStyle = "#555b65";
        ctx.fillRect(-22, -35, 44, 60);

        ctx.fillStyle = "#ff3333";
        ctx.fillRect(-19, -38, 38, 24);

        ctx.fillRect(-29, -5, 12, 35);
        ctx.fillRect(17, -5, 12, 35);

        ctx.fillStyle = "#fff3a0";
        ctx.fillRect(-13, -31, 9, 8);
        ctx.fillRect(4, -31, 9, 8);

        ctx.fillStyle = "#171717";
        ctx.fillRect(-12, 3, 24, 8);
        ctx.fillRect(-17, 27, 13, 17);
        ctx.fillRect(4, 27, 13, 17);

    } else {
        // 보라색 유령
        ctx.fillStyle = "#bb66ff";

        ctx.beginPath();
        ctx.arc(0, -10, 23, Math.PI, 0);
        ctx.lineTo(23, 25);
        ctx.lineTo(10, 15);
        ctx.lineTo(0, 25);
        ctx.lineTo(-10, 15);
        ctx.lineTo(-23, 25);
        ctx.closePath();
        ctx.fill();

        ctx.fillStyle = "white";
        ctx.fillRect(-13, -15, 8, 11);
        ctx.fillRect(5, -15, 8, 11);

        ctx.fillStyle = "#222";
        ctx.fillRect(-10, -12, 4, 6);
        ctx.fillRect(7, -12, 4, 6);
    }

    ctx.restore();
}

// 적 화면에 표시
function drawEnemies() {
    const visible = [];

    for (const enemy of enemies) {
        const dx = enemy.x-player.x;
        const dy = enemy.y-player.y;

        const dist = Math.hypot(dx, dy);

        const angle = normalizeAngle(
            Math.atan2(dy, dx)-player.angle
        );

        if (Math.abs(angle) < FOV/2 + 0.2) {
            visible.push({
                enemy,
                dist,
                angle
            });
        }
    }

    visible.sort((a,b) => b.dist-a.dist);

    for (const item of visible) {
        const enemy = item.enemy;
        const dist = item.dist;
        const angle = item.angle;

        const screenX = (0.5+angle/FOV)*W;

        const size = Math.min(
            220,
            H/dist*enemy.size
        );

        const screenY = H/2+size*0.15;

        const rayIndex = Math.floor(screenX/W*RAYS);

        if (rayIndex < 0 || rayIndex >= RAYS) continue;
        if (dist > zBuffer[rayIndex]+0.1) continue;

        drawEnemyShape(
            enemy,
            screenX,
            screenY,
            size
        );

        // 체력 표시
        const barWidth = size*0.7;
        const barX = screenX-barWidth/2;
        const barY = screenY-size*0.75;

        ctx.fillStyle = "#222";
        ctx.fillRect(barX, barY, barWidth, 5);

        ctx.fillStyle = "#ff4444";

        ctx.fillRect(
            barX,
            barY,
            barWidth*enemy.hp/enemy.maxHp,
            5
        );
    }
}

// 총 모양과 발사 애니메이션
function drawGun() {
    const cx = W/2;

    const recoil = muzzleFlash > 0 ? 8 : 0;

    ctx.fillStyle = "#151a22";
    ctx.fillRect(cx-45, H-105+recoil, 90, 105);

    ctx.fillStyle = "#424b5c";
    ctx.fillRect(cx-28, H-135+recoil, 56, 70);

    ctx.fillStyle = "#778397";
    ctx.fillRect(cx-14, H-150+recoil, 28, 25);

    ctx.fillStyle = "#0b0e14";
    ctx.fillRect(cx-9, H-151+recoil, 18, 16);

    // 총구 섬광
    if (muzzleFlash > 0) {
        ctx.fillStyle =
            muzzleFlash % 2 === 0 ? "#fff36a" : "#ff7b19";

        ctx.beginPath();
        ctx.moveTo(cx, H-160+recoil);
        ctx.lineTo(cx-35, H-205);
        ctx.lineTo(cx-10, H-195);
        ctx.lineTo(cx, H-235);
        ctx.lineTo(cx+10, H-195);
        ctx.lineTo(cx+35, H-205);
        ctx.closePath();
        ctx.fill();
    }

    // 탄환 궤적
    if (bulletFrames > 0) {
        ctx.strokeStyle = "#fff46a";
        ctx.lineWidth = 5;

        ctx.beginPath();
        ctx.moveTo(cx, H-160+recoil);
        ctx.lineTo(cx, H/2+20);
        ctx.stroke();

        ctx.fillStyle = "#ffffff";
        ctx.beginPath();
        ctx.arc(cx, H/2+20, 4, 0, Math.PI*2);
        ctx.fill();
    }
}

// 조준점
function drawCrosshair() {
    const cx = W/2;
    const cy = H/2;

    ctx.strokeStyle = "white";
    ctx.lineWidth = 2;

    ctx.beginPath();

    ctx.moveTo(cx-10, cy);
    ctx.lineTo(cx-3, cy);

    ctx.moveTo(cx+3, cy);
    ctx.lineTo(cx+10, cy);

    ctx.moveTo(cx, cy-10);
    ctx.lineTo(cx, cy-3);

    ctx.moveTo(cx, cy+3);
    ctx.lineTo(cx, cy+10);

    ctx.stroke();

    if (hitMarker > 0) {
        ctx.strokeStyle = "#ff4444";
        ctx.lineWidth = 4;

        ctx.beginPath();

        ctx.moveTo(cx-14, cy-14);
        ctx.lineTo(cx+14, cy+14);

        ctx.moveTo(cx+14, cy-14);
        ctx.lineTo(cx-14, cy+14);

        ctx.stroke();
    }
}

// 조준한 적 확인
function getTargetEnemy() {
    let target = null;
    let closest = Infinity;

    for (const enemy of enemies) {
        const dx = enemy.x-player.x;
        const dy = enemy.y-player.y;

        const dist = Math.hypot(dx, dy);

        const angle = normalizeAngle(
            Math.atan2(dy, dx)-player.angle
        );

        if (Math.abs(angle) < 0.10 && dist < closest) {
            const wallDistance = castRay(player.angle);

            if (wallDistance > dist-0.2) {
                target = enemy;
                closest = dist;
            }
        }
    }

    return target;
}

// 총 발사
function shoot() {
    if (!gameRunning || gameOver || stageCleared) return;
    if (ammo <= 0 || shootCooldown > 0) return;

    ammo--;

    shootCooldown = 0.25;
    muzzleFlash = 7;
    bulletFrames = 5;

    const target = getTargetEnemy();

    if (target) {
        target.hp--;
        hitMarker = 8;

        if (target.hp <= 0) {
            score += target.type === "robot" ? 200 : 100;

            enemies = enemies.filter(
                e => e.hp > 0
            );
        }
    }

    updateHUD();
}

// 재장전
function reload() {
    if (ammo === maxAmmo || reloadTime > 0) return;

    reloadTime = 1.2;

    setTimeout(() => {
        if (gameRunning && !gameOver) {
            ammo = maxAmmo;
            reloadTime = 0;
            updateHUD();
        }
    }, 1200);
}

// 적 생성
function makeEnemies(count) {
    const types = [
        {
            type: "alien",
            name: "ALIEN",
            color: "#39ff14",
            hp: 1,
            maxHp: 1,
            speed: 0.65,
            size: 0.8
        },
        {
            type: "robot",
            name: "ROBOT",
            color: "#ff3333",
            hp: 3,
            maxHp: 3,
            speed: 0.35,
            size: 1.0
        },
        {
            type: "ghost",
            name: "GHOST",
            color: "#bb66ff",
            hp: 1,
            maxHp: 1,
            speed: 1.0,
            size: 0.7
        }
    ];

    const positions = [
        [3.5,1.5],
        [5.5,1.5],
        [8.5,1.5],
        [3.5,3.5],
        [8.5,3.5],
        [3.5,6.5],
        [8.5,6.5],
        [5.5,8.5],
        [8.5,8.5]
    ];

    const result = [];

    for (let i=0; i<count; i++) {
        const pos = positions[i % positions.length];
        const type = types[
            Math.floor(Math.random()*types.length)
        ];

        result.push({
            ...type,
            x: pos[0],
            y: pos[1],
            lastAttack: 0
        });
    }

    return result;
}

// 적 움직임
function updateEnemies(dt) {
    for (const enemy of enemies) {
        const dx = player.x-enemy.x;
        const dy = player.y-enemy.y;

        const dist = Math.hypot(dx,dy);

        if (dist > 0.7) {
            const speed =
                enemy.speed*(1+stage*0.08);

            const nx =
                enemy.x+(dx/dist)*speed*dt;

            const ny =
                enemy.y+(dy/dist)*speed*dt;

            if (!isWall(nx,enemy.y)) {
                enemy.x = nx;
            }

            if (!isWall(enemy.x,ny)) {
                enemy.y = ny;
            }

        } else {
            const now = performance.now();

            if (
                !enemy.lastAttack ||
                now-enemy.lastAttack > 1000
            ) {
                hp -= 8;
                damageFlash = 8;
                enemy.lastAttack = now;
                updateHUD();
            }
        }
    }
}

// 화면 정보
function updateHUD() {
    document.getElementById("hp").textContent =
        "HP: "+Math.max(0,hp);

    document.getElementById("ammo").textContent =
        "AMMO: "+ammo;

    document.getElementById("score").textContent =
        "SCORE: "+score;

    document.getElementById("stage").textContent =
        "STAGE: "+stage;

    document.getElementById("enemyCount").textContent =
        "ENEMIES: "+enemies.length;
}

// 화면 메시지
function showOverlay(title,message,buttonText,callback) {
    const overlay = document.getElementById("overlay");

    overlay.innerHTML = `
        <h1>${title}</h1>
        <p>${message}</p>
        <button id="overlayButton">${buttonText}</button>
    `;

    overlay.style.display = "flex";

    document.getElementById("overlayButton").onclick =
        callback;
}

// 다음 스테이지
function nextStage() {
    stage++;

    player.x = 1.5;
    player.y = 1.5;
    player.angle = 0;

    hp = Math.min(100,hp+20);
    ammo = maxAmmo;

    enemies = makeEnemies(
        Math.min(4+stage*2,9)
    );

    stageCleared = false;
    gameOver = false;
    gameRunning = true;

    lastTime = 0;

    updateHUD();

    canvas.focus();

    animationId = requestAnimationFrame(loop);
}

// 스테이지 클리어
function clearStage() {
    gameRunning = false;
    stageCleared = true;

    showOverlay(
        "STAGE CLEAR!",
        "모든 적을 처치했다!<br>현재 점수: "+score,
        "NEXT STAGE",
        nextStage
    );
}

// 게임 오버
function endGame() {
    gameRunning = false;
    gameOver = true;

    showOverlay(
        "MISSION FAILED",
        "최종 점수: "+score+
        "<br>도달 스테이지: "+stage,
        "RESTART",
        startGame
    );
}

// 효과 시간 감소
function updateEffects(dt) {
    if (muzzleFlash > 0) muzzleFlash--;
    if (bulletFrames > 0) bulletFrames--;
    if (hitMarker > 0) hitMarker--;
    if (damageFlash > 0) damageFlash--;

    if (shootCooldown > 0) {
        shootCooldown -= dt;
    }
}

// 화면 그리기
function render() {
    drawWorld();
    drawEnemies();
    drawCrosshair();
    drawGun();

    if (damageFlash > 0) {
        ctx.fillStyle = "rgba(255,0,0,0.22)";
        ctx.fillRect(0,0,W,H);
    }

    if (reloadTime > 0) {
        ctx.fillStyle = "#ffff66";
        ctx.font = "20px monospace";
        ctx.fillText(
            "RELOADING...",
            W/2-65,
            H-20
        );
    }
}

// 메인 게임 반복
function loop(timestamp) {
    if (!gameRunning) return;

    const dt = Math.min(
        (timestamp-(lastTime || timestamp))/1000,
        0.05
    );

    lastTime = timestamp;

    movePlayer(dt);
    updateEnemies(dt);
    updateEffects(dt);
    render();
    updateHUD();

    if (hp <= 0) {
        endGame();
        return;
    }

    if (enemies.length === 0) {
        clearStage();
        return;
    }

    animationId = requestAnimationFrame(loop);
}

// 키보드 입력
document.addEventListener("keydown", e => {
    const key = e.key.toLowerCase();

    if (
        ["w","a","s","d","arrowleft","arrowright"," "]
        .includes(key)
    ) {
        e.preventDefault();
    }

    keys[key] = true;

    if (key === " " && !e.repeat) {
        shoot();
    }

    if (key === "r" && !e.repeat) {
        reload();
    }
});

document.addEventListener("keyup", e => {
    keys[e.key.toLowerCase()] = false;
});

window.addEventListener("blur", () => {
    keys = {};
});

canvas.addEventListener("click", () => {
    canvas.focus();
});

updateHUD();

</script>
</body>
</html>
"""

html = html.replace("__ENEMIES__", enemy_json)

components.html(
    html,
    height=570,
    scrolling=False
)
