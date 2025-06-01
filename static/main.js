// Replace UTC timestamp with local time for the visitor
(function(){
  var el = document.getElementById('last-updated');
  if(el){
    var utcText = el.textContent.match(/Last updated: (.*) UTC/);
    if(utcText && utcText[1]){
      var d = new Date(utcText[1]+' UTC');
      if(!isNaN(d)){
        var opts = {year:'numeric',month:'short',day:'numeric',hour:'2-digit',minute:'2-digit',second:'2-digit'};
        el.innerHTML = '<em>Last updated: '+d.toLocaleString(undefined,opts)+' (your local time)</em>';
      }
    }
  }
})();

// --- Financial animation: candlesticks, moving average, Bollinger Bands, volume, MACD ---
const canvas = document.getElementById('bg-canvas');
const ctx = canvas.getContext('2d');
function resize() {
    const dpr = window.devicePixelRatio || 1;
    canvas.width = window.innerWidth * dpr;
    canvas.height = window.innerHeight * dpr;
    canvas.style.width = window.innerWidth + 'px';
    canvas.style.height = window.innerHeight + 'px';
    ctx.setTransform(1, 0, 0, 1, 0, 0); // reset
    ctx.scale(dpr, dpr);
}
window.addEventListener('resize', resize);
resize();
const W = () => window.innerWidth;
const H = () => window.innerHeight;

// --- Chart data and helpers ---
let t = 0;
const FRAME_INTERVAL = 1000/30;
let candles = Array.from({length: 24}, (_, i) => {
    let base = H()/2 + Math.sin(i/3)*40;
    let open = base + Math.random()*20-10;
    let close = open + Math.random()*20-10;
    let high = Math.max(open, close) + Math.random()*8;
    let low = Math.min(open, close) - Math.random()*8;
    return {open, close, high, low};
});
let volumes = Array.from({length: 24}, () => 40 + Math.random()*60);
function calcMA(arr, n) {
    let out = Array(arr.length).fill(null);
    for(let i=n-1;i<arr.length;++i) {
        out[i] = arr.slice(i-n+1,i+1).reduce((a,b)=>a+b,0)/n;
    }
    return out;
}
function calcBollinger(arr, n, k) {
    let ma = calcMA(arr, n);
    let std = arr.map((_,i)=>{
        if(i<n-1) return null;
        let m = ma[i];
        let s = Math.sqrt(arr.slice(i-n+1,i+1).reduce((a,b)=>a+(b-m)*(b-m),0)/n);
        return s;
    });
    return {
        upper: ma.map((m,i)=>m!==null?m+k*std[i]:null),
        lower: ma.map((m,i)=>m!==null?m-k*std[i]:null)
    };
}
function calcMACD(arr) {
    function ema(n, arr) {
        let k = 2/(n+1), out = [];
        arr.forEach((v,i)=>{
            if(i===0) out.push(v);
            else out.push(v*k + out[out.length-1]*(1-k));
        });
        return out;
    }
    let macd = ema(12, arr).map((v,i)=>v-ema(26,arr)[i]);
    let signal = ema(9, macd);
    let hist = macd.map((v,i)=>v-signal[i]);
    return {macd, signal, hist};
}
let closes = candles.map(c=>c.close);
let ma20 = calcMA(closes, 20);
let ma50 = calcMA(closes, 50);
let boll = calcBollinger(closes, 20, 2);
let macdObj = calcMACD(closes);
let macdLine = macdObj.macd;
let signalLine = macdObj.signal;
let macdHist = macdObj.hist;

function drawGrid() {
    ctx.save();
    ctx.strokeStyle = '#b3d1e6';
    ctx.lineWidth = 1;
    for(let y=H()/4;y<H();y+=H()/4) {
        ctx.beginPath();
        ctx.moveTo(0,y);
        ctx.lineTo(W(),y);
        ctx.stroke();
    }
    ctx.restore();
}
function drawVolume() {
    ctx.save();
    let w = 24, gap = 10, x0 = 40;
    for(let i=0;i<volumes.length;++i) {
        let x = x0 + i*(w+gap);
        ctx.fillStyle = '#b3d1e6';
        ctx.globalAlpha = 0.5;
        ctx.fillRect(x, H()-volumes[i]-20, w, volumes[i]);
    }
    ctx.globalAlpha = 1;
    ctx.restore();
}
function drawLine() {
    ctx.save();
    ctx.beginPath();
    let w = 24, gap = 10, x0 = 40;
    for(let i=0;i<candles.length;++i) {
        let x = x0 + i*(w+gap) + w/2;
        ctx.lineTo(x, candles[i].close);
    }
    ctx.strokeStyle = '#0074d9';
    ctx.lineWidth = 2;
    ctx.shadowColor = '#0074d9';
    ctx.shadowBlur = 8;
    ctx.stroke();
    ctx.restore();
}
function drawMACD() {
    ctx.save();
    let base = H()-60;
    let scale = 8;
    ctx.beginPath();
    let w = 24, gap = 10, x0 = 40;
    for(let i=0;i<macdHist.length;++i) {
        let x = x0 + i*(w+gap) + w/2;
        ctx.lineTo(x, base-macdHist[i]*scale);
    }
    ctx.strokeStyle = '#ff4136';
    ctx.lineWidth = 2;
    ctx.globalAlpha = 0.7;
    ctx.stroke();
    ctx.globalAlpha = 1;
    ctx.restore();
    ctx.save();
    ctx.beginPath();
    for(let i=0;i<macdLine.length;++i) {
        let x = x0 + i*(w+gap) + w/2;
        ctx.lineTo(x, base-macdLine[i]*scale);
    }
    ctx.strokeStyle = '#0074d9';
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.restore();
    ctx.save();
    ctx.beginPath();
    for(let i=0;i<signalLine.length;++i) {
        let x = x0 + i*(w+gap) + w/2;
        ctx.lineTo(x, base-signalLine[i]*scale);
    }
    ctx.strokeStyle = '#2ecc40';
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.restore();
}
// --- MAKE ANIMATION MORE OBVIOUS ---
function drawCandles() {
    let w = 24;
    let gap = 10;
    let x0 = 40;
    for (let i=0; i<candles.length; ++i) {
        let c = candles[i];
        let x = x0 + i*(w+gap);
        ctx.save();
        ctx.shadowColor = c.close > c.open ? '#2ecc40' : '#ff4136';
        ctx.shadowBlur = 16;
        ctx.strokeStyle = '#222';
        ctx.beginPath();
        ctx.moveTo(x+w/2, c.high);
        ctx.lineTo(x+w/2, c.low);
        ctx.stroke();
        ctx.restore();
        ctx.save();
        ctx.lineWidth = 10;
        ctx.strokeStyle = c.close > c.open ? '#2ecc40' : '#ff4136';
        ctx.shadowColor = c.close > c.open ? '#2ecc40' : '#ff4136';
        ctx.shadowBlur = 24 + 8*Math.abs(Math.sin(Date.now()/400));
        ctx.beginPath();
        ctx.moveTo(x+w/2, c.open);
        ctx.lineTo(x+w/2, c.close);
        ctx.stroke();
        ctx.restore();
    }
}
function drawMA(ma, color) {
    ctx.save();
    ctx.beginPath();
    let w = 24, gap = 10, x0 = 40;
    for (let i=0; i<ma.length; ++i) {
        let x = x0 + i*(w+gap) + w/2;
        if (ma[i]!==null) ctx.lineTo(x, ma[i]);
    }
    ctx.strokeStyle = color;
    ctx.lineWidth = 4;
    ctx.globalAlpha = 0.85;
    ctx.shadowColor = color;
    ctx.shadowBlur = 12;
    ctx.stroke();
    ctx.globalAlpha = 1;
    ctx.restore();
}
function drawBollinger(boll, colorU, colorL) {
    ctx.save();
    ctx.beginPath();
    let w = 24, gap = 10, x0 = 40;
    for (let i=0; i<boll.upper.length; ++i) {
        let x = x0 + i*(w+gap) + w/2;
        if (boll.upper[i]!==null) ctx.lineTo(x, boll.upper[i]);
    }
    ctx.strokeStyle = colorU;
    ctx.lineWidth = 3;
    ctx.setLineDash([8,6]);
    ctx.shadowColor = colorU;
    ctx.shadowBlur = 10;
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.beginPath();
    for (let i=0; i<boll.lower.length; ++i) {
        let x = x0 + i*(w+gap) + w/2;
        if (boll.lower[i]!==null) ctx.lineTo(x, boll.lower[i]);
    }
    ctx.strokeStyle = colorL;
    ctx.shadowColor = colorL;
    ctx.shadowBlur = 10;
    ctx.stroke();
    ctx.restore();
}
// --- END MORE OBVIOUS ---
let lastFrame = 0;
let pageVisible = true;
document.addEventListener('visibilitychange', function() {
    pageVisible = !document.hidden;
});
function animate(now) {
    if (!pageVisible) { requestAnimationFrame(animate); return; }
    if (!lastFrame || now - lastFrame > FRAME_INTERVAL) {
        ctx.clearRect(0,0,W(),H());
        drawGrid();
        drawVolume();
        drawCandles();
        drawMA(ma20, '#0074d9');
        drawMA(ma50, '#b10dc9');
        drawBollinger(boll, '#39cccc', '#ffdc00');
        drawLine();
        drawMACD();
        if (t++ % 10 === 0) {
            candles.shift();
            let last = candles[candles.length-1];
            let open = last.close;
            let close_ = open + (Math.random()-0.5)*H()/30;
            let high_ = Math.max(open, close_) + Math.random()*10;
            let low_ = Math.min(open, close_) - Math.random()*10;
            candles.push({open: open, close: close_, high: high_, low: low_});
            volumes.shift();
            volumes.push(40 + Math.random()*60 + Math.abs(close_-open)*2);
            let closes = candles.map(c=>c.close);
            ma20 = calcMA(closes, 20);
            ma50 = calcMA(closes, 50);
            boll = calcBollinger(closes, 20, 2);
            macdObj = calcMACD(closes);
            macdLine = macdObj.macd;
            signalLine = macdObj.signal;
            macdHist = macdObj.hist;
        }
        lastFrame = now;
    }
    requestAnimationFrame(animate);
}
animate();
// --- END OPTIMIZED ---
