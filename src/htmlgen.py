from datetime import datetime
from .log import logger
import random
import time
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from .minify_assets import minify_html

# Initialize Jinja2 environment
def get_template_env():
    """Get Jinja2 environment with templates directory"""
    # Get the project root directory (parent of src)
    project_root = Path(__file__).parent.parent
    templates_dir = project_root / 'templates'
    
    # Create templates directory if it doesn't exist
    templates_dir.mkdir(exist_ok=True)
    
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=True,  # Enable autoescaping for security
        trim_blocks=True,  # Remove trailing newlines
        lstrip_blocks=True  # Remove leading spaces on line after blocks
    )
    
    return env

def generate_html(news, policies, econ, forex):
    """Generate HTML using Jinja2 templates"""
    try:
        # Get Jinja2 environment
        env = get_template_env()
        
        # Load the main template
        template = env.get_template('index.html')
        
        # Prepare template data
        template_data = {
            'title': 'Waneye Financial Overview',
            'page_title': 'Waneye Financial Overview',
            'last_updated': datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'),
            'cache_buster': int(time.time()),
            'news': news,
            'policies': policies,
            'econ': econ,
            'forex': forex
        }
        
        # Render the template
        html = template.render(**template_data)
        
        # Log successful template rendering
        logger.info("Successfully rendered HTML using Jinja2 templates")
        
        # Minify and return
        return minify_html(html)
        
    except Exception as e:
        logger.error(f"Error generating HTML with templates: {e}")
        # Re-raise the exception since we no longer have a fallback
        raise
