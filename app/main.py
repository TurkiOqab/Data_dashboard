"""
Data Dashboard - Main Application

An AI-powered dashboard for querying PowerPoint presentations
using natural language. Features bilingual Arabic/English support.
"""

import streamlit as st
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.components.upload import render_upload_section, render_file_info
from app.components.chat import render_chat_interface
from app.utils.helpers import load_environment
from app.utils.translations import get_text
from app.services.query_engine import QueryEngine

# Load environment variables
load_environment()

# Page configuration
st.set_page_config(
    page_title="Data Dashboard | لوحة البيانات",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def get_chatgpt_css(is_dark: bool, is_rtl: bool) -> str:
    """Generate ChatGPT-inspired CSS."""

    direction = "rtl" if is_rtl else "ltr"
    text_align = "right" if is_rtl else "left"

    if is_dark:
        colors = {
            'bg_main': '#212121',
            'bg_sidebar': '#171717',
            'bg_input': '#2f2f2f',
            'bg_user_msg': '#2f2f2f',
            'bg_assistant_msg': 'transparent',
            'bg_hover': '#3a3a3a',
            'text_primary': '#ececec',
            'text_secondary': '#b4b4b4',
            'text_muted': '#8e8e8e',
            'border': '#3a3a3a',
            'accent': '#d4a853',
            'accent_soft': 'rgba(212, 168, 83, 0.15)',
        }
    else:
        colors = {
            'bg_main': '#ffffff',
            'bg_sidebar': '#f9f9f9',
            'bg_input': '#f4f4f4',
            'bg_user_msg': '#f7f7f8',
            'bg_assistant_msg': '#ffffff',
            'bg_hover': '#ececec',
            'text_primary': '#0d0d0d',
            'text_secondary': '#374151',
            'text_muted': '#6b7280',
            'border': '#e5e5e5',
            'accent': '#b8860b',
            'accent_soft': 'rgba(184, 134, 11, 0.1)',
        }

    return f"""
    <style>
        /* ============================================
           FONTS
           ============================================ */
        @import url('https://fonts.googleapis.com/css2?family=Söhne:wght@400;500;600&family=Noto+Kufi+Arabic:wght@400;500;600&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

        /* ============================================
           CSS VARIABLES
           ============================================ */
        :root {{
            --bg-main: {colors['bg_main']};
            --bg-sidebar: {colors['bg_sidebar']};
            --bg-input: {colors['bg_input']};
            --bg-user: {colors['bg_user_msg']};
            --bg-assistant: {colors['bg_assistant_msg']};
            --bg-hover: {colors['bg_hover']};
            --text-primary: {colors['text_primary']};
            --text-secondary: {colors['text_secondary']};
            --text-muted: {colors['text_muted']};
            --border: {colors['border']};
            --accent: {colors['accent']};
            --accent-soft: {colors['accent_soft']};
            --font-main: {"'Noto Kufi Arabic', " if is_rtl else ""}'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            --chat-width: 768px;
        }}

        /* ============================================
           GLOBAL RESET
           ============================================ */
        .stApp {{
            background: var(--bg-main) !important;
        }}

        /* Hide all Streamlit chrome */
        #MainMenu, footer, header[data-testid="stHeader"],
        [data-testid="stSidebarCollapseButton"],
        [data-testid="collapsedControl"],
        .stDeployButton {{
            display: none !important;
        }}

        html, body, [class*="css"] {{
            font-family: var(--font-main) !important;
            direction: {direction};
        }}

        /* ============================================
           MAIN CONTAINER - Centered like ChatGPT
           ============================================ */
        .main .block-container {{
            max-width: var(--chat-width) !important;
            padding: 0 1rem 100px 1rem !important;
            margin: 0 auto !important;
        }}

        /* ============================================
           SIDEBAR
           ============================================ */
        section[data-testid="stSidebar"] {{
            background: var(--bg-sidebar) !important;
            border-{"left" if is_rtl else "right"}: 1px solid var(--border) !important;
            width: 260px !important;
        }}

        section[data-testid="stSidebar"] > div {{
            padding: 1rem !important;
            direction: {direction};
        }}

        section[data-testid="stSidebar"] .stButton > button {{
            width: 100%;
            justify-content: flex-start;
            background: transparent !important;
            border: 1px solid var(--border) !important;
            border-radius: 8px !important;
            color: var(--text-secondary) !important;
            font-size: 0.875rem !important;
            padding: 0.75rem 1rem !important;
            transition: background 0.15s ease !important;
        }}

        section[data-testid="stSidebar"] .stButton > button:hover {{
            background: var(--bg-hover) !important;
        }}

        /* ============================================
           HEADER - Minimal like ChatGPT
           ============================================ */
        .chat-header {{
            text-align: center;
            padding: 2rem 1rem 1rem;
        }}

        .chat-header-icon {{
            width: 48px;
            height: 48px;
            background: var(--accent);
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            margin-bottom: 0.75rem;
        }}

        .chat-header-title {{
            font-size: 1.25rem !important;
            font-weight: 600 !important;
            color: var(--text-primary) !important;
            margin: 0 !important;
        }}

        .chat-header-subtitle {{
            font-size: 0.875rem;
            color: var(--text-muted);
            margin-top: 0.25rem;
        }}

        /* ============================================
           WELCOME STATE
           ============================================ */
        .welcome-container {{
            text-align: center;
            padding: 3rem 1rem;
            max-width: 600px;
            margin: 0 auto;
        }}

        .welcome-icon {{
            font-size: 3rem;
            margin-bottom: 1rem;
        }}

        .welcome-title {{
            font-size: 1.5rem !important;
            font-weight: 600 !important;
            color: var(--text-primary) !important;
            margin-bottom: 0.5rem !important;
        }}

        .welcome-subtitle {{
            color: var(--text-muted);
            font-size: 1rem;
            margin-bottom: 2rem;
        }}

        .quick-actions {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            justify-content: center;
            margin-top: 1.5rem;
        }}

        .quick-action-btn {{
            background: var(--bg-input);
            border: 1px solid var(--border);
            border-radius: 1.5rem;
            padding: 0.625rem 1rem;
            font-size: 0.875rem;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.15s ease;
            font-family: var(--font-main);
        }}

        .quick-action-btn:hover {{
            background: var(--bg-hover);
            border-color: var(--accent);
            color: var(--text-primary);
        }}

        /* ============================================
           CHAT MESSAGES - ChatGPT Style
           ============================================ */
        [data-testid="stChatMessage"] {{
            background: transparent !important;
            border: none !important;
            border-radius: 0 !important;
            padding: 1.5rem 0 !important;
            margin: 0 !important;
            max-width: 100% !important;
            direction: {direction};
        }}

        /* Alternating backgrounds */
        [data-testid="stChatMessage"]:nth-child(odd) {{
            background: var(--bg-user) !important;
            margin: 0 -1rem !important;
            padding: 1.5rem 1rem !important;
        }}

        [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {{
            color: var(--text-primary) !important;
        }}

        [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {{
            color: var(--text-primary) !important;
            line-height: 1.6;
            font-size: 1rem;
        }}

        /* Avatar styling */
        [data-testid="stChatMessage"] [data-testid*="chatAvatar"] {{
            width: 28px !important;
            height: 28px !important;
            border-radius: 4px !important;
        }}

        /* ============================================
           CHAT INPUT - Fixed at bottom like ChatGPT
           ============================================ */
        [data-testid="stChatInput"] {{
            position: fixed !important;
            bottom: 0 !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
            width: 100% !important;
            max-width: var(--chat-width) !important;
            padding: 1rem !important;
            background: linear-gradient(to top, var(--bg-main) 85%, transparent) !important;
            z-index: 100 !important;
        }}

        [data-testid="stChatInput"] > div {{
            background: var(--bg-input) !important;
            border: 1px solid var(--border) !important;
            border-radius: 1.5rem !important;
            padding: 0.25rem !important;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08) !important;
            transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
        }}

        [data-testid="stChatInput"] > div:focus-within {{
            border-color: var(--accent) !important;
            box-shadow: 0 2px 12px rgba(0,0,0,0.12) !important;
        }}

        [data-testid="stChatInput"] textarea {{
            font-family: var(--font-main) !important;
            font-size: 1rem !important;
            color: var(--text-primary) !important;
            direction: {direction} !important;
            text-align: {text_align} !important;
            padding: 0.75rem 1rem !important;
            background: transparent !important;
            border: none !important;
        }}

        [data-testid="stChatInput"] textarea::placeholder {{
            color: var(--text-muted) !important;
        }}

        [data-testid="stChatInput"] button {{
            background: var(--accent) !important;
            border: none !important;
            border-radius: 50% !important;
            width: 32px !important;
            height: 32px !important;
            margin: 0.25rem !important;
        }}

        [data-testid="stChatInput"] button:disabled {{
            background: var(--text-muted) !important;
            opacity: 0.5 !important;
        }}

        [data-testid="stChatInput"] button svg {{
            fill: white !important;
            width: 16px !important;
            height: 16px !important;
        }}

        /* ============================================
           SUGGESTION CHIPS (above input)
           ============================================ */
        .suggestion-chips {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            justify-content: center;
            padding: 0.75rem 0;
            margin-bottom: 0.5rem;
        }}

        .suggestion-chip {{
            background: var(--bg-input);
            border: 1px solid var(--border);
            border-radius: 1rem;
            padding: 0.5rem 1rem;
            font-size: 0.8125rem;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.15s ease;
            font-family: var(--font-main);
            white-space: nowrap;
        }}

        .suggestion-chip:hover {{
            background: var(--bg-hover);
            border-color: var(--accent);
        }}

        /* ============================================
           FILE UPLOADER
           ============================================ */
        [data-testid="stFileUploader"] > div:first-child {{
            background: var(--bg-input) !important;
            border: 2px dashed var(--border) !important;
            border-radius: 12px !important;
            padding: 1.5rem !important;
            transition: all 0.2s ease;
        }}

        [data-testid="stFileUploader"] > div:first-child:hover {{
            border-color: var(--accent) !important;
            background: var(--accent-soft) !important;
        }}

        [data-testid="stFileUploader"] label,
        [data-testid="stFileUploader"] small {{
            color: var(--text-muted) !important;
        }}

        /* ============================================
           EXPANDER (for sources)
           ============================================ */
        [data-testid="stExpander"] {{
            background: var(--bg-input) !important;
            border: 1px solid var(--border) !important;
            border-radius: 8px !important;
            margin-top: 0.75rem !important;
        }}

        [data-testid="stExpander"] summary {{
            color: var(--text-secondary) !important;
            font-size: 0.875rem !important;
            padding: 0.75rem 1rem !important;
        }}

        [data-testid="stExpander"] summary:hover {{
            color: var(--text-primary) !important;
        }}

        /* ============================================
           BUTTONS
           ============================================ */
        .stButton > button {{
            background: var(--bg-input) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border) !important;
            border-radius: 8px !important;
            font-family: var(--font-main) !important;
            font-size: 0.875rem !important;
            padding: 0.625rem 1rem !important;
            transition: all 0.15s ease !important;
        }}

        .stButton > button:hover {{
            background: var(--bg-hover) !important;
            border-color: var(--accent) !important;
        }}

        /* ============================================
           SPINNER
           ============================================ */
        [data-testid="stSpinner"] {{
            color: var(--accent) !important;
        }}

        [data-testid="stSpinner"] > div {{
            border-top-color: var(--accent) !important;
        }}

        /* ============================================
           ALERTS
           ============================================ */
        [data-testid="stAlert"] {{
            background: var(--bg-input) !important;
            border: 1px solid var(--border) !important;
            border-radius: 8px !important;
            color: var(--text-secondary) !important;
        }}

        /* ============================================
           SCROLLBAR
           ============================================ */
        ::-webkit-scrollbar {{
            width: 6px;
        }}

        ::-webkit-scrollbar-track {{
            background: transparent;
        }}

        ::-webkit-scrollbar-thumb {{
            background: var(--border);
            border-radius: 3px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: var(--text-muted);
        }}

        /* ============================================
           DIVIDER
           ============================================ */
        hr {{
            border: none !important;
            height: 1px !important;
            background: var(--border) !important;
            margin: 1rem 0 !important;
        }}

        /* ============================================
           TEXT COLORS
           ============================================ */
        h1, h2, h3, h4, h5, h6 {{
            color: var(--text-primary) !important;
            font-family: var(--font-main) !important;
        }}

        p, span, div, label {{
            font-family: var(--font-main) !important;
        }}

        /* ============================================
           SLIDE CARDS
           ============================================ */
        .slide-card {{
            background: var(--bg-input);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.75rem 1rem;
            margin-bottom: 0.5rem;
        }}

        .slide-number {{
            background: var(--accent);
            color: white;
            padding: 0.125rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
        }}

        .slide-title {{
            color: var(--text-primary);
            font-weight: 500;
            margin-top: 0.375rem;
            font-size: 0.875rem;
        }}

        .badge {{
            background: var(--accent-soft);
            color: var(--accent);
            padding: 0.125rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            margin-top: 0.375rem;
            display: inline-block;
        }}

        /* ============================================
           RESPONSIVE
           ============================================ */
        @media (max-width: 768px) {{
            .main .block-container {{
                padding: 0 0.75rem 100px 0.75rem !important;
            }}

            [data-testid="stChatInput"] {{
                padding: 0.75rem !important;
            }}

            .welcome-container {{
                padding: 2rem 0.5rem;
            }}
        }}
    </style>
    """


def initialize_session_state():
    """Initialize session state variables."""
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = True
    if 'messages' not in st.session_state:
        st.session_state.messages = []


def render_welcome_state(lang: str):
    """Render the welcome state when no file is uploaded."""
    t = lambda key: get_text(key, lang)

    st.markdown(f"""
        <div class="welcome-container">
            <div class="welcome-icon">📊</div>
            <h2 class="welcome-title">{t('app_title')}</h2>
            <p class="welcome-subtitle">{t('app_subtitle')}</p>
        </div>
    """, unsafe_allow_html=True)

    # Instruction steps
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
            <div style="text-align: center; padding: 1rem;">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">1️⃣</div>
                <div style="font-weight: 500; color: var(--text-primary);">{t('step_upload')}</div>
                <div style="font-size: 0.875rem; color: var(--text-muted); margin-top: 0.25rem;">{t('step_upload_desc')}</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div style="text-align: center; padding: 1rem;">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">2️⃣</div>
                <div style="font-weight: 500; color: var(--text-primary);">{t('step_process')}</div>
                <div style="font-size: 0.875rem; color: var(--text-muted); margin-top: 0.25rem;">{t('step_process_desc')}</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div style="text-align: center; padding: 1rem;">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">3️⃣</div>
                <div style="font-weight: 500; color: var(--text-primary);">{t('step_ask')}</div>
                <div style="font-size: 0.875rem; color: var(--text-muted); margin-top: 0.25rem;">{t('step_ask_desc')}</div>
            </div>
        """, unsafe_allow_html=True)


def render_chat_header(lang: str):
    """Render minimal chat header."""
    t = lambda key: get_text(key, lang)

    filename = st.session_state.get('processed_file', {}).get('filename', '')

    st.markdown(f"""
        <div class="chat-header">
            <div class="chat-header-icon">📊</div>
            <h3 class="chat-header-title">{t('app_title')}</h3>
            <p class="chat-header-subtitle">{filename}</p>
        </div>
    """, unsafe_allow_html=True)


def main():
    """Main application entry point."""
    initialize_session_state()

    lang = st.session_state.language
    is_rtl = lang == 'ar'
    is_dark = st.session_state.dark_mode
    t = lambda key: get_text(key, lang)

    # Apply ChatGPT-style CSS
    st.markdown(get_chatgpt_css(is_dark, is_rtl), unsafe_allow_html=True)

    # Sidebar - minimal settings
    with st.sidebar:
        st.markdown(f"### {t('settings')}")

        # Theme toggle
        theme_label = "☀️ Light" if is_dark else "🌙 Dark"
        if st.button(theme_label, use_container_width=True, key="theme_toggle"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

        # Language toggle
        lang_label = "العربية" if lang == "en" else "English"
        if st.button(f"🌐 {lang_label}", use_container_width=True, key="lang_toggle"):
            st.session_state.language = "ar" if lang == "en" else "en"
            st.rerun()

        st.divider()

        # File upload
        st.markdown(f"### {t('upload_title')}")
        presentation = render_upload_section(lang=lang)

        if presentation:
            st.divider()
            render_file_info(presentation, lang=lang)

        # Clear chat button (only show if there are messages)
        if st.session_state.messages:
            st.divider()
            if st.button(f"🗑️ {t('clear_chat')}", use_container_width=True, key="clear_chat"):
                st.session_state.messages = []
                st.rerun()

    # Main content
    if st.session_state.get('processed_file'):
        # Chat mode
        render_chat_header(lang)
        render_chat_interface(lang=lang)
    else:
        # Welcome state
        render_welcome_state(lang)


if __name__ == "__main__":
    main()
