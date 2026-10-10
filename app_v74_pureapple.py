import http.server
import socketserver
import os
import email.parser
import json
import requests
import time
import threading

PORT = int(os.environ.get("PORT", 8080))
DIRECTORY = "uploads"
os.makedirs(DIRECTORY, exist_ok=True)

PERMANENT_API_KEY = "AQ.Ab8RN6IAvLHgzTtPpd3d6MCdrvXWRiJRrY4V_CLSBhvcgUlnBQ"

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MatrixMedia - V72 (API Upload Error Fix)</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        @import url('https://fonts.cdnfonts.com/css/apple-color-emoji');
        
        body { 
            background: #000000; /* Sleek pure black background */
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
            background: #0f1115; /* Subtle dark gray/blue */
            padding: 40px; 
            border-radius: 16px; 
            width: 100%;
            max-width: 1000px; 
            border: 1px solid #1f2937;
            box-shadow: 0 20px 40px -10px rgba(0,0,0,0.8); 
        }
        
        h2 { margin-top: 0; margin-bottom: 8px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px; font-size: 28px; }
        p { color: #9ca3af; line-height: 1.5; }
        
        .form-group {
            margin-bottom: 24px;
            text-align: left;
        }
        
        label { font-size: 14px; font-weight: 600; color: #9ca3af; display: block; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.5px; }
        
        input[type="text"], input[type="password"], input[type="file"], select { 
            width: 100%; 
            padding: 14px 16px; 
            background: #181b21; 
            color: #f3f4f6; 
            border: 1px solid #374151; 
            border-radius: 8px; 
            font-size: 15px; 
            box-sizing: border-box;
            transition: border-color 0.2s;
        }
        input[type="text"]:focus, input[type="password"]:focus, select:focus {
            outline: none;
            border-color: #3b82f6;
        }
        
        button {
            width: 100%;
            background: #2563eb; /* Professional deep blue */
            color: white;
            font-size: 16px;
            padding: 16px; 
            border-radius: 8px; 
            font-weight: 700; 
            cursor: pointer; 
            border: none; 
            margin-top: 10px;
            transition: all 0.2s ease;
            letter-spacing: 0.5px;
        }
        button:hover { background: #1d4ed8; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3); }
        button:disabled { background: #374151; cursor: not-allowed; color: #6b7280; transform: none; box-shadow: none; }
        
        .hidden { display: none !important; }
        
        /* Dashboard & Output Styles */
        .video-box { background: #111827; padding: 24px; border-radius: 12px; margin-bottom: 30px; border: 1px solid #1f2937; }
        .video-title { color: #f3f4f6; margin-top: 0; margin-bottom: 16px; font-size: 18px; font-weight: 600; }
        .output-grid { display: flex; flex-direction: column; gap: 16px; margin-top: 20px; }
        .card-section { background: #181b21; border: 1px solid #374151; padding: 20px; border-radius: 8px; }
        .card-title { font-weight: 700; color: #60a5fa; display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; font-size: 15px; text-transform: uppercase; letter-spacing: 0.5px; }
        .card-body { white-space: pre-wrap; font-size: 14px; line-height: 1.7; color: #d1d5db; }
        .copy-btn { width: auto; padding: 6px 14px; font-size: 12px; margin: 0; background: #1f2937; border: 1px solid #374151; color: #e5e7eb; font-weight: 600; border-radius: 6px; text-transform: none; }
        .copy-btn:hover { background: #374151; color: #fff; transform: none; box-shadow: none; }
        
        /* Badge */
        .badge { background: rgba(59, 130, 246, 0.1); color: #60a5fa; padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 700; border: 1px solid rgba(96, 165, 250, 0.2); display: inline-block; margin-bottom: 24px; }
        
        /* Video Studio Styles */
        .preview-container {
            width: 100%;
            background: #000;
            border-radius: 10px;
            position: relative;
            text-align: center;
            overflow: hidden;
            display: flex;
            justify-content: center;
            align-items: center;
            border: 1px solid rgba(255,255,255,0.15);
        }
        .preview-container:fullscreen {
            width: 100vw;
            height: 100vh;
            border: none;
            border-radius: 0;
        }
        video {
            width: 100%;
            max-height: 450px;
            display: block;
            background: #000;
            object-fit: contain;
        }
        .preview-container:fullscreen video {
            height: 100%;
            max-height: 100vh;
        }
        .overlay-preview-box {
            position: absolute;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            color: #ffffff;
            font-weight: 800;
            font-size: 16px;
            text-shadow: 2px 2px 6px rgba(0,0,0,0.9), 0 0 10px rgba(0,0,0,0.8);
            cursor: grab;
            z-index: 100;
            background: transparent;
            text-align: center;
            width: 90%;
            user-select: none;
            border: none;
            padding: 4px 10px;
        }
        .overlay-preview-box:active { cursor: grabbing; }
        
        .editor-toolbar {
            display: flex; gap: 8px; margin-top: 15px; background: #0d1117; padding: 12px; border-radius: 10px; align-items: center; flex-wrap: wrap;
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

// --- ADVANCED APPLE EMOJI ENGINE ---
let emojiCache = {};

function getEmojiHex(emoji) {
    let comp = [];
    for (let i = 0; i < emoji.length; i++) {
        let cp = emoji.codePointAt(i);
        comp.push(cp.toString(16));
        if (cp > 0xffff) i++;
    }
    if (comp.length > 1) {
        comp = comp.filter(c => c !== 'fe0f');
    }
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
    let lastIdx = 0;
    let match;
    emojiRegex.lastIndex = 0; 
    while ((match = emojiRegex.exec(text)) !== null) {
        if (match.index > lastIdx) {
            parts.push({ type: 'text', value: text.substring(lastIdx, match.index) });
        }
        parts.push({ type: 'emoji', value: match[0] });
        loadEmoji(match[0]);
        lastIdx = emojiRegex.lastIndex;
    }
    if (lastIdx < text.length) {
        parts.push({ type: 'text', value: text.substring(lastIdx) });
    }
    return parts;
}

function renderTextWithHtmlEmojis(text) {
    let parts = splitTextAndEmojis(text);
    let html = "";
    for(let p of parts) {
        if(p.type === 'text') {
            let div = document.createElement('div');
            div.innerText = p.value;
            html += div.innerHTML;
        } else {
            let img = emojiCache[p.value];
            if(img && img.src) {
                html += `<img src="${img.src}" style="height: 1.2em; width: 1.2em; vertical-align: -0.25em; margin: 0 0.1em; display: inline-block; border: none; box-shadow: none; background: transparent; filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.5));">`;
            } else {
                html += p.value; 
            }
        }
    }
    return html;
}
// -----------------------------------

function togglePass() {
    const p = document.getElementById('pass');
    p.type = p.type === 'password' ? 'text' : 'password';
}

function check() { 
    const pass = document.getElementById("pass").value;
    if(pass === "2008") { 
        document.getElementById("auth").classList.add("hidden"); 
        document.getElementById("main").classList.remove("hidden"); 
    } else {
        alert("❌ Incorrect Password!");
    }
}

function showFileNames(event) {
    const files = event.target.files;
    const fileListDiv = document.getElementById("fileList");
    if(files.length > 0) {
        fileListDiv.innerHTML = `📁 <b>${files.length} videos selected.</b> Ready for batch processing.`;
    } else {
        fileListDiv.innerHTML = "";
    }
}

function copyCardText(btn) {
    let text = btn.parentElement.nextElementSibling.innerText;
    navigator.clipboard.writeText(text).then(() => {
        let original = btn.innerText;
        btn.innerText = "✅ Copied!";
        setTimeout(() => btn.innerText = original, 2000);
    });
}

function toggleFullscreen(index) {
    let container = document.getElementById(`preview_container_${index}`);
    if (!document.fullscreenElement) {
        container.requestFullscreen().catch(err => alert(err.message));
    } else {
        document.exitFullscreen();
    }
}

async function processSingleVideo(f, index, niche, context) {
    let statusBox = document.getElementById(`res_${index}`);
    statusBox.innerHTML = "<p style='color:#f0b37e;'>⚡ <b>Analyzing video...</b></p>";
    
    const fd = new FormData();
    fd.append("video", f);
    fd.append("niche", niche);
    fd.append("context", context);
    
    try {
        const res = await fetch("/generate", {method: "POST", body: fd});
        const d = await res.json();
        if(d.structured) {
            let s = d.structured;
            let videoUrl = URL.createObjectURL(f);
            
            let html = '<div class="output-grid">';
            
            html += `<div class="card-section">
                <div class="card-title">🎥 Interactive Hook Studio</div>
                <div class="preview-container" id="preview_container_${index}">
                    <!-- Removed crossorigin="anonymous" to prevent canvas taint issues during export -->
                    <video id="vid_el_${index}" src="${videoUrl}" controls playsinline></video>
                    <div id="overlay_txt_${index}" class="overlay-preview-box" onmousedown="startDrag(event, 'overlay_txt_${index}')">🔥 Select a hook below</div>
                    <div id="overlay_watermark_${index}" class="overlay-preview-box" onmousedown="startDrag(event, 'overlay_watermark_${index}')" style="top: 85%; font-size: 14px; opacity: 0.8; color: rgba(255,255,255,0.7);">@Watermark</div>
                </div>
                
                <div class="editor-toolbar">
                    <select id="hook_select_${index}" onchange="updateTextInput(${index})" style="flex:1; max-width:18%;">
                        <option value="">-- AI Hooks --</option>
                    </select>
                    
                    <input type="text" id="custom_text_${index}" value="🔥 Select hook" oninput="updateOverlayFromInput(${index})" style="flex:2;" placeholder="Type or edit custom hook...">
                    
                    <!-- NEW: EMOJI MENU -->
                    <select id="emoji_select_${index}" onchange="insertEmoji(${index})" style="flex:0.5; max-width:80px; padding: 10px 5px;">
                        <option value="">🙂 Emoji</option>
                        <option value="🔥">🔥</option>
                        <option value="💯">💯</option>
                        <option value="👑">👑</option>
                        <option value="🚀">🚀</option>
                        <option value="💎">💎</option>
                        <option value="👀">👀</option>
                        <option value="⚡">⚡</option>
                        <option value="💸">💸</option>
                        <option value="💀">💀</option>
                        <option value="🤡">🤡</option>
                        <option value="📈">📈</option>
                        <option value="👇">👇</option>
                        <option value="👉">👉</option>
                    </select>
                    
                    <div style="display:flex; align-items:center;">
                        <label style="margin:0; font-size:12px; color:#38bdf8;">Size:</label>
                        <input type="range" id="size_range_${index}" min="10" max="60" value="16" oninput="updateSize(${index})">
                    </div>
                    
                    <div style="display:flex; align-items:center; gap: 5px; background: rgba(0,0,0,0.2); padding: 5px; border-radius: 6px; border: 1px solid #30363d;">
                        <input type="text" id="watermark_input_${index}" value="@Watermark" oninput="updateWatermarkInput(${index})" style="width: 100px; padding: 6px; font-size: 12px; margin:0;" placeholder="Watermark...">
                        <label style="margin:0; font-size:11px; color:#8b949e;">Size:</label>
                        <input type="range" id="w_size_range_${index}" min="8" max="50" value="14" oninput="updateWatermarkSize(${index})" style="width: 40px; margin:0;">
                    </div>
                    
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
            
            let videoEl = document.getElementById(`vid_el_${index}`);
            let overlayBox = document.getElementById(`overlay_txt_${index}`);
            
            let wBox = document.getElementById(`overlay_watermark_${index}`);
            document.addEventListener('fullscreenchange', () => {
                let isFS = document.fullscreenElement === videoEl;
                overlayBox.style.display = isFS ? 'none' : 'block';
                if(wBox) wBox.style.display = isFS ? 'none' : 'block';
            });
            
            setTimeout(() => {
                populateHookDropdown(index, s.hooks);
                updateOverlayFromInput(index);
            }, 100);
            
        } else {
            statusBox.innerHTML = `<p style='color:#ff7b72;'>Error: ${d.error}</p>`;
        }
    } catch(e) { 
        statusBox.innerHTML = `<p style='color:#ff7b72;'>Error: ${e.message}</p>`; 
    }
}

// Drag & Drop for Multiple Elements
let activeDrag = null;
function startDrag(e, elementId) {
    let box = document.getElementById(elementId);
    if (!box) return;
    activeDrag = {
        element: box,
        startX: e.clientX,
        startY: e.clientY,
        initialLeft: box.offsetLeft,
        initialTop: box.offsetTop
    };
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
function stopDrag() {
    activeDrag = null;
    document.removeEventListener('mousemove', onDrag);
    document.removeEventListener('mouseup', stopDrag);
}

// Insert Emoji Function
function insertEmoji(index) {
    let select = document.getElementById(`emoji_select_${index}`);
    let textInput = document.getElementById(`custom_text_${index}`);
    if(select && textInput && select.value) {
        textInput.value += " " + select.value;
        select.value = ""; // reset dropdown
        updateOverlayFromInput(index);
    }
}

function populateHookDropdown(index, hooksText) {
    let select = document.getElementById(`hook_select_${index}`);
    if (!select) return;
    let lines = hooksText.includes('\n') ? hooksText.split('\n') : hooksText.split(',');
    let count = 1;
    for (let line of lines) {
        let cleaned = line.replace(/^[0-9]+\.\s*\*\*/, '').replace(/\*\*/g, '').trim();
        if (cleaned.length > 3) {
            let opt = document.createElement('option');
            opt.value = cleaned;
            opt.text = `Hook ${count}: ${cleaned.substring(0, 30)}...`;
            select.appendChild(opt);
            count++;
        }
    }
    if (select.options.length > 1) {
        select.selectedIndex = 1;
        updateTextInput(index);
    }
}

function updateTextInput(index) {
    let select = document.getElementById(`hook_select_${index}`);
    let textInput = document.getElementById(`custom_text_${index}`);
    if (select && textInput && select.value) {
        textInput.value = select.value;
        updateOverlayFromInput(index);
    }
}

function updateOverlayFromInput(index) {
    let textInput = document.getElementById(`custom_text_${index}`);
    let overlayBox = document.getElementById(`overlay_txt_${index}`);
    if (textInput && overlayBox) {
        overlayBox.innerHTML = renderTextWithHtmlEmojis(textInput.value || " ");
    }
}

function updateSize(index) {
    let range = document.getElementById(`size_range_${index}`);
    let overlayBox = document.getElementById(`overlay_txt_${index}`);
    if (range && overlayBox) {
        overlayBox.style.fontSize = range.value + 'px';
    }
}

function updateWatermarkInput(index) {
    let wInput = document.getElementById(`watermark_input_${index}`);
    let wBox = document.getElementById(`overlay_watermark_${index}`);
    if (wInput && wBox) {
        wBox.innerHTML = renderTextWithHtmlEmojis(wInput.value || " ");
    }
}

function updateWatermarkSize(index) {
    let range = document.getElementById(`w_size_range_${index}`);
    let wBox = document.getElementById(`overlay_watermark_${index}`);
    if (range && wBox) {
        wBox.style.fontSize = range.value + 'px';
    }
}

function wrapTextCanvas(ctx, text, x, y, maxWidth, lineHeight, fontSize) {
    let lines = [];
    let currentLine = [];
    let currentLineWidth = 0;
    
    let rawWords = text.split(' ');
    ctx.textAlign = "left"; 
    
    function getPartWidth(part) {
        return part.type === 'text' ? ctx.measureText(part.value).width : (fontSize * 1.15);
    }
    
    for (let word of rawWords) {
        let parts = splitTextAndEmojis(word);
        let wordWidth = parts.reduce((sum, p) => sum + getPartWidth(p), 0);
        let spaceWidth = ctx.measureText(" ").width;
        
        if (currentLineWidth + wordWidth > maxWidth && currentLine.length > 0) {
            lines.push(currentLine);
            currentLine = [...parts];
            currentLineWidth = wordWidth;
        } else {
            if (currentLine.length > 0) {
                currentLine.push({ type: 'text', value: ' ' });
                currentLineWidth += spaceWidth;
            }
            currentLine.push(...parts);
            currentLineWidth += wordWidth;
        }
    }
    if (currentLine.length > 0) lines.push(currentLine);
    
    let startY = y - ((lines.length * lineHeight) / 2) + (lineHeight / 2);
    
    for (let k = 0; k < lines.length; k++) {
        let lineParts = lines[k];
        let lineWidth = lineParts.reduce((sum, p) => sum + getPartWidth(p), 0);
        let currX = x - (lineWidth / 2); 
        
        for (let part of lineParts) {
            if (part.type === 'text') {
                ctx.fillText(part.value, currX, startY + (k * lineHeight));
                currX += ctx.measureText(part.value).width;
            } else if (part.type === 'emoji') {
                let img = emojiCache[part.value];
                let eSize = fontSize * 1.15;
                if (img && img.complete && img.naturalWidth > 0) {
                    ctx.drawImage(img, currX, startY + (k * lineHeight) - (fontSize * 0.85), eSize, eSize);
                } else {
                    ctx.fillText(part.value, currX, startY + (k * lineHeight));
                }
                currX += eSize;
            }
        }
    }
}

async function exportVideoWithOverlay(index, filename, btn) {
    let exportBtn = btn || event.target;
    let oldBtnText = exportBtn ? exportBtn.innerText : "📥 Export HD";
    
    try {
        let videoEl = document.getElementById(`vid_el_${index}`);
        let textInput = document.getElementById(`custom_text_${index}`);
        let overlayBox = document.getElementById(`overlay_txt_${index}`);
        let wInput = document.getElementById(`watermark_input_${index}`);
        let wBox = document.getElementById(`overlay_watermark_${index}`);
        
        let hookText = textInput ? textInput.value : "";
        let watermarkText = wInput ? wInput.value : "";
        if (!hookText) { alert("⚠️ Provide a hook to overlay!"); return; }
        if (!window.MediaRecorder || !videoEl) { alert("⚠️ Browser unsupported for direct export."); return; }
        
        if (exportBtn) exportBtn.disabled = true;
        if (exportBtn) exportBtn.innerText = "⏳ Initializing Export...";
        
        // Ensure video is ready
        if (videoEl.paused) {
            await videoEl.play().catch(e => console.log("Initial play catch:", e));
            videoEl.pause();
        }
        
        let totalDuration = videoEl.duration;
        if (!totalDuration || isNaN(totalDuration)) totalDuration = 15;
        
        let canvas = document.createElement('canvas');
        canvas.width = videoEl.videoWidth || 1080;
        canvas.height = videoEl.videoHeight || 1920;
        let ctx = canvas.getContext('2d');
        
        let canvasStream = canvas.captureStream(30);
        let combinedStream = new MediaStream([...canvasStream.getVideoTracks()]);
        
        try {
            let audioTracks = [];
            if (videoEl.captureStream) audioTracks = videoEl.captureStream().getAudioTracks();
            else if (videoEl.mozCaptureStream) audioTracks = videoEl.mozCaptureStream().getAudioTracks();
            
            if (audioTracks.length > 0) {
                combinedStream.addTrack(audioTracks[0]);
            } else {
                let audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                if (audioCtx.state === 'suspended') await audioCtx.resume();
                if (!videoEl._audioSourceNode) {
                    videoEl._audioSourceNode = audioCtx.createMediaElementSource(videoEl);
                    videoEl._audioDestNode = audioCtx.createMediaStreamDestination();
                    videoEl._audioSourceNode.connect(videoEl._audioDestNode);
                    videoEl._audioSourceNode.connect(audioCtx.destination);
                }
                if (videoEl._audioDestNode && videoEl._audioDestNode.stream.getAudioTracks().length > 0) {
                    combinedStream.addTrack(videoEl._audioDestNode.stream.getAudioTracks()[0]);
                }
            }
        } catch(e) { console.warn("Audio capture warning:", e); }
        
        let options = { mimeType: 'video/webm;codecs=vp9' };
        if (!MediaRecorder.isTypeSupported(options.mimeType)) {
            options = { mimeType: 'video/webm' };
        }
        options.videoBitsPerSecond = 8000000;
        
        let recorder;
        try {
            recorder = new MediaRecorder(combinedStream, options);
        } catch(e) {
            recorder = new MediaRecorder(combinedStream);
        }
        
        let chunks = [];
        recorder.ondataavailable = e => { if(e.data && e.data.size > 0) chunks.push(e.data); };
        
        let isFinished = false;
        let finalizeExport = () => {
            if(isFinished) return;
            isFinished = true;
            
            if(recorder && recorder.state === "recording") recorder.stop();
            
            if (exportBtn) exportBtn.innerText = "⏳ Saving File...";
            
            setTimeout(() => {
                let mime = recorder.mimeType || 'video/webm';
                let blob = new Blob(chunks, { type: mime });
                let url = URL.createObjectURL(blob);
                let a = document.createElement('a');
                a.href = url;
                a.download = `MatrixMedia_${filename.replace(/\.[^/.]+$/, "")}.webm`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                
                if (exportBtn) {
                    exportBtn.innerText = "✅ Downloaded!";
                    setTimeout(() => {
                        exportBtn.innerText = oldBtnText;
                        exportBtn.disabled = false;
                    }, 3000);
                }
            }, 800);
        };

        videoEl.currentTime = 0;
        await new Promise(r => setTimeout(r, 200));
        
        recorder.start(500);
        await videoEl.play();
        
        let startTime = Date.now();
        let durationMs = totalDuration * 1000;
        
        let progressTimer = setInterval(() => {
            let current = videoEl.currentTime;
            let percent = Math.min(Math.round((current / totalDuration) * 100), 100);
            let remaining = Math.max(Math.ceil(totalDuration - current), 0);
            if (exportBtn) {
                exportBtn.innerText = `⏳ Exporting... ${percent}% (${remaining}s left)`;
            }
            
            if (percent >= 100 || videoEl.ended || current >= totalDuration || (Date.now() - startTime) > durationMs + 3000) {
                clearInterval(progressTimer);
                finalizeExport();
            }
        }, 300);

        videoEl.onended = () => {
            clearInterval(progressTimer);
            finalizeExport();
        };
        
        let containerRect = document.getElementById(`preview_container_${index}`).getBoundingClientRect();
        let boxRect = overlayBox.getBoundingClientRect();
        let relX = (boxRect.left - containerRect.left) / containerRect.width;
        let relY = (boxRect.top - containerRect.top) / containerRect.height;
        let fontSizeVal = parseInt(window.getComputedStyle(overlayBox).fontSize) || 16;
        let scaleFactor = canvas.width / containerRect.width;
        let finalFontSize = fontSizeVal * scaleFactor;
        
        let wRect = wBox ? wBox.getBoundingClientRect() : null;
        let wRelX = wRect ? (wRect.left - containerRect.left) / containerRect.width : 0;
        let wRelY = wRect ? (wRect.top - containerRect.top) / containerRect.height : 0;
        let wFontSizeVal = wBox ? parseInt(window.getComputedStyle(wBox).fontSize) || 14 : 14;
        let wFinalFontSize = wFontSizeVal * scaleFactor;
        
        // Strict iOS Emoji Font Stack forced via CDN
        let emojiFontStack = `"Apple Color Emoji", sans-serif`;
        
        function drawLoop() {
            if (isFinished) return;
            ctx.drawImage(videoEl, 0, 0, canvas.width, canvas.height);
            
            // Draw Main Hook
            ctx.save();
            ctx.font = `bold ${finalFontSize}px -apple-system, BlinkMacSystemFont, ${emojiFontStack}`;
            ctx.fillStyle = "#ffffff";
            ctx.shadowColor = "rgba(0, 0, 0, 0.9)";
            ctx.shadowBlur = 12;
            ctx.shadowOffsetX = 3;
            ctx.shadowOffsetY = 3;
            ctx.textAlign = "center";
            
            let targetX = relX * canvas.width + (boxRect.width * scaleFactor / 2);
            let targetY = relY * canvas.height + (finalFontSize / 2);
            wrapTextCanvas(ctx, hookText, targetX, targetY, canvas.width * 0.9, finalFontSize * 1.3, finalFontSize);
            ctx.restore();
            
            // Draw Watermark
            if (watermarkText && wRect) {
                ctx.save();
                ctx.font = `bold ${wFinalFontSize}px -apple-system, BlinkMacSystemFont, ${emojiFontStack}`;
                ctx.fillStyle = "rgba(255, 255, 255, 0.7)";
                ctx.shadowColor = "rgba(0, 0, 0, 0.8)";
                ctx.shadowBlur = 8;
                ctx.textAlign = "center";
                
                let wTargetX = wRelX * canvas.width + (wRect.width * scaleFactor / 2);
                let wTargetY = wRelY * canvas.height + (wFinalFontSize / 2);
                wrapTextCanvas(ctx, watermarkText, wTargetX, wTargetY, canvas.width * 0.9, wFinalFontSize * 1.3, wFinalFontSize);
                ctx.restore();
            }
            
            requestAnimationFrame(drawLoop);
        }
        requestAnimationFrame(drawLoop);

    } catch (err) {
        console.error("Export error:", err);
        alert("⚠️ Export Error: " + err.message);
        if (exportBtn) {
            exportBtn.innerText = oldBtnText;
            exportBtn.disabled = false;
        }
    }
}

async function run() {
    const files = document.getElementById("vid").files;
    if(files.length === 0) return;
    
    document.getElementById("genBtn").disabled = true;
    document.getElementById("genBtn").innerText = "⏳ Processing 3 at a time...";
    
    const out = document.getElementById("out");
    out.innerHTML = `<h3 style="color:#00c6ff;">🚀 Processing ${files.length} Videos (3x Batch Mode)...</h3>`;
    
    const niche = document.getElementById("niche").value;
    const context = document.getElementById("context").value;

    for(let i=0; i<files.length; i++) {
        let f = files[i];
        let vidBox = document.createElement("div");
        vidBox.className = "video-box";
        vidBox.innerHTML = `<h4 class="video-title">📹 ${i+1}. ${f.name}</h4><div id="res_${i}"><p style='color:#8b949e;'>⏳ Queue...</p></div>`;
        out.appendChild(vidBox);
    }

    const chunkSize = 3;
    for (let i = 0; i < files.length; i += chunkSize) {
        const chunk = Array.from(files).slice(i, i + chunkSize);
        const promises = chunk.map((f, idx) => processSingleVideo(f, i + idx, niche, context));
        await Promise.all(promises);
    }
    
    let doneMsg = document.createElement("h3");
    doneMsg.style.color = "#3fb950";
    doneMsg.innerText = "✅ All Videos Processed!";
    out.appendChild(doneMsg);
    
    document.getElementById("genBtn").disabled = false;
    document.getElementById("genBtn").innerText = "⚡ Transcribe & Generate All";
}
</script>
</body>
</html>
"""

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == '/' or self.path.startswith('/?'):
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(HTML.encode("utf-8"))
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/generate':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                content_type = self.headers.get('Content-Type', '')
                msg_bytes = b"Content-Type: " + content_type.encode('latin1') + b"\r\n\r\n" + body
                msg = email.parser.BytesParser().parsebytes(msg_bytes)
                
                form_data = {}
                files = {}
                for part in msg.walk():
                    if part.is_multipart(): continue
                    cd = part.get('Content-Disposition', '')
                    params = {k.strip(): v.strip('"') for k, v in [i.split('=', 1) for i in cd.split(';') if '=' in i]}
                    name = params.get('name')
                    filename = params.get('filename')
                    payload = part.get_payload(decode=True)
                    if filename: files[name] = (filename, payload)
                    elif name: form_data[name] = payload.decode('utf-8', errors='ignore') if payload else ''
                
                vid_filename, vid_bytes = files['video']
                temp_path = os.path.join(DIRECTORY, f"{int(time.time())}_{vid_filename}")
                with open(temp_path, 'wb') as f: f.write(vid_bytes)
                
                upload_res = requests.post(f"https://generativelanguage.googleapis.com/upload/v1beta/files?key={PERMANENT_API_KEY}", 
                                           headers={"X-Goog-Upload-Protocol": "raw", "X-Goog-Upload-Header-Content-Length": str(os.path.getsize(temp_path)), "X-Goog-Upload-Header-Content-Type": "video/mp4"}, 
                                           data=open(temp_path, "rb"))
                file_info = upload_res.json()["file"]
                
                poll_count = 0
                while file_info.get("state") == "PROCESSING" and poll_count < 35: 
                    time.sleep(2)
                    file_info = requests.get(f"https://generativelanguage.googleapis.com/v1beta/{file_info['name']}?key={PERMANENT_API_KEY}").json()
                    poll_count += 1

                payload = {
                    "contents": [{
                        "parts": [
                            {"text": f"""Analyze the video and return a JSON object with EXACTLY these keys: "transcript", "visual", "hooks", "yt", "ig", "tiktok", "snap", "fb", "hashtags".
CRITICAL INSTRUCTION: You MUST describe what is ACTUALLY happening in the video (e.g., if it's a bodybuilding video about gear, write about bodybuilding and gear). DO NOT write about "wealth", "luxury", or anything else if it is not visually present in the video. The 'User Niche' ({form_data.get('niche')}) is ONLY to guide the writing style or formatting, NOT to change the facts of the video. If the niche contradicts the video content, IGNORE THE NICHE completely.
You MUST provide values for "snap" (Snapchat Spotlight caption) and "fb" (Facebook Reels caption). 
Include iOS emojis naturally. Ensure the JSON format is perfectly valid."""},
                            {"file_data": {"mime_type": "video/mp4", "file_uri": file_info["uri"]}}
                        ]
                    }],
                    "generationConfig": {
                        "responseMimeType": "application/json"
                    }
                }
                
                models_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={PERMANENT_API_KEY}"
                models_res = requests.get(models_url).json()
                
                dynamic_models = []
                for m in models_res.get("models", []):
                    if "generateContent" in m.get("supportedGenerationMethods", []):
                        m_name = m.get("name", "").replace("models/", "")
                        if "gemini" in m_name and "vision" not in m_name: 
                            dynamic_models.append(m_name)
                
                def sort_key(name):
                    score = 100
                    if "1.5" in name: score -= 50
                    if "flash" in name: score -= 20
                    return score
                
                dynamic_models.sort(key=sort_key)
                if not dynamic_models: dynamic_models = ["gemini-1.5-flash", "gemini-1.5-pro"]

                max_retries_per_model = 3
                success = False
                structured_data = {}
                error_msg = ""
                
                for model_name in dynamic_models:
                    if success: break
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={PERMANENT_API_KEY}"
                    
                    for attempt in range(max_retries_per_model):
                        try:
                            resp = requests.post(url, json=payload).json()
                        except Exception as e:
                            error_msg = f"Network error: {str(e)}"
                            time.sleep(2)
                            continue
                            
                        if "candidates" in resp and len(resp["candidates"]) > 0:
                            candidate = resp["candidates"][0]
                            if "content" in candidate and "parts" in candidate["content"]:
                                raw_text = candidate["content"]["parts"][0]["text"].strip()
                                if raw_text.startswith("```json"): raw_text = raw_text[7:-3].strip()
                                elif raw_text.startswith("```"): raw_text = raw_text[3:-3].strip()
                                
                                try:
                                    structured_data = json.loads(raw_text)
                                    # Anti-[object Object] Sanitizer
                                    for key in structured_data:
                                        if isinstance(structured_data[key], dict):
                                            structured_data[key] = "\n".join([str(v) for v in structured_data[key].values()])
                                        elif isinstance(structured_data[key], list):
                                            structured_data[key] = "\n".join([str(x) for x in structured_data[key]])
                                        else:
                                            structured_data[key] = str(structured_data[key])
                                    success = True
                                    break
                                except Exception as json_err:
                                    structured_data = {
                                        "transcript": raw_text, "visual": "Parse error", "hooks": "Check transcript.",
                                        "yt": "Parse error", "ig": "Parse error", "tiktok": "Parse error",
                                        "snap": "Parse error", "fb": "Parse error", "hashtags": "#viral #shorts"
                                    }
                                    success = True
                                    break
                            elif candidate.get("finishReason") == "SAFETY":
                                error_msg = "Google Safety Filter 🚫: Video blocked. Switching model..."
                                break 
                        
                        err_code = resp.get("error", {}).get("code")
                        if err_code in [503, 429]: 
                            time.sleep(3 + (attempt * 2)) 
                            error_msg = str(resp.get("error", {}).get("message", resp))
                        else:
                            error_msg = str(resp.get("error", {}).get("message", resp))
                            break 
                
                if os.path.exists(temp_path): os.remove(temp_path)

                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                
                if success:
                    self.wfile.write(json.dumps({"structured": structured_data}).encode("utf-8"))
                else:
                    self.wfile.write(json.dumps({"error": error_msg or "Unknown generation error"}).encode("utf-8"))

            except Exception as e:
                if temp_path and os.path.exists(temp_path): 
                    try: os.remove(temp_path)
                    except: pass
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

if __name__ == "__main__":
    print(f"🚀 MATRIX CLIPPER CLOUD READY ON PORT {PORT}")
    # Bound to 0.0.0.0 so cloud providers (Render/Railway) can route external traffic
    server = ThreadedHTTPServer(("0.0.0.0", PORT), Handler)
    server.serve_forever()
