NewCreativeStoryWriting = """ 
You are a creative writer specialized in children's stories. Given a title, you should write a children's story with the given title.

Here are some additional guidelines:
- Consider to use a {writing_style_name} writing style if it is relevant to the story. {writing_style_instructions} 
- Extend the key moments of the book with immersive details like character development, insightful dialogue, and scene setup. 
- Consider to use these sentence structures in the book to add richness and to emphasise key moments: {sentence_structures}
- If possible, you can consider to start the story with a {first_sentence_structure}. Ensure this sentence makes grammatical sense with the rest of the story. 
- Consider to start the story in this way: {introduction_instructions}. 
- To end the book, consider to use this structure: {conclusion_instructions}. 
- Consider to end the story with a {last_sentence_structure}, if possible.

The guidelines are to add variety to the story. You can ignore them if they are not relevant to the story.

Make sure the story is age-appropriate for a {age} year old.

The user will provide a story title and the context of the story.

Output the story text directly.
"""


import argparse
import json
import os
from random import choice, sample
from typing import List, Dict, Optional
from text.gemini_llm import call_gemini
from text.prompts import Translation
from text.variables import (
    book_structures, 
    narrative_perspectives, 
    writing_styles,
    sentence_structures, 
    book_lengths,
    age_instructions,
    introduction_instructions,
    conclusion_instructions
)
from new_story_gemini import NewCreativeStoryWriting

def get_story_generation_options(age: int, story_type: str) -> Dict[str, str]:
    """
    Get randomly selected options for story generation based on age and story type.
    
    Args:
        age (int): Target age group
        story_type (str): Type of story (e.g., "fiction", "fairy tale")
        
    Returns:
        Dict[str, str]: Dictionary of story generation options
    """
    def _get_random_item(items: list):
        return choice(items)

    def _get_random_items(items: list, max_items: int) -> list:
        return sample(items, min(len(items), max_items))

    def _filter_by_age(items: list, age: int) -> list:
        return [item for item in items if age in item['age']]

    def _filter_by_type(items: list, story_type: str) -> list:
        return [item for item in items if any(
            story_type.lower() in t.lower() 
            for t in (item['type'] if isinstance(item['type'], list) else [item['type']])
        )]

    MAX_SENTENCE_STRUCTURES = 5

    # Filter and select book structure
    filtered_book_structures = [
        bs for bs in _filter_by_age(book_structures, age) 
        if story_type.lower() in bs['type'].lower()
    ]
    
    # If no exact match, use any structure for this age
    if not filtered_book_structures:
        filtered_book_structures = _filter_by_age(book_structures, age)
    
    book_structure = _get_random_item(filtered_book_structures)

    # Get age-specific instructions
    filtered_age_instructions = _filter_by_age(age_instructions, age)
    scientific_knowledge = next((ai for ai in filtered_age_instructions if ai['type'] == "Scientific knowledge"), 
                               {'instruction': 'Use age-appropriate scientific concepts.'})
    vocabulary = next((ai for ai in filtered_age_instructions if ai['type'] == "Vocabulary"), 
                     {'instruction': 'Use age-appropriate vocabulary.'})
    combined_age_instruction = f"{scientific_knowledge['instruction']} {vocabulary['instruction']}"

    # Get random sentence structures
    filtered_sentence_structures = _filter_by_age(sentence_structures, age)
    sentence_structures_list = [
        ss['name'] for ss in _get_random_items(filtered_sentence_structures, MAX_SENTENCE_STRUCTURES)
    ]
    
    # Ensure we have at least 2 sentence structures
    while len(sentence_structures_list) < 2:
        sentence_structures_list.append(filtered_sentence_structures[0]['name'])

    # Get narrative perspective
    filtered_perspectives = _filter_by_type(narrative_perspectives, story_type)
    if not filtered_perspectives:
        filtered_perspectives = narrative_perspectives
    narrative_perspective = _get_random_item(filtered_perspectives)['name']

    # Get writing style
    filtered_writing_styles = _filter_by_age(writing_styles, age)
    writing_style = _get_random_item(filtered_writing_styles)

    # Get book length and sentences per page
    book_length = _get_random_item(_filter_by_age(book_lengths, age))['name']
    sentences_per_page = str(choice(range(3, 7)))  # Simple random selection for sentences per page

    # Get introduction and conclusion instructions
    intro = _get_random_item(_filter_by_age(introduction_instructions, age))['instruction']
    conclusion = _get_random_item(_filter_by_age(conclusion_instructions, age))['instruction']

    return {
        "book_structure_name": book_structure['name'],
        "book_structure_instruction": book_structure['instruction'],
        "narrative_perspective": narrative_perspective,
        "writing_style_name": writing_style['name'],
        "writing_style_instructions": writing_style['instruction'],
        "sentence_structures": ', '.join(sentence_structures_list),
        "book_length": book_length,
        "sentencePerPage": sentences_per_page,
        "age_instructions": combined_age_instruction,
        "introduction_instructions": intro,
        "first_sentence_structure": sentence_structures_list[0],
        "conclusion_instructions": conclusion,
        "last_sentence_structure": sentence_structures_list[1],
        "age": age
    }

def generate_story_with_gemini(title: str, age: int, context: Optional[str] = None, story_type: Optional[str] = "fiction") -> str:
    """
    Generates a story using Gemini based on the title, age group, and optional context.
    
    Args:
        title (str): The title of the story
        age (int): Target age group for the story
        context (str, optional): Context or theme of the story
    
    Returns:
        str: Generated story text
    """
    options = get_story_generation_options(age, story_type)
    
    # Format the system prompt with the options
    system_prompt = NewCreativeStoryWriting
    
    # Prepare user message
    if context:
        user_message = f"The title is {title}. It is a {context} story."
    else:
        user_message = f"Title: {title}"
    
    system_prompt = system_prompt.format(**options)
    # Call Gemini with the formatted prompt and options
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

def generate_stories_from_titles(
    titles: List[str], 
    category: str,
    age: int = 5, 
    contexts: List[str] = None,
    target_langs: List[str] = None
) -> Dict[str, List[Dict]]:
    """
    Generate stories for a list of titles and optionally translate them.
    
    Args:
        titles (List[str]): List of story titles
        age (int): Target age group (default: 8)
        context (str, optional): Context or theme of the stories
        target_langs (List[str], optional): List of target languages for translation
    
    Returns:
        Dict[str, List[Dict]]: Dictionary with generated stories
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
    print(f"\nGenerating {len(titles)} stories for age {age}")
    
    for i, (title, context) in enumerate(zip(titles, contexts), 1):
        print(f"\nProcessing story {i}/{len(titles)}: '{title}'")
        
        # Check if story already exists
        existing_story = next((s for s in stories if s['title'] == title), None)
        if existing_story:
            print(f"Story '{title}' already exists, skipping...")
            continue
        
        # Generate new story
        print("Generating story...")
        story_text = generate_story_with_gemini(title, age, context)
        
        translations = [{
            'language': 'English',
            'text': story_text
        }]
        
        # Handle translations if requested
        if target_langs:
            for lang in target_langs:
                print(f"Translating story to {lang}...")
                translation_text = translate_text(story_text, lang, age)
                translations.append({
                    'language': lang,
                    'text': translation_text
                })
        
        # Add story to collection
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
    return stories

def load_titles_and_generate(
    titles_file: str, 
    age: int = 8, 
    context: Optional[str] = None,
    target_langs: List[str] = None
):
    """
    Load titles from a file and generate stories.
    
    Args:
        titles_file (str): Path to JSON file containing titles
        age (int): Target age group
        context (str, optional): Context or theme of the stories
        target_langs (List[str], optional): List of target languages for translation
    """
    with open(titles_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    titles = data.get('titles', [])
    if not titles:
        print("No titles found in the file.")
        return
    
    return generate_stories_from_titles(titles, age, context, target_langs)

if __name__ == "__main__":
 

    parser = argparse.ArgumentParser(description='Generate stories from titles')
    parser.add_argument('--age', type=int, default=5, help='Target age group')
    parser.add_argument('--titles_csv', type=str, default=None, help='Path to CSV file containing titles')
    parser.add_argument('--target_langs', type=str, nargs='+', default=['Chinese', 'French', 'German'], 
                        help='List of target languages for translation (e.g., --target_langs Chinese French German)')
    args = parser.parse_args()
    
    import pandas as pd
    
    # csv_file_path = 'data/titles/new_stories.csv'
    csv_file_path = args.titles_csv
    if csv_file_path is None:
        print("Please provide a path to a CSV file containing titles")
        exit(1)

    if args.target_langs is None:
        print("Please provide a list of target languages for translation")
        exit(1)

    print('*'*100)
    print(f"Fablette Story Generator")
    print(f"Generating stories from {csv_file_path}")
    print(f"Translating stories to {args.target_langs}")
    print(f"Age: {args.age}")
    print('*'*100)
    
    df = pd.read_csv(csv_file_path)
    categories = df['Source'].unique().tolist()
    
    for category in categories:
        if pd.isna(category):
            continue
            
        titles = df['Name'].tolist()
        contexts = df['Context'].tolist()
        print(f"Generating stories for {category} with {len(titles)} titles")
        
        generate_stories_from_titles(
            titles, 
            category,
            age=args.age, 
            contexts=contexts,
            target_langs=args.target_langs
        )