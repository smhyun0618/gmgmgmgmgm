
import streamlit as st
import streamlit.components.v1 as components
import json
import random

st.set_page_config(
    page_title="RETRO STRIKE",
    page_icon="🎮",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #080b12;
    color: white;
}
h1 {
    color: #42ff9e;
    text-align: center;
    font-family: monospace;
}
</style>
""", unsafe_allow_html=True)

st.title("⚔️ RETRO STRIKE 4.0")
st.caption("WASD 이동 | 방향키 시야 회전 | SPACE 발사")

# Python 리스트와 함수 활용
ENEMY_TYPES = [
    {
        "type": "alien",
        "name": "ALIEN",
        "color": "#39ff14",
        "hp": 1,
        "speed": 0.020,
        "size": 0.75
    },
    {
        "type": "robot",
        "name": "ROBOT",
        "color": "#ff3333",
        "hp": 3,
        "speed": 0.010,
        "size": 0.95
    },
    {
        "type": "ghost",
        "name": "GHOST",
        "color": "#bb66ff",
        "hp": 1,
        "speed": 0.038,
        "size": 0.65
    }
]

def create_enemies(stage):
    enemies = []
    count = 4 + stage * 2

    for i in range(count):
        enemy_type = random.choice(ENEMY_TYPES)

        enemies.append({
            "type": enemy_type["type"],
            "name": enemy_type["name"],
            "color": enemy_type["color"],
            "hp": enemy_type["hp"],
            "maxHp": enemy_type["hp"],
            "speed": enemy_type["speed"],
            "size": enemy_type["size"],
            "x": random.choice([3.5, 4.5, 6.5, 7.5]),
            "y": random.choice([3.5, 4.5, 5.5, 6.5])
        })

    return enemies


initial_enemies = create_enemies(1)
game_data = json.dumps(initial_enemies)

html = r"""
<!DOCTYPE html>
<html>
<head>
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
#gameBox {
    width: 100%;
    position: relative;
    background: black;
}
canvas {
    width: 100%;
    display: block;
    image-rendering: pixelated;
    outline: none;
}
#help {
    padding: 8px;
    background: #111827;
    text-align: center;
    color: #42ff9e;
    font-size: 13px;
}
#overlay {
    position: absolute;
    inset: 0;
    background: rgba(0,0,0,.88);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    text-align: center;
    z-index: 5;
}
#overlay h1 {
    color: #42ff9e;
    font-size: 36px;
}
#overlay p {
    color: white;
    line-height: 1.8;
}
#overlay button {
    background: #42ff9e;
    border: 0;
    padding: 13px 28px;
    font-weight: bold;
    cursor: pointer;
    font-size: 17px;
}
#hud {
    display: flex;
    justify-content: space-around;
    padding: 10px;
    background: #101722;
    color: #42ff9e;
    font-size: 15px;
    flex-wrap: wrap;
    gap: 8px;
}
</style>
</head>

<body>
<div id="gameBox">

<div id="hud">
    <span id="hp">HP: 100</span>
    <span id="ammo">AMMO: 20</span>
    <span id="score">SCORE: 0</span>
    <span id="stage">STAGE: 1</span>
    <span id="enemyCount">ENEMIES: 0</span>
</div>

<canvas id="game" width="800" height="450" tabindex="0"></canvas>

<div id="help">
    W/S 이동 · A/D 좌우 이동 · ←/→ 시야 회전 · SPACE 발사 · R 재장전
</div>

<div id="overlay">
    <h1>RETRO STRIKE</h1>
    <p>
        적을 모두 처치하고 다음 구역으로 이동하라.<br>
        WASD로 이동하고 SPACE로 발사하라.
    </p>
    <button id="startButton">START MISSION</button>
</div>

</div>

<script>
const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

const W = canvas.width;
const H = canvas.height;

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

const initialEnemyData = __INITIAL_ENEMIES__;

let player;
let enemies = [];
let keys = {};
let zBuffer = [];
let score = 0;
let stage = 1;
let hp = 100;
let ammo = 20;
let maxAmmo = 20;
let gameRunning = false;
let gameOver = false;
let stageCleared = false;

let muzzleFlash = 0;
let bulletEffect = 0;
let hitMarker = 0;
let hitEffect = 0;
let damageFlash = 0;
let shootCooldown = 0;
let reloadTime = 0;
let lastTime = 0;

const FOV = Math.PI / 3;
const RAYS = 400;
const MAX_DEPTH = 12;

function startGame() {
    player = {
        x: 1.5,
        y: 1.5,
        angle: 0
    };

    enemies = initialEnemyData.map(e => ({...e}));
    score = 0;
    stage = 1;
    hp = 100;
    ammo = maxAmmo;
    gameOver = false;
    stageCleared = false;
    gameRunning = true;

    document.getElementById("overlay").style.display = "none";
    canvas.focus();

    updateHUD();
    requestAnimationFrame(loop);
}

document.getElementById("startButton").addEventListener("click", startGame);

function isWall(x, y) {
    const mx = Math.floor(x);
    const my = Math.floor(y);

    if (my < 0 || my >= map.length || mx < 0 || mx >= map[0].length) {
        return true;
    }

    return map[my][mx] === "#";
}

function canMove(x, y) {
    const r = 0.20;

    return !isWall(x-r, y-r) &&
           !isWall(x+r, y-r) &&
           !isWall(x-r, y+r) &&
           !isWall(x+r, y+r);
}

function normalizeAngle(a) {
    while (a > Math.PI) a -= Math.PI * 2;
    while (a < -Math.PI) a += Math.PI * 2;
    return a;
}

function castRay(angle) {
    const step = 0.025;

    for (let d = 0.02; d < MAX_DEPTH; d += step) {
        const x = player.x + Math.cos(angle) * d;
        const y = player.y + Math.sin(angle) * d;

        if (isWall(x, y)) {
            return d;
        }
    }

    return MAX_DEPTH;
}

function movePlayer(dt) {
    const moveSpeed = 2.5 * dt;
    const turnSpeed = 2.0 * dt;

    if (keys["ArrowLeft"]) player.angle -= turnSpeed;
    if (keys["ArrowRight"]) player.angle += turnSpeed;

    const forward = (keys["w"] ? 1 : 0) - (keys["s"] ? 1 : 0);
    const side = (keys["d"] ? 1 : 0) - (keys["a"] ? 1 : 0);

    const dx = (
        Math.cos(player.angle) * forward -
        Math.sin(player.angle) * side
    ) * moveSpeed;

    const dy = (
        Math.sin(player.angle) * forward +
        Math.cos(player.angle) * side
    ) * moveSpeed;

    if (canMove(player.x + dx, player.y)) player.x += dx;
    if (canMove(player.x, player.y + dy)) player.y += dy;
}

function drawWorld() {
    // 하늘
    const sky = ctx.createLinearGradient(0, 0, 0, H/2);
    sky.addColorStop(0, "#080d20");
    sky.addColorStop(1, "#28334a");
    ctx.fillStyle = sky;
    ctx.fillRect(0, 0, W, H/2);

    // 바닥
    const floor = ctx.createLinearGradient(0, H/2, 0, H);
    floor.addColorStop(0, "#24232b");
    floor.addColorStop(1, "#090909");
    ctx.fillStyle = floor;
    ctx.fillRect(0, H/2, W, H/2);

    zBuffer = [];

    for (let i = 0; i < RAYS; i++) {
        const rayAngle = player.angle - FOV/2 + FOV * i/RAYS;
        const dist = castRay(rayAngle);
        const corrected = dist * Math.cos(rayAngle - player.angle);

        zBuffer[i] = corrected;

        const wallHeight = Math.min(H, H / Math.max(0.1, corrected));
        const y = (H - wallHeight) / 2;

        const shade = Math.max(35, 210 - corrected * 20);

        ctx.fillStyle = `rgb(${shade*.55},${shade*.65},${shade})`;
        ctx.fillRect(i * W/RAYS, y, W/RAYS + 1, wallHeight);

        // 벽의 세로 줄무늬
        if (i % 8 === 0) {
            ctx.fillStyle = "rgba(0,0,0,0.12)";
            ctx.fillRect(i * W/RAYS, y, 1, wallHeight);
        }
    }
}

function enemySprite(enemy, x, y, size) {
    const color = enemy.color;

    ctx.save();
    ctx.translate(x, y);
    ctx.scale(size, size);

    if (enemy.type === "alien") {
        // 외계인
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.ellipse(0, -12, 22, 28, 0, 0, Math.PI*2);
        ctx.fill();

        ctx.fillStyle = "#07120a";
        ctx.fillRect(-14, -19, 9, 12);
        ctx.fillRect(5, -19, 9, 12);

        ctx.fillStyle = "white";
        ctx.fillRect(-12, -17, 5, 7);
        ctx.fillRect(7, -17, 5, 7);

        ctx.fillStyle = "#0a2c0c";
        ctx.fillRect(-12, 5, 24, 8);
        ctx.fillRect(-20, 20, 12, 20);
        ctx.fillRect(8, 20, 12, 20);

    } else if (enemy.type === "robot") {
        // 로봇
        ctx.fillStyle = "#555b65";
        ctx.fillRect(-22, -35, 44, 58);

        ctx.fillStyle = color;
        ctx.fillRect(-19, -38, 38, 24);
        ctx.fillRect(-29, -5, 12, 35);
        ctx.fillRect(17, -5, 12, 35);

        ctx.fillStyle = "#fff3a0";
        ctx.fillRect(-13, -31, 9, 8);
        ctx.fillRect(4, -31, 9, 8);

        ctx.fillStyle = "#171717";
        ctx.fillRect(-12, 2, 24, 8);
        ctx.fillRect(-17, 27, 13, 17);
        ctx.fillRect(4, 27, 13, 17);

    } else {
        // 유령
        ctx.fillStyle = color;
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

function drawEnemies() {
    const visible = [];

    for (const enemy of enemies) {
        const dx = enemy.x - player.x;
        const dy = enemy.y - player.y;
        const dist = Math.hypot(dx, dy);
        const angle = normalizeAngle(Math.atan2(dy, dx) - player.angle);

        if (Math.abs(angle) < FOV/2 + 0.2 && dist > 0.1) {
            visible.push({enemy, dist, angle});
        }
    }

    visible.sort((a,b) => b.dist - a.dist);

    for (const item of visible) {
        const enemy = item.enemy;
        const dist = item.dist;
        const angle = item.angle;

        const screenX = (0.5 + angle/FOV) * W;
        const size = Math.min(220, H / dist * enemy.size);
        const screenY = H/2 + size * 0.15;

        const rayIndex = Math.floor(screenX / W * RAYS);

        if (rayIndex < 0 || rayIndex >= RAYS) continue;
        if (dist > zBuffer[rayIndex] + 0.1) continue;

        enemySprite(enemy, screenX, screenY, size/55);

        // 적 체력 표시
        const barWidth = size * 0.7;
        const barX = screenX - barWidth/2;
        const barY = screenY - size * 0.75;

        ctx.fillStyle = "#222";
        ctx.fillRect(barX, barY, barWidth, 5);

        ctx.fillStyle = "#ff4444";
        ctx.fillRect(
            barX,
            barY,
            barWidth * enemy.hp/enemy.maxHp,
            5
        );
    }
}

function drawGun() {
    const cx = W/2;

    // 총 모양
    ctx.fillStyle = "#151a22";
    ctx.fillRect(cx-45, H-105, 90, 105);

    ctx.fillStyle = "#424b5c";
    ctx.fillRect(cx-28, H-135, 56, 70);

    ctx.fillStyle = "#778397";
    ctx.fillRect(cx-14, H-150, 28, 25);

    ctx.fillStyle = "#0b0e14";
    ctx.fillRect(cx-9, H-151, 18, 16);

    // 발사 반동
    if (muzzleFlash > 0) {
        const flicker = muzzleFlash % 2 === 0;

        ctx.fillStyle = flicker ? "#fff36a" : "#ff7b19";
        ctx.beginPath();
        ctx.moveTo(cx, H-160);
        ctx.lineTo(cx-35, H-205);
        ctx.lineTo(cx-10, H-195);
        ctx.lineTo(cx, H-235);
        ctx.lineTo(cx+10, H-195);
        ctx.lineTo(cx+35, H-205);
        ctx.closePath();
        ctx.fill();
    }

    // 총알이 앞으로 날아가는 선
    if (bulletEffect > 0) {
        ctx.strokeStyle = "#fff46a";
        ctx.lineWidth = 5;
        ctx.beginPath();
        ctx.moveTo(cx, H-160);
        ctx.lineTo(cx, H/2+20);
        ctx.stroke();
    }
}

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

function getTargetEnemy() {
    let target = null;
    let closest = Infinity;

    for (const enemy of enemies) {
        const dx = enemy.x - player.x;
        const dy = enemy.y - player.y;
        const dist = Math.hypot(dx, dy);
        const angle = normalizeAngle(
            Math.atan2(dy, dx) - player.angle
        );

        if (Math.abs(angle) < 0.09 && dist < closest) {
            const wallDistance = castRay(player.angle);

            if (wallDistance > dist - 0.2) {
                target = enemy;
                closest = dist;
            }
        }
    }

    return target;
}

function shoot() {
    if (!gameRunning || gameOver || stageCleared) return;
    if (ammo <= 0 || shootCooldown > 0) return;

    ammo--;
    shootCooldown = 0.25;
    muzzleFlash = 7;
    bulletEffect = 5;

    const target = getTargetEnemy();

    if (target) {
        target.hp--;
        hitMarker = 8;

        if (target.hp <= 0) {
            score += target.type === "robot" ? 200 : 100;
            enemies = enemies.filter(e => e.hp > 0);
        }
    }

    updateHUD();
}

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

function updateEnemies(dt) {
    for (const enemy of enemies) {
        const dx = player.x - enemy.x;
        const dy = player.y - enemy.y;
        const dist = Math.hypot(dx, dy);

        if (dist > 0.65) {
            const speed = enemy.speed * (1 + stage * 0.1);
            const nx = enemy.x + dx/dist * speed * dt * 60;
            const ny = enemy.y + dy/dist * speed * dt * 60;

            if (!isWall(nx, enemy.y)) enemy.x = nx;
            if (!isWall(enemy.x, ny)) enemy.y = ny;
        } else {
            if (!enemy.lastAttack || performance.now() - enemy.lastAttack > 1000) {
                hp -= 8;
                damageFlash = 8;
                enemy.lastAttack = performance.now();
                updateHUD();
            }
        }
    }
}

function updateHUD() {
    document.getElementById("hp").textContent = "HP: " + hp;
    document.getElementById("ammo").textContent = "AMMO: " + ammo;
    document.getElementById("score").textContent = "SCORE: " + score;
    document.getElementById("stage").textContent = "STAGE: " + stage;
    document.getElementById("enemyCount").textContent =
        "ENEMIES: " + enemies.length;
}

function showOverlay(title, message, buttonText, callback) {
    const overlay = document.getElementById("overlay");

    overlay.innerHTML = `
        <h1>${title}</h1>
        <p>${message}</p>
        <button id="overlayButton">${buttonText}</button>
    `;

    overlay.style.display = "flex";
    document.getElementById("overlayButton").onclick = callback;
}

function nextStage() {
    stage++;
    enemies = makeEnemies(4 + stage * 2);
    player.x = 1.5;
    player.y = 1.5;
    player.angle = 0;
    ammo = maxAmmo;
    hp = Math.min(100, hp + 20);
    stageCleared = false;

    updateHUD();
    requestAnimationFrame(loop);
}

function makeEnemies(count) {
    const types = [
        {
            type: "alien", name: "ALIEN",
            color: "#39ff14", hp: 1,
            maxHp: 1, speed: 0.020, size: 0.75
        },
        {
            type: "robot", name: "ROBOT",
            color: "#ff3333", hp: 3,
            maxHp: 3, speed: 0.010, size: 0.95
        },
        {
            type: "ghost", name: "GHOST",
            color: "#bb66ff", hp: 1,
            maxHp: 1, speed: 0.038, size: 0.65
        }
    ];

    const result = [];

    for (let i = 0; i < count; i++) {
        const type = types[Math.floor(Math.random()*types.length)];

        let x, y;
        let attempts = 0;

        do {
            x = 2.5 + Math.random()*6;
            y = 2.5 + Math.random()*6;
            attempts++;
        } while (
            (isWall(x,y) || Math.hypot(x-player.x,y-player.y)<2.5)
            && attempts < 100
        );

        result.push({
            ...type,
            x, y,
            lastAttack: 0
        });
    }

    return result;
}

function endGame() {
    gameRunning = false;
    gameOver = true;

    showOverlay(
        "MISSION FAILED",
        "최종 점수: " + score + "<br>도달 스테이지: " + stage,
        "RESTART",
        startGame
    );
}

function clearStage() {
    gameRunning = false;
    stageCleared = true;

    showOverlay(
        "STAGE CLEAR!",
        "모든 적을 처치했다!<br>점수: " + score,
        "NEXT STAGE",
        nextStage
    );
}

function updateEffects() {
    if (muzzleFlash > 0) muzzleFlash--;
    if (bulletEffect > 0) bulletEffect--;
    if (hitMarker > 0) hitMarker--;
    if (damageFlash > 0) damageFlash--;
    if (shootCooldown > 0) shootCooldown -= 1/60;
}

function render() {
    drawWorld();
    drawEnemies();
    drawCrosshair();
    drawGun();

    if (damageFlash > 0) {
        ctx.fillStyle = "rgba(255,0,0,0.22)";
        ctx.fillRect(0, 0, W, H);
    }

    if (reloadTime > 0) {
        ctx.fillStyle = "#ffff66";
        ctx.font = "20px monospace";
        ctx.fillText("RELOADING...", W/2-65, H-20);
    }
}

function loop(timestamp) {
    if (!gameRunning) return;

    const dt = Math.min((timestamp - (lastTime || timestamp))/1000, 0.05);
    lastTime = timestamp;

    movePlayer(dt);
    updateEnemies(dt);
    updateEffects();
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

    requestAnimationFrame(loop);
}

document.addEventListener("keydown", e => {
    const key = e.key.toLowerCase();

    if (["w","a","s","d","arrowleft","arrowright"," "].includes(key)) {
        e.preventDefault();
    }

    keys[key] = true;

    if (key === " " && !e.repeat) shoot();
    if (key === "r" && !e.repeat) reload();
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

html = html.replace(
    "__INITIAL_ENEMIES__",
    game_data
)

components.html(
    html,
    height=570,
    scrolling=False
)
