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

# Load environment variables
load_environment()

# Page configuration
st.set_page_config(
    page_title="Data Dashboard | لوحة البيانات",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


def get_app_css(is_dark: bool, is_rtl: bool) -> str:
    """Generate application CSS."""

    direction = "rtl" if is_rtl else "ltr"
    text_align = "right" if is_rtl else "left"

    if is_dark:
        colors = {
            'bg_main': '#1a1a1a',
            'bg_secondary': '#242424',
            'bg_card': '#2d2d2d',
            'bg_hover': '#363636',
            'text_primary': '#ffffff',
            'text_secondary': '#a0a0a0',
            'text_muted': '#707070',
            'border': '#404040',
            'accent': '#d4a853',
            'accent_hover': '#e5b964',
            'accent_soft': 'rgba(212, 168, 83, 0.15)',
        }
    else:
        colors = {
            'bg_main': '#ffffff',
            'bg_secondary': '#f7f7f8',
            'bg_card': '#ffffff',
            'bg_hover': '#f0f0f0',
            'text_primary': '#1a1a1a',
            'text_secondary': '#666666',
            'text_muted': '#999999',
            'border': '#e0e0e0',
            'accent': '#c9940a',
            'accent_hover': '#b8860b',
            'accent_soft': 'rgba(201, 148, 10, 0.1)',
        }

    return f"""
    <style>
        /* ============================================
           FONTS
           ============================================ */
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Sans+Arabic:wght@400;500;600&display=swap');

        /* ============================================
           CSS VARIABLES
           ============================================ */
        :root {{
            --bg-main: {colors['bg_main']};
            --bg-secondary: {colors['bg_secondary']};
            --bg-card: {colors['bg_card']};
            --bg-hover: {colors['bg_hover']};
            --text-primary: {colors['text_primary']};
            --text-secondary: {colors['text_secondary']};
            --text-muted: {colors['text_muted']};
            --border: {colors['border']};
            --accent: {colors['accent']};
            --accent-hover: {colors['accent_hover']};
            --accent-soft: {colors['accent_soft']};
            --font-main: {"'IBM Plex Sans Arabic', " if is_rtl else ""}'IBM Plex Sans', -apple-system, sans-serif;
        }}

        /* ============================================
           GLOBAL STYLES
           ============================================ */
        .stApp {{
            background: var(--bg-main) !important;
        }}

        #MainMenu, footer {{
            display: none !important;
        }}

        html, body, [class*="css"] {{
            font-family: var(--font-main) !important;
            direction: {direction};
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: var(--text-primary) !important;
            font-family: var(--font-main) !important;
        }}

        p, span, div, label {{
            font-family: var(--font-main) !important;
        }}

        /* ============================================
           MAIN CONTAINER
           ============================================ */
        .main .block-container {{
            max-width: 900px !important;
            padding: 2rem 1rem 120px 1rem !important;
            margin: 0 auto !important;
        }}

        /* ============================================
           SIDEBAR
           ============================================ */
        section[data-testid="stSidebar"] {{
            background: var(--bg-secondary) !important;
            border-{"left" if is_rtl else "right"}: 1px solid var(--border) !important;
            width: 280px !important;
        }}

        section[data-testid="stSidebar"] > div {{
            padding: 1.5rem 1rem !important;
            direction: {direction};
        }}

        /* ============================================
           WELCOME HEADER
           ============================================ */
        .app-header {{
            text-align: center;
            padding: 2rem 0 1rem;
        }}

        .app-logo {{
            width: 64px;
            height: 64px;
            background: linear-gradient(135deg, var(--accent), var(--accent-hover));
            border-radius: 16px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 20px var(--accent-soft);
        }}

        .app-title {{
            font-size: 1.75rem !important;
            font-weight: 600 !important;
            color: var(--text-primary) !important;
            margin: 0 0 0.5rem 0 !important;
        }}

        .app-subtitle {{
            font-size: 1rem;
            color: var(--text-muted);
            margin: 0;
        }}

        /* ============================================
           UPLOAD ZONE - Main Feature
           ============================================ */
        .upload-section {{
            margin: 2rem 0;
        }}

        .upload-zone {{
            background: var(--bg-card);
            border: 2px dashed var(--border);
            border-radius: 16px;
            padding: 3rem 2rem;
            text-align: center;
            transition: all 0.2s ease;
            cursor: pointer;
        }}

        .upload-zone:hover {{
            border-color: var(--accent);
            background: var(--accent-soft);
        }}

        .upload-icon {{
            font-size: 3rem;
            margin-bottom: 1rem;
        }}

        .upload-text {{
            font-size: 1.125rem;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
            font-weight: 500;
        }}

        .upload-hint {{
            font-size: 0.875rem;
            color: var(--text-muted);
        }}

        /* Style Streamlit's file uploader */
        [data-testid="stFileUploader"] {{
            margin-top: 1rem;
        }}

        [data-testid="stFileUploader"] > div:first-child {{
            background: var(--bg-card) !important;
            border: 2px dashed var(--border) !important;
            border-radius: 12px !important;
            padding: 2rem !important;
            transition: all 0.2s ease !important;
        }}

        [data-testid="stFileUploader"] > div:first-child:hover {{
            border-color: var(--accent) !important;
            background: var(--accent-soft) !important;
        }}

        [data-testid="stFileUploader"] label {{
            color: var(--text-secondary) !important;
            font-size: 1rem !important;
        }}

        [data-testid="stFileUploader"] small {{
            color: var(--text-muted) !important;
        }}

        /* ============================================
           STEPS
           ============================================ */
        .steps-container {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
            margin: 2rem 0;
        }}

        .step-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.2s ease;
        }}

        .step-card:hover {{
            border-color: var(--accent);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}

        .step-number {{
            width: 32px;
            height: 32px;
            background: var(--accent);
            color: white;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            margin-bottom: 0.75rem;
        }}

        .step-title {{
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
        }}

        .step-desc {{
            font-size: 0.875rem;
            color: var(--text-muted);
            line-height: 1.5;
        }}

        /* ============================================
           CHAT HEADER
           ============================================ */
        .chat-header {{
            text-align: center;
            padding: 1.5rem 0;
            border-bottom: 1px solid var(--border);
            margin-bottom: 1rem;
        }}

        .chat-file-name {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: var(--accent-soft);
            color: var(--accent);
            padding: 0.5rem 1rem;
            border-radius: 2rem;
            font-size: 0.875rem;
            font-weight: 500;
        }}

        /* ============================================
           CHAT MESSAGES
           ============================================ */
        [data-testid="stChatMessage"] {{
            background: var(--bg-card) !important;
            border: 1px solid var(--border) !important;
            border-radius: 12px !important;
            padding: 1rem 1.25rem !important;
            margin-bottom: 0.75rem !important;
            direction: {direction};
        }}

        [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {{
            color: var(--text-primary) !important;
            line-height: 1.6;
        }}

        /* ============================================
           CHAT INPUT
           ============================================ */
        [data-testid="stChatInput"] {{
            position: fixed !important;
            bottom: 0 !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
            width: 100% !important;
            max-width: 900px !important;
            padding: 1rem !important;
            background: linear-gradient(to top, var(--bg-main) 80%, transparent) !important;
            z-index: 100 !important;
        }}

        [data-testid="stChatInput"] > div {{
            background: var(--bg-card) !important;
            border: 1px solid var(--border) !important;
            border-radius: 12px !important;
            box-shadow: 0 2px 12px rgba(0,0,0,0.1) !important;
        }}

        [data-testid="stChatInput"] > div:focus-within {{
            border-color: var(--accent) !important;
        }}

        [data-testid="stChatInput"] textarea {{
            font-family: var(--font-main) !important;
            color: var(--text-primary) !important;
            direction: {direction} !important;
            text-align: {text_align} !important;
        }}

        [data-testid="stChatInput"] textarea::placeholder {{
            color: var(--text-muted) !important;
        }}

        [data-testid="stChatInput"] button {{
            background: var(--accent) !important;
            border: none !important;
            border-radius: 8px !important;
        }}

        [data-testid="stChatInput"] button svg {{
            fill: white !important;
        }}

        /* ============================================
           BUTTONS
           ============================================ */
        .stButton > button {{
            background: var(--bg-card) !important;
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

        /* Primary button style */
        .primary-btn > button {{
            background: var(--accent) !important;
            color: white !important;
            border: none !important;
        }}

        .primary-btn > button:hover {{
            background: var(--accent-hover) !important;
        }}

        /* ============================================
           EXPANDER
           ============================================ */
        [data-testid="stExpander"] {{
            background: var(--bg-card) !important;
            border: 1px solid var(--border) !important;
            border-radius: 8px !important;
        }}

        [data-testid="stExpander"] summary {{
            color: var(--text-secondary) !important;
            font-size: 0.875rem !important;
        }}

        /* ============================================
           ALERTS
           ============================================ */
        [data-testid="stAlert"] {{
            background: var(--bg-card) !important;
            border: 1px solid var(--border) !important;
            border-radius: 8px !important;
        }}

        /* ============================================
           SPINNER
           ============================================ */
        [data-testid="stSpinner"] > div {{
            border-top-color: var(--accent) !important;
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
           SLIDE CARDS
           ============================================ */
        .slide-card {{
            background: var(--bg-secondary);
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
           FILE INFO
           ============================================ */
        .file-info {{
            background: var(--accent-soft);
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        }}

        .file-info-name {{
            color: var(--text-primary);
            font-weight: 600;
            font-size: 0.9rem;
            margin-bottom: 0.25rem;
        }}

        .file-info-detail {{
            color: var(--text-muted);
            font-size: 0.8rem;
        }}

        /* ============================================
           SCROLLBAR
           ============================================ */
        ::-webkit-scrollbar {{
            width: 8px;
        }}

        ::-webkit-scrollbar-track {{
            background: transparent;
        }}

        ::-webkit-scrollbar-thumb {{
            background: var(--border);
            border-radius: 4px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: var(--text-muted);
        }}

        /* ============================================
           RESPONSIVE
           ============================================ */
        @media (max-width: 768px) {{
            .main .block-container {{
                padding: 1rem 0.75rem 120px 0.75rem !important;
            }}

            .steps-container {{
                grid-template-columns: 1fr;
            }}

            [data-testid="stChatInput"] {{
                padding: 0.75rem !important;
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
    """Render the welcome state with prominent upload."""
    t = lambda key: get_text(key, lang)

    # Header
    st.markdown(f"""
        <div class="app-header">
            <div class="app-logo">📊</div>
            <h1 class="app-title">{t('app_title')}</h1>
            <p class="app-subtitle">{t('app_subtitle')}</p>
        </div>
    """, unsafe_allow_html=True)

    # Main upload area - use file uploader directly to avoid duplicate title
    uploaded_file = st.file_uploader(
        t('upload_label'),
        type=["pptx"],
        help=t('upload_help'),
        key="main_uploader"
    )

    if uploaded_file is not None:
        from app.services.pptx_processor import PPTXProcessor
        from app.services.embeddings import EmbeddingsService, create_slide_embedding_content

        # Check if already processed
        if 'processed_file' not in st.session_state or st.session_state.processed_file.get('name') != uploaded_file.name:
            with st.spinner(t('processing')):
                try:
                    processor = PPTXProcessor()
                    result = processor.process_uploaded_file(uploaded_file)

                    embeddings = EmbeddingsService()
                    embeddings.clear_collection()

                    slides_to_embed = []
                    for slide in result.slides:
                        slide_id = f"{result.filename}_slide_{slide.slide_number}"
                        content = create_slide_embedding_content(slide.to_dict())
                        slides_to_embed.append({
                            'id': slide_id,
                            'content': content,
                            'metadata': {
                                'filename': result.filename,
                                'slide_number': slide.slide_number,
                                'title': slide.title or f"{t('slide')} {slide.slide_number}",
                                'has_chart': slide.has_chart,
                                'has_image': slide.has_image,
                                'has_table': len(slide.tables) > 0
                            }
                        })

                    embeddings.add_slides_batch(slides_to_embed)

                    st.session_state.processed_file = {
                        'name': uploaded_file.name,
                        'data': result
                    }
                    st.session_state.embeddings_ready = True
                    st.session_state.messages = []

                    st.success(t('upload_success').format(slides=result.total_slides, filename=result.filename))
                    st.rerun()

                except Exception as e:
                    st.error(t('upload_error').format(error=str(e)))

    # Steps below
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
            <div class="step-card">
                <div class="step-number">1</div>
                <div class="step-title">{t('step_upload')}</div>
                <div class="step-desc">{t('step_upload_desc')}</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="step-card">
                <div class="step-number">2</div>
                <div class="step-title">{t('step_process')}</div>
                <div class="step-desc">{t('step_process_desc')}</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="step-card">
                <div class="step-number">3</div>
                <div class="step-title">{t('step_ask')}</div>
                <div class="step-desc">{t('step_ask_desc')}</div>
            </div>
        """, unsafe_allow_html=True)


def render_chat_state(lang: str):
    """Render the chat interface after file upload."""
    t = lambda key: get_text(key, lang)

    file_data = st.session_state.get('processed_file', {})
    filename = file_data.get('name', '')
    presentation = file_data.get('data')
    slide_count = presentation.total_slides if presentation else 0

    # Chat header with file info
    st.markdown(f"""
        <div class="chat-header">
            <span class="chat-file-name">📄 {filename} • {slide_count} {t('slides')}</span>
        </div>
    """, unsafe_allow_html=True)

    # Chat interface
    render_chat_interface(lang=lang)


def main():
    """Main application entry point."""
    initialize_session_state()

    lang = st.session_state.language
    is_rtl = lang == 'ar'
    is_dark = st.session_state.dark_mode
    t = lambda key: get_text(key, lang)

    # Apply CSS
    st.markdown(get_app_css(is_dark, is_rtl), unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown(f"### ⚙️ {t('settings')}")

        # Theme toggle
        col1, col2 = st.columns(2)
        with col1:
            theme_icon = "☀️" if is_dark else "🌙"
            if st.button(theme_icon, use_container_width=True, key="theme_toggle", help=t('toggle_theme')):
                st.session_state.dark_mode = not st.session_state.dark_mode
                st.rerun()

        with col2:
            lang_label = "ع" if lang == "en" else "En"
            if st.button(lang_label, use_container_width=True, key="lang_toggle", help=t('toggle_language')):
                st.session_state.language = "ar" if lang == "en" else "en"
                st.rerun()

        # Show file info if uploaded
        if st.session_state.get('processed_file'):
            st.divider()
            file_data = st.session_state.processed_file
            presentation = file_data.get('data')
            slide_count = presentation.total_slides if presentation else 0
            st.markdown(f"""
                <div class="file-info">
                    <div class="file-info-name">📄 {file_data.get('name', '')}</div>
                    <div class="file-info-detail">{slide_count} {t('slides')}</div>
                </div>
            """, unsafe_allow_html=True)

            # Upload new file option
            st.markdown(f"#### {t('upload_title')}")
            new_presentation = render_upload_section(lang=lang)
            if new_presentation:
                st.session_state.messages = []
                st.rerun()

            # Clear chat
            if st.session_state.messages:
                st.divider()
                if st.button(f"🗑️ {t('clear_chat')}", use_container_width=True, key="clear_chat"):
                    st.session_state.messages = []
                    st.rerun()

    # Main content
    if st.session_state.get('processed_file'):
        render_chat_state(lang)
    else:
        render_welcome_state(lang)


if __name__ == "__main__":
    main()
