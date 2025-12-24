"""
Translations Module

Provides bilingual support for English and Arabic.
"""

TRANSLATIONS = {
    'en': {
        # App Header
        'app_title': 'Data Dashboard',
        'app_subtitle': 'Upload presentations and ask questions in natural language',

        # Settings
        'settings': 'Settings',
        'toggle_theme': 'Toggle dark/light mode',
        'toggle_language': 'Switch language',
        'api_key_label': 'API Key (optional)',
        'api_key_help': 'Enter your Anthropic API key to enable AI features',
        'api_key_warning': 'API key not found. Add your key in the sidebar for full AI capabilities.',

        # Steps
        'step_upload': 'Upload',
        'step_upload_desc': 'Drag and drop a PowerPoint file (.pptx) in the sidebar to get started',
        'step_process': 'Process',
        'step_process_desc': 'The system extracts text, tables, and analyzes visual content automatically',
        'step_ask': 'Ask',
        'step_ask_desc': 'Use natural language to find information and insights from your slides',

        # Suggested Questions
        'suggested_questions': 'Suggested Questions',

        # Upload Section
        'upload_title': 'Upload Presentation',
        'upload_label': 'Drag and drop a file (PowerPoint or PDF)',
        'upload_help': 'Upload a .pptx or .pdf file to analyze its contents',
        'upload_success': 'Processed {slides} slides from {filename}',
        'upload_loaded': 'Currently loaded: {filename}',
        'upload_error': 'Error processing file: {error}',
        'processing': 'Processing presentation...',

        # File Info
        'file_overview': 'Presentation Overview',
        'file_name': 'File',
        'total_slides': 'Total Slides',
        'slide': 'Slide',
        'untitled': 'Untitled',
        'chart': 'Chart',
        'image': 'Image',
        'table': 'Table',
        'tables': 'tables',

        # Chat Interface
        'chat_title': 'Ask Questions',
        'chat_placeholder': 'Ask about your slides...',
        'chat_upload_first': 'Upload a presentation to start asking questions.',
        'chat_thinking': 'Thinking...',
        'chat_error': 'Sorry, I encountered an error: {error}',
        'clear_chat': 'Clear Chat',
        'sources': 'Sources',
        'slides': 'slides',
        'relevance': 'Relevance',
        'relevance_high': 'High',
        'relevance_medium': 'Medium',
        'relevance_low': 'Low',

        # Quick Actions
        'quick_actions': 'Quick Actions',
        'action_summarize': 'Summarize All',
        'action_summarize_query': 'Give me a summary of all the slides',
        'action_key_points': 'Key Points',
        'action_key_points_query': 'What are the main key points from this presentation?',
        'action_data_charts': 'Data & Charts',
        'action_data_charts_query': 'What data and charts are shown in this presentation?',

        # Slide Browser
        'browse_slides': 'Browse Slides',
        'select_slide': 'Select a slide to view',
        'content': 'Content',
        'speaker_notes': 'Speaker Notes',
        'contains_chart': 'Contains Chart',
        'contains_image': 'Contains Image',
        'has_notes': 'Has Notes',

    },
    'ar': {
        # App Header
        'app_title': 'لوحة البيانات',
        'app_subtitle': 'ارفع العروض التقديمية واطرح الأسئلة بلغة طبيعية',

        # Settings
        'settings': 'الإعدادات',
        'toggle_theme': 'تبديل الوضع الداكن/الفاتح',
        'toggle_language': 'تغيير اللغة',
        'api_key_label': 'مفتاح API (اختياري)',
        'api_key_help': 'أدخل مفتاح Anthropic API لتفعيل ميزات الذكاء الاصطناعي',
        'api_key_warning': 'لم يتم العثور على مفتاح API. أضف مفتاحك في الشريط الجانبي للحصول على جميع الميزات.',

        # Steps
        'step_upload': 'الرفع',
        'step_upload_desc': 'اسحب وأفلت ملف PowerPoint (.pptx) في الشريط الجانبي للبدء',
        'step_process': 'المعالجة',
        'step_process_desc': 'يقوم النظام باستخراج النصوص والجداول وتحليل المحتوى المرئي تلقائياً',
        'step_ask': 'السؤال',
        'step_ask_desc': 'استخدم اللغة الطبيعية للعثور على المعلومات والرؤى من الشرائح',

        # Suggested Questions
        'suggested_questions': 'أسئلة مقترحة',

        # Upload Section
        'upload_title': 'رفع العرض التقديمي',
        'upload_label': 'اسحب وأفلت ملف (PowerPoint أو PDF)',
        'upload_help': 'ارفع ملف .pptx أو .pdf لتحليل محتواه',
        'upload_success': 'تمت معالجة {slides} شريحة من {filename}',
        'upload_loaded': 'محمّل حالياً: {filename}',
        'upload_error': 'خطأ في معالجة الملف: {error}',
        'processing': 'جاري معالجة العرض التقديمي...',

        # File Info
        'file_overview': 'نظرة عامة على العرض',
        'file_name': 'الملف',
        'total_slides': 'إجمالي الشرائح',
        'slide': 'شريحة',
        'untitled': 'بدون عنوان',
        'chart': 'رسم بياني',
        'image': 'صورة',
        'table': 'جدول',
        'tables': 'جداول',

        # Chat Interface
        'chat_title': 'اطرح الأسئلة',
        'chat_placeholder': 'اسأل عن الشرائح...',
        'chat_upload_first': 'ارفع عرضاً تقديمياً للبدء في طرح الأسئلة.',
        'chat_thinking': 'جاري التفكير...',
        'chat_error': 'عذراً، حدث خطأ: {error}',
        'clear_chat': 'مسح',
        'sources': 'المصادر',
        'slides': 'شرائح',
        'relevance': 'الصلة',
        'relevance_high': 'عالية',
        'relevance_medium': 'متوسطة',
        'relevance_low': 'منخفضة',

        # Quick Actions
        'quick_actions': 'إجراءات سريعة',
        'action_summarize': 'تلخيص الكل',
        'action_summarize_query': 'أعطني ملخصاً لجميع الشرائح',
        'action_key_points': 'النقاط الرئيسية',
        'action_key_points_query': 'ما هي النقاط الرئيسية من هذا العرض التقديمي؟',
        'action_data_charts': 'البيانات والرسوم',
        'action_data_charts_query': 'ما هي البيانات والرسوم البيانية المعروضة في هذا العرض؟',

        # Slide Browser
        'browse_slides': 'تصفح الشرائح',
        'select_slide': 'اختر شريحة للعرض',
        'content': 'المحتوى',
        'speaker_notes': 'ملاحظات المتحدث',
        'contains_chart': 'يحتوي على رسم بياني',
        'contains_image': 'يحتوي على صورة',
        'has_notes': 'يحتوي على ملاحظات',

    }
}


def get_text(key: str, lang: str = 'en') -> str:
    """
    Get translated text for a given key.

    Args:
        key: Translation key
        lang: Language code ('en' or 'ar')

    Returns:
        Translated string or key if not found
    """
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)
