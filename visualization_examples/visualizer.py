import argparse
import os
import json
import html
import re


def _parse_span(pos_str, len_str, fallback_length=0):
    """Parse a position+length or range-format span entry.

    Supports two formats:
    - 'line:col' with a separate integer length  (single-line legacy)
    - 'startLine:startCol-endLine:endCol'         (multi-line range)

    Returns a dict with keys 'pos' and either 'length' (int, single-line)
    or 'endPos' (str 'line:col', multi-line).
    """
    pos_str = pos_str.strip()
    # Detect range format: contains '-' between two line:col pairs
    # e.g. "15:8-17:3"
    range_match = re.match(r'^(\d+:\d+)-(\d+:\d+)$', pos_str)
    if range_match:
        return {'pos': range_match.group(1), 'endPos': range_match.group(2)}
    # Legacy single-line: pos + length
    try:
        length = int(len_str) if len_str else fallback_length
    except ValueError:
        length = fallback_length
    return {'pos': pos_str, 'length': length}


def parse_markdown_table(markdown_content):
    """Parse a markdown mapping table into groups with one-to-many support.

    Each row becomes a group with one File1 position and potentially
    multiple File2 positions (comma-separated in the Doc B columns).
    Supports both 'line:col' + length (single-line) and
    'startLine:startCol-endLine:endCol' (multi-line range) formats.
    """
    lines = markdown_content.strip().split('\n')

    # Find the table start (line with | separators followed by --- line)
    table_start = None
    for i, line in enumerate(lines):
        if '|' in line and (i + 1 < len(lines) and '---' in lines[i + 1]):
            table_start = i
            break

    if table_start is None:
        return [], []

    # Extract headers
    header_line = lines[table_start]
    headers = [h.strip() for h in header_line.split('|')[1:-1]]

    # Extract rows as mapping groups
    groups = []
    for idx, line in enumerate(lines[table_start + 2:]):
        if not line.strip() or '|' not in line:
            break
        cells = [c.strip() for c in line.split('|')[1:-1]]
        if len(cells) != len(headers):
            continue
        row = dict(zip(headers, cells))

        file1_pos = row.get('Doc A Position', '').strip()
        file1_len_str = row.get('Doc A Length', '').strip()
        file2_pos_str = row.get('Doc B Position', '').strip()
        file2_len_str = row.get('Doc B Length', '').strip()
        label = row.get('Label', '').strip()
        description = row.get('Description', '').strip()

        # Parse File1 span (single-line or range)
        f1_span = _parse_span(file1_pos, file1_len_str)
        file1_length = f1_span.get('length', 0)
        if 'endPos' in f1_span:
            file1_end_pos = f1_span['endPos']
        else:
            file1_end_pos = None

        # Parse comma-separated Doc B positions (one-to-many)
        file2_positions = []
        if file2_pos_str:
            positions = [p.strip() for p in file2_pos_str.split(',')]
            lengths_raw = [l.strip() for l in file2_len_str.split(',')] if file2_len_str else []

            for i, pos in enumerate(positions):
                len_s = lengths_raw[i] if i < len(lengths_raw) else ''
                span = _parse_span(pos, len_s, file1_length)
                file2_positions.append(span)

        group = {
            'Group_ID': str(idx),
            'File1_Pos': file1_pos,
            'File1_Length': file1_length,
            'File2_Positions': file2_positions,
            'Label': label,
            'Description': description,
        }
        if file1_end_pos:
            group['File1_EndPos'] = file1_end_pos
        groups.append(group)

    return groups, headers


def create_visualization(file1_path, file2_path, markdown_path, output_html_path):
    if not os.path.exists(markdown_path):
        print(f"Error: Markdown file not found: {markdown_path}")
        return

    # Read mapping groups from Markdown
    with open(markdown_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    groups, fieldnames = parse_markdown_table(markdown_content)

    if not groups:
        print(f"Error: No mapping table found in {markdown_path}")
        return

    # Read Files
    def read_file_lines(path):
        if not os.path.exists(path):
            return []
        with open(path, 'r', encoding='utf-8') as f:
            return [line.rstrip('\n') for line in f.readlines()]

    f1_lines = read_file_lines(file1_path)
    f2_lines = read_file_lines(file2_path)

    template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DSPy Visualizer</title>
    <script src="https://cdn.jsdelivr.net/npm/leader-line-new@1.1.9/leader-line.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Fira+Code&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0f172a;
            --panel-bg: #1e293b;
            --text-color: #f8fafc;
            --accent-color: #38bdf8;
            --match-color: rgba(56, 189, 248, 0.2);
            --match-border: #38bdf8;
            --header-bg: #1e293b;
            --selection-bg: rgba(255, 255, 255, 0.1);
        }

        /* Overlap colors - distinct hues per group slot */
        .overlap-0 { background: rgba(56, 189, 248, 0.25); border-bottom-color: #38bdf8; }
        .overlap-1 { background: rgba(251, 146, 60, 0.25); border-bottom-color: #fb923c; }
        .overlap-2 { background: rgba(167, 139, 250, 0.25); border-bottom-color: #a78bfa; }
        .overlap-3 { background: rgba(74, 222, 128, 0.25); border-bottom-color: #4ade80; }
        .overlap-4 { background: rgba(251, 191, 36, 0.25); border-bottom-color: #fbbf24; }
        .overlap-5 { background: rgba(248, 113, 113, 0.25); border-bottom-color: #f87171; }
        .overlap-multi {
            background: repeating-linear-gradient(
                45deg,
                rgba(56, 189, 248, 0.2),
                rgba(56, 189, 248, 0.2) 3px,
                rgba(251, 146, 60, 0.2) 3px,
                rgba(251, 146, 60, 0.2) 6px
            );
            border-bottom: 2px dashed #fb923c;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: 'Inter', sans-serif;
            margin: 0;
            display: flex;
            flex-direction: column;
            height: 100vh;
            overflow: hidden;
        }

        header {
            background: var(--header-bg);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #334155;
            z-index: 100;
        }

        h1 { margin: 0; font-size: 1.25rem; font-weight: 600; color: var(--accent-color); }

        .controls {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        .btn {
            background: #334155;
            color: white;
            border: 1px solid #475569;
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.85rem;
            white-space: nowrap;
            transition: all 0.2s;
        }

        .btn:hover { background: #475569; }
        .btn.primary { background: var(--accent-color); color: #0f172a; border-color: var(--accent-color); font-weight: 600; }
        .btn.danger { background: #ef4444; border-color: #b91c1c; }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; }

        .main-container {
            display: flex;
            flex: 1;
            padding: 20px;
            gap: 40px;
            overflow: hidden;
            position: relative;
        }

        .file-panel {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: var(--panel-bg);
            border-radius: 12px;
            border: 1px solid #334155;
            overflow: hidden;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }

        .panel-header {
            padding: 10px 20px;
            background: #0f172a;
            border-bottom: 1px solid #334155;
            font-size: 0.9rem;
            font-weight: 600;
            color: #94a3b8;
            display: flex;
            justify-content: space-between;
        }

        .code-view {
            flex: 1;
            overflow: auto;
            padding: 20px;
            position: relative;
            counter-reset: line;
        }

        .code-line {
            font-family: 'Fira Code', monospace;
            font-size: 13px;
            line-height: 1.6;
            white-space: pre-wrap;
            word-break: break-all;
            position: relative;
            padding-left: 0;
            min-height: 1.6em;
        }

        .code-line:hover {
            background: rgba(255,255,255,0.02);
        }

        .match-span {
            border-bottom: 2px solid var(--match-border);
            border-radius: 2px;
            cursor: pointer;
            padding: 1px 0;
            transition: background 0.2s;
        }

        .match-span:hover, .match-span.highlighted {
            filter: brightness(1.6);
            box-shadow: 0 0 8px currentColor;
        }

        /* Context Menu */
        #context-menu {
            position: absolute;
            background: #1e293b;
            border: 1px solid #475569;
            border-radius: 6px;
            padding: 8px;
            display: none;
            z-index: 1000;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        }

        /* Tooltip */
        #tooltip {
            position: fixed;
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 12px 16px;
            font-family: 'Inter', sans-serif;
            font-size: 13px;
            color: #f8fafc;
            z-index: 1000;
            max-width: 450px;
            display: none;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
            pointer-events: none;
            line-height: 1.5;
        }

        .badge {
            font-size: 0.8rem;
            color: #94a3b8;
            margin-left: 12px;
            font-weight: 400;
        }

        /* Helper for text selection */
        ::selection {
            background: rgba(56, 189, 248, 0.3);
        }
    </style>
</head>
<body>
    <header>
        <h1>DSPy Visualizer: TITLE_PLACEHOLDER <span class="badge" id="match-count"></span></h1>
        <div class="controls">
            <button class="btn" onclick="toggleAll()">Toggle All Arrows</button>
        </div>
    </header>

    <div class="main-container">
        <div class="file-panel">
            <div class="panel-header">FILE1_NAME</div>
            <div class="code-view" id="file1-container"></div>
        </div>

        <div class="file-panel">
            <div class="panel-header">FILE2_NAME</div>
            <div class="code-view" id="file2-container"></div>
        </div>
    </div>

    <!-- Context Menu for Match Actions -->
    <div id="context-menu">
        <button class="btn danger" onclick="deleteGroup(currentContextGroupId)">Delete Mapping</button>
    </div>

    <!-- Tooltip for mapping details -->
    <div id="tooltip"></div>

    <script>
        // Data injected from Python
        let groups = GROUPS_DATA;
        const file1Lines = FILE1_LINES;
        const file2Lines = FILE2_LINES;

        let leaderLines = {}; // gid -> [{line: LeaderLine, el2: Element}]
        let allVisible = false;
        let currentContextGroupId = null;

        function escapeHtml(text) {
            if (!text) return "";
            return text
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }

        function parsePos(posStr) {
            if (!posStr || posStr.indexOf(':') === -1) return null;
            const parts = posStr.split(':');
            return { line: parseInt(parts[0]), col: parseInt(parts[1]) };
        }

        // Expand a span entry into per-line segments.
        // A span is {pos, length} (single-line) or {pos, endPos} (multi-line range).
        // Returns array of {lineNum, col, length, segIdx} where segIdx distinguishes
        // multiple DOM elements for the same logical span.
        function expandSpanToLines(span, linesArr) {
            const start = parsePos(span.pos);
            if (!start) return [];

            if (span.endPos) {
                // Multi-line range: startLine:startCol - endLine:endCol
                const end = parsePos(span.endPos);
                if (!end) return [];
                const segments = [];
                for (let ln = start.line; ln <= end.line; ln++) {
                    const lineText = linesArr[ln - 1] || '';
                    const col = (ln === start.line) ? start.col : 1;
                    const endCol = (ln === end.line) ? end.col : lineText.length + 1;
                    const len = endCol - col;
                    if (len > 0) {
                        segments.push({ lineNum: ln, col, length: len, segIdx: ln - start.line });
                    }
                }
                return segments;
            } else {
                // Single-line legacy
                return [{ lineNum: start.line, col: start.col, length: span.length, segIdx: 0 }];
            }
        }

        function getAllSpansForGroup(gid) {
            const spans = [];
            document.querySelectorAll(`[data-group-id="${gid}"]`).forEach(el => spans.push(el));
            return spans;
        }

        // Render a single file panel
        function renderFile(fileNum, linesArr, containerId) {
            const container = document.getElementById(containerId);
            container.innerHTML = '';

            // Build per-line highlights from groups
            const lineHighlights = {};

            function addHighlight(lineNum, entry) {
                if (!lineHighlights[lineNum]) lineHighlights[lineNum] = [];
                lineHighlights[lineNum].push(entry);
            }

            groups.forEach(g => {
                if (fileNum === 1) {
                    const span = { pos: g.File1_Pos, length: g.File1_Length, endPos: g.File1_EndPos };
                    expandSpanToLines(span, linesArr).forEach(seg => {
                        addHighlight(seg.lineNum, {
                            groupId: g.Group_ID,
                            col: seg.col,
                            length: seg.length,
                            spanId: `group-${g.Group_ID}-f1-seg${seg.segIdx}`,
                            label: g.Label
                        });
                    });
                } else {
                    g.File2_Positions.forEach((fp, idx) => {
                        expandSpanToLines(fp, linesArr).forEach(seg => {
                            addHighlight(seg.lineNum, {
                                groupId: g.Group_ID,
                                col: seg.col,
                                length: seg.length,
                                spanId: `group-${g.Group_ID}-f2-${idx}-seg${seg.segIdx}`,
                                label: g.Label
                            });
                        });
                    });
                }
            });

            linesArr.forEach((lineText, idx) => {
                const lineNum = idx + 1;
                const div = document.createElement('div');
                div.className = 'code-line';
                div.dataset.line = lineNum;
                div.dataset.file = fileNum;

                const highlights = lineHighlights[lineNum];
                if (highlights) {
                    const sorted = highlights.sort((a, b) => a.col - b.col);

                    // Build character-level group assignments for overlap detection
                    // charGroups[i] = array of highlight entries covering char at position i
                    const charGroups = new Array(lineText.length).fill(null).map(() => []);
                    sorted.forEach(h => {
                        const start = h.col - 1;
                        let len = h.length;
                        if (start + len > lineText.length) len = lineText.length - start;
                        for (let i = start; i < start + len; i++) {
                            charGroups[i].push(h);
                        }
                    });

                    // Find which groupIds actually overlap with at least one other group
                    const overlappingGroups = new Set();
                    for (let i = 0; i < lineText.length; i++) {
                        if (charGroups[i].length > 1) {
                            charGroups[i].forEach(h => overlappingGroups.add(h.groupId));
                        }
                    }

                    // Assign color index only to groups that overlap; others stay at index 0 (default blue)
                    const groupColorMap = {};
                    let colorCounter = 1; // 0 reserved for non-overlapping default
                    overlappingGroups.forEach(gid => {
                        groupColorMap[gid] = colorCounter++;
                    });

                    // Walk character positions and emit spans for contiguous regions with same group set
                    let htmlContent = "";
                    let i = 0;
                    while (i < lineText.length) {
                        const cur = charGroups[i];
                        if (cur.length === 0) {
                            // Find end of plain region
                            let j = i + 1;
                            while (j < lineText.length && charGroups[j].length === 0) j++;
                            htmlContent += escapeHtml(lineText.substring(i, j));
                            i = j;
                        } else {
                            // Find end of region with same group set signature
                            const sig = cur.map(h => h.groupId).sort().join(',');
                            let j = i + 1;
                            while (j < lineText.length) {
                                const nsig = charGroups[j].map(h => h.groupId).sort().join(',');
                                if (nsig !== sig) break;
                                j++;
                            }

                            const segText = lineText.substring(i, j);
                            const isMulti = cur.length > 1;

                            // Use first highlight's metadata for id/events; list all group ids
                            const primary = cur[0];
                            const allGids = cur.map(h => h.groupId).join(' ');
                            const allLabels = cur.map(h => h.label).join(' | ');

                            let classes = 'match-span';
                            if (isMulti) {
                                classes += ' overlap-multi';
                            } else {
                                const colorIdx = (groupColorMap[primary.groupId] ?? 0) % 6;
                                classes += ` overlap-${colorIdx}`;
                            }

                            // Build data attrs and click handler for all groups
                            const onclickHandlers = cur.map(h => `handleGroupClick(event, '${h.groupId}')`).join('; ');
                            htmlContent += `<span id="${primary.spanId}" class="${classes}" data-group-ids="${allGids}" data-group-id="${primary.groupId}" title="${escapeHtml(allLabels)}" onclick="${onclickHandlers}">${escapeHtml(segText)}</span>`;

                            // Also emit hidden zero-width anchors for non-primary spans so LeaderLine can find them
                            cur.slice(1).forEach(h => {
                                htmlContent += `<span id="${h.spanId}" data-group-id="${h.groupId}" style="display:inline;width:0;height:0;overflow:hidden;position:absolute"></span>`;
                            });

                            i = j;
                        }
                    }
                    if (i < lineText.length) htmlContent += escapeHtml(lineText.substring(i));

                    div.innerHTML = htmlContent;
                } else {
                    div.innerHTML = escapeHtml(lineText);
                }

                container.appendChild(div);
            });
        }

        function showTooltip(gid, el) {
            const g = groups.find(g => g.Group_ID === gid);
            if (!g) return;

            const tooltip = document.getElementById('tooltip');
            let html = `<strong>${escapeHtml(g.Label)}</strong>`;

            if (g.Description) {
                html += `<div style="margin-top:6px;color:#94a3b8;font-size:12px">${escapeHtml(g.Description)}</div>`;
            }

            // Extract text from a span (single or multi-line)
            function extractSpanText(span, linesArr) {
                const segs = expandSpanToLines(span, linesArr);
                return segs.map(s => {
                    const line = linesArr[s.lineNum - 1] || '';
                    return line.substring(s.col - 1, s.col - 1 + s.length);
                }).join('\\n');
            }

            // Show source text from File1
            const pos1 = parsePos(g.File1_Pos);
            if (pos1) {
                const text = extractSpanText({pos: g.File1_Pos, length: g.File1_Length, endPos: g.File1_EndPos}, file1Lines);
                html += `<div style="margin-top:8px;padding-top:8px;border-top:1px solid #475569">`;
                html += `<span style="color:#94a3b8">Source:</span> <span style="background:rgba(56,189,248,0.2);padding:2px 4px;border-radius:2px">"${escapeHtml(text)}"</span>`;
                html += `</div>`;
            }

            // Show target locations in File2
            if (g.File2_Positions.length > 0) {
                html += `<div style="margin-top:6px"><span style="color:#94a3b8">Maps to ${g.File2_Positions.length} location(s):</span></div>`;
                g.File2_Positions.forEach((fp, idx) => {
                    const pos = parsePos(fp.pos);
                    if (pos) {
                        const text = extractSpanText(fp, file2Lines);
                        html += `<div style="margin-top:4px;font-size:12px;padding-left:8px">`;
                        html += `<span style="color:#64748b">Line ${pos.line}:</span> <span style="background:rgba(56,189,248,0.2);padding:1px 3px;border-radius:2px">"${escapeHtml(text)}"</span>`;
                        html += `</div>`;
                    }
                });
            }

            tooltip.innerHTML = html;
            tooltip.style.display = 'block';

            const rect = el.getBoundingClientRect();
            tooltip.style.left = rect.left + 'px';
            tooltip.style.top = (rect.bottom + 8) + 'px';
        }

        function hideTooltip() {
            document.getElementById('tooltip').style.display = 'none';
        }

        function renderAll() {
            // Clear existing LeaderLines
            Object.values(leaderLines).forEach(arr => arr.forEach(item => item.line.remove()));
            leaderLines = {};

            renderFile(1, file1Lines, 'file1-container');
            renderFile(2, file2Lines, 'file2-container');

            // Update count badge
            const totalArrows = groups.reduce((sum, g) => sum + g.File2_Positions.length, 0);
            document.getElementById('match-count').textContent =
                `${groups.length} mappings, ${totalArrows} arrows`;

            // Draw LeaderLine arrows per group
            setTimeout(() => {
                groups.forEach(g => {
                    const gid = g.Group_ID;
                    // Use first segment of File1 span as arrow source
                    const el1 = document.getElementById(`group-${gid}-f1-seg0`);
                    if (!el1) return;

                    const groupItems = [];
                    g.File2_Positions.forEach((_, idx) => {
                        // Use first segment of each File2 span as arrow target
                        const el2 = document.getElementById(`group-${gid}-f2-${idx}-seg0`);
                        if (el2) {
                            const line = new LeaderLine(el1, el2, {
                                color: 'rgba(56, 189, 248, 0.6)',
                                size: 2,
                                path: 'curved',
                                startSocket: 'right',
                                endSocket: 'left',
                                hide: !allVisible
                            });
                            if (allVisible) line._permanent = true;
                            groupItems.push({ line, el2 });
                        }
                    });

                    leaderLines[gid] = groupItems;

                    // Collect all spans in this group for hover/highlight
                    const allSpans = getAllSpansForGroup(gid);
                    if (allVisible) {
                        allSpans.forEach(s => s.classList.add('highlighted'));
                    }

                    // Hover: show all arrows + tooltip for the group
                    allSpans.forEach(span => {
                        span.onmouseenter = () => {
                            const isPermanent = groupItems.length > 0 && groupItems[0].line._permanent;
                            if (!isPermanent) {
                                allSpans.forEach(s => s.classList.add('highlighted'));
                                groupItems.forEach(item => {
                                    item.line.setOptions({ color: 'rgba(56, 189, 248, 1)', size: 3 });
                                    item.line.show('draw');
                                });
                                showTooltip(gid, span);
                            }
                        };
                        span.onmouseleave = () => {
                            const isPermanent = groupItems.length > 0 && groupItems[0].line._permanent;
                            if (!isPermanent) {
                                allSpans.forEach(s => s.classList.remove('highlighted'));
                                groupItems.forEach(item => {
                                    item.line.hide();
                                    item.line.setOptions({ color: 'rgba(56, 189, 248, 0.6)', size: 2 });
                                });
                                hideTooltip();
                            }
                        };
                    });
                });
            }, 100);
        }

        function handleGroupClick(e, gid) {
            e.stopPropagation();

            // Show context menu
            const menu = document.getElementById('context-menu');
            menu.style.display = 'block';
            menu.style.left = e.pageX + 'px';
            menu.style.top = e.pageY + 'px';
            currentContextGroupId = gid;

            // Toggle permanent arrow state for the group
            const groupItems = leaderLines[gid];
            if (groupItems && groupItems.length > 0) {
                const isPermanent = groupItems[0].line._permanent;
                const allSpans = getAllSpansForGroup(gid);

                if (isPermanent) {
                    groupItems.forEach(item => {
                        item.line.hide();
                        item.line._permanent = false;
                    });
                    allSpans.forEach(s => s.classList.remove('highlighted'));
                    hideTooltip();
                } else {
                    groupItems.forEach(item => {
                        item.line.show('draw');
                        item.line._permanent = true;
                    });
                    allSpans.forEach(s => s.classList.add('highlighted'));
                }
            }
        }

        function deleteGroup(gid) {
            if (!confirm('Delete this mapping?')) return;
            groups = groups.filter(g => g.Group_ID !== gid);
            document.getElementById('context-menu').style.display = 'none';
            renderAll();
        }

        function toggleAll() {
            allVisible = !allVisible;
            renderAll();
        }

        // Hide context menu on click elsewhere
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.match-span') && !e.target.closest('#context-menu')) {
                document.getElementById('context-menu').style.display = 'none';
            }
        });

        // Reposition LeaderLines on scroll/resize
        ['file1-container', 'file2-container'].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.addEventListener('scroll', () => {
                    Object.values(leaderLines).forEach(arr =>
                        arr.forEach(item => item.line.position())
                    );
                });
            }
        });

        window.addEventListener('resize', () => {
            Object.values(leaderLines).forEach(arr =>
                arr.forEach(item => item.line.position())
            );
        });

        window.onload = renderAll;
    </script>
</body>
</html>
"""
    # Inject Data
    try:
        groups_json = json.dumps(groups)
    except (TypeError, ValueError) as e:
        print(f"Error serializing groups to JSON: {e}")
        return

    html_content = template.replace('GROUPS_DATA', groups_json)
    html_content = html_content.replace('FILE1_LINES', json.dumps(f1_lines))
    html_content = html_content.replace('FILE2_LINES', json.dumps(f2_lines))

    html_content = html_content.replace('FILE1_NAME', os.path.basename(file1_path))
    html_content = html_content.replace('FILE2_NAME', os.path.basename(file2_path))
    html_content = html_content.replace('TITLE_PLACEHOLDER', f"Match: {os.path.basename(file1_path)} vs {os.path.basename(file2_path)}")

    if os.path.dirname(output_html_path):
        os.makedirs(os.path.dirname(output_html_path), exist_ok=True)
    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Visualization created at {output_html_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create HTML visualization from markdown mappings.")
    parser.add_argument("file1", help="Path to the first file (e.g., Python script)")
    parser.add_argument("file2", help="Path to the second file (e.g., prompt+response.txt)")
    parser.add_argument("markdown", help="Path to the markdown mapping file")
    parser.add_argument("output", help="Path to the output HTML file")

    args = parser.parse_args()
    create_visualization(args.file1, args.file2, args.markdown, args.output)
