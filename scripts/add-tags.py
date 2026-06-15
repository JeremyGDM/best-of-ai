#!/usr/bin/env python3
"""Add tags to all tool markdown files based on category and description keywords."""

import os
import re

TOOLS_DIR = os.path.join(os.path.dirname(__file__), '..', 'content', 'tools')

CATEGORY_TAGS = {
    '3d':                      ['3d', 'design', 'creative'],
    'academia':                ['research', 'education', 'academic'],
    'ad-generator':            ['advertising', 'marketing', 'creative'],
    'ai-agents':               ['ai_agent', 'automation'],
    'ai-companion':            ['ai_companion', 'chatbot'],
    'ai-directories':          ['directory', 'reference'],
    'animation':               ['animation', 'video', 'creative'],
    'app-builders':            ['no_code', 'app_builder', 'developer_tools'],
    'audio':                   ['audio', 'creative'],
    'automation':              ['automation', 'workflow', 'productivity'],
    'background-remover':      ['image_editing', 'design', 'creative'],
    'business-tools':          ['business', 'productivity'],
    'calendar-scheduling':     ['scheduling', 'productivity', 'calendar'],
    'chatbots':                ['chatbot', 'text_generation', 'ai_assistant'],
    'climate':                 ['climate', 'environment'],
    'code-assistant':          ['code_generation', 'developer_tools', 'productivity'],
    'copywriting':             ['writing', 'marketing', 'text_generation'],
    'crm':                     ['crm', 'sales', 'business'],
    'customer-support':        ['customer_support', 'chatbot', 'business'],
    'data':                    ['data_analysis', 'analytics', 'business'],
    'devtools':                ['developer_tools', 'code_generation'],
    'document-ai':             ['document_ai', 'pdf', 'productivity'],
    'e-commerce':              ['ecommerce', 'business', 'marketing'],
    'email-assistants':        ['email', 'productivity', 'writing'],
    'farming':                 ['farming', 'agriculture'],
    'fashion':                 ['fashion', 'design'],
    'finance':                 ['finance', 'business', 'analytics'],
    'food':                    ['food', 'lifestyle'],
    'gaming':                  ['gaming', 'creative'],
    'government':              ['government', 'civic'],
    'graphic-design':          ['design', 'image_editing', 'creative'],
    'healthcare':              ['healthcare', 'medical'],
    'home-design':             ['home_design', 'design', 'creative'],
    'hr':                      ['hr', 'business', 'recruitment'],
    'image-editing':           ['image_editing', 'design', 'creative'],
    'image-generation':        ['image_generation', 'creative', 'text_to_image'],
    'infographics':            ['design', 'data_visualization', 'marketing'],
    'job-tools':               ['career', 'hr', 'recruitment'],
    'knowledge-management':    ['knowledge_base', 'productivity', 'note_taking'],
    'language-learning':       ['language_learning', 'education'],
    'lead-generation':         ['sales', 'marketing', 'business'],
    'learning-tools':          ['education', 'learning'],
    'legal-assistants':        ['legal', 'document_ai', 'business'],
    'local-search-engines':    ['search', 'local'],
    'logo-generator':          ['design', 'image_generation', 'branding'],
    'market-research':         ['market_research', 'business', 'analytics'],
    'marketing':               ['marketing', 'business'],
    'meeting-assistants':      ['meeting', 'productivity', 'transcription'],
    'meme-generator':          ['meme', 'creative', 'social_media'],
    'models':                  ['llm', 'foundation_model', 'ai_model'],
    'music-generation':        ['music_generation', 'audio', 'creative'],
    'no-code':                 ['no_code', 'automation', 'app_builder'],
    'note-taking-apps':        ['note_taking', 'productivity', 'knowledge_base'],
    'others':                  ['other'],
    'personal-assistants':     ['ai_assistant', 'productivity', 'chatbot'],
    'podcast':                 ['podcast', 'audio', 'content_creation'],
    'presentation':            ['presentation', 'productivity', 'design'],
    'productivity':            ['productivity', 'ai_assistant'],
    'project-management':      ['project_management', 'productivity', 'team'],
    'real-estate':             ['real_estate', 'business'],
    'research-tools':          ['research', 'analytics', 'academic'],
    'resume-tools':            ['resume', 'career', 'writing'],
    'sales-tools':             ['sales', 'business', 'crm'],
    'search-engines':          ['search', 'ai_assistant'],
    'seo':                     ['seo', 'marketing', 'analytics'],
    'social-media-tools':      ['social_media', 'marketing', 'content_creation'],
    'spreadsheets':            ['spreadsheet', 'data_analysis', 'productivity'],
    'supply-chain':            ['supply_chain', 'logistics', 'business'],
    'talking-avatar-generator':['avatar', 'video_generation', 'creative'],
    'text-to-speech':          ['text_to_speech', 'audio', 'voice'],
    'transcription':           ['transcription', 'speech_to_text', 'audio'],
    'translator':              ['translation', 'language', 'multilingual'],
    'video':                   ['video', 'creative'],
    'video-editor':            ['video_editing', 'creative', 'video'],
    'video-enhancer':          ['video_editing', 'upscaling', 'creative'],
    'video-generator':         ['video_generation', 'creative', 'text_to_video'],
    'video-subtitling':        ['video_editing', 'transcription', 'subtitle'],
    'voice-cloning':           ['voice_cloning', 'audio', 'creative'],
    'weather':                 ['weather', 'data_analysis'],
    'website-builders':        ['website_builder', 'no_code', 'design'],
    'workflow-automation':     ['automation', 'workflow', 'productivity'],
    'writing-assistants':      ['writing', 'text_generation', 'productivity'],
}

KEYWORD_TAGS = [
    (re.compile(r'open[ -]source', re.I),       'open_source'),
    (re.compile(r'\bAPI\b'),                     'api_available'),
    (re.compile(r'browser extension|chrome extension', re.I), 'browser_extension'),
    (re.compile(r'mobile app|iOS|Android', re.I), 'mobile_app'),
    (re.compile(r'real-?time', re.I),            'real_time'),
    (re.compile(r'multimodal|multi-modal', re.I),'multimodal'),
    (re.compile(r'collaboration|collaborative', re.I), 'collaboration'),
    (re.compile(r'enterprise', re.I),            'enterprise'),
]


def get_category(text):
    m = re.search(r"^category:\s*['\"]?([^'\"'\n]+)['\"]?", text, re.M)
    return m.group(1).strip() if m else None


def get_description(text):
    m = re.search(r"^description:\s*['\"]?(.*?)(?:['\"]?\s*\n(?:\w|\Z))", text, re.M | re.S)
    return m.group(1).strip() if m else ''


def build_tags(category, description):
    tags = list(CATEGORY_TAGS.get(category, []))
    for pattern, tag in KEYWORD_TAGS:
        if pattern.search(description) and tag not in tags:
            tags.append(tag)
    return tags


def process_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip files that already have tags
    if re.search(r'^tags:', content, re.M):
        return False

    # Find frontmatter block (between first and second ---)
    m = re.match(r'^(---\n)(.*?)(---\n)', content, re.S)
    if not m:
        return False

    fm = m.group(2)
    category = get_category(fm)
    description = get_description(fm)

    tags = build_tags(category, description)
    if not tags:
        return False

    tags_line = 'tags: [' + ', '.join(tags) + ']\n'
    new_fm = fm + tags_line
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
