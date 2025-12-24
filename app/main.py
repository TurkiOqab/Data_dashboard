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

from app.components.upload import render_upload_section, render_file_info, render_slide_browser
from app.components.chat import render_chat_interface, render_quick_actions, render_chat_controls, add_user_query
from app.utils.helpers import load_environment
from app.utils.translations import get_text, TRANSLATIONS
from app.services.query_engine import QueryEngine

# Load environment variables
load_environment()

# Page configuration
st.set_page_config(
    page_title="Data Dashboard | لوحة البيانات",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


def get_custom_css(is_dark: bool, is_rtl: bool) -> str:
    """Generate custom CSS based on theme and direction."""

    direction = "rtl" if is_rtl else "ltr"
    text_align = "right" if is_rtl else "left"
    opposite_align = "left" if is_rtl else "right"

    # Refined color palette
    if is_dark:
        colors = {
            'bg_primary': '#0c1220',
            'bg_secondary': '#151d2e',
            'bg_card': '#1a2438',
            'bg_card_hover': '#222f47',
            'bg_elevated': '#1e293b',
            'text_primary': '#f8fafc',
            'text_secondary': '#a1b4c7',
            'text_muted': '#6b7f94',
            'accent': '#e5a84b',
            'accent_hover': '#f0bc6a',
            'accent_subtle': 'rgba(229, 168, 75, 0.12)',
            'accent_glow': 'rgba(229, 168, 75, 0.25)',
            'border': '#2d3f56',
            'border_light': '#384a63',
            'success': '#34d399',
            'error': '#f87171',
            'info': '#60a5fa',
            'shadow_color': 'rgba(0, 0, 0, 0.4)',
        }
    else:
        colors = {
            'bg_primary': '#f5f7fa',
            'bg_secondary': '#ffffff',
            'bg_card': '#ffffff',
            'bg_card_hover': '#f8f9fb',
            'bg_elevated': '#ffffff',
            'text_primary': '#1a202c',
            'text_secondary': '#4a5568',
            'text_muted': '#718096',
            'accent': '#c9940a',
            'accent_hover': '#a67c08',
            'accent_subtle': 'rgba(201, 148, 10, 0.08)',
            'accent_glow': 'rgba(201, 148, 10, 0.15)',
            'border': '#e2e8f0',
            'border_light': '#edf2f7',
            'success': '#10b981',
            'error': '#ef4444',
            'info': '#3b82f6',
            'shadow_color': 'rgba(0, 0, 0, 0.08)',
        }

    return f"""
    <style>
        /* ============================================
           FONT IMPORTS
           ============================================ */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Noto+Kufi+Arabic:wght@400;500;600;700&display=swap');

        /* ============================================
           CSS VARIABLES
           ============================================ */
        :root {{
            --bg-primary: {colors['bg_primary']};
            --bg-secondary: {colors['bg_secondary']};
            --bg-card: {colors['bg_card']};
            --bg-card-hover: {colors['bg_card_hover']};
            --bg-elevated: {colors['bg_elevated']};
            --text-primary: {colors['text_primary']};
            --text-secondary: {colors['text_secondary']};
            --text-muted: {colors['text_muted']};
            --accent: {colors['accent']};
            --accent-hover: {colors['accent_hover']};
            --accent-subtle: {colors['accent_subtle']};
            --accent-glow: {colors['accent_glow']};
            --border: {colors['border']};
            --border-light: {colors['border_light']};
            --success: {colors['success']};
            --error: {colors['error']};
            --info: {colors['info']};
            --shadow-color: {colors['shadow_color']};

            --font-display: 'Plus Jakarta Sans', 'Noto Kufi Arabic', system-ui, sans-serif;
            --font-body: {"'Noto Kufi Arabic', 'Plus Jakarta Sans'" if is_rtl else "'Plus Jakarta Sans', 'Noto Kufi Arabic'"}, system-ui, sans-serif;

            --radius-xs: 6px;
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --radius-xl: 20px;
            --radius-2xl: 28px;

            --shadow-sm: 0 1px 3px var(--shadow-color);
            --shadow-md: 0 4px 16px var(--shadow-color);
            --shadow-lg: 0 12px 40px var(--shadow-color);
            --shadow-glow: 0 0 30px var(--accent-glow);

            --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
            --transition-base: 250ms cubic-bezier(0.4, 0, 0.2, 1);
            --transition-slow: 350ms cubic-bezier(0.4, 0, 0.2, 1);
        }}

        /* ============================================
           GLOBAL RESET & BASE STYLES
           ============================================ */
        .stApp {{
            background: var(--bg-primary) !important;
        }}

        .stApp > header {{
            background: transparent !important;
        }}

        /* Hide Streamlit branding */
        #MainMenu, footer, header[data-testid="stHeader"] {{
            visibility: hidden !important;
            height: 0 !important;
        }}

        .main .block-container {{
            padding: 1.5rem 2.5rem 3rem !important;
            max-width: 1440px;
        }}

        /* ============================================
           TYPOGRAPHY
           ============================================ */
        html, body, [class*="css"] {{
            font-family: var(--font-body) !important;
            direction: {direction};
        }}

        h1, h2, h3, h4, h5, h6 {{
            font-family: var(--font-display) !important;
            color: var(--text-primary) !important;
            font-weight: 600 !important;
            letter-spacing: -0.01em;
            direction: {direction};
            text-align: {text_align};
        }}

        p, span, div, label, li {{
            font-family: var(--font-body) !important;
            color: var(--text-secondary);
            direction: {direction};
            text-align: {text_align};
        }}

        /* ============================================
           COMPLETELY HIDE ALL BROKEN MATERIAL ICONS
           ============================================ */

        /* Nuclear option: Hide ALL elements containing material icon text */
        [data-testid="stSidebarCollapseButton"],
        [data-testid="collapsedControl"],
        button[kind="headerNoPadding"],
        .stDeployButton {{
            display: none !important;
        }}

        /* Hide icon fonts that render as text */
        span[class*="material"],
        i[class*="material"],
        .material-icons,
        .material-symbols-outlined,
        .material-symbols-rounded {{
            font-size: 0 !important;
            visibility: hidden !important;
        }}

        /* Fix any stray icon text in buttons */
        button span[data-testid] {{
            font-family: var(--font-body) !important;
        }}

        /* ============================================
           SIDEBAR
           ============================================ */
        section[data-testid="stSidebar"] {{
            background: var(--bg-secondary) !important;
            border-{opposite_align}: 1px solid var(--border) !important;
            width: 320px !important;
        }}

        section[data-testid="stSidebar"] > div {{
            padding: 1.5rem 1.25rem !important;
            direction: {direction};
        }}

        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
            direction: {direction};
            text-align: {text_align};
        }}

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {{
            font-size: 0.95rem !important;
            font-weight: 600 !important;
            color: var(--text-primary) !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 1rem !important;
        }}

        /* ============================================
           CUSTOM HEADER
           ============================================ */
        .dashboard-header {{
            background: linear-gradient(145deg, var(--bg-card) 0%, var(--bg-elevated) 100%);
            border: 1px solid var(--border);
            border-radius: var(--radius-2xl);
            padding: 2rem 2.5rem;
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
            box-shadow: var(--shadow-md);
        }}

        .dashboard-header::before {{
            content: '';
            position: absolute;
            top: -50%;
            {opposite_align}: -20%;
            width: 60%;
            height: 200%;
            background: radial-gradient(ellipse, var(--accent-glow) 0%, transparent 70%);
            opacity: 0.5;
            pointer-events: none;
        }}

        .dashboard-header::after {{
            content: '';
            position: absolute;
            inset: 0;
            background-image: url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M20 0L40 20L20 40L0 20L20 0z' fill='none' stroke='%23{"e5a84b" if is_dark else "c9940a"}' stroke-width='0.3' opacity='0.15'/%3E%3C/svg%3E");
            background-size: 24px 24px;
            opacity: 0.6;
            pointer-events: none;
        }}

        .header-content {{
            position: relative;
            z-index: 2;
            display: flex;
            align-items: center;
            gap: 1.25rem;
            flex-direction: {"row-reverse" if is_rtl else "row"};
        }}

        .header-icon {{
            width: 56px;
            height: 56px;
            background: linear-gradient(135deg, var(--accent) 0%, var(--accent-hover) 100%);
            border-radius: var(--radius-lg);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.75rem;
            box-shadow: var(--shadow-md), var(--shadow-glow);
            flex-shrink: 0;
        }}

        .header-text {{
            flex: 1;
        }}

        .header-title {{
            font-size: 2rem !important;
            font-weight: 700 !important;
            color: var(--text-primary) !important;
            margin: 0 0 0.35rem 0 !important;
            line-height: 1.2;
        }}

        .header-subtitle {{
            font-size: 1rem !important;
            color: var(--text-muted) !important;
            margin: 0 !important;
            font-weight: 400;
        }}

        /* ============================================
           CARDS
           ============================================ */
        .card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-xl);
            padding: 1.5rem;
            transition: all var(--transition-base);
            position: relative;
            overflow: hidden;
        }}

        .card::before {{
            content: '';
            position: absolute;
            top: 0;
            {text_align}: 0;
            width: 4px;
            height: 100%;
            background: var(--accent);
            opacity: 0;
            transition: opacity var(--transition-base);
        }}

        .card:hover {{
            background: var(--bg-card-hover);
            border-color: var(--border-light);
            box-shadow: var(--shadow-md);
            transform: translateY(-2px);
        }}

        .card:hover::before {{
            opacity: 1;
        }}

        .card-title {{
            font-size: 1.05rem !important;
            font-weight: 600 !important;
            color: var(--text-primary) !important;
            margin-bottom: 0.6rem !important;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            flex-direction: {"row-reverse" if is_rtl else "row"};
        }}

        .card-title .step-number {{
            width: 28px;
            height: 28px;
            background: var(--accent);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.8rem;
            color: {"#1a202c" if not is_dark else "#1a202c"};
            font-weight: 700;
            flex-shrink: 0;
        }}

        .card-description {{
            color: var(--text-muted) !important;
            font-size: 0.9rem;
            line-height: 1.6;
            margin: 0;
        }}

        /* ============================================
           BUTTONS
           ============================================ */
        .stButton > button {{
            background: var(--bg-card) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-md) !important;
            padding: 0.65rem 1.25rem !important;
            font-weight: 500 !important;
            font-family: var(--font-body) !important;
            font-size: 0.9rem !important;
            transition: all var(--transition-fast) !important;
            direction: {direction};
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }}

        .stButton > button:hover {{
            background: var(--accent) !important;
            color: {"#1a202c" if not is_dark else "#1a202c"} !important;
            border-color: var(--accent) !important;
            transform: translateY(-1px);
            box-shadow: var(--shadow-sm);
        }}

        .stButton > button:active {{
            transform: translateY(0);
        }}

        /* Primary buttons */
        .stButton > button[kind="primary"],
        .stButton > button[data-testid="baseButton-primary"] {{
            background: linear-gradient(135deg, var(--accent) 0%, var(--accent-hover) 100%) !important;
            color: {"#1a202c" if not is_dark else "#1a202c"} !important;
            border: none !important;
            font-weight: 600 !important;
            box-shadow: var(--shadow-sm);
        }}

        .stButton > button[kind="primary"]:hover,
        .stButton > button[data-testid="baseButton-primary"]:hover {{
            box-shadow: var(--shadow-md), var(--shadow-glow);
        }}

        /* ============================================
           CHAT INTERFACE
           ============================================ */
        [data-testid="stChatMessage"] {{
            background: var(--bg-card) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-lg) !important;
            padding: 1rem 1.25rem !important;
            margin-bottom: 0.75rem !important;
            direction: {direction};
            box-shadow: var(--shadow-sm);
        }}

        /* User messages */
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {{
            background: var(--accent-subtle) !important;
            border-color: var(--accent) !important;
            border-{text_align}-width: 3px !important;
        }}

        /* Chat input */
        [data-testid="stChatInput"] > div {{
            background: var(--bg-card) !important;
            border: 2px solid var(--border) !important;
            border-radius: var(--radius-lg) !important;
            transition: all var(--transition-fast);
        }}

        [data-testid="stChatInput"] > div:focus-within {{
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 4px var(--accent-subtle) !important;
        }}

        [data-testid="stChatInput"] textarea {{
            font-family: var(--font-body) !important;
            direction: {direction} !important;
            text-align: {text_align} !important;
            color: var(--text-primary) !important;
        }}

        [data-testid="stChatInput"] textarea::placeholder {{
            color: var(--text-muted) !important;
        }}

        /* Chat input send button */
        [data-testid="stChatInput"] button {{
            background: var(--accent) !important;
            border: none !important;
            border-radius: var(--radius-sm) !important;
        }}

        [data-testid="stChatInput"] button svg {{
            fill: {"#1a202c" if not is_dark else "#1a202c"} !important;
        }}

        /* ============================================
           FILE UPLOADER
           ============================================ */
        [data-testid="stFileUploader"] {{
            direction: {direction};
        }}

        [data-testid="stFileUploader"] > div:first-child {{
            background: var(--bg-card) !important;
            border: 2px dashed var(--border) !important;
            border-radius: var(--radius-lg) !important;
            padding: 1.5rem !important;
            transition: all var(--transition-base);
            text-align: center;
        }}

        [data-testid="stFileUploader"] > div:first-child:hover {{
            border-color: var(--accent) !important;
            background: var(--accent-subtle) !important;
        }}

        [data-testid="stFileUploader"] label {{
            color: var(--text-secondary) !important;
            font-size: 0.9rem !important;
        }}

        [data-testid="stFileUploader"] small {{
            color: var(--text-muted) !important;
        }}

        /* ============================================
           INPUTS & FORM ELEMENTS
           ============================================ */
        .stTextInput > div > div > input,
        .stSelectbox > div > div,
        .stTextArea textarea {{
            background: var(--bg-card) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-md) !important;
            color: var(--text-primary) !important;
            font-family: var(--font-body) !important;
            direction: {direction};
            text-align: {text_align};
            padding: 0.65rem 0.9rem !important;
            transition: all var(--transition-fast);
        }}

        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div:focus-within,
        .stTextArea textarea:focus {{
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 3px var(--accent-subtle) !important;
            outline: none !important;
        }}

        .stTextInput label,
        .stSelectbox label,
        .stTextArea label {{
            color: var(--text-secondary) !important;
            font-weight: 500 !important;
            font-size: 0.85rem !important;
            margin-bottom: 0.4rem !important;
        }}

        /* ============================================
           EXPANDER
           ============================================ */
        [data-testid="stExpander"] {{
            background: var(--bg-card) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-md) !important;
            overflow: hidden;
        }}

        [data-testid="stExpander"] summary {{
            padding: 0.9rem 1rem !important;
            font-weight: 500 !important;
            color: var(--text-primary) !important;
            direction: {direction};
        }}

        [data-testid="stExpander"] summary:hover {{
            background: var(--bg-card-hover) !important;
        }}

        [data-testid="stExpander"] [data-testid="stExpanderDetails"] {{
            padding: 0 1rem 1rem !important;
            direction: {direction};
        }}

        /* ============================================
           ALERTS & NOTIFICATIONS
           ============================================ */
        .stAlert, [data-testid="stAlert"] {{
            background: var(--bg-card) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-md) !important;
            direction: {direction};
        }}

        [data-testid="stAlert"] > div {{
            direction: {direction};
            text-align: {text_align};
        }}

        /* Success alert */
        [data-testid="stAlert"][data-baseweb*="positive"] {{
            border-{text_align}: 4px solid var(--success) !important;
        }}

        /* Warning alert */
        [data-testid="stAlert"][data-baseweb*="warning"] {{
            border-{text_align}: 4px solid var(--accent) !important;
        }}

        /* Error alert */
        [data-testid="stAlert"][data-baseweb*="negative"] {{
            border-{text_align}: 4px solid var(--error) !important;
        }}

        /* Info alert */
        [data-testid="stAlert"][data-baseweb*="info"] {{
            border-{text_align}: 4px solid var(--info) !important;
        }}

        /* ============================================
           CUSTOM COMPONENTS
           ============================================ */
        .slide-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 1rem 1.25rem;
            margin-bottom: 0.75rem;
            transition: all var(--transition-base);
            direction: {direction};
        }}

        .slide-card:hover {{
            border-color: var(--accent);
            box-shadow: var(--shadow-sm);
        }}

        .slide-number {{
            background: var(--accent);
            color: {"#1a202c" if not is_dark else "#1a202c"};
            padding: 0.2rem 0.6rem;
            border-radius: var(--radius-xs);
            font-size: 0.75rem;
            font-weight: 700;
            display: inline-block;
            margin-bottom: 0.5rem;
        }}

        .slide-title {{
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.35rem;
            font-size: 0.95rem;
        }}

        .slide-badges {{
            display: flex;
            gap: 0.4rem;
            margin-top: 0.6rem;
            flex-wrap: wrap;
            flex-direction: {"row-reverse" if is_rtl else "row"};
        }}

        .badge {{
            background: var(--accent-subtle);
            color: var(--accent);
            padding: 0.2rem 0.5rem;
            border-radius: var(--radius-xs);
            font-size: 0.7rem;
            font-weight: 600;
        }}

        /* ============================================
           DIVIDER
           ============================================ */
        hr {{
            border: none !important;
            height: 1px !important;
            background: var(--border) !important;
            margin: 1.25rem 0 !important;
        }}

        /* ============================================
           SCROLLBAR
           ============================================ */
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
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
           SPINNER
           ============================================ */
        [data-testid="stSpinner"] > div {{
            border-top-color: var(--accent) !important;
        }}

        /* ============================================
           ANIMATIONS
           ============================================ */
        @keyframes fadeSlideIn {{
            from {{
                opacity: 0;
                transform: translateY(12px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .animate-in {{
            animation: fadeSlideIn 0.5s ease-out forwards;
        }}

        .delay-1 {{ animation-delay: 0.1s; opacity: 0; }}
        .delay-2 {{ animation-delay: 0.2s; opacity: 0; }}
        .delay-3 {{ animation-delay: 0.3s; opacity: 0; }}

        /* ============================================
           RESPONSIVE
           ============================================ */
        @media (max-width: 768px) {{
            .main .block-container {{
                padding: 1rem !important;
            }}

            .dashboard-header {{
                padding: 1.5rem;
            }}

            .header-title {{
                font-size: 1.5rem !important;
            }}

            .header-icon {{
                width: 44px;
                height: 44px;
                font-size: 1.25rem;
            }}

            section[data-testid="stSidebar"] {{
                width: 280px !important;
            }}
        }}

        /* ============================================
           RTL SPECIFIC FIXES
           ============================================ */
        {"" if not is_rtl else '''
        /* Flip chevrons and arrows for RTL */
        [data-testid="stExpander"] summary svg {
            transform: scaleX(-1);
        }

        /* Fix select dropdown alignment */
        .stSelectbox [data-baseweb="select"] > div {
            flex-direction: row-reverse;
        }
        '''}
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


def render_header(lang: str):
    """Render the main dashboard header."""
    t = lambda key: get_text(key, lang)

    st.markdown(f"""
        <div class="dashboard-header animate-in">
            <div class="header-content">
                <div class="header-icon">📊</div>
                <div class="header-text">
                    <h1 class="header-title">{t('app_title')}</h1>
                    <p class="header-subtitle">{t('app_subtitle')}</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_welcome_cards(lang: str):
    """Render the welcome state with step cards."""
    t = lambda key: get_text(key, lang)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
            <div class="card animate-in delay-1">
                <div class="card-title">
                    <span class="step-number">1</span>
                    <span>{t('step_upload')}</span>
                </div>
                <p class="card-description">{t('step_upload_desc')}</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="card animate-in delay-2">
                <div class="card-title">
                    <span class="step-number">2</span>
                    <span>{t('step_process')}</span>
                </div>
                <p class="card-description">{t('step_process_desc')}</p>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="card animate-in delay-3">
                <div class="card-title">
                    <span class="step-number">3</span>
                    <span>{t('step_ask')}</span>
                </div>
                <p class="card-description">{t('step_ask_desc')}</p>
            </div>
        """, unsafe_allow_html=True)


def render_suggested_questions(lang: str):
    """Render AI-generated suggested questions based on uploaded content."""
    t = lambda key: get_text(key, lang)

    # Check if we have a presentation loaded
    if not st.session_state.get('embeddings_ready', False):
        return

    # Generate questions if not cached or language changed
    cache_key = f"suggested_questions_{lang}"
    if cache_key not in st.session_state:
        try:
            query_engine = QueryEngine()
            questions = query_engine.generate_example_questions(num_questions=6, lang=lang)
            st.session_state[cache_key] = questions
        except Exception:
            st.session_state[cache_key] = []

    questions = st.session_state.get(cache_key, [])

    if not questions:
        return

    st.markdown(f"### {t('suggested_questions')}")

    cols = st.columns(2)
    for i, question in enumerate(questions):
        with cols[i % 2]:
            if st.button(
                f'"{question}"',
                key=f"suggested_q_{i}",
                use_container_width=True
            ):
                add_user_query(question)


def main():
    """Main application entry point."""
    initialize_session_state()

    lang = st.session_state.language
    is_rtl = lang == 'ar'
    is_dark = st.session_state.dark_mode
    t = lambda key: get_text(key, lang)

    # Apply custom CSS
    st.markdown(get_custom_css(is_dark, is_rtl), unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        # Language & Theme toggles
        st.markdown(f"### {t('settings')}")

        col1, col2 = st.columns(2)
        with col1:
            theme_icon = "☀️" if is_dark else "🌙"
            if st.button(theme_icon, help=t('toggle_theme'), use_container_width=True):
                st.session_state.dark_mode = not st.session_state.dark_mode
                st.rerun()

        with col2:
            new_lang = "ar" if lang == "en" else "en"
            lang_label = "العربية" if lang == "en" else "English"
            if st.button(lang_label, help=t('toggle_language'), use_container_width=True):
                st.session_state.language = new_lang
                st.rerun()

        st.divider()

        # File upload
        presentation = render_upload_section(lang=lang)

        if presentation:
            st.divider()
            render_file_info(presentation, lang=lang)


    # Main content area
    render_header(lang)

    if st.session_state.get('processed_file'):
        # Dashboard with chat
        col1, col2 = st.columns([3, 2])

        with col1:
            st.markdown(f"### {t('chat_title')}")
            render_chat_controls(lang=lang)
            render_chat_interface(lang=lang)

        with col2:
            render_quick_actions(lang=lang)
            st.divider()
            render_suggested_questions(lang=lang)
            st.divider()

            if st.session_state.get('processed_file', {}).get('data'):
                render_slide_browser(st.session_state.processed_file['data'], lang=lang)
    else:
        # Welcome state
        render_welcome_cards(lang)


if __name__ == "__main__":
    main()
