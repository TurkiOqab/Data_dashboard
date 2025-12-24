"""
File Upload Component

Handles PowerPoint file uploads and processing.
"""

import streamlit as st
from typing import Optional, Callable

from ..services.pptx_processor import PPTXProcessor, ProcessedPresentation
from ..services.embeddings import EmbeddingsService, create_slide_embedding_content
from ..utils.translations import get_text


def render_upload_section(
    on_upload_complete: Optional[Callable[[ProcessedPresentation], None]] = None,
    lang: str = 'en'
) -> Optional[ProcessedPresentation]:
    """
    Render the file upload section.

    Args:
        on_upload_complete: Callback when upload is processed
        lang: Language code for translations

    Returns:
        ProcessedPresentation if a file was processed
    """
    t = lambda key: get_text(key, lang)

    st.markdown(f"### {t('upload_title')}")

    uploaded_file = st.file_uploader(
        t('upload_label'),
        type=["pptx"],
        help=t('upload_help')
    )

    if uploaded_file is not None:
        # Check if this file was already processed
        if 'processed_file' in st.session_state:
            if st.session_state.processed_file.get('name') == uploaded_file.name:
                st.success(t('upload_loaded').format(filename=uploaded_file.name))
                return st.session_state.processed_file.get('data')

        # Process new file
        with st.spinner(t('processing')):
            try:
                # Initialize processor
                processor = PPTXProcessor()
                result = processor.process_uploaded_file(uploaded_file)

                # Store slides in vector database
                embeddings = EmbeddingsService()

                # Clear previous data for fresh start
                embeddings.clear_collection()

                # Prepare slides for embedding
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

                # Store in session state
                st.session_state.processed_file = {
                    'name': uploaded_file.name,
                    'data': result
                }
                st.session_state.embeddings_ready = True

                # Clear cached suggested questions so new ones are generated
                for key in list(st.session_state.keys()):
                    if key.startswith('suggested_questions_'):
                        del st.session_state[key]

                st.success(t('upload_success').format(
                    slides=result.total_slides,
                    filename=result.filename
                ))

                if on_upload_complete:
                    on_upload_complete(result)

                return result

            except Exception as e:
                st.error(t('upload_error').format(error=str(e)))
                return None

    return None


def render_file_info(presentation: ProcessedPresentation, lang: str = 'en'):
    """Render information about the processed file."""
    t = lambda key: get_text(key, lang)

    with st.expander(t('file_overview'), expanded=False):
        st.markdown(f"**{t('file_name')}:** {presentation.filename}")
        st.markdown(f"**{t('total_slides')}:** {presentation.total_slides}")

        # Show slide summary
        for slide in presentation.slides:
            indicators = []
            if slide.has_chart:
                indicators.append(t('chart'))
            if slide.has_image:
                indicators.append(t('image'))
            if slide.tables:
                table_count = len(slide.tables)
                indicators.append(f"{table_count} {t('tables') if table_count > 1 else t('table')}")

            indicator_str = f" [{', '.join(indicators)}]" if indicators else ""
            title = slide.title or t('untitled')

            st.markdown(f"- **{t('slide')} {slide.slide_number}:** {title}{indicator_str}")


def render_slide_browser(presentation: ProcessedPresentation, lang: str = 'en'):
    """Render a browser for viewing individual slides."""
    t = lambda key: get_text(key, lang)

    st.markdown(f"### {t('browse_slides')}")

    # Slide selector
    slide_options = [
        f"{t('slide')} {s.slide_number}: {s.title or t('untitled')}"
        for s in presentation.slides
    ]

    selected = st.selectbox(
        t('select_slide'),
        options=range(len(slide_options)),
        format_func=lambda x: slide_options[x]
    )

    if selected is not None:
        slide = presentation.slides[selected]

        # Display slide content in a card-style layout
        st.markdown(f"""
            <div class="slide-card">
                <span class="slide-number">{t('slide')} {slide.slide_number}</span>
                <div class="slide-title">{slide.title or t('untitled')}</div>
            </div>
        """, unsafe_allow_html=True)

        # Text content
        if slide.text_content:
            st.markdown(f"**{t('content')}:**")
            for text in slide.text_content:
                st.markdown(f"- {text}")

        # Tables
        if slide.tables:
            st.markdown(f"**{t('table')}:**")
            for i, table in enumerate(slide.tables):
                st.markdown(f"*{t('table')} {i+1}:*")
                st.markdown(table.to_markdown())

        # Badges for content types
        badges_html = '<div class="slide-badges">'
        if slide.has_chart:
            badges_html += f'<span class="badge">{t("contains_chart")}</span>'
        if slide.has_image:
            badges_html += f'<span class="badge">{t("contains_image")}</span>'
        if slide.raw_notes:
            badges_html += f'<span class="badge">{t("has_notes")}</span>'
        badges_html += '</div>'

        if slide.has_chart or slide.has_image or slide.raw_notes:
            st.markdown(badges_html, unsafe_allow_html=True)

        # Notes
        if slide.raw_notes:
            with st.expander(t('speaker_notes')):
                st.markdown(slide.raw_notes)
