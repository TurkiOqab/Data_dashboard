"""
Chat Interface Component

Provides a conversational interface for querying slide content.
"""

import streamlit as st
from typing import List, Dict, Any, Optional

from ..services.query_engine import QueryEngine
from ..services.embeddings import EmbeddingsService
from ..utils.translations import get_text


def initialize_chat_state():
    """Initialize chat-related session state."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    if 'query_engine' not in st.session_state:
        st.session_state.query_engine = None


def render_chat_interface(lang: str = 'en'):
    """Render the chat interface for querying slides."""
    initialize_chat_state()
    t = lambda key: get_text(key, lang)

    # Check if embeddings are ready
    if not st.session_state.get('embeddings_ready', False):
        st.info(t('chat_upload_first'))
        return

    # Initialize query engine if needed
    if st.session_state.query_engine is None:
        try:
            st.session_state.query_engine = QueryEngine()
        except Exception as e:
            st.warning(f"Note: Running without AI features. {str(e)}")
            st.session_state.query_engine = QueryEngine()

    # Check for pending quick action query
    pending_query = st.session_state.pop('pending_query', None)

    # Avatar settings (using simple emojis that Streamlit supports)
    user_avatar = "👨"
    assistant_avatar = "🤖"

    # Display chat history
    for message in st.session_state.messages:
        avatar = user_avatar if message["role"] == "user" else assistant_avatar
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

            # Show source slides for assistant messages
            if message["role"] == "assistant" and message.get("slides"):
                render_source_slides(message["slides"], lang)

    # Chat input or pending query
    prompt = st.chat_input(t('chat_placeholder'))

    # Use pending query if no direct input
    if pending_query and not prompt:
        prompt = pending_query

    if prompt:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user", avatar=user_avatar):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant", avatar=assistant_avatar):
            with st.spinner(t('chat_thinking')):
                try:
                    result = st.session_state.query_engine.chat(
                        prompt,
                        chat_history=st.session_state.messages[:-1]
                    )

                    st.markdown(result["answer"])

                    # Show source slides
                    if result.get("relevant_slides"):
                        render_source_slides(result["relevant_slides"], lang)

                    # Store assistant message
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result["answer"],
                        "slides": result.get("relevant_slides", [])
                    })

                except Exception as e:
                    error_msg = t('chat_error').format(error=str(e))
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })


def render_source_slides(slides: List[Dict[str, Any]], lang: str = 'en'):
    """Render the source slides used to generate a response."""
    t = lambda key: get_text(key, lang)

    if not slides:
        return

    with st.expander(f"{t('sources')} ({len(slides)} {t('slides')})", expanded=False):
        for slide in slides:
            metadata = slide.get('metadata', {})
            slide_num = metadata.get('slide_number', '?')
            title = metadata.get('title', t('untitled'))
            distance = slide.get('distance', 0)

            # Relevance indicator
            if distance < 0.5:
                relevance = t('relevance_high')
            elif distance < 1.0:
                relevance = t('relevance_medium')
            else:
                relevance = t('relevance_low')

            st.markdown(f"""
                <div class="slide-card">
                    <span class="slide-number">{t('slide')} {slide_num}</span>
                    <div class="slide-title">{title}</div>
                    <div class="slide-badges">
                        <span class="badge">{t('relevance')}: {relevance}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Show content preview
            content = slide.get('content', '')
            if len(content) > 200:
                content = content[:200] + "..."
            st.caption(content)


def render_quick_actions(lang: str = 'en'):
    """Render quick action buttons for common queries."""
    t = lambda key: get_text(key, lang)

    st.markdown(f"### {t('quick_actions')}")

    # Vertical layout for better text display
    if st.button(f"📋  {t('action_summarize')}", use_container_width=True, key="qa_summarize"):
        add_user_query(t('action_summarize_query'))

    if st.button(f"🎯  {t('action_key_points')}", use_container_width=True, key="qa_keypoints"):
        add_user_query(t('action_key_points_query'))

    if st.button(f"📊  {t('action_data_charts')}", use_container_width=True, key="qa_charts"):
        add_user_query(t('action_data_charts_query'))


def add_user_query(query: str):
    """Programmatically add a user query via quick actions."""
    st.session_state.pending_query = query
    st.rerun()


def clear_chat():
    """Clear chat history."""
    st.session_state.messages = []


def render_chat_controls(lang: str = 'en'):
    """Render chat control buttons."""
    t = lambda key: get_text(key, lang)

    col1, col2 = st.columns([1, 4])

    with col1:
        if st.button(f"🗑️ {t('clear_chat')}", type="secondary"):
            clear_chat()
            st.rerun()
