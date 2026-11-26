
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="RETRO STRIKE",
    page_icon="",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: #090d16;
    color: white;
}
header, footer {
    visibility: hidden;
}
.block-container {
    padding-top: 1rem;
    max-width: 1100px;
}
</style>
""", unsafe_allow_html=True)

st.title("RETRO STRIKE")
st.caption("SURVIVE THE MISSION. ELIMINATE ALL HOSTILES.")

game_html = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
* { box-sizing: border-box; }
body {
    margin: 0;
    background: #080b12;
    color: white;
    font-family: monospace;
}
#game {
    width: 100%;
    max-width: 900px;
    margin: auto;
    position: relative;
}
#hud {
    display: flex;
    justify-content: space-between;
    gap: 8px;
    padding: 10px;
    background: #111827;
    border: 1px solid #39465d;
    font-size: 14px;
    flex-wrap: wrap;
}
#canvas {
    display: block;
    width: 100%;
    height: auto;
    background: black;
    border: 2px solid #39465d;
    outline: none;
}
#overlay {
    position: absolute;
    top: 42px;
    left: 0;
    width: 100%;
    height: 450px;
    background: rgba(3, 7, 15, .9);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    z-index: 5;
}
#overlay h1 {
    color: #ff4242;
    font-size: 38px;
    text-shadow: 0 0 15px red;
}
#overlay button {
    margin-top: 15px;
    padding: 13px 30px;
    background: #b91c1c;
    color: white;
    border: 1px solid #ff7777;
    font-family: monospace;
    font-size: 17px;
    cursor: pointer;
}
#warning {
    color: #ff5555;
    font-weight: bold;
    min-height: 18px;
    text-align: center;
}
#help {
    padding: 9px;
    color: #9ca3af;
    font-size: 12px;
    text-align: center;
}
</style>
</head>

<body>
<div id="game">

<div id="hud">
    <span id="hp">HP: 100</span>
    <span id="ammo">AMMO: 12/12</span>
    <span id="score">SCORE: 0</span>
    <span id="stage">STAGE: 1</span>
    <span id="time">TIME: 90</span>
    <span id="hostiles">HOSTILES: 0</span>
</div>

<canvas id="canvas" width="800" height="450" tabindex="0"></canvas>

<div id="warning"></div>

<div id="overlay">
    <h1>RETRO STRIKE</h1>
    <p>ELIMINATE ALL HOSTILES</p>
    <p>WASD: MOVE | LEFT/RIGHT: TURN | SPACE: FIRE | R: RELOAD</p>
    <button id="mainButton" onclick="startGame()">START MISSION</button>
</div>

<div id="help">
    RUSHER: FAST | SNIPER: LONG RANGE | TANK: HEAVY ARMOR | DRONE: HEALER
</div>

</div>

<script>
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

const W = 800;
const H = 450;
const FOV = Math.PI / 3;
const RAYS = 400;
const MAX_AMMO = 12;

const MAP = [
    "111111111111",
    "100000000001",
    "101110010101",
    "100010000001",
    "100010110001",
    "100000000001",
    "101101010101",
    "100000000001",
    "100000000001",
    "111111111111"
];

const SPAWNS = [
    [9.5, 1.5],
    [10.5, 3.5],
    [8.5, 5.5],
    [5.5, 8.5],
    [9.5, 8.5],
    [1.5, 7.5],
    [6.5, 3.5],
    [2.5, 8.5],
    [10.5, 7.5]
];

const TYPES = {
    rusher: {
        name: "RUSHER",
        hp: 45,
        speed: 1.45,
        damage: 9,
        color: "#ff4545"
    },
    sniper: {
        name: "SNIPER",
        hp: 35,
        speed: 0.55,
        damage: 17,
        color: "#ffb347"
    },
    tank: {
        name: "TANK",
        hp: 150,
        speed: 0.38,
        damage: 20,
        color: "#9b75ff"
    },
    drone: {
        name: "DRONE",
        hp: 40,
        speed: 0.65,
        damage: 0,
        color: "#4de6ff"
    }
};

let player = {
    x: 1.5,
    y: 1.5,
    angle: 0,
    hp: 100,
    ammo: MAX_AMMO
};

let enemies = [];
let stage = 1;
let score = 0;
let timeLeft = 90;
let gameRunning = false;
let stageCleared = false;
let gameOver = false;
let lastTime = 0;
let animationId = null;

let keys = {};
let zBuffer = [];
let effects = [];
let muzzleFlash = 0;
let hitFlash = 0;
let reloadTime = 0;
let shootCooldown = 0;
let damageFlash = 0;
let warningText = "";
let warningTimer = 0;


// ------------------------------
// 기본 함수
// ------------------------------

function isWall(x, y) {
    const mx = Math.floor(x);
    const my = Math.floor(y);

    if (
        my < 0 || my >= MAP.length ||
        mx < 0 || mx >= MAP[0].length
    ) return true;

    return MAP[my][mx] === "1";
}

function canMove(x, y) {
    const r = 0.18;

    return !isWall(x-r,y-r) &&
           !isWall(x+r,y-r) &&
           !isWall(x-r,y+r) &&
           !isWall(x+r,y+r);
}

function normalizeAngle(a) {
    while (a > Math.PI) a -= Math.PI*2;
    while (a < -Math.PI) a += Math.PI*2;
    return a;
}

function distance(x1,y1,x2,y2) {
    return Math.hypot(x2-x1,y2-y1);
}

function hasLineOfSight(x1,y1,x2,y2) {
    const d = distance(x1,y1,x2,y2);
    const steps = Math.ceil(d*12);

    for (let i=1;i<steps;i++) {
        const t = i/steps;
        if (isWall(
            x1+(x2-x1)*t,
            y1+(y2-y1)*t
        )) return false;
    }

    return true;
}


// ------------------------------
// 적 생성
// ------------------------------

function makeEnemies(count) {
    const result = [];
    const positions = [...SPAWNS];

    for (let i=positions.length-1;i>0;i--) {
        const j = Math.floor(Math.random()*(i+1));
        [positions[i],positions[j]] =
        [positions[j],positions[i]];
    }

    const types = [
        "rusher",
        "rusher",
        "sniper",
        "tank",
        "drone"
    ];

    for (let i=0;i<count;i++) {
        const type = types[
            Math.floor(Math.random()*types.length)
        ];

        const data = TYPES[type];
        const pos = positions[i%positions.length];

        result.push({
            type: type,
            x: pos[0],
            y: pos[1],
            hp: data.hp+(stage-1)*5,
            maxHp: data.hp+(stage-1)*5,
            speed: data.speed,
            damage: data.damage,
            attackCooldown: Math.random(),
            aimTimer: 0,
            aiming: false,
            targetX: 0,
            targetY: 0,
            healCooldown: 0
        });
    }

    return result;
}


// ------------------------------
// 픽셀 아트 캐릭터 그리기
// ------------------------------

function drawPixelEnemy(e, screenX, screenY, size) {

    const s = size/16;
    const x = screenX-8*s;
    const y = screenY-16*s;

    function px(a,b,w,h,color) {
        ctx.fillStyle = color;
        ctx.fillRect(
            x+a*s,
            y+b*s,
            w*s,
            h*s
        );
    }

    function outline(a,b,w,h,color="#080b12") {
        px(a,b,w,h,color);
    }

    // RUSHER: 붉은 괴물
    if (e.type === "rusher") {

        // 뿔
        px(2,2,2,3,"#741b1b");
        px(12,2,2,3,"#741b1b");

        // 몸통
        px(4,3,8,2,"#bd3030");
        px(2,5,12,6,"#a92323");
        px(3,11,10,3,"#751919");

        // 팔
        px(0,6,3,5,"#8f2020");
        px(13,6,3,5,"#8f2020");

        // 얼굴
        px(4,4,8,4,"#d94b3e");
        px(5,6,2,1,"#ffff55");
        px(9,6,2,1,"#ffff55");

        // 입
        px(6,8,4,1,"#240707");

        // 다리
        px(4,13,3,3,"#481313");
        px(9,13,3,3,"#481313");

        // 발톱
        px(3,15,4,1,"#d7d7d7");
        px(9,15,4,1,"#d7d7d7");
    }

    // SNIPER: 소총을 든 기계 병사
    else if (e.type === "sniper") {

        // 머리와 헬멧
        px(4,1,8,2,"#6d777f");
        px(3,3,10,4,"#9da7a9");
        px(5,4,2,2,"#ff3838");
        px(9,4,2,2,"#ff3838");

        // 몸통 갑옷
        px(3,7,10,6,"#45515e");
        px(5,8,6,3,"#d18b32");
        px(6,9,4,1,"#252d38");

        // 어깨
        px(1,7,3,3,"#7d8992");
        px(12,7,3,3,"#7d8992");

        // 총
        px(11,9,5,2,"#1b222c");
        px(14,8,2,1,"#c2c9ce");
        px(15,10,1,2,"#c2c9ce");

        // 다리
        px(4,13,3,3,"#303a45");
        px(9,13,3,3,"#303a45");
    }

    // TANK: 중장갑 로봇
    else if (e.type === "tank") {

        // 머리
        px(4,1,8,3,"#8170c5");
        px(3,3,10,3,"#6455a2");

        // 눈
        px(5,4,2,1,"#ff3030");
        px(9,4,2,1,"#ff3030");

        // 거대한 어깨
        px(0,6,5,5,"#7568b5");
        px(11,6,5,5,"#7568b5");

        // 몸통
        px(3,6,10,8,"#51458d");
        px(5,8,6,4,"#a79be6");

        // 가슴 장갑
        px(6,9,4,2,"#282345");

        // 다리
        px(3,14,4,2,"#332c59");
        px(9,14,4,2,"#332c59");

        // 장갑판
        px(1,7,2,2,"#c0b8ff");
        px(13,7,2,2,"#c0b8ff");
    }

    // DRONE: 공중 전투 기계
    else if (e.type === "drone") {

        // 좌우 날개
        px(0,6,4,3,"#268ca2");
        px(12,6,4,3,"#268ca2");

        // 날개 끝
        px(0,5,2,1,"#9af4ff");
        px(14,5,2,1,"#9af4ff");

        // 중심 기체
        px(4,3,8,9,"#3bb8d2");
        px(3,5,10,5,"#16859d");

        // 유리창
        px(5,5,6,3,"#c2faff");
        px(6,6,4,1,"#277c99");

        // 아래쪽 장치
        px(6,12,4,2,"#246b80");
        px(7,14,2,1,"#9af4ff");

        // 엔진
        px(1,9,2,2,"#ffbd45");
        px(13,9,2,2,"#ffbd45");
    }

    // 회복 효과
    if (e.type === "drone") {
        ctx.fillStyle = "#5dff9a";
        ctx.fillRect(x+7*s,y-3*s,2*s,2*s);
    }

    // 저격 조준 표시
    if (e.type === "sniper" && e.aiming) {
        ctx.strokeStyle = "#ff3030";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(screenX,screenY-size);
        ctx.lineTo(W/2,H/2);
        ctx.stroke();
    }

    // 체력바
    ctx.fillStyle = "#111";
    ctx.fillRect(
        screenX-size*0.45,
        screenY-size*1.1,
        size*0.9,
        6
    );

    ctx.fillStyle = TYPES[e.type].color;
    ctx.fillRect(
        screenX-size*0.45,
        screenY-size*1.1,
        size*0.9*Math.max(0,e.hp/e.maxHp),
        6
    );

    // 적 이름
    ctx.fillStyle = TYPES[e.type].color;
    ctx.font = "10px monospace";
    ctx.textAlign = "center";
    ctx.fillText(
        TYPES[e.type].name,
        screenX,
        screenY-size*1.2
    );
}


// ------------------------------
// 화면 표시
// ------------------------------

function updateHUD() {
    document.getElementById("hp").textContent =
        "HP: "+Math.max(0,Math.ceil(player.hp));

    document.getElementById("ammo").textContent =
        "AMMO: "+player.ammo+"/"+MAX_AMMO;

    document.getElementById("score").textContent =
        "SCORE: "+score;

    document.getElementById("stage").textContent =
        "STAGE: "+stage;

    document.getElementById("time").textContent =
        "TIME: "+Math.max(0,Math.ceil(timeLeft));

    document.getElementById("hostiles").textContent =
        "HOSTILES: "+enemies.filter(e=>e.hp>0).length;

    document.getElementById("hp").style.color =
        player.hp<=30 ? "#ff4444" : "#dce8ff";

    document.getElementById("time").style.color =
        timeLeft<=15 ? "#ff4444" : "#dce8ff";
}

function showOverlay(title,message,buttonText,action) {
    const overlay = document.getElementById("overlay");
    overlay.style.display = "flex";

    overlay.querySelector("h1").textContent = title;
    overlay.querySelectorAll("p")[0].textContent = message;
    overlay.querySelectorAll("p")[1].textContent =
        "SCORE: "+score+" | STAGE: "+stage;

    const button = document.getElementById("mainButton");
    button.textContent = buttonText;
    button.onclick = action;
}


// ------------------------------
// 게임 시작 및 스테이지
// ------------------------------

function startGame() {
    if (animationId !== null) {
        cancelAnimationFrame(animationId);
        animationId = null;
    }

    stage = 1;
    score = 0;

    player = {
        x: 1.5,
        y: 1.5,
        angle: 0,
        hp: 100,
        ammo: MAX_AMMO
    };

    timeLeft = 90;
    enemies = makeEnemies(4);

    effects = [];
    keys = {};

    reloadTime = 0;
    shootCooldown = 0;
    damageFlash = 0;
    muzzleFlash = 0;

    stageCleared = false;
    gameOver = false;
    gameRunning = true;
    lastTime = 0;

    document.getElementById("overlay").style.display = "none";

    canvas.focus();
    updateHUD();

    animationId = requestAnimationFrame(loop);
}

function nextStage() {
    if (!stageCleared || gameRunning) return;

    stage++;

    player.hp = Math.min(100,player.hp+20);
    player.ammo = MAX_AMMO;
    player.x = 1.5;
    player.y = 1.5;
    player.angle = 0;

    timeLeft = Math.max(45,90-(stage-1)*5);
    enemies = makeEnemies(Math.min(4+stage*2,9));

    effects = [];
    keys = {};

    reloadTime = 0;
    shootCooldown = 0;
    damageFlash = 0;
    muzzleFlash = 0;

    stageCleared = false;
    gameOver = false;
    gameRunning = true;
    lastTime = 0;

    document.getElementById("overlay").style.display = "none";

    updateHUD();
    canvas.focus();

    animationId = requestAnimationFrame(loop);
}

function clearStage() {
    if (!gameRunning || stageCleared) return;

    gameRunning = false;
    stageCleared = true;
    animationId = null;

    showOverlay(
        "STAGE CLEAR",
        "ALL HOSTILES ELIMINATED",
        "NEXT STAGE",
        nextStage
    );
}

function endGame(reason) {
    if (gameOver) return;

    gameRunning = false;
    gameOver = true;
    animationId = null;

    showOverlay(
        "MISSION FAILED",
        reason,
        "RESTART",
        startGame
    );
}


// ------------------------------
// 플레이어 이동
// ------------------------------

function movePlayer(dt) {
    const moveSpeed = 2.6;
    const turnSpeed = 2.1;

    if (keys["ArrowLeft"]) {
        player.angle -= turnSpeed*dt;
    }

    if (keys["ArrowRight"]) {
        player.angle += turnSpeed*dt;
    }

    let forward = 0;
    let side = 0;

    if (keys["KeyW"]) forward++;
    if (keys["KeyS"]) forward--;
    if (keys["KeyD"]) side++;
    if (keys["KeyA"]) side--;

    const length = Math.hypot(forward,side)||1;
    forward /= length;
    side /= length;

    const dx = (
        Math.cos(player.angle)*forward-
        Math.sin(player.angle)*side
    )*moveSpeed*dt;

    const dy = (
        Math.sin(player.angle)*forward+
        Math.cos(player.angle)*side
    )*moveSpeed*dt;

    if (canMove(player.x+dx,player.y)) player.x+=dx;
    if (canMove(player.x,player.y+dy)) player.y+=dy;
}


// ------------------------------
// 3D 화면 렌더링
// ------------------------------

function castRay(angle) {
    const step = 0.025;
    let d = 0;

    while (d<15) {
        d+=step;

        const x = player.x+Math.cos(angle)*d;
        const y = player.y+Math.sin(angle)*d;

        if (isWall(x,y)) return d;
    }

    return 15;
}

function drawWorld() {
    const sky = ctx.createLinearGradient(0,0,0,H/2);
    sky.addColorStop(0,"#111827");
    sky.addColorStop(1,"#334155");

    ctx.fillStyle = sky;
    ctx.fillRect(0,0,W,H/2);

    const floor = ctx.createLinearGradient(0,H/2,0,H);
    floor.addColorStop(0,"#252b35");
    floor.addColorStop(1,"#080a0e");

    ctx.fillStyle = floor;
    ctx.fillRect(0,H/2,W,H/2);

    zBuffer = [];

    for (let i=0;i<RAYS;i++) {
        const camera = i/RAYS-0.5;
        const angle = player.angle+camera*FOV;

        const rawDist = castRay(angle);
        const corrected = rawDist*Math.cos(camera*FOV);

        zBuffer[i] = corrected;

        const wallHeight = Math.min(H,H/(corrected*0.72));
        const shade = Math.max(35,180-corrected*17);

        ctx.fillStyle =
            `rgb(${shade},${shade},${shade+12})`;

        ctx.fillRect(
            i*W/RAYS,
            H/2-wallHeight/2,
            W/RAYS+1,
            wallHeight
        );
    }
}

function drawEnemies() {
    const visible = enemies
        .filter(e=>e.hp>0)
        .map(e=>({
            enemy:e,
            dist:distance(player.x,player.y,e.x,e.y)
        }))
        .sort((a,b)=>b.dist-a.dist);

    for (const item of visible) {
        const e = item.enemy;
        const d = item.dist;

        const angle = normalizeAngle(
            Math.atan2(e.y-player.y,e.x-player.x)-player.angle
        );

        if (Math.abs(angle)>FOV/2+0.2) continue;

        const screenX = W/2+(angle/FOV)*W;
        const size = Math.min(170,H/(d*0.48));
        const screenY = H/2+size*0.12;

        const rayIndex = Math.floor(screenX/W*RAYS);

        if (
            rayIndex>=0 &&
            rayIndex<RAYS &&
            d>zBuffer[rayIndex]+0.2
        ) continue;

        drawPixelEnemy(e,screenX,screenY,size);
    }
}


// ------------------------------
// 총기와 조준점
// ------------------------------

function drawGun() {
    const bob = (
        keys["KeyW"] || keys["KeyS"] ||
        keys["KeyA"] || keys["KeyD"]
    ) ? Math.sin(performance.now()*0.012)*5 : 0;

    ctx.fillStyle = "#202b3b";
    ctx.fillRect(W/2-45,H-90+bob,90,90);

    ctx.fillStyle = "#64748b";
    ctx.fillRect(W/2-25,H-115+bob,50,55);

    ctx.fillStyle = "#111827";
    ctx.fillRect(W/2-13,H-137+bob,26,30);

    if (muzzleFlash>0) {
        ctx.fillStyle = "#ffe66d";

        ctx.beginPath();
        ctx.moveTo(W/2,H-145+bob);
        ctx.lineTo(W/2-28,H-195+bob);
        ctx.lineTo(W/2,H-180+bob);
        ctx.lineTo(W/2+28,H-195+bob);
        ctx.closePath();
        ctx.fill();
    }
}

function drawCrosshair() {
    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = 2;

    ctx.beginPath();
    ctx.moveTo(W/2-10,H/2);
    ctx.lineTo(W/2-4,H/2);
    ctx.moveTo(W/2+4,H/2);
    ctx.lineTo(W/2+10,H/2);
    ctx.moveTo(W/2,H/2-10);
    ctx.lineTo(W/2,H/2-4);
    ctx.moveTo(W/2,H/2+4);
    ctx.lineTo(W/2,H/2+10);
    ctx.stroke();

    if (hitFlash>0) {
        ctx.strokeStyle = "#ff3333";
        ctx.lineWidth = 3;

        ctx.beginPath();
        ctx.moveTo(W/2-12,H/2-12);
        ctx.lineTo(W/2+12,H/2+12);
        ctx.moveTo(W/2+12,H/2-12);
        ctx.lineTo(W/2-12,H/2+12);
        ctx.stroke();
    }
}


// ------------------------------
// 사격과 재장전
// ------------------------------

function shoot() {
    if (!gameRunning || reloadTime>0 || shootCooldown>0) return;

    if (player.ammo<=0) {
        warningText = "OUT OF AMMO! PRESS R";
        warningTimer = 1;
        return;
    }

    player.ammo--;
    shootCooldown = 0.25;
    muzzleFlash = 0.09;

    let target = null;
    let bestDist = 999;

    for (const e of enemies) {
        if (e.hp<=0) continue;

        const d = distance(player.x,player.y,e.x,e.y);

        const angle = normalizeAngle(
            Math.atan2(e.y-player.y,e.x-player.x)-player.angle
        );

        if (
            Math.abs(angle)<0.12 &&
            d<bestDist &&
            hasLineOfSight(player.x,player.y,e.x,e.y)
        ) {
            target = e;
            bestDist = d;
        }
    }

    if (target) {
        const damage = target.type==="tank" ? 30 : 45;

        target.hp-=damage;
        hitFlash = 0.12;

        if (target.hp<=0) {
            score += target.type==="tank" ? 40 : 20;
        }
    }

    updateHUD();
}

function reload() {
    if (
        !gameRunning ||
        reloadTime>0 ||
        player.ammo===MAX_AMMO
    ) return;

    reloadTime = 1.25;
    warningText = "RELOADING...";
    warningTimer = 1.25;
}


// ------------------------------
// 적 AI
// ------------------------------

function updateEnemies(dt) {
    for (const e of enemies) {
        if (e.hp<=0) continue;

        const d = distance(player.x,player.y,e.x,e.y);

        const dx = player.x-e.x;
        const dy = player.y-e.y;
        const angle = Math.atan2(dy,dx);

        e.attackCooldown-=dt;

        // 돌격형
        if (e.type==="rusher") {
            if (d>0.8) {
                const nx = e.x+Math.cos(angle)*e.speed*dt;
                const ny = e.y+Math.sin(angle)*e.speed*dt;

                if (canMove(nx,e.y)) e.x=nx;
                if (canMove(e.x,ny)) e.y=ny;
            } else if (e.attackCooldown<=0) {
                player.hp-=e.damage;
                damageFlash=0.25;
                e.attackCooldown=1.1;
            }
        }

        // 중장갑형
        else if (e.type==="tank") {
            if (d>1.15) {
                const nx = e.x+Math.cos(angle)*e.speed*dt;
                const ny = e.y+Math.sin(angle)*e.speed*dt;

                if (canMove(nx,e.y)) e.x=nx;
                if (canMove(e.x,ny)) e.y=ny;
            } else if (e.attackCooldown<=0) {
                player.hp-=e.damage;
                damageFlash=0.35;
                e.attackCooldown=1.7;
            }
        }

        // 저격형
        else if (e.type==="sniper") {
            if (d<3.5) {
                const nx = e.x-Math.cos(angle)*e.speed*dt;
                const ny = e.y-Math.sin(angle)*e.speed*dt;

                if (canMove(nx,e.y)) e.x=nx;
                if (canMove(e.x,ny)) e.y=ny;
            }

            if (
                d<10 &&
                hasLineOfSight(e.x,e.y,player.x,player.y)
            ) {
                if (!e.aiming && e.attackCooldown<=0) {
                    e.aiming=true;
                    e.aimTimer=1.3;
                    e.targetX=player.x;
                    e.targetY=player.y;
                }

                if (e.aiming) {
                    e.aimTimer-=dt;

                    if (e.aimTimer<=0) {
                        const targetDistance = distance(
                            player.x,player.y,
                            e.targetX,e.targetY
                        );

                        if (targetDistance<0.85) {
                            player.hp-=e.damage;
                            damageFlash=0.45;

                            warningText="SNIPER HIT!";
                            warningTimer=0.8;
                        }

                        e.aiming=false;
                        e.attackCooldown=2.2;
                    }
                }
            } else {
                e.aiming=false;
            }
        }

        // 지원형
        else if (e.type==="drone") {
            if (d<2.2) {
                const nx = e.x-Math.cos(angle)*e.speed*dt;
                const ny = e.y-Math.sin(angle)*e.speed*dt;

                if (canMove(nx,e.y)) e.x=nx;
                if (canMove(e.x,ny)) e.y=ny;
            }

            e.healCooldown-=dt;

            if (e.healCooldown<=0) {
                const ally = enemies.find(other =>
                    other!==e &&
                    other.hp>0 &&
                    other.hp<other.maxHp &&
                    distance(e.x,e.y,other.x,other.y)<4
                );

                if (ally) {
                    ally.hp=Math.min(ally.maxHp,ally.hp+12);

                    effects.push({
                        x:ally.x,
                        y:ally.y,
                        life:0.5
                    });
                }

                e.healCooldown=2.8;
            }
        }
    }

    if (damageFlash>0) damageFlash-=dt;
    if (warningTimer>0) warningTimer-=dt;
    if (muzzleFlash>0) muzzleFlash-=dt;
    if (hitFlash>0) hitFlash-=dt;
    if (shootCooldown>0) shootCooldown-=dt;

    if (reloadTime>0) {
        reloadTime-=dt;

        if (reloadTime<=0) {
            player.ammo=MAX_AMMO;
            warningText="RELOADED";
            warningTimer=0.7;
        }
    }

    effects=effects.filter(e=>{
        e.life-=dt;
        return e.life>0;
    });
}


// ------------------------------
// 최종 화면
// ------------------------------

function render() {
    drawWorld();
    drawEnemies();
    drawGun();
    drawCrosshair();

    if (damageFlash>0) {
        ctx.fillStyle =
            `rgba(255,0,0,${Math.min(0.35,damageFlash)})`;

        ctx.fillRect(0,0,W,H);
    }

    if (player.hp<=30) {
        const pulse =
            0.08+Math.abs(Math.sin(performance.now()*0.006))*0.12;

        ctx.fillStyle=`rgba(255,0,0,${pulse})`;
        ctx.fillRect(0,0,W,H);
    }

    if (reloadTime>0) {
        ctx.fillStyle="#ffe66d";
        ctx.font="bold 20px monospace";
        ctx.textAlign="center";
        ctx.fillText("RELOADING...",W/2,H/2+45);
    }

    if (warningTimer>0) {
        document.getElementById("warning").textContent=warningText;
    } else {
        document.getElementById("warning").textContent="";
    }

    for (const e of effects) {
        const angle=normalizeAngle(
            Math.atan2(e.y-player.y,e.x-player.x)-player.angle
        );

        if (Math.abs(angle)<FOV/2) {
            const x=W/2+angle/FOV*W;

            ctx.fillStyle="#5dff9a";
            ctx.font="bold 16px monospace";
            ctx.fillText("+HEAL",x,H/2-40);
        }
    }
}


// ------------------------------
// 게임 루프
// ------------------------------

function loop(timestamp) {
    if (!gameRunning) {
        animationId=null;
        return;
    }

    if (!lastTime) lastTime=timestamp;

    const dt=Math.min((timestamp-lastTime)/1000,0.05);
    lastTime=timestamp;

    timeLeft-=dt;

    movePlayer(dt);
    updateEnemies(dt);

    if (player.hp<=0) {
        player.hp=0;
        updateHUD();
        endGame("YOU WERE ELIMINATED");
        return;
    }

    if (timeLeft<=0) {
        timeLeft=0;
        updateHUD();
        endGame("TIME LIMIT EXCEEDED");
        return;
    }

    if (enemies.every(e=>e.hp<=0)) {
        updateHUD();
        clearStage();
        return;
    }

    updateHUD();
    render();

    animationId=requestAnimationFrame(loop);
}


// ------------------------------
// 키보드 입력
// ------------------------------

window.addEventListener("keydown",event=>{
    const allowed=[
        "KeyW","KeyA","KeyS","KeyD",
        "ArrowLeft","ArrowRight",
        "Space","KeyR"
    ];

    if (allowed.includes(event.code)) {
        event.preventDefault();
    }

    if (event.code==="Space"&&!event.repeat) shoot();
    if (event.code==="KeyR"&&!event.repeat) reload();

    keys[event.code]=true;
});

window.addEventListener("keyup",event=>{
    keys[event.code]=false;
});

window.addEventListener("blur",()=>{
    keys={};
});

canvas.addEventListener("click",()=>{
    canvas.focus();
    if (gameRunning) shoot();
});

updateHUD();

</script>
</body>
</html>
"""

components.html(game_html, height=540, scrolling=False)

st.markdown("""
---

### MISSION GUIDE

| 적 병과 | 특징 |
|---|---|
| RUSHER | 빠르게 추격하는 괴물 |
| SNIPER | 멀리서 조준하고 공격하는 병사 |
| TANK | 높은 체력을 가진 중장갑 로봇 |
| DRONE | 주변 적을 회복시키는 비행 기계 |

**조작법**

- W / A / S / D : 이동
- ← / → : 시야 회전
- SPACE : 사격
- R : 재장전
""")
