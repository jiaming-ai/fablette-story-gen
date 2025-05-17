import json
import os
from text.gemini_llm import call_gemini
from text.prompts import CreativeStoryWriting, Translation, StoryTitleBrainstorm
from text.azure_llm import call_azure_gpt4
from typing import List
import pandas as pd
def generate_story(title, age, context=None):
    """
    Generates a story using Gemini based on the title and target age group.
    
    Args:
        title (str): The title of the story
        age (int): Target age group for the story
    
    Returns:
        str: Generated story text
    """
    
    system_prompt = CreativeStoryWriting.format(age=age)
    if context:
        user_message = f"The title is {title}. It is a {context} story"
    else:
        user_message = f"Title: {title}"
    
    story = call_gemini(system_prompt, user_message)

    return story

def translate_text(text, target_lang, age):
    """
    Translates the given text to the target language using Gemini.
    
    Args:
        text (str): Text to translate
        target_lang (str): Target language code (e.g., 'es', 'fr', 'zh')
    
    Returns:
        str: Translated text
    """
    system_prompt = Translation.format(language=target_lang, age=age)
    translated = call_gemini(system_prompt, text)
    return translated

def create_all(category, titles, target_lang=['es'], age=8, context=None):
    """
    Generates stories for given titles and their translations, saving them to a JSON file.
    Each story is saved immediately after generation.
    
    Args:
        titles (list): List of story titles
        target_lang (list): List of target languages for translation (default: ['es'])
        age (int): Target age group (default: 8)
    """
    output_dir = 'generated_stories'
    os.makedirs(output_dir, exist_ok=True)
    fname = "_".join(category.split())
    output_file = os.path.join(output_dir, f'{fname}_{age}.json')
    
    # Load existing stories if file exists
    existing_stories = []
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            existing_stories = json.load(f)
    
    stories = existing_stories
    print(f"\nGenerating {len(titles)} stories for age {age}, translating to {', '.join(target_lang)}")
    
    for i, title in enumerate(titles, 1):
        print(f"\nProcessing story {i}/{len(titles)}: '{title}'")
        print("Generating story...")
        story_text = check_if_story_exists(category, title, age, "English")
        if story_text:
            print("Story already exists, skipping...")
            continue
        else:
            story_text = generate_story(title, age, context)

        translations = [{
            'language': 'English',
            'text': story_text
        }]
        
        for lang in target_lang:
            print(f"Translating story to {lang}...")
            translation_text = check_if_story_exists(category, title, age, lang)
            if translation_text:
                print(f"Story {title} in {lang} already exists, skipping...")
                continue
            else:
                translation_text = translate_text(story_text, lang, age)
                translations.append({
                    'language': lang,
                    'text': translation_text
                })
        
        stories.append({
            'title': title,
            'age_group': age,
            'translations': translations
        })
        
        # Save after each story is generated
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(stories, f, ensure_ascii=False, indent=2)
        print("✓ Story completed and saved")
    
    print(f"\nCompleted generating {len(titles)} stories")
    print("Done!")
    
    return stories

def generate_title_list(
    category: str,
    target_count: int,
    language: str = "English",
) -> List[str]:
    """
    Generate a list of titles up to the target count, excluding existing ones
    
    Args:
        category: The category/theme of titles to generate
        target_count: Number of titles desired
        language: Language to generate titles in
        titles_file: Path to the JSON file storing existing titles
    
    Returns:
        List of generated titles
    """
    output_dir = 'data/titles'
    os.makedirs(output_dir, exist_ok=True)
    fname = "_".join(category.split())
    titles_file = os.path.join(output_dir, f'{fname}.json')

    # Load existing titles if file exists
    existing_titles = []
    if os.path.exists(titles_file):
        try:
            with open(titles_file, 'r', encoding='utf-8') as f:
                existing_titles = json.load(f)['titles']
        except Exception as e:
            print(f"Warning: Could not load existing titles: {str(e)}")
    
    all_titles = set(existing_titles)
    
    # Keep generating until we reach target count
    while len(all_titles) < target_count:
        print(f"Current number of titles: {len(all_titles)}")
        print(f"Generating {target_count - len(all_titles)} more titles")

        # Prepare the title generation prompt
        excluded = json.dumps(list(all_titles))
        title_prompt = f"{category} in {language} language. Exclude {excluded}."
        
        try:
            # Generate titles using Azure GPT-4
            titles_response = call_azure_gpt4(
                prompt=title_prompt,
                system_prompt=StoryTitleBrainstorm
            )
            
            if not titles_response:
                raise ValueError("Failed to generate titles")
                
            titles_data = json.loads(titles_response)
            
            if not isinstance(titles_data, dict) or 'titles' not in titles_data:
                raise ValueError("Invalid title generation response format")
            
            if len(titles_data['titles']) == 0:
                print("No more titles can be generated")
                break
            
            # Add new unique titles
            all_titles.update(titles_data['titles'])
            
            # Save updated titles list
            with open(titles_file, 'w', encoding='utf-8') as f:
                json.dump({"titles": list(all_titles)}, f, indent=2)
            
        except Exception as e:
            print(f"Error in title generation: {str(e)}")
            break
        
        # Break if we haven't made progress
        if not titles_data.get('titles'):
            print("Warning: Could not generate more unique titles")
            break
    
    return list(all_titles)

def load_csv_and_generate(csv_file_path, target_lang=['Chinese','French','German'], age=6):
    df = pd.read_csv(csv_file_path)
    categories = df['Source'].unique()
    all_stories = {}
    for category in categories:
        titles = df[df['Source'] == category]['Name'].unique()
        print(f"Generating stories for {category} with {len(titles)} titles")
        # make sure category is not nan
        if pd.isna(category):
            continue
        category_no_space = category.replace(" ","_").replace("/","_")
        stories = create_all(category_no_space, titles, target_lang, age,context=category)
        all_stories[category_no_space] = stories

    with open('generated_stories/all_stories.json', 'w', encoding='utf-8') as f:
        json.dump(all_stories, f, ensure_ascii=False, indent=2)

def check_if_story_exists(category, story_title, age, language):
    json_path = f'generated_stories/{category}_{age}.json'
    if not os.path.exists(json_path):
        return False
    with open(json_path, 'r', encoding='utf-8') as f:
        stories = json.load(f)
        for story in stories:
            if story['title'] == story_title:
                for translation in story['translations']:
                    if translation['language'] == language and "text" in translation \
                        and translation['text'] is not None and len(translation['text']) > 100:
                        return translation['text']
    return False

if __name__ == "__main__":

    # titles = json.load(open('generated_stories/titles.json'))['titles'][:2]
    # stories = create_all(titles, target_lang=['Chinese','French','German'], age=7)

    # titles = generate_title_list(category='Fairy Tales', target_count=50, language='English')
    # print(titles)

    # titles = json.load(open('data/titles/Fairy_Tales.json'))['titles']
    # print(titles)
    # stories = create_all("Fairy Tales", titles, target_lang=['Chinese','French','German'], age=6)

    load_csv_and_generate('data/titles/all.csv', target_lang=['Chinese','French','German'], age=6)
    