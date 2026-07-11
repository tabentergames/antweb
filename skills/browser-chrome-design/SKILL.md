---
name: "browser-chrome-design"
description: "Design modern browser chrome UI"
---

# Browser Chrome UI Design

Create an HTML/CSS/SVG mockup of a modern desktop browser top chrome.

## Requirements

### Layout (Top to Bottom)
1. **macOS Window Controls** (left): Red/Yellow/Green dots
2. **Navigation Bar**: Back, Forward, Refresh buttons
3. **Omnibox/Address Bar**: Rounded rectangle with subtle inset, placeholder text
4. **Right Side Icons** (from left to right):
   - Bookmark icon
   - Extensions icon
   - Profile avatar circle
   - Kebab menu (three dots)
5. **Tab Strip** (below navigation): Rounded corners, slight gradient background

### Visual Style
- Glassmorphism: `backdrop-filter: blur(12px)`, semi-transparent white/gray
- Background: Light blue-gray gradient (`#e8ecf4` to `#dce3ef`)
- Shadows: Soft drop shadows (no hard edges)
- Border radius: 10-16px for all elements
- Icons: Simple line icons, ~18px size
- Spacing: Generous padding, minimal clutter

### Tab Strip Details
- Rounded corners on left and right ends
- One active tab in center with slight elevation
- Active tab: White background, top border accent (e.g., blue `#4a90d9`)
- Inactive tabs: Transparent/slightly darker than background
- + button at right end

### Color Palette
- Background: Linear gradient 135deg from `#e8ecf4` to `#dce3ef`
- Glass surface: rgba(255,255,255,0.6)
- Active tab: #ffffff with top border #4a90d9
- Hover states: Slight brightness increase (5-10%)

### Icons (SVG)
All icons should be simple, minimal line art:
- Window controls: Three circles
- Back/Forward/Refresh: Arrow symbols
- Bookmark: Star outline
- Extensions: Puzzle piece
- Profile: User circle icon
- Kebab menu: Three horizontal dots

## Output Format
Single HTML file with embedded CSS and inline SVG icons.
No external dependencies.
Responsive design (width 100%, height ~70px total chrome).

## Implementation Steps
1. Create HTML structure with semantic sections
2. Add glassmorphism base styles with backdrop-filter
3. Position window controls left, navigation buttons, omnibox center, icons right
4. Create rounded tab strip below with active state indicators
5. Add hover states and subtle transitions
6. Test visual hierarchy and spacing balance

## Sample Output

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Modern Browser Chrome UI</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --glass-bg: rgba(255, 255, 255, 0.6);
            --glass-border: rgba(255, 255, 255, 0.8);
            --bg-gradient-start: #e8ecf4;
            --bg-gradient-end: #dce3ef;
            --active-tab-accent: #4a90d9;
            --text-color: #1a2b3c;
            --icon-size: 18px;
        }

        body {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: linear-gradient(135deg, var(--bg-gradient-start), var(--bg-gradient-end));
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        }

        .browser-window {
            width: 90%;
            max-width: 1200px;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 
                0 25px 50px -12px rgba(0, 0, 0, 0.25),
                0 8px 10px -6px rgba(0, 0, 0, 0.1);
        }

        /* Top Chrome Container */
        .chrome-container {
            display: flex;
            flex-direction: column;
            gap: 8px;
            padding: 12px 16px;
            background: var(--glass-bg);
            backdrop-filter: blur(12px) saturate(120%);
            -webkit-backdrop-filter: blur(12px) saturate(120%);
        }

        /* Window Controls (macOS style) */
        .window-controls {
            display: flex;
            gap: 12px;
            padding-left: 16px;
        }

        .window-control {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #ff5f56;
            transition: transform 0.2s, opacity 0.2s;
        }

        .window-control:hover {
            transform: scale(1.1);
            opacity: 0.8;
        }

        .window-control.green { background: #27c93f; }
        .window-control.yellow { background: #ffbd2e; }

        /* Main Toolbar */
        .toolbar {
            display: flex;
            align-items: center;
            gap: 16px;
            padding-left: 8px;
        }

        /* Navigation Buttons */
        .nav-buttons {
            display: flex;
            gap: 8px;
        }

        .nav-btn {
            width: 32px;
            height: 32px;
            border-radius: 8px;
            border: none;
            background: rgba(0, 0, 0, 0.04);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
        }

        .nav-btn:hover {
            background: rgba(0, 0, 0, 0.08);
            transform: scale(1.05);
        }

        .nav-btn svg {
            width: var(--icon-size);
            height: var(--icon-size);
            stroke: #3a4b5c;
            stroke-width: 2;
            fill: none;
            stroke-linecap: round;
            stroke-linejoin: round;
        }

        /* Omnibox */
        .omnibox {
            flex: 1;
            max-width: 600px;
            height: 36px;
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.8);
            display: flex;
            align-items: center;
            padding: 0 16px;
            gap: 12px;
            box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.06);
        }

        .omnibox input {
            flex: 1;
            border: none;
            background: transparent;
            font-size: 14px;
            color: var(--text-color);
            outline: none;
        }

        /* Right Icons */
        .right-icons {
            display: flex;
            align-items: center;
            gap: 8px;
            padding-right: 8px;
        }

        .action-icon {
            width: 32px;
            height: 32px;
            border-radius: 8px;
            border: none;
            background: transparent;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
        }

        .action-icon:hover {
            background: rgba(0, 0, 0, 0.06);
        }

        .action-icon svg {
            width: var(--icon-size);
            height: var(--icon-size);
            stroke: #3a4b5c;
            stroke-width: 2;
            fill: none;
            stroke-linecap: round;
            stroke-linejoin: round;
        }

        /* Profile Avatar */
        .profile-avatar {
            width: 32px;
            height: 32px;
            border-radius: 8px;
            overflow: hidden;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .profile-avatar:hover {
            transform: scale(1.05);
        }

        /* Tab Strip */
        .tab-strip-container {
            background: var(--glass-bg);
            backdrop-filter: blur(12px) saturate(120%);
            -webkit-backdrop-filter: blur(12px) saturate(120%);
            border-top-left-radius: 16px;
            border-top-right-radius: 16px;
            padding: 8px 16px;
        }

        .tab-strip {
            display: flex;
            align-items: center;
            gap: 4px;
            padding: 8px 0;
            position: relative;
        }

        /* Tabs */
        .tab {
            height: 32px;
            max-width: 200px;
            min-width: 140px;
            border-radius: 10px 10px 0 0;
            background: rgba(255, 255, 255, 0.6);
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 0 12px;
            cursor: pointer;
            transition: all 0.2s ease;
            border-top: 3px solid transparent;
        }

        .tab:hover {
            background: rgba(255, 255, 255, 0.8);
        }

        .tab.active {
            background: #ffffff;
            border-top-color: var(--active-tab-accent);
            box-shadow: 
                0 -4px 12px -2px rgba(74, 144, 217, 0.1),
                0 2px 8px -2px rgba(0, 0, 0, 0.08);
        }

        .tab-icon {
            width: 16px;
            height: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .tab-icon svg {
            width: 14px;
            height: 14px;
            stroke: var(--active-tab-accent);
            stroke-width: 2;
            fill: none;
            stroke-linecap: round;
            stroke-linejoin: round;
        }

        .tab-title {
            font-size: 13px;
            color: #3a4b5c;
            font-weight: 500;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .close-tab {
            width: 20px;
            height: 20px;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: all 0.2s ease;
        }

        .tab:hover .close-tab,
        .tab.active .close-tab {
            opacity: 1;
        }

        .close-tab svg {
            width: 14px;
            height: 14px;
            stroke: #6b7c8d;
            stroke-width: 2;
            fill: none;
            stroke-linecap: round;
            stroke-linejoin: round;
        }

        /* Add Tab Button */
        .add-tab-btn {
            width: 32px;
            height: 32px;
            border-radius: 10px 10px 0 0;
            border: none;
            background: rgba(255, 255, 255, 0.6);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
        }

        .add-tab-btn:hover {
            background: rgba(74, 144, 217, 0.1);
        }

        .add-tab-btn svg {
            width: 18px;
            height: 18px;
            stroke: var(--active-tab-accent);
            stroke-width: 2;
            fill: none;
            stroke-linecap: round;
            stroke-linejoin: round;
        }
    </style>
</head>
<body>
    <div class="browser-window">
        <!-- Window Controls -->
        <div class="window-controls">
            <div class="window-control"></div>
            <div class="window-control yellow"></div>
            <div class="window-control green"></div>
        </div>

        <!-- Main Toolbar -->
        <div class="chrome-container">
            <div class="toolbar">
                <!-- Navigation Buttons -->
                <div class="nav-buttons">
                    <button class="nav-btn" aria-label="Back">
                        <svg viewBox="0 0 24 24">
                            <path d="M15 18l-6-6 6-6"/>
                        </svg>
                    </button>
                    <button class="nav-btn" aria-label="Forward">
                        <svg viewBox="0 0 24 24">
                            <path d="M9 18l6-6-6-6"/>
                        </svg>
                    </button>
                    <button class="nav-btn" aria-label="Refresh">
                        <svg viewBox="0 0 24 24">
                            <path d="M23 4v6h-6M1 20v-6h6"/>
                            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
                        </svg>
                    </button>
                </div>

                <!-- Omnibox -->
                <div class="omnobox">
                    <div class="omnibox-locked">
                        <svg viewBox="0 0 24 24" style="width: 14px; height: 14px;">
                            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                            <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                        </svg>
                    </div>
                    <input type="text" placeholder="Search or enter address">
                </div>

                <!-- Right Icons -->
                <div class="right-icons">
                    <button class="action-icon" aria-label="Bookmark">
                        <svg viewBox="0 0 24 24">
                            <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
                        </svg>
                    </button>
                    <button class="action-icon" aria-label="Extensions">
                        <svg viewBox="0 0 24 24">
                            <rect x="4" y="4" width="16" height="16" rx="2" ry="2"/>
                            <rect x="9" y="9" width="6" height="6"/>
                            <path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3"/>
                        </svg>
                    </button>
                    <div class="profile-avatar">
                        <svg viewBox="0 0 24 24" width="32" height="32">
                            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                            <circle cx="12" cy="7" r="4"/>
                        </svg>
                    </div>
                    <button class="action-icon" aria-label="Menu">
                        <svg viewBox="0 0 24 24">
                            <circle cx="12" cy="12" r="2"/>
                            <circle cx="19" cy="12" r="2"/>
                            <circle cx="5" cy="12" r="2"/>
                        </svg>
                    </button>
                </div>
            </div>

            <!-- Tab Strip -->
            <div class="tab-strip-container">
                <div class="tab-strip">
                    <!-- Active Tab -->
                    <div class="tab active">
                        <div class="tab-icon">
                            <svg viewBox="0 0 24 24">
                                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                            </svg>
                        </div>
                        <span class="tab-title">New Tab</span>
                        <button class="close-tab" aria-label="Close tab">
                            <svg viewBox="0 0 24 24">
                                <path d="M18 6L6 18M6 6l12 12"/>
                            </svg>
                        </button>
                    </div>

                    <!-- Add Tab Button -->
                    <button class="add-tab-btn" aria-label="New tab">
                        <svg viewBox="0 0 24 24">
                            <path d="M12 5v14M5 12h14"/>
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
```
