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
// Remove animation loop and dynamic updates. Draw once on load.
function drawAll() {
    ctx.clearRect(0,0,W(),H());
    drawGrid();
    drawVolume();
    drawCandles();
    drawMA(ma20, '#0074d9');
    drawMA(ma50, '#b10dc9');
    drawBollinger(boll, '#39cccc', '#ffdc00');
    drawLine();
    drawMACD();
    // If you have extra indicators, draw them here as well
}
// --- Utility: Generate random positions for mini-charts ---
function randomPositions(n, margin=60) {
    let positions = [];
    for (let i = 0; i < n; ++i) {
        let x = Math.random() * (W() - margin*2) + margin;
        let y = Math.random() * (H() - margin*2) + margin;
        positions.push([x, y]);
    }
    return positions;
}

// --- More technical indicators ---
function calcATR(candles, n) {
    let atr = Array(candles.length).fill(null);
    for (let i = n; i < candles.length; ++i) {
        let sum = 0;
        for (let j = i - n + 1; j <= i; ++j) {
            let tr = Math.max(
                candles[j].high - candles[j].low,
                Math.abs(candles[j].high - candles[j-1].close),
                Math.abs(candles[j].low - candles[j-1].close)
            );
            sum += tr;
        }
        atr[i] = sum / n;
    }
    return atr;
}
function calcCCI(candles, n) {
    let cci = Array(candles.length).fill(null);
    for (let i = n-1; i < candles.length; ++i) {
        let tp = candles.slice(i-n+1,i+1).map(c=>(c.high+c.low+c.close)/3);
        let ma = tp.reduce((a,b)=>a+b,0)/n;
        let md = tp.reduce((a,b)=>a+Math.abs(b-ma),0)/n;
        cci[i] = (tp[n-1]-ma)/(0.015*md||1);
    }
    return cci;
}
function calcADX(candles, n) {
    let adx = Array(candles.length).fill(null);
    let pdm = Array(candles.length).fill(0), ndm = Array(candles.length).fill(0), tr = Array(candles.length).fill(0);
    for (let i = 1; i < candles.length; ++i) {
        let up = candles[i].high - candles[i-1].high;
        let dn = candles[i-1].low - candles[i].low;
        pdm[i] = up > dn && up > 0 ? up : 0;
        ndm[i] = dn > up && dn > 0 ? dn : 0;
        tr[i] = Math.max(
            candles[i].high - candles[i].low,
            Math.abs(candles[i].high - candles[i-1].close),
            Math.abs(candles[i].low - candles[i-1].close)
        );
    }
    let smooth = (arr, n) => arr.map((_,i)=>i<n-1?null:arr.slice(i-n+1,i+1).reduce((a,b)=>a+b,0)/n);
    let pdi = smooth(pdm, n).map((v,i)=>v===null?null:100*v/(smooth(tr,n)[i]||1));
    let ndi = smooth(ndm, n).map((v,i)=>v===null?null:100*v/(smooth(tr,n)[i]||1));
    let dx = pdi.map((v,i)=>v===null||ndi[i]===null?null:100*Math.abs(v-ndi[i])/(v+ndi[i]||1));
    for (let i = n-1; i < candles.length; ++i) {
        adx[i] = dx.slice(i-n+1,i+1).reduce((a,b)=>a+(b||0),0)/n;
    }
    return adx;
}
function calcWilliamsR(candles, n) {
    let wr = Array(candles.length).fill(null);
    for (let i = n-1; i < candles.length; ++i) {
        let high = Math.max(...candles.slice(i-n+1,i+1).map(c=>c.high));
        let low = Math.min(...candles.slice(i-n+1,i+1).map(c=>c.low));
        wr[i] = -100 * (high - candles[i].close) / (high - low || 1);
    }
    return wr;
}
function calcOBV(closes, volumes) {
    let obv = [0];
    for (let i = 1; i < closes.length; ++i) {
        obv[i] = obv[i-1] + (closes[i] > closes[i-1] ? volumes[i] : closes[i] < closes[i-1] ? -volumes[i] : 0);
    }
    return obv;
}
function calcROC(arr, n) {
    let roc = Array(arr.length).fill(null);
    for (let i = n; i < arr.length; ++i) {
        roc[i] = 100 * (arr[i] - arr[i-n]) / (arr[i-n]||1);
    }
    return roc;
}
function calcEMA(arr, n) {
    let k = 2/(n+1), ema = [arr[0]];
    for (let i = 1; i < arr.length; ++i) {
        ema[i] = arr[i]*k + ema[i-1]*(1-k);
    }
    return ema;
}
function calcSMA(arr, n) {
    let sma = Array(arr.length).fill(null);
    for (let i = n-1; i < arr.length; ++i) {
        sma[i] = arr.slice(i-n+1,i+1).reduce((a,b)=>a+b,0)/n;
    }
    return sma;
}

// Calculate all indicators
let rsi = calcRSI(closes, 14);
let stoch = calcStochastic(closes, 14);
let sar = calcParabolicSAR(candles);
let atr = calcATR(candles, 14);
let cci = calcCCI(candles, 14);
let adx = calcADX(candles, 14);
let willr = calcWilliamsR(candles, 14);
let obv = calcOBV(closes, volumes);
let roc = calcROC(closes, 10);
let ema = calcEMA(closes, 10);
let sma = calcSMA(closes, 10);

// --- Draw mini-indicator charts at random positions ---
function drawMiniChart(data, color, label, x, y, w=80, h=32) {
    ctx.save();
    ctx.translate(x, y);
    ctx.beginPath();
    let n = data.length;
    for (let i = 0; i < n; ++i) {
        let px = (i/(n-1))*w;
        let val = data[i];
        if (val === null || isNaN(val)) continue;
        let min = Math.min(...data.filter(v=>v!==null)), max = Math.max(...data.filter(v=>v!==null));
        let py = h - ((val-min)/(max-min||1))*h;
        if (i === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
    }
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.globalAlpha = 0.7;
    ctx.stroke();
    ctx.globalAlpha = 1;
    ctx.font = 'bold 10px sans-serif';
    ctx.fillStyle = color;
    ctx.fillText(label, 4, 12);
    ctx.restore();
}

function drawAll() {
    ctx.clearRect(0,0,W(),H());
    drawGrid();
    drawVolume();
    drawCandles();
    drawMA(ma20, '#0074d9');
    drawMA(ma50, '#b10dc9');
    drawBollinger(boll, '#39cccc', '#ffdc00');
    drawLine();
    drawMACD();
    // Scatter mini-indicator charts all over the screen
    let indicators = [
        [rsi, '#ff851b', 'RSI'],
        [stoch, '#b10dc9', 'Stoch'],
        [sar, '#01ff70', 'SAR'],
        [atr, '#39cccc', 'ATR'],
        [cci, '#ff4136', 'CCI'],
        [adx, '#0074d9', 'ADX'],
        [willr, '#ffdc00', 'Williams %R'],
        [obv, '#0a192f', 'OBV'],
        [roc, '#2ecc40', 'ROC'],
        [ema, '#b3b3b3', 'EMA'],
        [sma, '#ff851b', 'SMA']
    ];
    let positions = randomPositions(indicators.length, 100);
    for (let i = 0; i < indicators.length; ++i) {
        drawMiniChart(indicators[i][0], indicators[i][1], indicators[i][2], positions[i][0], positions[i][1]);
    }
}
drawAll();
// --- END STATIC CHART ---
