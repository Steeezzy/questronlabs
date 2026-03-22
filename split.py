import sys

with open('admin/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Split main layout and views
pre_main = html.split('<main class="main-content">')[0] + '<main class="main-content">\n'
post_main = '\n    </main>\n' + html.split('</main>')[1]

views_html = html.split('<main class="main-content">')[1].split('</main>')[0]

# Split views by <!-- View: ... -->
views = {}
current_view = None
lines = views_html.split('\n')
for line in lines:
    if '<!-- View:' in line:
        current_view = line.split('<!-- View:')[1].split('-->')[0].strip().lower()
        views[current_view] = line + '\n'
    elif current_view:
        views[current_view] += line + '\n'

PAGES = {
    'overview': 'dashboard.html', # dashboard.html is overview
    'simulate': 'simulate.html',
    'projects': 'projects.html',
    'agents': 'agents.html'
}

for view_name, file_name in PAGES.items():
    vhtml = views[view_name]
    
    # Remove class "view-section active" and "view-section" and display hidden
    vhtml = vhtml.replace('class="view-section active"', '')
    vhtml = vhtml.replace('class="view-section"', '')
    vhtml = vhtml.replace('style="display:none;"', '') # just in case
    
    # Build complete HTML
    page_html = pre_main + vhtml + post_main
    
    # Fix Sidebar Links
    # We replace the entire nav-menu
    nav_menu = f"""
        <div class="nav-menu">
            <a class="nav-link {'active' if view_name == 'overview' else ''}" href="dashboard.html">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 12px;"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
                Overview
            </a>
            <a class="nav-link {'active' if view_name == 'simulate' else ''}" href="simulate.html">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 12px;"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                Simulation Engine
            </a>
            <a class="nav-link {'active' if view_name == 'projects' else ''}" href="projects.html">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 12px;"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
                Active Projects
            </a>
            <a class="nav-link {'active' if view_name == 'agents' else ''}" href="agents.html">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 12px;"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
                Global Roster
            </a>
        </div>
    """
    
    # Replace nav menu using split
    parts = page_html.split('<div class="nav-menu">')
    head = parts[0]
    tail = parts[1].split('</div>\n        \n        <div style="margin-top:auto; padding-top: 24px; border-top: 1px solid var(--border-light);">')[1]
    
    page_html = head + nav_menu + '<div style="margin-top:auto; padding-top: 24px; border-top: 1px solid var(--border-light);">' + tail
    
    # We must also clean up the JS block. Remove switchView function entirely.
    import re
    page_html = re.sub(r'function switchView\(viewId, el\) \{.*?\n        \}', '', page_html, flags=re.DOTALL)
    
    # Special: For Simulate page, we need the init call. For others, no. Look at script end.
    if view_name != 'simulate':
        page_html = page_html.replace("document.addEventListener('DOMContentLoaded', updateAgentPreview);", "")
        # Remove runSimulate from non-simulate pages to reduce bloat
        page_html = re.sub(r'async function runSimulate\(\) \{.*?\n        \}', '', page_html, flags=re.DOTALL)

    with open(f'admin/{file_name}', 'w', encoding='utf-8') as f:
        f.write(page_html)

print("Split success!")
