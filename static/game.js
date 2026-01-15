/* --- API連携機能 --- */
const api = {
    loadGame: async () => {
        const res = await fetch('/api/get_data');
        if (!res.ok) {
            console.error("Failed to load data");
            return null;
        }
        return await res.json();
    },
    saveGame: async () => {
        await fetch('/api/update_data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_token: game.user_token,
                stage: game.stage,
                stats: game.stats
            })
        });
    }
};

/* --- UI要素 --- */
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

const ui = {
    user_token: document.getElementById('uiUserToken'),
    stage: document.getElementById('uiStage'),
    hp: document.getElementById('uiHp'),
    btnAuto: document.getElementById('autoBtn'),
    shotNormal: document.getElementById('shotNormal'),
    shotPower: document.getElementById('shotPower'),
    costs: { atk: document.getElementById('costAtk'), crit: document.getElementById('costCrit') }
};

/* --- ゲーム本体 --- */
const game = {
    user_token: 0,
    stage: 1,
    shotType: 'normal',
    stats: { atk: 3, atkLevel: 1, critRate: 0.05, critLevel: 1 },
    
    autoActive: false,
    autoTimer: null,
    autoSpeed: 1000,
    enemy: { maxHp: 50, currentHp: 50, name: "Slime", color: "#2ecc71", scale: 1, shake: 0 },

    init: async () => {
        const savedData = await api.loadGame();
        if (savedData) {
            game.user_token = savedData.user_token;
            game.stage = savedData.stage;
            game.stats = savedData.stats;
        }

        game.spawnEnemy();
        game.updateUI();
        loop(); // 描画ループ開始
        
        // イベントリスナー設定
        document.getElementById('shotNormal').onclick = () => game.setShotType('normal');
        document.getElementById('shotPower').onclick = () => game.setShotType('power');
        document.getElementById('upAtkBtn').onclick = () => { game.upgrade('atk'); api.saveGame(); };
        document.getElementById('upCritBtn').onclick = () => { game.upgrade('crit'); api.saveGame(); };
        document.getElementById('autoBtn').onclick = () => game.toggleAuto();
        
        canvas.addEventListener('mousedown', () => {
            if(!game.autoActive) {
                game.attack();
            }
        });
        
        // オートセーブ (5秒ごと)
        setInterval(() => api.saveGame(), 5000);
    },

    setShotType: (type) => {
        game.shotType = type;
        ui.shotNormal.classList.remove('active');
        ui.shotPower.classList.remove('active');
        if (type === 'normal') ui.shotNormal.classList.add('active');
        else ui.shotPower.classList.add('active');
    },

    getCost: (type) => {
        const base = { atk: 50, crit: 100 };
        const lvl = game.stats[type + 'Level'];
        return Math.floor(base[type] * Math.pow(1.5, lvl - 1));
    },

    spawnEnemy: () => {
        // ステージ進行に合わせてHP増加
        const baseHp = 50 * Math.pow(1.2, game.stage - 1);
        game.enemy.maxHp = Math.floor(baseHp);
        game.enemy.currentHp = game.enemy.maxHp;
        game.enemy.shake = 0;
        
        const types = [
            {name: "Slime", color: "#2ecc71"}, 
            {name: "Purple", color: "#9b59b6"}, 
            {name: "Blue", color: "#3498db"}, 
            {name: "White", color: "#ecf0f1"}, 
            {name: "Red", color: "#e74c3c"}
        ];
        const type = types[(game.stage - 1) % types.length];
        game.enemy.name = type.name;
        game.enemy.color = type.color;
        game.enemy.scale = 0; // 出現アニメーション用
    },

    attack: () => {
        if (game.enemy.currentHp <= 0) return;
        // モーダルが開いているときは攻撃不可
        if (document.getElementById('duModal').style.display === 'flex') return;

        let cost = 1; let dmgMult = 1.0; let critBonus = 0;
        if (game.shotType === 'power') { cost = 10; dmgMult = 10.0; critBonus = 0.03; }

        if (game.user_token < cost) {
            if(game.autoActive) game.toggleAuto(); // オート停止
            effects.addText("No Tokens!", canvas.width/2, canvas.height/2, "red", true);
            return;
        }

        game.user_token -= cost;

        // ダメージ計算
        let dmg = game.stats.atk * dmgMult * (0.9 + Math.random() * 0.2);
        let isCrit = Math.random() < (game.stats.critRate + critBonus);
        if (isCrit) dmg *= 2.0;
        dmg = Math.floor(dmg);
        if(dmg < 1) dmg = 1;

        game.enemy.currentHp -= dmg;
        game.enemy.shake = 10; // 揺れる演出
        effects.addText(dmg, canvas.width/2, canvas.height/2 - 50, isCrit ? "#f1c40f" : "#fff", isCrit);

        if (game.enemy.currentHp <= 0) {
            game.enemy.currentHp = 0;
            game.onWin();
        }
        game.updateUI();
    },

    onWin: () => {
        // 報酬計算
        const baseReward = Math.floor(game.enemy.maxHp / 10);
        const variance = Math.random() * 1.5 + 0.5;
        let reward = Math.floor(baseReward * variance) + 2;

        // オート中なら自動回収、手動ならダブルアップチャンス
        if (game.autoActive) {
            game.user_token += reward;
            effects.explodeCoins(reward);
            effects.addText("+" + reward, canvas.width/2, canvas.height/2, "#f1c40f", true);
            api.saveGame();
            setTimeout(() => {
                game.stage++;
                game.spawnEnemy();
                game.updateUI();
            }, 600);
        } else {
            doubleUp.init(reward);
        }
    },

    upgrade: (type) => {
        const cost = game.getCost(type);
        if (game.user_token >= cost) {
            game.user_token -= cost;
            game.stats[type + 'Level']++;
            
            if (type === 'atk') game.stats.atk += 2;
            if (type === 'crit') game.stats.critRate += 0.02;
            
            game.updateUI();
            effects.addText("UPGRADE!", canvas.width/2, canvas.height - 100, "#3498db");
        }
    },

    updateUI: () => {
        ui.user_token.innerText = Math.floor(game.user_token);
        ui.stage.innerText = "Lv." + game.stage;
        ui.hp.innerText = Math.ceil(game.enemy.currentHp) + " / " + game.enemy.maxHp;
        ui.costs.atk.innerText = game.getCost('atk');
        ui.costs.crit.innerText = game.getCost('crit');
        
        document.getElementById('upAtkBtn').disabled = game.user_token < game.getCost('atk');
        document.getElementById('upCritBtn').disabled = game.user_token < game.getCost('crit');
    },

    toggleAuto: () => {
        game.autoActive = !game.autoActive;
        if (game.autoActive) {
            ui.btnAuto.classList.add('active');
            ui.btnAuto.innerHTML = "AUTO<br>ON";
            game.autoTimer = setInterval(() => game.attack(), game.autoSpeed);
        } else {
            ui.btnAuto.classList.remove('active');
            ui.btnAuto.innerHTML = "AUTO<br>OFF";
            clearInterval(game.autoTimer);
        }
    }
};

/* --- ダブルアップ機能 --- */
const doubleUp = {
    pool: 0, dealerVal: 0, isActive: false,

    init: (amount) => {
        doubleUp.pool = amount;
        document.getElementById('duModal').style.display = 'flex';
        document.getElementById('duStartButtons').style.display = 'block';
        document.getElementById('duGameArea').style.display = 'none';
        document.getElementById('duWinAmount').innerText = amount + " Tokens";
        document.getElementById('duWinAmount').style.color = "#f1c40f";
        
        document.getElementById('btnDuStart').onclick = doubleUp.start;
        document.getElementById('btnDuCollect').onclick = () => { doubleUp.collect(); api.saveGame(); };
        document.getElementById('btnHigh').onclick = () => doubleUp.guess('high');
        document.getElementById('btnLow').onclick = () => doubleUp.guess('low');
    },

    start: () => {
        document.getElementById('duStartButtons').style.display = 'none';
        document.getElementById('duGameArea').style.display = 'block';
        doubleUp.nextRound();
    },

    nextRound: () => {
        doubleUp.isActive = true;
        doubleUp.dealerVal = Math.floor(Math.random() * 13) + 1;
        
        const dealerEl = document.getElementById('cardDealer');
        dealerEl.innerText = doubleUp.toCardStr(doubleUp.dealerVal);
        dealerEl.style.color = (doubleUp.dealerVal > 10 || doubleUp.dealerVal == 1) ? '#e74c3c' : 'black';
        
        const playerEl = document.getElementById('cardPlayer');
        playerEl.innerText = "?";
        playerEl.style.background = "#333";
        playerEl.style.color = "#333";
        
        document.getElementById('duMessage').innerText = "High or Low?";
        document.getElementById('duControls').style.display = "flex";
    },

    guess: (choice) => {
        if (!doubleUp.isActive) return;
        doubleUp.isActive = false;

        const playerVal = Math.floor(Math.random() * 13) + 1;
        const playerEl = document.getElementById('cardPlayer');
        playerEl.style.background = "white";
        playerEl.innerText = doubleUp.toCardStr(playerVal);
        playerEl.style.color = (playerVal > 10 || playerVal == 1) ? '#e74c3c' : 'black';

        let win = false;
        let draw = (playerVal === doubleUp.dealerVal);
        
        if (choice === 'high' && playerVal > doubleUp.dealerVal) win = true;
        if (choice === 'low' && playerVal < doubleUp.dealerVal) win = true;

        if (draw) {
            document.getElementById('duMessage').innerText = "DRAW! Try Again.";
            setTimeout(() => doubleUp.nextRound(), 1000);
        } else if (win) {
            doubleUp.pool *= 2;
            document.getElementById('duWinAmount').innerText = doubleUp.pool + " Tokens";
            document.getElementById('duMessage').innerText = "YOU WIN!!";
            effects.explodeCoins(20);
            setTimeout(() => {
                document.getElementById('duStartButtons').style.display = 'block';
                document.getElementById('duGameArea').style.display = 'none';
                document.getElementById('duMessage').innerText = "Double Up Again?";
            }, 1000);
        } else {
            doubleUp.pool = 0;
            document.getElementById('duWinAmount').innerText = "LOSE...";
            document.getElementById('duWinAmount').style.color = "gray";
            document.getElementById('duControls').style.display = "none";
            setTimeout(() => { doubleUp.collect(); api.saveGame(); }, 1500);
        }
    },

    collect: () => {
        document.getElementById('duModal').style.display = 'none';
        if (doubleUp.pool > 0) {
            game.user_token += doubleUp.pool;
            effects.explodeCoins(doubleUp.pool);
            effects.addText("GET " + doubleUp.pool + "!", canvas.width/2, canvas.height/2, "#f1c40f", true);
        }
        game.updateUI();
        setTimeout(() => { 
            game.stage++; 
            game.spawnEnemy(); 
            game.updateUI(); 
        }, 500);
    },

    toCardStr: (val) => {
        if(val===1) return "A"; if(val===11) return "J"; if(val===12) return "Q"; if(val===13) return "K";
        return val;
    }
};

/* --- 演出エンジン (Canvas) --- */
const effects = {
    texts: [], particles: [],
    
    addText: (text, x, y, color, isBig = false) => {
        effects.texts.push({ 
            text: text, 
            x: x + (Math.random()-0.5)*40, 
            y: y, 
            vy: -2, 
            life: 60, 
            color: color, 
            size: isBig ? 30 : 20 
        });
    },
    
    explodeCoins: (amount) => {
        const cnt = Math.min(amount, 60);
        for(let i=0; i<cnt; i++) {
            effects.particles.push({
                x: canvas.width/2, y: canvas.height/2,
                vx: (Math.random()-0.5)*15, vy: (Math.random()-0.5)*15-5,
                life: 60+Math.random()*30, gravity: 0.5
            });
        }
    },
    
    updateAndDraw: () => {
        // テキスト演出
        for(let i=0; i<effects.texts.length; i++){
            let t = effects.texts[i]; 
            t.y += t.vy; 
            t.life--;
            
            ctx.globalAlpha = Math.max(0, t.life/20);
            ctx.fillStyle = t.color; 
            ctx.font = `bold ${t.size}px Arial`;
            ctx.textAlign="center";
            ctx.lineWidth=4; 
            ctx.strokeStyle="black"; 
            ctx.strokeText(t.text, t.x, t.y);
            ctx.fillText(t.text, t.x, t.y);
            
            if(t.life<=0){ effects.texts.splice(i,1); i--; }
        }
        
        // パーティクル演出
        ctx.globalAlpha = 1.0;
        for(let i=0; i<effects.particles.length; i++){
            let p = effects.particles[i]; 
            p.x += p.vx; 
            p.y += p.vy; 
            p.vy += p.gravity; 
            p.life--;
            
            if(p.y > canvas.height-20){ p.y = canvas.height-20; p.vy *= -0.6; }
            
            ctx.fillStyle = "#f1c40f"; 
            ctx.beginPath(); 
            ctx.arc(p.x, p.y, 5, 0, Math.PI*2); 
            ctx.fill(); 
            ctx.stroke();
            
            if(p.life<=0){ effects.particles.splice(i,1); i--; }
        }
    }
};

/* --- メイン描画ループ --- */
function loop() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // 敵の描画
    if (game.enemy.currentHp > 0) {
        // 出現・被弾アニメーション
        if (game.enemy.scale < 1) game.enemy.scale += 0.1;
        let sx = (Math.random()-0.5) * game.enemy.shake;
        let sy = (Math.random()-0.5) * game.enemy.shake;
        game.enemy.shake *= 0.8;
        
        const breath = Math.sin(Date.now()/400)*5;
        
        ctx.save();
        ctx.translate(canvas.width/2 + sx, canvas.height/2 + 50 + sy);
        ctx.scale(game.enemy.scale, game.enemy.scale);
        
        // スライムの体
        ctx.fillStyle = game.enemy.color;
        ctx.beginPath();
        const r = 80 + breath;
        ctx.arc(0, 0, r, Math.PI, 0); // 上半円
        ctx.bezierCurveTo(r + 5, 60, -(r + 5), 60, -r, 0); // 下部
        ctx.fill();
        
        // 目
        ctx.fillStyle = "white"; 
        ctx.beginPath(); ctx.arc(-30,-20,15,0,Math.PI*2); ctx.fill();
        ctx.beginPath(); ctx.arc(30,-20,15,0,Math.PI*2); ctx.fill();
        
        ctx.fillStyle = "black"; 
        ctx.beginPath(); ctx.arc(-30,-20,5,0,Math.PI*2); ctx.fill();
        ctx.beginPath(); ctx.arc(30,-20,5,0,Math.PI*2); ctx.fill();
        
        // テキスト
        ctx.fillStyle = "white"; 
        ctx.font="bold 20px Arial"; 
        ctx.textAlign="center";
        ctx.fillText(`Lv.${game.stage} ${game.enemy.name}`, 0, -100);
        
        ctx.restore();
    }
    
    effects.updateAndDraw();
    requestAnimationFrame(loop);
}

// ゲーム開始
game.init();