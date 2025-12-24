"""
Chat Interface Component

Provides a conversational interface for querying slide content.
"""

import streamlit as st
from typing import List, Dict, Any

from ..services.query_engine import QueryEngine
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
            st.warning(f"Running without AI features: {str(e)}")
            st.session_state.query_engine = QueryEngine()

    # Check for pending query
    pending_query = st.session_state.pop('pending_query', None)

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Show source slides for assistant messages
            if message["role"] == "assistant" and message.get("slides"):
                render_source_slides(message["slides"], lang)

    # Show suggestion chips if no messages yet
    if not st.session_state.messages:
        render_suggestion_chips(lang)

    # Chat input
    prompt = st.chat_input(t('chat_placeholder'))

    # Use pending query if no direct input
    if pending_query and not prompt:
        prompt = pending_query

    if prompt:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
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


def render_suggestion_chips(lang: str = 'en'):
    """Render suggestion chips above the chat input."""
    t = lambda key: get_text(key, lang)

    suggestions = [
        t('action_summarize_query'),
        t('action_key_points_query'),
        t('action_data_charts_query'),
    ]

    cols = st.columns(len(suggestions))
    for i, suggestion in enumerate(suggestions):
        with cols[i]:
            # Truncate long suggestions
            display_text = suggestion[:40] + "..." if len(suggestion) > 40 else suggestion
            if st.button(display_text, key=f"suggestion_{i}", use_container_width=True):
                st.session_state.pending_query = suggestion
                st.rerun()


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
                    <span class="badge">{t('relevance')}: {relevance}</span>
                </div>
            """, unsafe_allow_html=True)

            # Show content preview
            content = slide.get('content', '')
            if len(content) > 200:
                content = content[:200] + "..."
            st.caption(content)


def add_user_query(query: str):
    """Programmatically add a user query."""
    st.session_state.pending_query = query
    st.rerun()
