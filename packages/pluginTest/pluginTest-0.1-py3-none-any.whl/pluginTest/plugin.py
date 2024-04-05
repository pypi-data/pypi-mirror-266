from mkdocs.plugins import BasePlugin
import re

class BadgesPlugin(BasePlugin):

    def on_page_content(self, markdown, page, config, site_navigation=None, **kwargs):
        # Define a regular expression pattern to search for the badge Markdown
        badge_pattern = r'\|Example badge\|works\|'
        
        # Define the replacement HTML for the badge
        badge_html = '''
        <div class="badge-container">
            <img src="https://img.shields.io/badge/example-badge-green" alt="Example Badge">
        </div>
        '''

        # Use the re.sub() function to replace the Markdown pattern with the badge HTML
        markdown = re.sub(badge_pattern, badge_html, markdown)

        return markdown