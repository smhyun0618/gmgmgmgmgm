
import streamlit as st
import streamlit.components.v1 as components
import random
import json

st.set_page_config(
    page_title="RETRO STRIKE 3.0",
    page_icon="🎮",
    layout="wide"
)

# ======================================
# 1. Python으로 적 생성
# ======================================

def create_enemies(count=5):
    enemies = []

    positions = [
        (3.5, 3.5), (5.5, 3.5),
        (3.5, 5.5), (5.5, 5.5),
        (7.5, 7.5), (2.5, 7.5),
        (7.5, 2.5), (1.5, 5.5)
    ]

    random.shuffle(positions)

    for i in range(min(count, len(positions))):
        x, y = positions[i]

        enemies.append({
            "x": x,
            "y": y,
            "hp": 2,
            "alive": True
        })

    return enemies


initial_enemies = create_enemies(5)

# ======================================
# 2. 화면 디자인
# ======================================

st.markdown("""
<style>
.stApp {
    background: #080d18;
    color: #d9faff;
}
header {visibility:hidden;}

h1 {
    color:#54eaff !important;
    font-family:monospace;
}

.block-container {
    padding-top:1rem;
    max-width:1200px;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
# ⚡ RETRO STRIKE 3.0
### DOOM EDITION // FIRST PERSON SURVIVAL

`WASD MOVEMENT` | `RAYCASTING ENGINE` | `SPACE COMBAT`
""")

st.caption(
    "적을 모두 처치하고 다음 스테이지로 진입하세요."
)

# ======================================
# 3. 게임 화면 HTML + JavaScript
# ======================================

game_data = json.dumps(initial_enemies)

html = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">

<style>
* {
    box-sizing:border-box;
}

body {
    margin:0;
    background:#080d18;
    color:#65eaff;
    font-family:monospace;
    overflow:hidden;
}

#game {
    width:100%;
    max-width:1100px;
    margin:auto;
}

#hud {
    display:flex;
    justify-content:space-around;
    flex-wrap:wrap;
    gap:7px;
    padding:12px;
    background:#101c30;
    border:1px solid #246c86;
    font-size:14px;
}

.stat {
    min-width:90px;
    text-align:center;
}

.stat strong {
    display:block;
    color:#fff;
    font-size:22px;
    margin-top:4px;
}

canvas {
    display:block;
    width:100%;
    height:auto;
    aspect-ratio:16/9;
    background:#050914;
    border:2px solid #36d9ee;
    cursor:crosshair;
    touch-action:none;
}

#info {
    background:#101c30;
    padding:10px;
    display:flex;
    justify-content:space-between;
    flex-wrap:wrap;
    gap:8px;
    font-size:12px;
}

#overlay {
    position:fixed;
    inset:0;
    background:rgba(0,0,0,.88);
    display:flex;
    align-items:center;
    justify-content:center;
    z-index:20;
    padding:20px;
}

#panel {
    background:#102338;
    border:2px solid #42eaff;
    padding:30px;
    text-align:center;
    max-width:440px;
    width:100%;
    box-shadow:0 0 30px #087c9b;
}

button {
    background:#123b53;
    color:#6df3ff;
    border:1px solid #48eaff;
    padding:13px 25px;
    cursor:pointer;
    font-family:monospace;
    font-weight:bold;
    font-size:16px;
}

button:hover {
    background:#17617c;
}

#message {
    color:#ffdc75;
    font-size:14px;
    min-height:20px;
}

#controls {
    display:flex;
    justify-content:center;
    flex-wrap:wrap;
    gap:12px;
    padding:12px;
    color:#9bbaca;
    font-size:12px;
}
</style>
</head>

<body>

<div id="game">

<div id="hud">
    <div class="stat">HEALTH<strong id="hp">100</strong></div>
    <div class="stat">ARMOR<strong id="armor">50</strong></div>
    <div class="stat">SCORE<strong id="score">0</strong></div>
    <div class="stat">STAGE<strong id="stage">1</strong></div>
    <div class="stat">AMMO<strong id="ammo">20</strong></div>
    <div class="stat">KILLS<strong id="kills">0</strong></div>
</div>

<canvas id="screen" width="960" height="540"></canvas>

<div id="info">
    <span id="status">SYSTEM READY</span>
    <span id="enemyCount">HOSTILES: 5</span>
</div>

<div id="controls">
    W/S: MOVE |
    A/D: STRAFE |
    ←/→: TURN |
    SPACE: FIRE |
    R: RELOAD |
    CLICK SCREEN: MOUSE LOOK
</div>

</div>

<div id="overlay">
    <div id="panel">
        <h1>⚡ RETRO STRIKE</h1>
        <h2>DOOM EDITION</h2>
        <p>ENTER THE BATTLEFIELD</p>
        <p>WASD로 이동하고 적을 처치하세요.</p>
        <button id="start">START MISSION</button>
    </div>
</div>

<script>

const canvas = document.getElementById("screen");
const ctx = canvas.getContext("2d");

const W = canvas.width;
const H = canvas.height;

const map = [
"111111111111",
"100000000001",
"101101001101",
"100000000001",
"101001101101",
"100000000001",
"101101001101",
"100000000001",
"111111111111"
].map(row => row.split("").map(Number));

const keys = {};

let player = {
    x:1.5,
    y:1.5,
    angle:0,
    hp:100,
    armor:50,
    ammo:20,
    score:0,
    kills:0,
    stage:1
};

let enemies = [];
let running = false;
let lastTime = 0;
let shootCooldown = 0;
let reloadCooldown = 0;
let damageFlash = 0;
let muzzleFlash = 0;
let gameTime = 0;
let zBuffer = [];

const FOV = Math.PI / 3;
const MAX_DISTANCE = 14;

function makeEnemies(count) {

    let result = [];

    for(let i=0;i<count;i++) {

        let x,y;
        let attempts=0;

        do {
            x = 2.5 + Math.random()*8;
            y = 1.5 + Math.random()*6;

            attempts++;

        } while (
            (isWall(x,y) ||
            Math.hypot(x-player.x,y-player.y)<3 ||
            result.some(e=>Math.hypot(e.x-x,e.y-y)<1))
            && attempts<100
        );

        result.push({
            x:x,
            y:y,
            hp:player.stage>=3?3:2,
            alive:true,
            phase:Math.random()*6
        });
    }

    return result;
}

function isWall(x,y) {

    const mx=Math.floor(x);
    const my=Math.floor(y);

    if(
        my<0 || my>=map.length ||
        mx<0 || mx>=map[0].length
    ) return true;

    return map[my][mx]===1;
}

function startGame() {

    player={
        x:1.5,
        y:1.5,
        angle:0,
        hp:100,
        armor:50,
        ammo:20,
        score:0,
        kills:0,
        stage:1
    };

    enemies=makeEnemies(5);

    running=true;

    document.getElementById("overlay").style.display="none";
    document.getElementById("status").textContent="MISSION ACTIVE";

    updateHUD();

    lastTime=performance.now();

    requestAnimationFrame(loop);
}

document.getElementById("start").onclick=startGame;

// =====================================
// KEYBOARD INPUT
// =====================================

document.addEventListener("keydown",e=>{

    const blocked=[
        "Space","ArrowLeft","ArrowRight",
        "ArrowUp","ArrowDown"
    ];

    if(blocked.includes(e.code)) {
        e.preventDefault();
    }

    keys[e.code]=true;

    if(e.code==="Space" && !e.repeat) {
        shoot();
    }

    if(e.code==="KeyR" && !e.repeat) {
        reload();
    }
});

document.addEventListener("keyup",e=>{
    keys[e.code]=false;
});

window.addEventListener("blur",()=>{
    for(const k in keys) keys[k]=false;
});

// =====================================
// MOUSE LOOK
// =====================================

canvas.addEventListener("click",()=>{

    if(!running) return;

    if(canvas.requestPointerLock) {
        canvas.requestPointerLock();
    }
});

document.addEventListener("mousemove",e=>{

    if(
        document.pointerLockElement===canvas &&
        running
    ) {
        player.angle+=e.movementX*0.0025;
    }
});

// =====================================
// MOVEMENT
// =====================================

function move(dx,dy) {

    const radius=0.20;

    if(!isWall(player.x+dx+Math.sign(dx)*radius,player.y)) {
        player.x+=dx;
    }

    if(!isWall(player.x,player.y+dy+Math.sign(dy)*radius)) {
        player.y+=dy;
    }
}

function updateMovement(dt) {

    const speed=3.0*dt;
    const turn=2.2*dt;

    if(keys["ArrowLeft"]) player.angle-=turn;
    if(keys["ArrowRight"]) player.angle+=turn;

    let forward=0;
    let strafe=0;

    if(keys["KeyW"]) forward+=speed;
    if(keys["KeyS"]) forward-=speed;
    if(keys["KeyA"]) strafe-=speed;
    if(keys["KeyD"]) strafe+=speed;

    if(forward!==0 || strafe!==0) {

        const length=Math.hypot(forward,strafe);

        forward/=Math.max(1,length/speed);
        strafe/=Math.max(1,length/speed);

        const dx=
            Math.cos(player.angle)*forward+
            Math.cos(player.angle+Math.PI/2)*strafe;

        const dy=
            Math.sin(player.angle)*forward+
            Math.sin(player.angle+Math.PI/2)*strafe;

        move(dx,dy);
    }
}

// =====================================
// RAYCASTING ENGINE
// =====================================

function castRay(angle) {

    const step=0.025;

    let distance=0;
    let hit=false;
    let hitX=0;
    let hitY=0;

    while(distance<MAX_DISTANCE) {

        distance+=step;

        const x=player.x+Math.cos(angle)*distance;
        const y=player.y+Math.sin(angle)*distance;

        if(isWall(x,y)) {
            hit=true;
            hitX=x;
            hitY=y;
            break;
        }
    }

    return {
        distance:distance,
        hit:hit,
        x:hitX,
        y:hitY
    };
}

function drawWorld() {

    // SKY
    const sky=ctx.createLinearGradient(0,0,0,H/2);
    sky.addColorStop(0,"#080e20");
    sky.addColorStop(1,"#35465a");

    ctx.fillStyle=sky;
    ctx.fillRect(0,0,W,H/2);

    // FLOOR
    const floor=ctx.createLinearGradient(0,H/2,0,H);
    floor.addColorStop(0,"#273746");
    floor.addColorStop(1,"#070b12");

    ctx.fillStyle=floor;
    ctx.fillRect(0,H/2,W,H/2);

    zBuffer=[];

    const strips=480;
    const stripWidth=W/strips;

    for(let i=0;i<strips;i++) {

        const camera=(i/strips)-0.5;
        const rayAngle=player.angle+camera*FOV;

        const ray=castRay(rayAngle);

        const corrected=
            ray.distance*Math.cos(rayAngle-player.angle);

        zBuffer[i]=corrected;

        const wallHeight=Math.min(
            H,
            H/corrected
        );

        const y=(H-wallHeight)/2;

        let side=Math.abs(
            Math.sin(rayAngle)
        );

        let brightness=Math.max(
            25,
            220-corrected*18
        );

        if(side<0.35) brightness*=0.75;

        const texture=(Math.floor(ray.x*8)+Math.floor(ray.y*8))%2;

        const r=Math.floor(brightness*0.23);
        const g=Math.floor(brightness*0.62);
        const b=Math.floor(brightness*(texture?1:0.78));

        ctx.fillStyle=`rgb(${r},${g},${b})`;

        ctx.fillRect(
            i*stripWidth,
            y,
            stripWidth+1,
            wallHeight
        );

        if(i%30===0) {
            ctx.fillStyle="rgba(0,240,255,0.18)";
            ctx.fillRect(i*stripWidth,y,2,wallHeight);
        }
    }
}

// =====================================
// ENEMY RENDERING
// =====================================

function drawEnemies() {

    const visible=enemies
        .filter(e=>e.alive)
        .map(e=>{

            let dx=e.x-player.x;
            let dy=e.y-player.y;

            let distance=Math.hypot(dx,dy);

            let angle=Math.atan2(dy,dx)-player.angle;

            while(angle>Math.PI) angle-=Math.PI*2;
            while(angle<-Math.PI) angle+=Math.PI*2;

            return {e,distance,angle};
        })
        .sort((a,b)=>b.distance-a.distance);

    for(const item of visible) {

        const {e,distance,angle}=item;

        if(Math.abs(angle)>FOV*0.85) continue;

        const corrected=distance*Math.cos(angle);

        if(corrected<0.2) continue;

        const screenX=
            W/2+(angle/FOV)*W;

        const size=Math.min(
            260,
            H/corrected*0.65
        );

        const column=Math.max(
            0,
            Math.min(479,Math.floor(screenX/W*480))
        );

        if(zBuffer[column]<corrected) continue;

        const y=H/2-size/2+
            Math.sin(gameTime*3+e.phase)*5;

        ctx.save();

        ctx.shadowColor="#00eeff";
        ctx.shadowBlur=18;

        ctx.font=`${size*0.75}px serif`;
        ctx.textAlign="center";

        ctx.fillText(
            "🤖",
            screenX,
            y+size*0.8
        );

        ctx.restore();

        if(corrected<7) {

            ctx.fillStyle="#25101b";
            ctx.fillRect(
                screenX-size*.35,
                y-13,
                size*.7,
                7
            );

            ctx.fillStyle="#ff425d";
            ctx.fillRect(
                screenX-size*.35,
                y-13,
                size*.7*(e.hp/(player.stage>=3?3:2)),
                7
            );
        }
    }
}

// =====================================
// WEAPON
// =====================================

function drawWeapon() {

    const x=W/2;
    const y=H-35;

    ctx.save();

    if(muzzleFlash>0) {

        ctx.fillStyle="#fff5a3";
        ctx.shadowColor="#00eaff";
        ctx.shadowBlur=35;

        ctx.beginPath();
        ctx.arc(x,y-135,35,0,Math.PI*2);
        ctx.fill();
    }

    // Gun body
    ctx.fillStyle="#101b2c";

    ctx.beginPath();
    ctx.moveTo(x-75,H);
    ctx.lineTo(x-35,y-100);
    ctx.lineTo(x+35,y-100);
    ctx.lineTo(x+75,H);
    ctx.closePath();
    ctx.fill();

    ctx.strokeStyle="#38dff5";
    ctx.lineWidth=3;
    ctx.stroke();

    ctx.fillStyle="#1e627b";
    ctx.fillRect(x-13,y-125,26,60);

    ctx.fillStyle="#8ffaff";
    ctx.fillRect(x-5,y-115,10,25);

    ctx.restore();

    // Crosshair
    ctx.strokeStyle="#d3ffff";
    ctx.lineWidth=2;

    ctx.beginPath();
    ctx.moveTo(x-18,H/2);
    ctx.lineTo(x-6,H/2);

    ctx.moveTo(x+6,H/2);
    ctx.lineTo(x+18,H/2);

    ctx.moveTo(x,H/2-18);
    ctx.lineTo(x,H/2-6);

    ctx.moveTo(x,H/2+6);
    ctx.lineTo(x,H/2+18);

    ctx.stroke();
}

// =====================================
// SHOOTING
// =====================================

function shoot() {

    if(!running || shootCooldown>0) return;

    if(player.ammo<=0) {

        setMessage("OUT OF AMMO!");
        return;
    }

    player.ammo--;

    shootCooldown=0.3;
    muzzleFlash=0.12;

    let target=null;
    let best=Infinity;

    for(const e of enemies) {

        if(!e.alive) continue;

        const dx=e.x-player.x;
        const dy=e.y-player.y;

        const distance=Math.hypot(dx,dy);

        let angle=Math.atan2(dy,dx)-player.angle;

        while(angle>Math.PI) angle-=Math.PI*2;
        while(angle<-Math.PI) angle+=Math.PI*2;

        if(
            Math.abs(angle)<0.10 &&
            distance<best
        ) {

            const wall=castRay(player.angle);

            if(wall.distance>distance-0.25) {
                target=e;
                best=distance;
            }
        }
    }

    if(target) {

        target.hp--;

        if(target.hp<=0) {

            target.alive=false;
            player.score+=100;
            player.kills++;

            setMessage("TARGET DESTROYED +100");

        } else {

            player.score+=25;
            setMessage("ENEMY HIT!");
        }

    } else {

        setMessage("SHOT MISSED!");
    }

    if(enemies.every(e=>!e.alive)) {
        setMessage("STAGE CLEAR!");
    }

    updateHUD();
}

// =====================================
// RELOAD
// =====================================

function reload() {

    if(!running || reloadCooldown>0) return;

    if(player.ammo===20) return;

    reloadCooldown=0.6;
    player.ammo=20;

    setMessage("RELOADING COMPLETE");

    updateHUD();
}

// =====================================
// ENEMY AI
// =====================================

function updateEnemies(dt) {

    for(const e of enemies) {

        if(!e.alive) continue;

        const dx=player.x-e.x;
        const dy=player.y-e.y;

        const distance=Math.hypot(dx,dy);

        if(distance<0.8) {

            e.attackTimer=(e.attackTimer||0)+dt;

            if(e.attackTimer>1.2) {

                e.attackTimer=0;

                const absorbed=Math.min(
                    player.armor,8
                );

                player.armor-=absorbed;
                player.hp-=8-absorbed;

                damageFlash=0.2;

                setMessage("WARNING! UNDER ATTACK");

                if(player.hp<=0) {
                    player.hp=0;
                    endGame();
                }
            }

        } else if(distance<6) {

            const speed=0.35*dt;

            const nx=e.x+(dx/distance)*speed;
            const ny=e.y+(dy/distance)*speed;

            if(!isWall(nx,e.y)) e.x=nx;
            if(!isWall(e.x,ny)) e.y=ny;
        }
    }
}

// =====================================
// STAGE
// =====================================

function nextStage() {

    player.stage++;

    player.hp=Math.min(100,player.hp+20);
    player.armor=Math.min(100,player.armor+20);
    player.ammo=20;

    player.x=1.5;
    player.y=1.5;
    player.angle=0;

    enemies=makeEnemies(
        Math.min(4+player.stage,10)
    );

    setMessage("STAGE "+player.stage+" START!");
    updateHUD();
}

// =====================================
// HUD
// =====================================

function updateHUD() {

    document.getElementById("hp").textContent=player.hp;
    document.getElementById("armor").textContent=player.armor;
    document.getElementById("score").textContent=player.score;
    document.getElementById("stage").textContent=player.stage;
    document.getElementById("ammo").textContent=player.ammo;
    document.getElementById("kills").textContent=player.kills;

    document.getElementById("enemyCount").textContent=
        "HOSTILES: "+enemies.filter(e=>e.alive).length;
}

function setMessage(msg) {
    document.getElementById("status").textContent=msg;
}

// =====================================
// END GAME
// =====================================

function endGame() {

    running=false;

    document.exitPointerLock?.();

    document.getElementById("overlay").style.display="flex";

    document.getElementById("panel").innerHTML=`
        <h1>MISSION FAILED</h1>
        <h2>FINAL SCORE: ${player.score}</h2>
        <p>TOTAL KILLS: ${player.kills}</p>
        <p>STAGE: ${player.stage}</p>
        <button id="restart">RESTART MISSION</button>
    `;

    document.getElementById("restart").onclick=startGame;
}

// =====================================
// DAMAGE EFFECT
// =====================================

function drawDamage() {

    if(damageFlash>0) {

        ctx.fillStyle=`rgba(255,0,30,${damageFlash*0.6})`;
        ctx.fillRect(0,0,W,H);
    }
}

// =====================================
// MAIN LOOP
// =====================================

function loop(now) {

    if(!running) return;

    const dt=Math.min((now-lastTime)/1000,0.05);

    lastTime=now;
    gameTime+=dt;

    shootCooldown=Math.max(0,shootCooldown-dt);
    reloadCooldown=Math.max(0,reloadCooldown-dt);
    muzzleFlash=Math.max(0,muzzleFlash-dt);
    damageFlash=Math.max(0,damageFlash-dt);

    updateMovement(dt);
    updateEnemies(dt);

    drawWorld();
    drawEnemies();
    drawWeapon();
    drawDamage();

    if(player.hp<=0) {
        endGame();
        return;
    }

    if(enemies.every(e=>!e.alive)) {

        if(!window.stageCleared) {

            window.stageCleared=true;

            setMessage("STAGE CLEAR! PRESS ENTER");

        }

        if(keys["Enter"]) {

            window.stageCleared=false;
            keys["Enter"]=false;

            nextStage();
        }

    } else {
        window.stageCleared=false;
    }

    updateHUD();

    requestAnimationFrame(loop);
}

// =====================================
// INITIAL PREVIEW
// =====================================

ctx.fillStyle="#080e20";
ctx.fillRect(0,0,W,H);

ctx.fillStyle="#48eaff";
ctx.font="bold 35px monospace";
ctx.textAlign="center";
ctx.fillText("RETRO STRIKE 3.0",W/2,H/2);

</script>

</body>
</html>
"""

# ======================================
# 4. 초기 적 데이터 전달
# ======================================

html = html.replace(
    "const initialEnemyData = [];",
    "const initialEnemyData = " + game_data + ";"
)

# ======================================
# 5. 게임 출력
# ======================================

components.html(
    html,
    height=720,
    scrolling=False
)

st.markdown("---")
st.caption(
    "RETRO STRIKE 3.0 | PYTHON + STREAMLIT + JAVASCRIPT"
)
