#!/usr/bin/env python3
"""Add tags to all tool markdown files based on category and description keywords."""

import os
import re

TOOLS_DIR = os.path.join(os.path.dirname(__file__), '..', 'content', 'tools')

CATEGORY_TAGS = {
    '3d':                      ['3d', 'design', 'creative', 'modeling', 'rendering', 'visualization', '3d_art', 'digital_art', 'sculpting'],
    'academia':                ['research', 'education', 'academic', 'papers', 'scholars', 'literature', 'citations', 'peer_review', 'university'],
    'ad-generator':            ['advertising', 'marketing', 'creative', 'ads', 'campaigns', 'ad_copy', 'digital_ads', 'performance', 'targeting'],
    'ai-agents':               ['ai_agent', 'automation', 'autonomous', 'ai_assistants', 'agents', 'multi_agent', 'task_automation', 'orchestration', 'agentic'],
    'ai-companion':            ['ai_companion', 'chatbot', 'conversation', 'ai_assistant', 'chat', 'companionship', 'emotional_support', 'roleplay', 'personal'],
    'ai-directories':          ['directory', 'reference', 'tools', 'discovery', 'listing', 'ai_tools', 'catalog', 'collection', 'curation'],
    'animation':               ['animation', 'video', 'creative', 'motion', 'graphics', 'motion_design', '2d_animation', '3d_animation', 'visual_effects'],
    'app-builders':            ['no_code', 'app_builder', 'developer_tools', 'app_development', 'lowcode', 'rapid_prototyping', 'mobile_apps', 'web_apps', 'deployment'],
    'audio':                   ['audio', 'creative', 'sound', 'music', 'recording', 'audio_editing', 'sound_design', 'mixing', 'production'],
    'automation':              ['automation', 'workflow', 'productivity', 'repetitive_tasks', 'efficiency', 'process_automation', 'triggers', 'scheduling', 'bots'],
    'background-remover':      ['image_editing', 'design', 'creative', 'background', 'image_processing', 'cutout', 'transparency', 'photo_editing', 'visual'],
    'business-tools':          ['business', 'productivity', 'enterprise', 'operations', 'management', 'documents', 'contracts', 'proposals', 'workflow'],
    'calendar-scheduling':     ['scheduling', 'productivity', 'calendar', 'time_management', 'meetings', 'appointments', 'booking', 'availability', 'planning'],
    'chatbots':                ['chatbot', 'text_generation', 'ai_assistant', 'conversational', 'nlp', 'dialogue', 'llm', 'general_ai', 'question_answering'],
    'climate':                 ['climate', 'environment', 'sustainability', 'emissions', 'green', 'carbon', 'renewable_energy', 'esg', 'net_zero'],
    'code-assistant':          ['code_generation', 'developer_tools', 'productivity', 'coding', 'programming', 'autocomplete', 'debugging', 'refactoring', 'ide'],
    'copywriting':             ['writing', 'marketing', 'text_generation', 'copy', 'content', 'ad_copy', 'seo_writing', 'brand_voice', 'persuasion'],
    'crm':                     ['crm', 'sales', 'business', 'customers', 'relationships', 'pipeline', 'contacts', 'deals', 'customer_data'],
    'customer-support':        ['customer_support', 'chatbot', 'business', 'help_desk', 'support', 'ticketing', 'live_chat', 'service', 'resolution'],
    'data':                    ['data_analysis', 'analytics', 'business', 'insights', 'visualization', 'data_science', 'reporting', 'dashboards', 'sql'],
    'devtools':                ['developer_tools', 'code_generation', 'infrastructure', 'deployment', 'development', 'devops', 'ci_cd', 'cloud', 'api'],
    'document-ai':             ['document_ai', 'pdf', 'productivity', 'extraction', 'documents', 'ocr', 'summarization', 'document_processing', 'parsing'],
    'e-commerce':              ['ecommerce', 'business', 'marketing', 'retail', 'shopping', 'online_store', 'product_catalog', 'checkout', 'conversions'],
    'email-assistants':        ['email', 'productivity', 'writing', 'communication', 'inbox', 'email_management', 'drafting', 'scheduling', 'follow_up'],
    'farming':                 ['farming', 'agriculture', 'agritech', 'crops', 'sustainability', 'precision_agriculture', 'soil', 'yield', 'irrigation'],
    'fashion':                 ['fashion', 'design', 'style', 'clothing', 'retail', 'styling', 'outfit', 'trend', 'wardrobe'],
    'finance':                 ['finance', 'business', 'analytics', 'accounting', 'investment', 'financial_planning', 'budgeting', 'fintech', 'reporting'],
    'food':                    ['food', 'lifestyle', 'cooking', 'recipes', 'nutrition', 'meal_planning', 'ingredients', 'diet', 'culinary'],
    'gaming':                  ['gaming', 'creative', 'entertainment', 'games', 'interactive', 'game_development', 'procedural', 'npcs', 'immersive'],
    'government':              ['government', 'civic', 'public', 'policy', 'official', 'compliance', 'federal', 'public_sector', 'security'],
    'graphic-design':          ['design', 'image_editing', 'creative', 'visual', 'branding', 'typography', 'layouts', 'ui_design', 'illustration'],
    'healthcare':              ['healthcare', 'medical', 'health', 'wellness', 'clinical', 'diagnosis', 'patient', 'ehr', 'telemedicine'],
    'home-design':             ['home_design', 'design', 'creative', 'interior', 'architecture', 'floor_plan', 'furniture', 'renovation', 'decor'],
    'hr':                      ['hr', 'business', 'recruitment', 'employees', 'human_resources', 'onboarding', 'performance', 'payroll', 'talent'],
    'image-editing':           ['image_editing', 'design', 'creative', 'photo', 'visual', 'retouching', 'filters', 'enhancement', 'manipulation'],
    'image-generation':        ['image_generation', 'creative', 'text_to_image', 'visual', 'graphics', 'generative_ai', 'art', 'diffusion', 'prompting'],
    'infographics':            ['design', 'data_visualization', 'marketing', 'visual', 'creative', 'charts', 'diagrams', 'storytelling', 'communication'],
    'job-tools':               ['career', 'hr', 'recruitment', 'jobs', 'employment', 'job_search', 'resume', 'interview', 'hiring'],
    'knowledge-management':    ['knowledge_base', 'productivity', 'note_taking', 'organization', 'information', 'second_brain', 'wiki', 'search', 'retrieval'],
    'language-learning':       ['language_learning', 'education', 'languages', 'learning', 'multilingual', 'vocabulary', 'grammar', 'speaking', 'immersion'],
    'lead-generation':         ['sales', 'marketing', 'business', 'leads', 'prospecting', 'outreach', 'pipeline', 'b2b', 'conversion'],
    'learning-tools':          ['education', 'learning', 'teaching', 'courses', 'training', 'tutoring', 'study', 'assessment', 'e_learning'],
    'legal-assistants':        ['legal', 'document_ai', 'business', 'contracts', 'compliance', 'law', 'legal_research', 'due_diligence', 'drafting'],
    'local-search-engines':    ['search', 'local', 'location', 'maps', 'discovery', 'places', 'reviews', 'navigation', 'geo'],
    'logo-generator':          ['design', 'image_generation', 'branding', 'logo', 'identity', 'brand_assets', 'visual_identity', 'symbols', 'creative'],
    'market-research':         ['market_research', 'business', 'analytics', 'consumer', 'insights', 'surveys', 'competitive_analysis', 'trends', 'intelligence'],
    'marketing':               ['marketing', 'business', 'campaigns', 'growth', 'promotion', 'demand_generation', 'brand', 'digital_marketing', 'roi'],
    'meeting-assistants':      ['meeting', 'productivity', 'transcription', 'collaboration', 'notes', 'summaries', 'action_items', 'video_calls', 'recap'],
    'meme-generator':          ['meme', 'creative', 'social_media', 'humor', 'content', 'viral', 'fun', 'images', 'captions'],
    'models':                  ['llm', 'foundation_model', 'ai_model', 'machine_learning', 'neural', 'inference', 'fine_tuning', 'api', 'open_source'],
    'music-generation':        ['music_generation', 'audio', 'creative', 'music', 'composition', 'ai_music', 'beats', 'melody', 'soundtrack'],
    'no-code':                 ['no_code', 'automation', 'app_builder', 'lowcode', 'visual', 'drag_and_drop', 'workflow', 'builder', 'citizen_developer'],
    'note-taking-apps':        ['note_taking', 'productivity', 'knowledge_base', 'organization', 'documentation', 'markdown', 'journaling', 'tasks', 'sync'],
    'others':                  ['other', 'miscellaneous', 'tools', 'utilities', 'general', 'innovative', 'niche', 'experimental', 'unique'],
    'personal-assistants':     ['ai_assistant', 'productivity', 'chatbot', 'support', 'helpful', 'personal', 'tasks', 'reminders', 'smart'],
    'podcast':                 ['podcast', 'audio', 'content_creation', 'media', 'broadcasting', 'episodes', 'hosting', 'editing', 'distribution'],
    'presentation':            ['presentation', 'productivity', 'design', 'slides', 'communication', 'pitch_deck', 'storytelling', 'visual', 'templates'],
    'productivity':            ['productivity', 'ai_assistant', 'efficiency', 'workflow', 'organization', 'tasks', 'focus', 'time_management', 'collaboration'],
    'project-management':      ['project_management', 'productivity', 'team', 'collaboration', 'planning', 'tasks', 'milestones', 'tracking', 'agile'],
    'real-estate':             ['real_estate', 'business', 'property', 'housing', 'investment', 'listings', 'mortgage', 'valuation', 'market_data'],
    'research-tools':          ['research', 'analytics', 'academic', 'studies', 'investigation', 'literature_review', 'citations', 'discovery', 'synthesis'],
    'resume-tools':            ['resume', 'career', 'writing', 'job_search', 'cv', 'cover_letter', 'ats', 'interview', 'professional'],
    'sales-tools':             ['sales', 'business', 'crm', 'revenue', 'conversion', 'pipeline', 'prospecting', 'closing', 'forecasting'],
    'search-engines':          ['search', 'ai_assistant', 'discovery', 'information', 'query', 'web_search', 'answers', 'knowledge', 'retrieval'],
    'seo':                     ['seo', 'marketing', 'analytics', 'ranking', 'optimization', 'keywords', 'content_seo', 'backlinks', 'serp'],
    'social-media-tools':      ['social_media', 'marketing', 'content_creation', 'engagement', 'posting', 'scheduling', 'analytics', 'audience', 'platform'],
    'spreadsheets':            ['spreadsheet', 'data_analysis', 'productivity', 'data', 'sheets', 'formulas', 'excel', 'automation', 'calculations'],
    'supply-chain':            ['supply_chain', 'logistics', 'business', 'inventory', 'management', 'procurement', 'distribution', 'forecasting', 'operations'],
    'talking-avatar-generator':['avatar', 'video_generation', 'creative', 'video', 'animation', 'digital_human', 'lip_sync', 'presenter', 'synthetic_media'],
    'text-to-speech':          ['text_to_speech', 'audio', 'voice', 'narration', 'accessibility', 'tts', 'speech_synthesis', 'voiceover', 'reading'],
    'transcription':           ['transcription', 'speech_to_text', 'audio', 'text', 'conversion', 'captions', 'subtitles', 'accuracy', 'real_time'],
    'translator':              ['translation', 'language', 'multilingual', 'communication', 'localization', 'globalization', 'language_ai', 'interpretation', 'text'],
    'video':                   ['video', 'creative', 'media', 'content', 'production', 'recording', 'streaming', 'publishing', 'video_creation'],
    'video-editor':            ['video_editing', 'creative', 'video', 'production', 'media', 'cutting', 'transitions', 'effects', 'export'],
    'video-enhancer':          ['video_editing', 'upscaling', 'creative', 'quality', 'enhancement', 'restoration', 'sharpening', 'resolution', 'denoising'],
    'video-generator':         ['video_generation', 'creative', 'text_to_video', 'animation', 'production', 'ai_video', 'generative', 'short_form', 'clips'],
    'video-subtitling':        ['video_editing', 'transcription', 'subtitle', 'accessibility', 'video', 'captions', 'multilingual', 'auto_subtitle', 'srt'],
    'voice-cloning':           ['voice_cloning', 'audio', 'creative', 'voice', 'synthesis', 'tts', 'custom_voice', 'realistic', 'voice_ai'],
    'weather':                 ['weather', 'data_analysis', 'climate', 'forecasting', 'real_time', 'meteorology', 'alerts', 'temperature', 'precipitation'],
    'website-builders':        ['website_builder', 'no_code', 'design', 'web', 'creation', 'cms', 'hosting', 'templates', 'publishing'],
    'workflow-automation':     ['automation', 'workflow', 'productivity', 'efficiency', 'process', 'integration', 'triggers', 'bots', 'orchestration'],
    'writing-assistants':      ['writing', 'text_generation', 'productivity', 'content', 'editing', 'grammar', 'paraphrasing', 'ai_writing', 'drafting'],
}

KEYWORD_TAGS = [
    (re.compile(r'open[ -]source', re.I),       'open_source'),
    (re.compile(r'\bAPI\b|api access'),                     'api_available'),
    (re.compile(r'browser extension|chrome extension|firefox', re.I), 'browser_extension'),
    (re.compile(r'mobile app|iOS|Android|iphone|android', re.I), 'mobile_app'),
    (re.compile(r'real-?time|realtime', re.I),            'real_time'),
    (re.compile(r'multimodal|multi-modal', re.I),'multimodal'),
    (re.compile(r'collaboration|collaborative|team|teamwork', re.I), 'collaboration'),
    (re.compile(r'enterprise', re.I),            'enterprise'),
    (re.compile(r'free|freemium', re.I),        'free_tier'),
    (re.compile(r'custom|customizable|personali[sz]', re.I), 'customizable'),
    (re.compile(r'integration|integrates with', re.I),     'integrations'),
    (re.compile(r'cloud|cloud-?based|saas', re.I),        'cloud_based'),
    (re.compile(r'secure|security|encryption|privacy', re.I), 'secure'),
    (re.compile(r'template|prebuilt|preset', re.I),       'templates'),
    (re.compile(r'machine learning|ml|neural|deep learning', re.I), 'machine_learning'),
    (re.compile(r'natural language|nlp|language model', re.I), 'nlp'),
    (re.compile(r'image|visual|graphics', re.I),          'image_based'),
    (re.compile(r'voice|audio|sound', re.I),              'voice_enabled'),
    (re.compile(r'autonomous|autonomous ai|self-operating', re.I), 'autonomous'),
    (re.compile(r'analytics|insights|reporting|dashboard', re.I), 'analytics'),
    (re.compile(r'training|train|fine-?tune|finetuning', re.I), 'training'),
    (re.compile(r'model|models|llm|foundation', re.I),     'model_based'),
]

# Additional semantic tags based on description keywords
SEMANTIC_TAGS = [
    (re.compile(r'speed|fast|quick|efficient|instant', re.I), 'fast'),
    (re.compile(r'easy|simple|straightforward|intuitive', re.I), 'easy_to_use'),
    (re.compile(r'powerful|advanced|professional|robust', re.I), 'powerful'),
    (re.compile(r'affordable|cheap|inexpensive|low cost', re.I), 'affordable'),
    (re.compile(r'flexible|adaptable|versatile', re.I), 'versatile'),
    (re.compile(r'open[ -]source|github', re.I), 'community_driven'),
    (re.compile(r'plugin|extension|addon', re.I), 'extensible'),
]


def get_category(text):
    m = re.search(r"^category:\s*['\"]?([^'\"'\n]+)['\"]?", text, re.M)
    return m.group(1).strip() if m else None


def get_description(text):
    m = re.search(r"^description:\s*['\"]?(.*?)(?:['\"]?\s*\n(?:\w|\Z))", text, re.M | re.S)
    return m.group(1).strip() if m else ''


def build_tags(category, description):
    tags = []

    # Add category tags
    tags.extend(CATEGORY_TAGS.get(category, []))

    # Add keyword-based tags
    for pattern, tag in KEYWORD_TAGS:
        if pattern.search(description) and tag not in tags:
            tags.append(tag)

    # Add semantic tags
    for pattern, tag in SEMANTIC_TAGS:
        if pattern.search(description) and tag not in tags:
            tags.append(tag)

    # Remove duplicates while preserving order
    seen = set()
    unique_tags = []
    for tag in tags:
        if tag not in seen:
            seen.add(tag)
            unique_tags.append(tag)

    # Ensure at least 8 tags by adding generic/contextual tags
    generic_tags = ['ai_powered', 'intelligent', 'platform', 'tool', 'service', 'solution', 'saas', 'online']
    for gtag in generic_tags:
        if len(unique_tags) >= 8:
            break
        if gtag not in unique_tags:
            unique_tags.append(gtag)

    return unique_tags[:15]  # Cap at 15 tags


def process_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find frontmatter block (between first and second ---)
    m = re.match(r'^(---\n)(.*?)(---\n)', content, re.S)
    if not m:
        return False

    fm = m.group(2)
    category = get_category(fm)
    description = get_description(fm)

    tags = build_tags(category, description)

    # Ensure at least 8 tags
    if len(tags) < 8 and category:
        base_tags = CATEGORY_TAGS.get(category, [])
        for tag in base_tags:
            if tag not in tags and len(tags) < 8:
                tags.append(tag)

    if not tags:
        return False

    # Remove existing tags line if present
    fm_lines = fm.split('\n')
    fm_lines = [line for line in fm_lines if not line.startswith('tags:')]
    fm = '\n'.join(fm_lines)

    tags_line = 'tags: [' + ', '.join(tags[:12]) + ']\n'
    new_fm = fm + '\n' + tags_line if not fm.endswith('\n') else fm + tags_line
    new_content = m.group(1) + new_fm + m.group(3) + content[m.end():]

    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    return True


def main():
    files = sorted(f for f in os.listdir(TOOLS_DIR) if f.endswith('.md'))
    updated = 0
    for fname in files:
        path = os.path.join(TOOLS_DIR, fname)
        if process_file(path):
            updated += 1
    print(f'Updated {updated}/{len(files)} files.')


if __name__ == '__main__':
    main()
