from flask import Flask, request, jsonify
import os, re, json, time, uuid
import requests

app = Flask(__name__)
PORT = int(os.environ.get("PORT", 8080))
DIRECTORY = "uploads"
os.makedirs(DIRECTORY, exist_ok=True)
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 500 MB per upload

# Set this in Render -> your service -> Environment as GEMINI_API_KEY
PERMANENT_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
GEMINI = "https://generativelanguage.googleapis.com"

HTML = r'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MatrixMedia Studio</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        @import url('https://fonts.cdnfonts.com/css/apple-color-emoji');
        
        body { 
            background: #000000; 
            color: #e5e7eb; 
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Apple Color Emoji", sans-serif; 
            margin: 0;
            padding: 40px 20px; 
            box-sizing: border-box;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            min-height: 100vh;
            -webkit-font-smoothing: antialiased;
        }
        
        .box { 
            background: #0f1115; 
            padding: 40px; 
            border-radius: 16px; 
            width: 100%;
            max-width: 1000px; 
            border: 1px solid #1f2937;
            box-shadow: 0 20px 40px -10px rgba(0,0,0,0.8); 
        }
        
        h2 { margin-top: 0; margin-bottom: 8px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px; font-size: 28px; }
        p { color: #9ca3af; line-height: 1.5; }
        
        .form-group { margin-bottom: 24px; text-align: left; }
        
        label { font-size: 14px; font-weight: 600; color: #9ca3af; display: block; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.5px; }
        
        input[type="text"], input[type="password"], input[type="file"], select { 
            width: 100%; padding: 14px 16px; background: #181b21; color: #f3f4f6; 
            border: 1px solid #374151; border-radius: 8px; font-size: 15px; 
            box-sizing: border-box; transition: border-color 0.2s;
        }
        input[type="text"]:focus, input[type="password"]:focus, select:focus { outline: none; border-color: #3b82f6; }
        
        button {
            width: 100%; background: #2563eb; color: white; font-size: 16px;
            padding: 16px; border-radius: 8px; font-weight: 700; cursor: pointer; 
            border: none; margin-top: 10px; transition: all 0.2s ease; letter-spacing: 0.5px;
        }
        button:hover { background: #1d4ed8; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3); }
        button:disabled { background: #374151; cursor: not-allowed; color: #6b7280; transform: none; box-shadow: none; }
        
        .hidden { display: none !important; }
        
        .video-box { background: #111827; padding: 24px; border-radius: 12px; margin-bottom: 30px; border: 1px solid #1f2937; }
        .video-title { color: #f3f4f6; margin-top: 0; margin-bottom: 16px; font-size: 18px; font-weight: 600; }
        .output-grid { display: flex; flex-direction: column; gap: 16px; margin-top: 20px; }
        .card-section { background: #181b21; border: 1px solid #374151; padding: 20px; border-radius: 8px; }
        .card-title { font-weight: 700; color: #60a5fa; display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; font-size: 15px; text-transform: uppercase; letter-spacing: 0.5px; }
        .card-body { white-space: pre-wrap; font-size: 14px; line-height: 1.7; color: #d1d5db; }
        .copy-btn { width: auto; padding: 6px 14px; font-size: 12px; margin: 0; background: #1f2937; border: 1px solid #374151; color: #e5e7eb; font-weight: 600; border-radius: 6px; text-transform: none; }
        .copy-btn:hover { background: #374151; color: #fff; }
        
        .badge { background: rgba(59, 130, 246, 0.1); color: #60a5fa; padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 700; border: 1px solid rgba(96, 165, 250, 0.2); display: inline-block; margin-bottom: 24px; }
        
        .preview-container {
            width: 100%; background: #000; border-radius: 10px; position: relative;
            text-align: center; overflow: hidden; display: flex; justify-content: center;
            align-items: center; border: 1px solid rgba(255,255,255,0.15);
        }
        .preview-container:fullscreen { width: 100vw; height: 100vh; border: none; border-radius: 0; }
        video { width: 100%; max-height: 450px; display: block; background: #000; object-fit: contain; }
        .preview-container:fullscreen video { height: 100%; max-height: 100vh; }
        .overlay-preview-box {
            position: absolute; top: 20px; left: 50%; transform: translateX(-50%);
            color: #ffffff; font-weight: 800; font-size: 16px;
            text-shadow: 2px 2px 6px rgba(0,0,0,0.9), 0 0 10px rgba(0,0,0,0.8);
            cursor: grab; z-index: 100; background: transparent; text-align: center;
            width: 90%; user-select: none; border: none; padding: 4px 10px;
        }
        .overlay-preview-box:active { cursor: grabbing; }
        
        .editor-toolbar {
            display: flex; gap: 8px; margin-top: 15px; background: #0d1117; padding: 12px; 
            border-radius: 10px; align-items: center; flex-wrap: wrap;
        }
        .editor-toolbar input[type="text"], .editor-toolbar select { width: auto; flex: 1; padding: 10px; margin: 0; font-size: 13px; border-radius: 6px; }
        .editor-toolbar input[type="range"] { margin: auto 5px; width: 60px; }
        .export-btn { width: auto; margin: 0; padding: 10px 12px; background: linear-gradient(90deg, #10b981, #059669); font-size: 13px; }
        
        #auth { text-align: center; padding: 20px 0; position: relative; z-index: 50; }
    </style>
</head>
<body>

<div class="box">
    <!-- AUTHENTICATION SCREEN -->
    <div id="auth" style="text-align: center;">
        <h2 class="glow-text">MatrixMedia Pro</h2>
        <p style="margin-bottom: 30px; color: #8b949e;">Enter your team passcode to access the AI dashboard.</p>
        
        <div style="max-width: 400px; margin: 0 auto; text-align: left;">
            <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #a5b4fc;">Secure Password</label>
            <div style="display: flex; gap: 10px; margin-bottom: 20px;">
                <input type="password" id="pass" placeholder="Enter password..." required style="flex: 1; padding: 14px; background: #0d1117; color: #fff; border: 1px solid #30363d; border-radius: 10px; font-size: 15px;" onkeypress="if(event.key === 'Enter') check();">
                <button type="button" onclick="togglePass()" style="width: 55px; margin: 0; padding: 0; background: #21262d; border: 1px solid #30363d; border-radius: 10px; font-size: 20px; cursor: pointer; display: flex; align-items: center; justify-content: center;">👁️</button>
            </div>
            <button type="button" onclick="check()" style="width: 100%; background: linear-gradient(90deg, #00c6ff, #0072ff); color: white; font-size: 16px; padding: 16px; border-radius: 10px; font-weight: 800; cursor: pointer; border: none;">Access Tool 🚀</button>
        </div>
    </div>

    <!-- MAIN DASHBOARD -->
    <div id="main" class="hidden">
        <h2>🎬 MatrixMedia V74</h2>
        <div class="badge">✨ Pro Edit Studio | 🔥 Emoji Engine | 📥 Master Export</div>
        
        <form id="uploadForm" onsubmit="event.preventDefault(); run();">
            <div class="form-group">
                <label>1. Upload Videos (.mp4, .mov):</label>
                <input type="file" id="vid" accept="video/*" multiple required onchange="showFileNames(event)">
                <div id="fileList" style="font-size: 13px; color: #58a6ff; margin-top: 10px; font-weight: 600;"></div>
            </div>
            
            <div class="form-group">
                <label>2. Content Niche:</label>
                <select id="niche">
                    <option>Luxury & Wealth Motivation</option>
                    <option>Fitness & Bodybuilding</option>
                    <option>Relationship Transparency</option>
                    <option>Sigma & Mindset</option>
                    <option>Auto-Detect Strictly From Video Frames</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>3. Video Context (Optional):</label>
                <input type="text" id="context" placeholder="Brief note about the clip...">
            </div>
            
            <button type="submit" id="genBtn">⚡ Transcribe & Generate All</button>
        </form>
        
        <div id="out" style="margin-top: 30px;"></div>
    </div>
</div>

<script>
let emojiCache = {};
function getEmojiHex(emoji) {
    let comp = [];
    for (let i = 0; i < emoji.length; i++) {
        let cp = emoji.codePointAt(i);
        comp.push(cp.toString(16));
        if (cp > 0xffff) i++;
    }
    if (comp.length > 1) comp = comp.filter(c => c !== 'fe0f');
    return comp.join('-');
}
function loadEmoji(emojiChar) {
    if (emojiCache[emojiChar]) return;
    let hex = getEmojiHex(emojiChar);
    let img = new Image();
    img.crossOrigin = "anonymous"; 
    img.src = `https://cdnjs.cloudflare.com/ajax/libs/emoji-datasource-apple/15.0.0/img/apple/64/${hex}.png`;
    emojiCache[emojiChar] = img;
}
const commonEmojis = ["🔥", "💯", "👑", "🚀", "💎", "👀", "⚡", "💸", "💀", "🤡", "📈", "👇", "👉"];
commonEmojis.forEach(loadEmoji);
const emojiRegex = /([\p{Emoji_Presentation}\p{Extended_Pictographic}])/gu;

function splitTextAndEmojis(text) {
    let parts = [];
    let lastIdx = 0, match;
    emojiRegex.lastIndex = 0; 
    while ((match = emojiRegex.exec(text)) !== null) {
        if (match.index > lastIdx) parts.push({ type: 'text', value: text.substring(lastIdx, match.index) });
        parts.push({ type: 'emoji', value: match[0] });
        loadEmoji(match[0]);
        lastIdx = emojiRegex.lastIndex;
    }
    if (lastIdx < text.length) parts.push({ type: 'text', value: text.substring(lastIdx) });
    return parts;
}
function renderTextWithHtmlEmojis(text) {
    let parts = splitTextAndEmojis(text), html = "";
    for(let p of parts) {
        if(p.type === 'text') {
            let div = document.createElement('div');
            div.innerText = p.value;
            html += div.innerHTML;
        } else {
            let img = emojiCache[p.value];
            if(img && img.src) html += `<img src="${img.src}" style="height: 1.2em; width: 1.2em; vertical-align: -0.25em; margin: 0 0.1em; display: inline-block; border: none; filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.5));">`;
            else html += p.value; 
        }
    }
    return html;
}

function togglePass() {
    const p = document.getElementById('pass');
    p.type = p.type === 'password' ? 'text' : 'password';
}
function check() { 
    if(document.getElementById("pass").value === "2008") { 
        document.getElementById("auth").classList.add("hidden"); 
        document.getElementById("main").classList.remove("hidden"); 
    } else alert("❌ Incorrect Password!");
}
function showFileNames(event) {
    const files = event.target.files;
    document.getElementById("fileList").innerHTML = files.length > 0 ? `📁 <b>${files.length} videos selected.</b> Ready.` : "";
}
function copyCardText(btn) {
    navigator.clipboard.writeText(btn.parentElement.nextElementSibling.innerText).then(() => {
        let orig = btn.innerText;
        btn.innerText = "✅ Copied!";
        setTimeout(() => btn.innerText = orig, 2000);
    });
}
function toggleFullscreen(index) {
    let container = document.getElementById(`preview_container_${index}`);
    if (!document.fullscreenElement) container.requestFullscreen();
    else document.exitFullscreen();
}

async function processSingleVideo(f, index, niche, context) {
    let statusBox = document.getElementById(`res_${index}`);
    statusBox.innerHTML = "<p style='color:#f0b37e;'>⚡ <b>Uploading & Analyzing video...</b></p>";
    
    const fd = new FormData();
    fd.append("video", f);
    fd.append("niche", niche);
    fd.append("context", context);
    
    try {
        const res = await fetch("/generate", {method: "POST", body: fd});
        const textResp = await res.text();
        let d;
        try { d = JSON.parse(textResp); } catch(err) { throw new Error("Server error: " + textResp.substring(0, 80)); }

        if(d.structured) {
            let s = d.structured, videoUrl = URL.createObjectURL(f);
            let html = '<div class="output-grid">';
            html += `<div class="card-section">
                <div class="card-title">🎥 Interactive Hook Studio</div>
                <div class="preview-container" id="preview_container_${index}">
                    <video id="vid_el_${index}" src="${videoUrl}" controls playsinline></video>
                    <div id="overlay_txt_${index}" class="overlay-preview-box" onmousedown="startDrag(event, 'overlay_txt_${index}')">🔥 Select a hook below</div>
                    <div id="overlay_watermark_${index}" class="overlay-preview-box" onmousedown="startDrag(event, 'overlay_watermark_${index}')" style="top: 85%; font-size: 14px; opacity: 0.8; color: rgba(255,255,255,0.7);">@Watermark</div>
                </div>
                <div class="editor-toolbar">
                    <select id="hook_select_${index}" onchange="updateTextInput(${index})" style="flex:1; max-width:18%;"><option value="">-- AI Hooks --</option></select>
                    <input type="text" id="custom_text_${index}" value="🔥 Select hook" oninput="updateOverlayFromInput(${index})" style="flex:2;" placeholder="Edit hook...">
                    <select id="emoji_select_${index}" onchange="insertEmoji(${index})" style="flex:0.5; max-width:80px; padding: 10px 5px;"><option value="">🙂 Emoji</option><option value="🔥">🔥</option><option value="💯">💯</option><option value="👑">👑</option><option value="🚀">🚀</option><option value="💎">💎</option><option value="👀">👀</option><option value="⚡">⚡</option><option value="💸">💸</option><option value="💀">💀</option><option value="🤡">🤡</option><option value="📈">📈</option><option value="👇">👇</option><option value="👉">👉</option></select>
                    <div style="display:flex; align-items:center;"><label style="margin:0; font-size:12px; color:#38bdf8;">Size:</label><input type="range" id="size_range_${index}" min="10" max="60" value="16" oninput="updateSize(${index})"></div>
                    <button type="button" class="export-btn" style="background:#3b82f6;" onclick="toggleFullscreen(${index})">🔲 FS</button>
                    <button type="button" class="export-btn" onclick="exportVideoWithOverlay(${index}, '${f.name.replace(/'/g, "\\'")}')">📥 Export HD</button>
                </div>
            </div>`;
            html += `<div class="card-section"><div class="card-title">📝 Transcript <button class="copy-btn" onclick="copyCardText(this)">Copy</button></div><div class="card-body">${s.transcript || ''}</div></div>`;
            html += `<div class="card-section"><div class="card-title">👁️ Visual Analysis <button class="copy-btn" onclick="copyCardText(this)">Copy</button></div><div class="card-body">${s.visual || ''}</div></div>`;
            html += `<div class="card-section"><div class="card-title">🔥 Hooks <button class="copy-btn" onclick="copyCardText(this)">Copy</button></div><div class="card-body">${s.hooks || ''}</div></div>`;
            html += `<div class="card-section"><div class="card-title">🎬 YouTube Shorts <button class="copy-btn" onclick="copyCardText(this)">Copy</button></div><div class="card-body">${s.yt || ''}</div></div>`;
            html += `<div class="card-section"><div class="card-title">📸 IG Reels <button class="copy-btn" onclick="copyCardText(this)">Copy</button></div><div class="card-body">${s.ig || ''}</div></div>`;
            html += `<div class="card-section"><div class="card-title">🎵 TikTok <button class="copy-btn" onclick="copyCardText(this)">Copy</button></div><div class="card-body">${s.tiktok || ''}</div></div>`;
            html += `<div class="card-section"><div class="card-title">👻 Snapchat Spotlight <button class="copy-btn" onclick="copyCardText(this)">Copy</button></div><div class="card-body">${s.snap || ''}</div></div>`;
            html += `<div class="card-section"><div class="card-title">📘 Facebook Reels <button class="copy-btn" onclick="copyCardText(this)">Copy</button></div><div class="card-body">${s.fb || ''}</div></div>`;
            html += `<div class="card-section"><div class="card-title">🏷️ Hashtags <button class="copy-btn" onclick="copyCardText(this)">Copy</button></div><div class="card-body">${s.hashtags || ''}</div></div>`;
            html += '</div>';
            statusBox.innerHTML = html;
            setTimeout(() => { populateHookDropdown(index, s.hooks); updateOverlayFromInput(index); }, 100);
        } else {
            statusBox.innerHTML = `<p style='color:#ff7b72;'>Error: ${d.error}</p>`;
        }
    } catch(e) { statusBox.innerHTML = `<p style='color:#ff7b72;'>Error: ${e.message}</p>`; }
}

function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

async function run() {
    const files = Array.from(document.getElementById('vid').files);
    if (!files.length) return;
    const niche = document.getElementById('niche').value;
    const context = document.getElementById('context').value;
    const btn = document.getElementById('genBtn');
    const out = document.getElementById('out');
    btn.disabled = true;
    out.innerHTML = `<h3 style="color:#38bdf8;">🚀 Processing ${files.length} Videos (3x Batch Mode)...</h3>`;
    files.forEach((f, i) => {
        out.insertAdjacentHTML('beforeend',
            `<div class="video-box"><h3 class="video-title">🎞️ ${i + 1}. ${escapeHtml(f.name)}</h3><div id="res_${i}"></div></div>`);
    });
    let next = 0;
    async function worker() {
        while (next < files.length) {
            const i = next++;
            await processSingleVideo(files[i], i, niche, context);
        }
    }
    await Promise.all([worker(), worker(), worker()]);
    out.insertAdjacentHTML('beforeend', '<h3 style="color:#4ade80;">✅ All Videos Processed!</h3>');
    btn.disabled = false;
}

function drawOverlayText(ctx, text, cx, topY, fontPx, maxWidth) {
    const parts = splitTextAndEmojis(text);
    const tokens = [];
    for (const p of parts) {
        if (p.type === 'emoji') tokens.push({ t: 'emoji', v: p.value });
        else p.value.split(/(\s+)/).forEach(w => { if (w) tokens.push({ t: 'text', v: w }); });
    }
    ctx.font = `800 ${fontPx}px Inter, -apple-system, sans-serif`;
    const widthOf = tk => tk.t === 'emoji' ? fontPx * 1.2 : ctx.measureText(tk.v).width;
    const lines = [[]];
    let cur = 0;
    for (const tk of tokens) {
        const w = widthOf(tk);
        if (cur + w > maxWidth && lines[lines.length - 1].length && tk.v.trim() !== '') {
            lines.push([]); cur = 0;
        }
        lines[lines.length - 1].push(tk); cur += w;
    }
    const lineH = fontPx * 1.3;
    ctx.textBaseline = 'top';
    ctx.textAlign = 'left';
    ctx.fillStyle = '#ffffff';
    ctx.shadowColor = 'rgba(0,0,0,0.9)';
    ctx.shadowBlur = fontPx * 0.4;
    ctx.shadowOffsetX = fontPx * 0.1;
    ctx.shadowOffsetY = fontPx * 0.1;
    lines.forEach((line, li) => {
        const lw = line.reduce((a, tk) => a + widthOf(tk), 0);
        let x = cx - lw / 2;
        const y = topY + li * lineH;
        for (const tk of line) {
            if (tk.t === 'emoji') {
                const img = emojiCache[tk.v];
                if (img && img.complete && img.naturalWidth) ctx.drawImage(img, x, y, fontPx * 1.2, fontPx * 1.2);
                x += fontPx * 1.2;
            } else {
                ctx.fillText(tk.v, x, y);
                x += ctx.measureText(tk.v).width;
            }
        }
    });
    ctx.shadowColor = 'transparent';
}

async function exportVideoWithOverlay(index, fileName) {
    const video = document.getElementById(`vid_el_${index}`);
    const hookBox = document.getElementById(`overlay_txt_${index}`);
    const wmBox = document.getElementById(`overlay_watermark_${index}`);
    if (!video || !video.videoWidth) { alert("Video is not loaded yet."); return; }
    if (typeof MediaRecorder === 'undefined') { alert("Your browser does not support export. Use Chrome or Brave."); return; }

    const W = video.videoWidth, H = video.videoHeight;
    const canvas = document.createElement('canvas');
    canvas.width = W; canvas.height = H;
    const ctx = canvas.getContext('2d');

    const vr = video.getBoundingClientRect();
    const scale = Math.min(vr.width / W, vr.height / H);
    const offX = (vr.width - W * scale) / 2, offY = (vr.height - H * scale) / 2;
    function place(box) {
        const b = box.getBoundingClientRect();
        return {
            cx: (b.left + b.width / 2 - vr.left - offX) / scale,
            top: (b.top - vr.top - offY) / scale,
            font: parseFloat(getComputedStyle(box).fontSize) / scale,
            text: box.innerText
        };
    }
    const hook = place(hookBox), wm = place(wmBox);

    const stream = canvas.captureStream(30);
    try {
        const vs = video.captureStream ? video.captureStream() : video.mozCaptureStream();
        vs.getAudioTracks().forEach(t => stream.addTrack(t));
    } catch (e) { console.warn("No audio track captured", e); }

    const mime = ["video/mp4;codecs=avc1", "video/webm;codecs=vp9,opus", "video/webm"].find(m => MediaRecorder.isTypeSupported(m));
    const rec = new MediaRecorder(stream, mime ? { mimeType: mime, videoBitsPerSecond: 8000000 } : {});
    const chunks = [];
    rec.ondataavailable = e => { if (e.data.size) chunks.push(e.data); };

    const btns = document.querySelectorAll(`#preview_container_${index} ~ .editor-toolbar .export-btn`);
    btns.forEach(b => b.disabled = true);
    const done = new Promise(res => { rec.onstop = res; });

    video.pause(); video.currentTime = 0;
    await new Promise(r => { video.onseeked = r; });
    rec.start();
    await video.play();

    function frame() {
        ctx.drawImage(video, 0, 0, W, H);
        drawOverlayText(ctx, hook.text, hook.cx, hook.top, hook.font, W * 0.9);
        drawOverlayText(ctx, wm.text, wm.cx, wm.top, wm.font, W * 0.9);
        if (!video.ended && !video.paused) requestAnimationFrame(frame);
        else rec.stop();
    }
    video.onended = () => { if (rec.state !== 'inactive') rec.stop(); };
    frame();
    await done;
    btns.forEach(b => b.disabled = false);

    const type = rec.mimeType || 'video/webm';
    const ext = type.includes('mp4') ? 'mp4' : 'webm';
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob(chunks, { type }));
    a.download = fileName.replace(/\.[^.]+$/, '') + '_hook.' + ext;
    a.click();
}

let activeDrag = null;
function startDrag(e, id) {
    let box = document.getElementById(id);
    if (!box) return;
    activeDrag = { element: box, startX: e.clientX, startY: e.clientY, initialLeft: box.offsetLeft, initialTop: box.offsetTop };
    document.addEventListener('mousemove', onDrag);
    document.addEventListener('mouseup', stopDrag);
    e.preventDefault();
}
function onDrag(e) {
    if (!activeDrag) return;
    activeDrag.element.style.left = (activeDrag.initialLeft + (e.clientX - activeDrag.startX)) + 'px';
    activeDrag.element.style.top = (activeDrag.initialTop + (e.clientY - activeDrag.startY)) + 'px';
    activeDrag.element.style.transform = 'none';
}
function stopDrag() { activeDrag = null; document.removeEventListener('mousemove', onDrag); document.removeEventListener('mouseup', stopDrag); }

function insertEmoji(index) {
    let sel = document.getElementById(`emoji_select_${index}`), txt = document.getElementById(`custom_text_${index}`);
    if(sel && txt && sel.value) { txt.value += " " + sel.value; sel.value = ""; updateOverlayFromInput(index); }
}
function populateHookDropdown(index, hooksText) {
    let sel = document.getElementById(`hook_select_${index}`);
    if (!sel) return;
    let lines = hooksText.split('\n'), count = 1;
    for (let line of lines) {
        let cleaned = line.replace(/^[0-9]+\.\s*\*\*/, '').replace(/\*\*/g, '').trim();
        if (cleaned.length > 3) {
            let opt = document.createElement('option');
            opt.value = cleaned; opt.text = `Hook ${count}: ${cleaned.substring(0, 25)}...`;
            sel.appendChild(opt); count++;
        }
    }
    if (sel.options.length > 1) { sel.selectedIndex = 1; updateTextInput(index); }
}
function updateTextInput(index) {
    let sel = document.getElementById(`hook_select_${index}`), txt = document.getElementById(`custom_text_${index}`);
    if (sel && txt && sel.value) { txt.value = sel.value; updateOverlayFromInput(index); }
}
function updateOverlayFromInput(index) {
    let txt = document.getElementById(`custom_text_${index}`), box = document.getElementById(`overlay_txt_${index}`);
    if (txt && box) box.innerHTML = renderTextWithHtmlEmojis(txt.value || " ");
}
function updateSize(index) {
    let range = document.getElementById(`size_range_${index}`), box = document.getElementById(`overlay_txt_${index}`);
    if (range && box) box.style.fontSize = range.value + 'px';
}
</script>
</body>
</html>
'''

@app.route('/')
def index():
    return HTML

KEYS = ["transcript", "visual", "hooks", "yt", "ig", "tiktok", "snap", "fb", "hashtags"]
_model_cache = {"t": 0, "models": []}


def api_error(resp):
    try:
        j = resp.json()
        msg = (j.get("error") or {}).get("message") or str(j)[:300]
    except Exception:
        msg = (resp.text or "")[:300]
    return f"Gemini API {resp.status_code}: {msg}"


def auth_headers(extra=None):
    h = {"x-goog-api-key": PERMANENT_API_KEY}
    if extra:
        h.update(extra)
    return h


def upload_to_gemini(path, mime_type, display_name):
    """Resumable upload (start -> upload+finalize). Always returns the file object or raises a readable error."""
    size = os.path.getsize(path)
    start = requests.post(
        f"{GEMINI}/upload/v1beta/files",
        headers=auth_headers({
            "X-Goog-Upload-Protocol": "resumable",
            "X-Goog-Upload-Command": "start",
            "X-Goog-Upload-Header-Content-Length": str(size),
            "X-Goog-Upload-Header-Content-Type": mime_type,
        }),
        json={"file": {"display_name": display_name}},
        timeout=60,
    )
    if start.status_code != 200:
        raise Exception(api_error(start))
    upload_url = start.headers.get("x-goog-upload-url")
    if not upload_url:
        raise Exception("Gemini did not return an upload URL.")

    with open(path, "rb") as fh:
        up = requests.post(
            upload_url,
            headers={
                "Content-Length": str(size),
                "X-Goog-Upload-Offset": "0",
                "X-Goog-Upload-Command": "upload, finalize",
            },
            data=fh,
            timeout=900,
        )
    if up.status_code != 200:
        raise Exception(api_error(up))
    info = up.json().get("file")
    if not info:
        raise Exception("Upload finished but Gemini returned no file info: " + up.text[:200])
    return info


def wait_until_active(info, max_wait=180):
    waited = 0
    while info.get("state") == "PROCESSING" and waited < max_wait:
        time.sleep(3)
        waited += 3
        r = requests.get(f"{GEMINI}/v1beta/{info['name']}", headers=auth_headers(), timeout=30)
        if r.status_code != 200:
            raise Exception(api_error(r))
        info = r.json()
    if info.get("state") == "FAILED":
        raise Exception("Gemini could not process this video file.")
    if info.get("state") == "PROCESSING":
        raise Exception("Gemini is still processing the video (timed out). Try a shorter clip.")
    if not info.get("uri"):
        raise Exception("Gemini returned no file URI: " + str(info)[:200])
    return info


def get_models():
    if _model_cache["models"] and time.time() - _model_cache["t"] < 3600:
        return _model_cache["models"]
    preferred = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.5-pro", "gemini-1.5-flash", "gemini-1.5-pro"]
    avail = []
    try:
        r = requests.get(f"{GEMINI}/v1beta/models?pageSize=200", headers=auth_headers(), timeout=30).json()
        skip = ("tts", "image", "embedding", "live", "audio", "robotics", "computer-use", "aqa")
        for m in r.get("models", []):
            name = m.get("name", "").replace("models/", "")
            if name.startswith("gemini") and "generateContent" in m.get("supportedGenerationMethods", []) \
                    and not any(s in name for s in skip):
                avail.append(name)
    except Exception:
        pass
    ordered = [m for m in preferred if m in avail]
    ordered += [m for m in avail if "flash" in m and m not in ordered]
    ordered += [m for m in avail if m not in ordered]
    models = (ordered or preferred)[:4]
    _model_cache.update(t=time.time(), models=models)
    return models


def parse_model_text(raw):
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip()).strip()
    try:
        data = json.loads(raw)
        if isinstance(data, list) and data and isinstance(data[0], dict):
            data = data[0]
        if not isinstance(data, dict):
            raise ValueError("not an object")
    except Exception:
        out = {k: "" for k in KEYS}
        out["transcript"] = raw
        return out
    out = {}
    for k in KEYS:
        v = data.get(k, "")
        if isinstance(v, list):
            v = "\n".join(str(x) for x in v)
        elif isinstance(v, dict):
            v = "\n".join(f"{a}: {b}" for a, b in v.items())
        out[k] = str(v)
    return out


@app.route('/generate', methods=['POST'])
def generate():
    temp_path = None
    gem_file = None
    try:
        if not PERMANENT_API_KEY:
            return jsonify({"error": "GEMINI_API_KEY is not set. Add it in Render -> Environment."})

        file = request.files.get('video')
        if not file or file.filename == '':
            return jsonify({"error": "No video file found in request."})

        niche = request.form.get('niche', 'Luxury & Wealth Motivation')
        context = request.form.get('context', '').strip()

        safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", file.filename)
        temp_path = os.path.join(DIRECTORY, f"{uuid.uuid4().hex}_{safe_name}")
        file.save(temp_path)
        mime_type = "video/quicktime" if safe_name.lower().endswith(".mov") else "video/mp4"

        gem_file = upload_to_gemini(temp_path, mime_type, safe_name)
        gem_file = wait_until_active(gem_file)

        prompt = (
            'Analyze the video and return a JSON object with EXACTLY these keys: '
            '"transcript", "visual", "hooks", "yt", "ig", "tiktok", "snap", "fb", "hashtags".\n'
            f'CRITICAL: Describe what is ACTUALLY happening in the video. Niche is ({niche}). '
            'Provide values for "snap" and "fb". Use emojis naturally. Valid JSON only.'
        )
        if context:
            prompt += f'\nExtra context from the editor: {context}'

        payload = {
            "contents": [{"parts": [
                {"text": prompt},
                {"file_data": {"mime_type": mime_type, "file_uri": gem_file["uri"]}},
            ]}],
            "generationConfig": {"responseMimeType": "application/json"},
        }

        errors = []
        for model in get_models():
            try:
                r = requests.post(f"{GEMINI}/v1beta/models/{model}:generateContent",
                                  headers=auth_headers(), json=payload, timeout=300)
            except requests.RequestException as e:
                errors.append(f"{model}: {e}")
                continue
            if r.status_code != 200:
                errors.append(f"{model}: {api_error(r)}")
                continue
            try:
                raw = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError, TypeError):
                errors.append(f"{model}: empty response (possibly blocked)")
                continue
            return jsonify({"structured": parse_model_text(raw)})

        return jsonify({"error": "All models failed. " + " | ".join(errors[-3:])})

    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        if temp_path and os.path.exists(temp_path):
            try: os.remove(temp_path)
            except Exception: pass
        if gem_file and gem_file.get("name"):
            try: requests.delete(f"{GEMINI}/v1beta/{gem_file['name']}", headers=auth_headers(), timeout=15)
            except Exception: pass


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
