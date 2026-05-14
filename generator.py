import os

# 配置文件路径
INPUT_JS_FILE = "dashboard_data.js"
OUTPUT_HTML_FILE = "index.html"

def generate_html():
    if not os.path.exists(INPUT_JS_FILE):
        print(f"错误: 找不到输入文件 {INPUT_JS_FILE}。请先运行 parser.py。")
        return

    with open(INPUT_JS_FILE, "r", encoding="utf-8") as f:
        js_content = f.read()

    # 使用 Python 的 Raw String (r"")，避免 SyntaxWarning
    html_template = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Samsung RAN4 Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* 核心网格布局 */
        .schedule-grid {
            display: grid;
            grid-template-columns: 120px repeat(4, minmax(280px, 1fr));
            gap: 16px;
            align-items: stretch;
        }
        
        .time-cell {
            padding-top: 2rem;
            font-family: ui-monospace, monospace;
            font-size: 0.875rem;
            font-weight: 700;
            color: #64748b;
            background-color: transparent;
            display: flex;
            align-items: flex-start;
        }

        /* 房间基础样式 */
        .room-yang { border-left: 6px solid #3b82f6; background-color: #f0f7ff; border-color: #e2e8f0; }
        .room-shan { border-left: 6px solid #10b981; background-color: #f0fdf4; border-color: #e2e8f0; }
        .room-gene { border-left: 6px solid #8b5cf6; background-color: #f5f3ff; border-color: #e2e8f0; }
        .room-adhoc { border-left: 6px solid #f59e0b; background-color: #fffbeb; border-color: #e2e8f0; }
        .unowned-cell { border: 1px dashed #cbd5e1; background-color: #f8fafc; color: #94a3b8; }
        
        /* 未选中卡片深度暗化 */
        .is-dimmed {
            opacity: 0.15 !important;
            filter: grayscale(100%);
            pointer-events: none;
        }

        /* 休息行跨列 */
        .break-row {
            grid-column: 2 / -1;
            background-color: #f1f5f9;
            border-left: 8px solid #64748b;
            padding: 1.25rem;
            border-radius: 0.75rem;
            text-align: center;
            font-weight: 900;
            color: #475569;
            text-transform: uppercase;
        }

        .owner-badge {
            font-size: 11px;
            padding: 3px 10px;
            border-radius: 9999px;
            background: white;
            border: 1px solid #e2e8f0;
            font-weight: 800;
            color: #334155;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }

        .active-badge {
            background-color: #f59e0b !important;
            color: white !important;
            border: none;
        }

        .conflict-alert {
            background-color: #fee2e2;
            color: #b91c1c;
            padding: 0.5rem;
            border-radius: 0.5rem;
            border: 2px solid #fecaca;
            font-size: 10px;
            font-weight: 900;
            margin-top: 0.5rem;
        }

        .flex-card { transition: all 0.3s ease; border: 1px solid transparent; }
    </style>
</head>
<body class="bg-slate-100 text-slate-900 min-h-screen flex flex-col antialiased">

    <header class="bg-white border-b sticky top-0 z-50 px-6 py-4 shadow-md">
        <div class="max-w-[1800px] mx-auto flex flex-col lg:flex-row justify-between items-center gap-6">
            <div>
                <h1 class="text-2xl font-black text-slate-800 tracking-tight">Samsung RAN4 Dashboard</h1>
                <p class="text-xs font-bold text-slate-400 uppercase tracking-widest mt-1">Dalian, China | May 2026</p>
            </div>
            
            <div class="flex items-center gap-4 bg-amber-50 p-2.5 rounded-2xl border border-amber-200">
                <label for="delegateFilter" class="text-sm font-black text-amber-800 ml-2 whitespace-nowrap">HIGHLIGHT DELEGATE:</label>
                <select id="delegateFilter" class="bg-white border-2 border-amber-300 text-sm font-black rounded-xl p-2 min-w-[220px] cursor-pointer focus:outline-none focus:border-amber-500">
                    <option value="All">--- ALL ---</option>
                    <option value="Jackson">Jackson</option>
                    <option value="Tina">Tina</option>
                    <option value="Bozhi">Bozhi</option>
                    <option value="Taekhoon">Taekhoon</option>
                    <option value="Xin">Xin</option>
                    <option value="Lili">Lili</option>
                    <option value="Yanze">Yanze</option>
                    <option value="Dong">Dong</option>
                    <option value="Xiaoming">Xiaoming</option>
                    <option value="Xinyan">Xinyan</option>
                    <option value="Hongjun">Hongjun</option>
                </select>
            </div>
        </div>
        <nav id="dayTabs" class="max-w-[1800px] mx-auto flex gap-3 mt-4 overflow-x-auto pb-1"></nav>
    </header>

    <main class="max-w-[1800px] mx-auto p-6 w-full flex-grow">
        <div id="scheduleGrid" class="overflow-x-auto bg-white rounded-3xl shadow-2xl border p-8 min-h-[700px]"></div>
    </main>

    <script>
        __INJECT_DATA_HERE__

        let currentDay = "Monday";
        let currentFilter = "All";

        function initTabs() {
            const container = document.getElementById('dayTabs');
            container.innerHTML = Object.keys(scheduleData).map(day => `
                <button onclick="switchDay('${day}')" class="px-8 py-3 rounded-xl font-black text-sm uppercase transition-all ${currentDay === day ? 'bg-slate-800 text-white shadow-lg' : 'bg-white text-slate-400 border border-slate-200 hover:bg-slate-50'}">
                    ${day}
                </button>
            `).join('');
        }

        function switchDay(day) { currentDay = day; initTabs(); renderSchedule(); }

        function isPersonMatch(personStr, filterName) {
            if (!personStr || filterName === "All") return false;
            const cleanName = personStr.replace(/\s*\(monitoring\)/gi, "").trim();
            return cleanName === filterName.trim();
        }

        function getOwners(topics) {
            let o = []; (topics || []).forEach(t => o.push(...(DELEGATE_MAP[t] || [])));
            return [...new Set(o)];
        }

        function renderSchedule() {
            const container = document.getElementById('scheduleGrid');
            const data = scheduleData[currentDay];
            
            let html = `<div class="schedule-grid">
                <div class="text-[10px] font-black text-slate-300 uppercase p-2 flex items-end">Time</div>
                <div class="text-[10px] font-black text-blue-500 p-2 border-b-4 border-blue-500">Yang</div>
                <div class="text-[10px] font-black text-emerald-500 p-2 border-b-4 border-emerald-500">Shan</div>
                <div class="text-[10px] font-black text-violet-500 p-2 border-b-4 border-violet-500">Gene</div>
                <div class="text-[10px] font-black text-orange-500 p-2 border-b-4 border-orange-500">Ad-hoc</div>`;

            data.forEach(row => {
                html += `<div class="time-cell">${row.time}</div>`;
                
                if (row.isBreak) {
                    html += `<div class="break-row shadow-inner my-2">${row.text}</div>`;
                } else {
                    const rowMap = {};
                    row.rooms.forEach(room => {
                        getOwners(room.topics).forEach(o => {
                            const n = o.replace(/\s*\(monitoring\)/gi, "").trim();
                            rowMap[n] = (rowMap[n] || 0) + 1;
                        });
                    });

                    for (let i = 0; i < 4; i++) {
                        const room = row.rooms[i];
                        if (room) {
                            const owners = getOwners(room.topics);
                            const isHit = currentFilter !== "All" && owners.some(o => isPersonMatch(o, currentFilter));
                            const isDimmed = currentFilter !== "All" && !isHit;
                            const conflicts = owners.filter(o => rowMap[o.replace(/\s*\(monitoring\)/gi, "").trim()] > 1);
                            
                            let cardClass = "p-5 rounded-2xl flex flex-col gap-3 flex-card transition-all shadow-sm ";
                            cardClass += (owners.length > 0) ? "room-" + room.name.toLowerCase().replace(' ', '') : "unowned-cell ";
                            
                            if (isDimmed) cardClass += "is-dimmed ";

                            // --- 修复: 将每一行包裹在独立 div 中，防止粘连 ---
                            let lines = room.text.split('<br>');
                            let formattedLines = lines.map(line => {
                                // 如果是空行，用带高度的空 div 占位，保持原有间距
                                if (!line.trim()) return '<div class="h-2"></div>';

                                let topicMatches = [...line.matchAll(/\[([0-9]+(?:-[A-Z])?)\]/g)];
                                
                                if (currentFilter !== "All") {
                                    if (topicMatches.length > 0) {
                                        let isLineHit = false;
                                        topicMatches.forEach(match => {
                                            let tOwners = DELEGATE_MAP[match[1]] || [];
                                            if (tOwners.some(o => isPersonMatch(o, currentFilter))) {
                                                isLineHit = true;
                                            }
                                        });

                                        if (isLineHit) {
                                            return `<div class="bg-yellow-100 border-l-4 border-orange-500 text-orange-900 font-bold px-3 py-1.5 rounded-r-md shadow-sm my-1 transition-all">${line}</div>`;
                                        } else {
                                            return `<div class="opacity-30 grayscale mb-1">${line}</div>`;
                                        }
                                    } else {
                                        return `<div class="opacity-50 grayscale mb-1">${line}</div>`;
                                    }
                                } else {
                                    // Default All (显示所有人)
                                    if (topicMatches.length > 0) {
                                        let hasMonitoring = false;
                                        let hasActive = false;
                                        topicMatches.forEach(match => {
                                            let tOwners = DELEGATE_MAP[match[1]] || [];
                                            if (tOwners.length > 0) {
                                                if (tOwners.every(o => o.includes('monitoring'))) {
                                                    hasMonitoring = true;
                                                } else {
                                                    hasActive = true;
                                                }
                                            }
                                        });
                                        // 纯 Monitoring 议题置灰
                                        if (hasMonitoring && !hasActive) {
                                            return `<div class="text-slate-400 opacity-60 font-medium mb-1">${line}</div>`;
                                        }
                                    }
                                    // 正常的议题（非高亮，非 monitoring）
                                    return `<div class="mb-1">${line}</div>`;
                                }
                            });
                            // 因为已经全部用 div 包裹，直接 join('') 即可完美换行
                            let formattedText = formattedLines.join('');

                            html += `
                                <div class="${cardClass}" style="min-height: 180px;">
                                    <div class="text-[10px] font-black uppercase opacity-40">${room.name}</div>
                                    <div class="text-[13px] leading-relaxed flex-grow text-slate-800">${formattedText}</div>
                                    ${owners.length > 0 ? `
                                        <div class="mt-4 flex flex-wrap gap-2 pt-3 border-t border-black/5">
                                            ${owners.map(o => {
                                                let isMatch = currentFilter !== 'All' && isPersonMatch(o, currentFilter);
                                                let activeClass = isMatch ? 'active-badge' : '';
                                                let dimClass = (currentFilter !== 'All' && !isMatch) ? 'opacity-30 grayscale' : '';
                                                let monClass = o.includes('monitoring') ? 'monitoring' : '';
                                                return `<span class="owner-badge ${activeClass} ${dimClass} ${monClass}">👤 ${o}</span>`;
                                            }).join('')}
                                        </div>
                                    ` : ''}
                                    ${conflicts.length > 0 ? `<div class="conflict-alert">⚠️ CONFLICT: ${conflicts.map(c => c.replace(/\s*\(monitoring\)/gi, "").trim()).join(', ')}</div>` : ''}
                                </div>`;
                        } else {
                            html += `<div class="unowned-cell rounded-2xl"></div>`;
                        }
                    }
                }
            });
            container.innerHTML = html + `</div>`;
        }

        document.getElementById('delegateFilter').addEventListener('change', (e) => {
            currentFilter = e.target.value;
            renderSchedule();
        });

        initTabs(); renderSchedule();
    </script>
</body>
</html>
    """

    final_html = html_template.replace("__INJECT_DATA_HERE__", js_content)
    with open(OUTPUT_HTML_FILE, "w", encoding="utf-8") as f:
        f.write(final_html)
    
    print(f"Success! 行间距修复版 Dashboard 已生成: {OUTPUT_HTML_FILE}")

if __name__ == "__main__":
    generate_html()