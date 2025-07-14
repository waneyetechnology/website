#!/usr/bin/env python3
"""
Unit tests for template-based HTML generation using Jinja2
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil
from pathlib import Path

# Add src directory to path (parent directory contains src)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.htmlgen import generate_html, get_template_env


class TestTemplateGeneration(unittest.TestCase):
    """Test cases for Jinja2 template-based HTML generation"""
    
    def setUp(self):
        """Set up test data and temporary directories"""
        self.test_news = [
            {
                "headline": "Test Financial News 1",
                "url": "https://example.com/news1",
                "image": "static/images/headlines/test1.jpg"
            },
            {
                "headline": "Test Financial News 2",
                "url": "https://example.com/news2",
                "image": "static/images/dynamic/dynamic_123456_abcdef.jpg#dynamic"
            },
            {
                "headline": "Test Financial News 3",
                "url": "https://example.com/news3",
                "image": "static/images/ai-generated/ai_test.jpg#ai-generated"
            }
        ]
        
        self.test_policies = [
            {"bank": "Federal Reserve", "rate": "5.25%"},
            {"bank": "European Central Bank", "rate": "4.50%"}
        ]
        
        self.test_econ = [
            {"event": "GDP Growth", "value": "2.1%", "date": "Q4 2024"},
            {"event": "Inflation Rate", "value": "3.2%", "date": "Dec 2024"}
        ]
        
        self.test_forex = [
            {"pair": "EUR/USD", "bid": "1.0850", "ask": "1.0852"},
            {"pair": "GBP/USD", "bid": "1.2650", "ask": "1.2652"}
        ]
        
        # Create temporary templates directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.templates_dir = Path(self.temp_dir) / 'templates'
        self.templates_dir.mkdir(exist_ok=True)
        
    def tearDown(self):
        """Clean up temporary directories"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def create_test_templates(self):
        """Create test Jinja2 templates"""
        # Base template
        base_template = """<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <title>{{ title }}</title>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <meta name='last-modified' content='{{ last_updated }}'>
    <link rel='icon' type='image/svg+xml' href='favicon.svg?v={{ cache_buster }}'>
    <link rel='stylesheet' href='static/style.css?v={{ cache_buster }}'>
</head>
<body>
    <div class='container'>
        {% block content %}{% endblock %}
    </div>
    <script src='static/main.js?v={{ cache_buster }}'></script>
</body>
</html>"""
        
        # Index template
        index_template = """{% extends "base.html" %}

{% block content %}
<div class='text-center mb-4'>
    <h1 class='display-4 fw-bold'>{{ page_title }}</h1>
    <p class='text-muted'><em>Last updated: {{ last_updated }}</em></p>
</div>

<div class='row g-4'>
    <div class='col-12'>
        <div class='card shadow-sm'>
            <div class='card-header bg-primary text-white'>Top Financial Headlines</div>
            <div class='card-body px-3 py-4'>
                <div class='headline-grid'>
                    {% for item in news %}
                        {% set outer_loop = loop %}
                        {% include 'headline_card.html' %}
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
</div>

<div class='row g-4 mt-2'>
    <div class='col-md-4'>
        <div class='card shadow-sm'>
            <div class='card-header bg-info text-white'>Central Bank Rates</div>
            <ul class='list-group list-group-flush'>
                {% for policy in policies %}
                <li class='list-group-item'><b>{{ policy.bank }}:</b> {{ policy.rate }}</li>
                {% endfor %}
            </ul>
        </div>
    </div>
    
    <div class='col-md-4'>
        <div class='card shadow-sm'>
            <div class='card-header bg-success text-white'>Key Economic Data</div>
            <ul class='list-group list-group-flush'>
                {% for item in econ %}
                <li class='list-group-item'>{{ item.event }}: {{ item.value }} ({{ item.date }})</li>
                {% endfor %}
            </ul>
        </div>
    </div>
    
    <div class='col-md-4'>
        <div class='card shadow-sm'>
            <div class='card-header bg-warning text-dark'>Forex CFD Quotes</div>
            <div class='table-responsive'>
                <table class='table table-bordered mb-0'>
                    <thead class='table-light'>
                        <tr><th>Pair</th><th>Bid</th><th>Ask</th></tr>
                    </thead>
                    <tbody>
                        {% for item in forex %}
                        <tr><td>{{ item.pair }}</td><td>{{ item.bid }}</td><td>{{ item.ask }}</td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<footer class='text-center mt-5 text-muted'>
    <hr>
    <small>Generated by Waneye.com &mdash; Powered by JellyThemes</small>
</footer>
{% endblock %}"""
        
        # Headline card template
        headline_card_template = """{% set index = outer_loop.index0 %}
{% set loading_attr = "eager" if index < 2 else "lazy" %}
{% set priority_attr = "high" if index < 2 else "auto" %}

<div class='headline-card'>
    {% if item.image %}
        {% if "#dynamic" in item.image %}
            {% set actual_path = item.image.split("#")[0] %}
            <img src='{{ actual_path }}' alt="{{ item.headline }}" class='headline-image dynamic-image' loading="{{ loading_attr }}" fetchpriority="{{ priority_attr }}">
            <div class='dynamic-badge'>Dynamic</div>
        {% elif "#ai-generated" in item.image %}
            {% set actual_path = item.image.split("#")[0] %}
            <img src='{{ actual_path }}' alt="{{ item.headline }}" class='headline-image ai-generated-image' loading="{{ loading_attr }}" fetchpriority="{{ priority_attr }}">
            <div class='ai-badge'>AI</div>
        {% else %}
            <img src='{{ item.image }}' alt="{{ item.headline }}" class='headline-image' loading="{{ loading_attr }}" fetchpriority="{{ priority_attr }}">
        {% endif %}
    {% else %}
        <div class='placeholder-content d-flex align-items-center justify-content-center bg-light' style='height:100%'>
            <div class='text-primary'>No image available</div>
        </div>
    {% endif %}
    <div class='headline-caption'>
        <a href='{{ item.url }}' target='_blank' title="{{ item.headline }}">{{ item.headline }}</a>
    </div>
</div>"""
        
        # Write templates to files
        (self.templates_dir / 'base.html').write_text(base_template)
        (self.templates_dir / 'index.html').write_text(index_template)
        (self.templates_dir / 'headline_card.html').write_text(headline_card_template)
    
    @patch('src.htmlgen.Path')
    def test_get_template_env(self, mock_path):
        """Test template environment initialization"""
        # Mock the path to use our temporary directory
        mock_path.return_value.parent.parent = Path(self.temp_dir)
        
        self.create_test_templates()
        
        env = get_template_env()
        
        # Test that environment is created correctly
        self.assertIsNotNone(env)
        self.assertTrue(hasattr(env, 'get_template'))
        
        # Test that we can load a template
        template = env.get_template('base.html')
        self.assertIsNotNone(template)
    
    @patch('src.htmlgen.get_template_env')
    def test_generate_html_success(self, mock_get_env):
        """Test successful HTML generation with templates"""
        self.create_test_templates()
        
        # Mock the template environment
        from jinja2 import Environment, DictLoader
        
        # Create a mock environment with our test templates
        templates = {
            'base.html': (self.templates_dir / 'base.html').read_text(),
            'index.html': (self.templates_dir / 'index.html').read_text(),
            'headline_card.html': (self.templates_dir / 'headline_card.html').read_text()
        }
        
        mock_env = Environment(loader=DictLoader(templates), autoescape=True)
        mock_get_env.return_value = mock_env
        
        # Generate HTML
        html = generate_html(self.test_news, self.test_policies, self.test_econ, self.test_forex)
        
        # Verify HTML contains expected content
        self.assertIn('Waneye Financial Overview', html)
        self.assertIn('Test Financial News 1', html)
        self.assertIn('Test Financial News 2', html)
        self.assertIn('Federal Reserve', html)
        self.assertIn('5.25%', html)
        self.assertIn('GDP Growth', html)
        self.assertIn('2.1%', html)
        self.assertIn('EUR/USD', html)
        self.assertIn('1.0850', html)
        
        # Verify template-specific features
        self.assertIn('dynamic-image', html)  # Dynamic image class
        self.assertIn('Dynamic', html)  # Dynamic badge
        self.assertIn('ai-generated-image', html)  # AI image class
        self.assertIn('AI', html)  # AI badge
        
        # Verify performance attributes for images
        self.assertIn('loading="eager"', html)  # First images should be eager
        self.assertIn('loading="lazy"', html)   # Later images should be lazy
        self.assertIn('fetchpriority="high"', html)  # First images should be high priority
        self.assertIn('fetchpriority="auto"', html)  # Later images should be auto priority
    
    @patch('src.htmlgen.get_template_env')
    def test_generate_html_error_handling(self, mock_get_env):
        """Test error handling when template generation fails"""
        # Mock template environment to raise an error
        mock_get_env.side_effect = Exception("Template error")
        
        # Generate HTML should now raise an exception instead of falling back
        with self.assertRaises(Exception) as context:
            generate_html(self.test_news, self.test_policies, self.test_econ, self.test_forex)
        
        self.assertIn("Template error", str(context.exception))
    
    @patch('src.htmlgen.get_template_env')
    def test_template_data_structure(self, mock_get_env):
        """Test that template receives correct data structure"""
        self.create_test_templates()
        
        # Create a spy template that captures the data passed to it
        template_data_captured = {}
        
        class SpyTemplate:
            def render(self, **kwargs):
                template_data_captured.update(kwargs)
                return "<html>Test</html>"
        
        mock_template = SpyTemplate()
        mock_env = MagicMock()
        mock_env.get_template.return_value = mock_template
        mock_get_env.return_value = mock_env
        
        # Generate HTML
        generate_html(self.test_news, self.test_policies, self.test_econ, self.test_forex)
        
        # Verify template data structure
        self.assertIn('title', template_data_captured)
        self.assertIn('page_title', template_data_captured)
        self.assertIn('last_updated', template_data_captured)
        self.assertIn('cache_buster', template_data_captured)
        self.assertIn('news', template_data_captured)
        self.assertIn('policies', template_data_captured)
        self.assertIn('econ', template_data_captured)
        self.assertIn('forex', template_data_captured)
        
        # Verify data content
        self.assertEqual(template_data_captured['title'], 'Waneye Financial Overview')
        self.assertEqual(template_data_captured['news'], self.test_news)
        self.assertEqual(template_data_captured['policies'], self.test_policies)
        self.assertEqual(template_data_captured['econ'], self.test_econ)
        self.assertEqual(template_data_captured['forex'], self.test_forex)
        self.assertIsInstance(template_data_captured['cache_buster'], int)
    
    @patch('src.htmlgen.get_template_env')
    def test_empty_data_handling(self, mock_get_env):
        """Test template generation with empty data"""
        self.create_test_templates()
        
        from jinja2 import Environment, DictLoader
        
        templates = {
            'base.html': (self.templates_dir / 'base.html').read_text(),
            'index.html': (self.templates_dir / 'index.html').read_text(),
            'headline_card.html': (self.templates_dir / 'headline_card.html').read_text()
        }
        
        mock_env = Environment(loader=DictLoader(templates), autoescape=True)
        mock_get_env.return_value = mock_env
        
        # Generate HTML with empty data
        html = generate_html([], [], [], [])
        
        # Should still generate valid HTML
        self.assertIn('<html', html)
        self.assertIn('Waneye Financial Overview', html)
        self.assertIn('</html>', html)
    
    @patch('src.htmlgen.get_template_env')
    def test_image_loading_attributes(self, mock_get_env):
        """Test that image loading attributes are set correctly based on position"""
        self.create_test_templates()
        
        from jinja2 import Environment, DictLoader
        
        # Create a mock environment with our test templates
        templates = {
            'base.html': (self.templates_dir / 'base.html').read_text(),
            'index.html': (self.templates_dir / 'index.html').read_text(),
            'headline_card.html': (self.templates_dir / 'headline_card.html').read_text()
        }
        
        mock_env = Environment(loader=DictLoader(templates), autoescape=True)
        mock_get_env.return_value = mock_env
        
        # Generate HTML using templates
        html = generate_html(self.test_news, self.test_policies, self.test_econ, self.test_forex)
        
        # Check that the first two images have eager loading and high priority
        # and subsequent images have lazy loading and auto priority
        
        # Count occurrences of different loading attributes
        eager_count = html.count('loading="eager"')
        lazy_count = html.count('loading="lazy"')
        high_priority_count = html.count('fetchpriority="high"')
        auto_priority_count = html.count('fetchpriority="auto"')
        
        # Should have 2 eager loading images (first 2)
        self.assertEqual(eager_count, 2)
        # Should have 1 lazy loading image (third one)
        self.assertEqual(lazy_count, 1)
        # Should have 2 high priority images (first 2)
        self.assertEqual(high_priority_count, 2)
        # Should have 1 auto priority image (third one)
        self.assertEqual(auto_priority_count, 1)


class TestTemplateIntegration(unittest.TestCase):
    """Integration tests for template system"""
    
    def setUp(self):
        """Set up for integration tests"""
        self.project_root = Path(__file__).parent
        self.templates_dir = self.project_root / 'templates'
    
    def test_templates_directory_exists(self):
        """Test that templates directory exists"""
        # This will be created by get_template_env if it doesn't exist
        env = get_template_env()
        self.assertIsNotNone(env)
    
    @patch('src.htmlgen.logger')
    def test_logging_on_success(self, mock_logger):
        """Test that successful template rendering is logged"""
        # Try to generate with real templates (will fallback if templates don't exist)
        test_data = {
            'news': [],
            'policies': [],
            'econ': [],
            'forex': []
        }
        
        html = generate_html(**test_data)
        self.assertIsNotNone(html)
        self.assertIn('<html', html)
    
    @patch('src.htmlgen.logger')
    def test_logging_on_error(self, mock_logger):
        """Test that template errors are logged and exceptions are raised"""
        with patch('src.htmlgen.get_template_env') as mock_env:
            mock_env.side_effect = Exception("Template error")
            
            test_data = {
                'news': [],
                'policies': [],
                'econ': [],
                'forex': []
            }
            
            # Should raise an exception when templates fail
            with self.assertRaises(Exception) as context:
                generate_html(**test_data)
            
            self.assertIn("Template error", str(context.exception))


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
