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

from app.components.chat import render_chat_interface
from app.utils.helpers import load_environment
from app.utils.translations import get_text

# Load environment variables
load_environment()

# Page configuration - no sidebar
st.set_page_config(
    page_title="Data Dashboard | لوحة البيانات",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def get_app_css(is_dark: bool, is_rtl: bool) -> str:
    """Generate application CSS with top navbar."""

    direction = "rtl" if is_rtl else "ltr"
    text_align = "right" if is_rtl else "left"
    flex_dir = "row-reverse" if is_rtl else "row"

    if is_dark:
        colors = {
            'bg_main': '#1a1a1a',
            'bg_navbar': '#242424',
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
            'bg_navbar': '#f7f7f8',
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
            --bg-navbar: {colors['bg_navbar']};
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

        /* Hide Streamlit elements */
        #MainMenu, footer, header[data-testid="stHeader"],
        section[data-testid="stSidebar"],
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="collapsedControl"] {{
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
           TOP NAVBAR
           ============================================ */
        .navbar {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 60px;
            background: var(--bg-navbar);
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 1.5rem;
            z-index: 1000;
            flex-direction: {flex_dir};
        }}

        .navbar-brand {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            flex-direction: {flex_dir};
        }}

        .navbar-logo {{
            width: 36px;
            height: 36px;
            background: linear-gradient(135deg, var(--accent), var(--accent-hover));
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
        }}

        .navbar-title {{
            font-size: 1.125rem;
            font-weight: 600;
            color: var(--text-primary);
            margin: 0;
        }}

        .navbar-actions {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            flex-direction: {flex_dir};
        }}

        .nav-btn {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.5rem 0.75rem;
            font-size: 0.875rem;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.15s ease;
            font-family: var(--font-main);
            display: flex;
            align-items: center;
            gap: 0.375rem;
        }}

        .nav-btn:hover {{
            background: var(--bg-hover);
            border-color: var(--accent);
            color: var(--text-primary);
        }}

        .nav-btn.active {{
            background: var(--accent-soft);
            border-color: var(--accent);
            color: var(--accent);
        }}

        /* File indicator in navbar */
        .nav-file {{
            background: var(--accent-soft);
            border: 1px solid var(--accent);
            border-radius: 2rem;
            padding: 0.375rem 0.875rem;
            font-size: 0.8rem;
            color: var(--accent);
            font-weight: 500;
            max-width: 200px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}

        /* ============================================
           MAIN CONTAINER
           ============================================ */
        .main .block-container {{
            max-width: 900px !important;
            padding: 80px 1rem 120px 1rem !important;
            margin: 0 auto !important;
        }}

        /* ============================================
           WELCOME HEADER
           ============================================ */
        .app-header {{
            text-align: center;
            padding: 2rem 0 1.5rem;
        }}

        .app-logo {{
            width: 72px;
            height: 72px;
            background: linear-gradient(135deg, var(--accent), var(--accent-hover));
            border-radius: 16px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 2.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 20px var(--accent-soft);
        }}

        .app-title {{
            font-size: 2rem !important;
            font-weight: 600 !important;
            color: var(--text-primary) !important;
            margin: 0 0 0.5rem 0 !important;
        }}

        .app-subtitle {{
            font-size: 1.125rem;
            color: var(--text-muted);
            margin: 0;
        }}

        /* ============================================
           UPLOAD ZONE
           ============================================ */
        [data-testid="stFileUploader"] {{
            margin-top: 1.5rem;
        }}

        [data-testid="stFileUploader"] > div:first-child {{
            background: var(--bg-card) !important;
            border: 2px dashed var(--border) !important;
            border-radius: 16px !important;
            padding: 2.5rem !important;
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
           STEP CARDS
           ============================================ */
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
            width: 36px;
            height: 36px;
            background: var(--accent);
            color: white;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 1rem;
            margin-bottom: 0.75rem;
        }}

        .step-title {{
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
            font-size: 1rem;
        }}

        .step-desc {{
            font-size: 0.875rem;
            color: var(--text-muted);
            line-height: 1.5;
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
            text-align: {text_align};
        }}

        [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {{
            direction: {direction} !important;
            text-align: {text_align} !important;
        }}

        [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {{
            color: var(--text-primary) !important;
            line-height: 1.8;
            direction: {direction} !important;
            text-align: {text_align} !important;
        }}

        [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] ul,
        [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] ol {{
            direction: {direction} !important;
            text-align: {text_align} !important;
            padding-{"right" if is_rtl else "left"}: 1.5rem !important;
            padding-{"left" if is_rtl else "right"}: 0 !important;
            margin: 0.75rem 0 !important;
        }}

        [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li {{
            color: var(--text-primary) !important;
            line-height: 1.8;
            margin-bottom: 0.5rem;
            direction: {direction} !important;
            text-align: {text_align} !important;
        }}

        [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li::marker {{
            color: var(--accent) !important;
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
            padding: 1.5rem 1rem !important;
            background: var(--bg-main) !important;
            z-index: 100 !important;
            border-top: 1px solid var(--border) !important;
        }}

        [data-testid="stChatInput"] > div {{
            background: var(--bg-card) !important;
            border: 1px solid var(--border) !important;
            border-radius: 12px !important;
            box-shadow: 0 2px 12px rgba(0,0,0,0.1) !important;
            min-height: 52px !important;
            display: flex !important;
            align-items: center !important;
            padding: 0.25rem !important;
            gap: 0.5rem !important;
        }}

        [data-testid="stChatInput"] > div:focus-within {{
            border-color: var(--accent) !important;
        }}

        [data-testid="stChatInput"] textarea {{
            font-family: var(--font-main) !important;
            color: var(--text-primary) !important;
            direction: {direction} !important;
            text-align: {text_align} !important;
            min-height: 24px !important;
            padding: 0.75rem 1rem !important;
            flex: 1 !important;
            padding-{"left" if is_rtl else "right"}: 50px !important;
        }}

        [data-testid="stChatInput"] textarea::placeholder {{
            color: var(--text-muted) !important;
        }}

        [data-testid="stChatInput"] button {{
            background: var(--accent) !important;
            border: none !important;
            border-radius: 8px !important;
            min-width: 40px !important;
            width: 40px !important;
            height: 40px !important;
            min-height: 40px !important;
            flex-shrink: 0 !important;
            position: absolute !important;
            {"left" if is_rtl else "right"}: 0.75rem !important;
            margin: 0 !important;
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
            padding: 0.5rem 1rem !important;
            transition: all 0.15s ease !important;
            min-height: 38px !important;
        }}

        .stButton > button:hover {{
            background: var(--bg-hover) !important;
            border-color: var(--accent) !important;
        }}

        /* ============================================
           EXPANDER & ALERTS
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

        [data-testid="stAlert"] {{
            background: var(--bg-card) !important;
            border: 1px solid var(--border) !important;
            border-radius: 8px !important;
        }}

        /* ============================================
           SPINNER & DIVIDER
           ============================================ */
        [data-testid="stSpinner"] > div {{
            border-top-color: var(--accent) !important;
        }}

        hr {{
            border: none !important;
            height: 1px !important;
            background: var(--border) !important;
            margin: 1.5rem 0 !important;
        }}

        /* ============================================
           SLIDE CARDS
           ============================================ */
        .slide-card {{
            background: var(--bg-card);
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
            .navbar {{
                padding: 0 1rem;
            }}

            .navbar-title {{
                display: none;
            }}

            .nav-file {{
                max-width: 120px;
            }}

            .main .block-container {{
                padding: 70px 0.75rem 120px 0.75rem !important;
            }}
        }}
    </style>
    """


def render_navbar(lang: str, is_dark: bool, has_file: bool = False, filename: str = ""):
    """Render the top navigation bar."""
    t = lambda key: get_text(key, lang)

    # Navbar HTML with buttons that will be handled by Streamlit
    file_indicator = f'<span class="nav-file">📄 {filename[:20]}{"..." if len(filename) > 20 else ""}</span>' if has_file else ""

    st.markdown(f"""
        <div class="navbar">
            <div class="navbar-brand">
                <div class="navbar-logo">📊</div>
                <span class="navbar-title">{t('app_title')}</span>
            </div>
            <div class="navbar-actions">
                {file_indicator}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Settings row below navbar (using Streamlit buttons)
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col2:
        theme_label = "☀️ Light" if is_dark else "🌙 Dark"
        if st.button(theme_label, key="theme_btn", use_container_width=True):
            st.session_state.dark_mode = not is_dark
            st.rerun()

    with col3:
        lang_label = "العربية" if lang == "en" else "English"
        if st.button(f"🌐 {lang_label}", key="lang_btn", use_container_width=True):
            st.session_state.language = "ar" if lang == "en" else "en"
            st.rerun()


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

    # File uploader - supports PPTX and PDF
    uploaded_file = st.file_uploader(
        t('upload_label'),
        type=["pptx", "pdf"],
        help=t('upload_help'),
        key="main_uploader"
    )

    if uploaded_file is not None:
        from app.services.embeddings import EmbeddingsService

        if 'processed_file' not in st.session_state or st.session_state.processed_file.get('name') != uploaded_file.name:
            with st.spinner(t('processing')):
                try:
                    file_ext = uploaded_file.name.lower().split('.')[-1]

                    embeddings = EmbeddingsService()
                    embeddings.clear_collection()

                    if file_ext == 'pptx':
                        # Process PowerPoint
                        from app.services.pptx_processor import PPTXProcessor
                        from app.services.embeddings import create_slide_embedding_content

                        processor = PPTXProcessor()
                        result = processor.process_uploaded_file(uploaded_file)

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
                        total_items = result.total_slides

                    elif file_ext == 'pdf':
                        # Process PDF
                        from app.services.pdf_processor import PDFProcessor, create_page_embedding_content

                        processor = PDFProcessor()
                        result = processor.process_uploaded_file(uploaded_file)

                        pages_to_embed = []
                        for page in result.pages:
                            page_id = f"{result.filename}_page_{page.page_number}"
                            content = create_page_embedding_content(page.to_dict())
                            pages_to_embed.append({
                                'id': page_id,
                                'content': content,
                                'metadata': {
                                    'filename': result.filename,
                                    'slide_number': page.page_number,  # Use slide_number for consistency
                                    'title': page.title or f"Page {page.page_number}",
                                    'has_chart': False,
                                    'has_image': False,
                                    'has_table': len(page.tables) > 0
                                }
                            })

                        embeddings.add_slides_batch(pages_to_embed)
                        total_items = result.total_pages

                    st.session_state.processed_file = {
                        'name': uploaded_file.name,
                        'data': result,
                        'type': file_ext
                    }
                    st.session_state.embeddings_ready = True
                    st.session_state.messages = []

                    st.success(t('upload_success').format(slides=total_items, filename=uploaded_file.name))
                    st.rerun()

                except Exception as e:
                    st.error(t('upload_error').format(error=str(e)))

    # Steps
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
    file_type = file_data.get('type', 'pptx')
    data = file_data.get('data')

    # Get page/slide count based on file type
    if file_type == 'pdf':
        slide_count = data.total_pages if data else 0
    else:
        slide_count = data.total_slides if data else 0

    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("📄 " + filename[:15] + "...", key="file_info", use_container_width=True):
            pass  # Could show file details

    with col2:
        if st.button(f"🗑️ {t('clear_chat')}", key="clear_chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    with col3:
        if st.button("📤 Upload New", key="new_upload", use_container_width=True):
            st.session_state.processed_file = None
            st.session_state.embeddings_ready = False
            st.session_state.messages = []
            st.rerun()

    st.markdown("---")

    # Chat interface
    render_chat_interface(lang=lang)


def main():
    """Main application entry point."""
    initialize_session_state()

    lang = st.session_state.language
    is_rtl = lang == 'ar'
    is_dark = st.session_state.dark_mode
    t = lambda key: get_text(key, lang)

    # Get file info
    has_file = st.session_state.get('processed_file') is not None
    filename = st.session_state.get('processed_file', {}).get('name', '') if has_file else ""

    # Apply CSS
    st.markdown(get_app_css(is_dark, is_rtl), unsafe_allow_html=True)

    # Render navbar
    render_navbar(lang, is_dark, has_file, filename)

    # Main content
    if has_file:
        render_chat_state(lang)
    else:
        render_welcome_state(lang)


if __name__ == "__main__":
    main()
