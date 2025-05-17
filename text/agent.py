import json
import os
from typing import List, Dict
from text.prompts import (
    StoryTitleBrainstorm,
    ExistingStory
)
from text.azure_llm import call_azure_gpt4

from random import choice, sample
import json
from dataclasses import dataclass
from text.variables import (
    book_structures, 
    number_of_main_characters,
    number_of_total_characters, 
    narrative_perspectives, 
    writing_styles,
    sentence_structures, 
    book_lengths,
    words_per_page,
    age_instructions,
    introduction_instructions,
    conclusion_instructions
)

@dataclass
class StoryGenerationOptions:
    book_structure_name: str
    book_structure_instruction: str
    number_of_main_characters: str
    number_of_total_characters: str
    narrative_perspective: str
    writing_style_name: str
    writing_style_instructions: str
    book_length: str
    words_per_page: str
    age_instructions: str
    introduction_instructions: str
    sentence_structures: str
    first_sentence_structure: str
    last_sentence_structure: str
    conclusion_instructions: str
    language: str = 'English'
    script: str = 'Latin'
    sensitivity_information: str = 'n/a'
    story_type: str = ''
    learning_objective: str = ''
    interest: str = ''
    age: str = ''

def get_random_generation_options(
    age: int, 
    story_type: str, 
    learning_objective: str = None, 
    interest: str = None
) -> StoryGenerationOptions:
    def _get_random_item(items: list):
        return choice(items)

    def _get_random_items(items: list, max_items: int) -> list:
        return sample(items, min(len(items), max_items))

    def _filter_by_age(items: list, age: int) -> list:
        return [item for item in items if age in item['age']]

    def _filter_by_type(items: list, story_type: str) -> list:
        return [item for item in items if story_type in item['type']]

    MAX_SENTENCE_STRUCTURES = 5

    # Filter and select book structure
    filtered_book_structures = [
        bs for bs in _filter_by_age(book_structures, age) 
        if bs['type'].lower() == story_type.lower()
    ]
    book_structure = _get_random_item(filtered_book_structures)

    # Get age-specific instructions
    scientific_knowledge = _get_random_item([
        ai for ai in _filter_by_age(age_instructions, age) 
        if ai['type'] == "Scientific knowledge"
    ])
    vocabulary = _get_random_item([
        ai for ai in _filter_by_age(age_instructions, age) 
        if ai['type'] == "Vocabulary"
    ])
    combined_age_instruction = f"{scientific_knowledge['instruction']} {vocabulary['instruction']}"

    # Get random sentence structures
    sentence_structures_list = [
        ss['name'] for ss in _get_random_items(
            _filter_by_age(sentence_structures, age), 
            MAX_SENTENCE_STRUCTURES
        )
    ]

    options = StoryGenerationOptions(
        book_structure_name=book_structure['name'],
        book_structure_instruction=book_structure['instruction'],
        number_of_main_characters=_get_random_item(_filter_by_age(number_of_main_characters, age))['name'],
        number_of_total_characters=_get_random_item(_filter_by_age(number_of_total_characters, age))['name'],
        narrative_perspective=_get_random_item(_filter_by_type(narrative_perspectives, story_type))['name'],
        writing_style_name=_get_random_item(_filter_by_age(writing_styles, age))['name'],
        writing_style_instructions=_get_random_item(_filter_by_age(writing_styles, age))['instruction'],
        book_length=_get_random_item(_filter_by_age(book_lengths, age))['name'],
        words_per_page=_get_random_item(_filter_by_age(words_per_page, age))['name'],
        age_instructions=combined_age_instruction,
        introduction_instructions=_get_random_item(_filter_by_age(introduction_instructions, age))['instruction'],
        sentence_structures=', '.join(sentence_structures_list),
        first_sentence_structure=sentence_structures_list[0],
        last_sentence_structure=sentence_structures_list[1],
        conclusion_instructions=_get_random_item(_filter_by_age(conclusion_instructions, age))['instruction'],
        story_type=story_type,
        age=str(age)
    )

    # Update optional parameters if provided
    if learning_objective is not None:
        options.learning_objective = learning_objective
    if interest is not None:
        options.interest = interest

    return options



def generate_and_save_titles(
    category: str,
    excluded_titles: List[str] = None,
    language: str = "English"
) -> List[str]:
    """
    Generate story titles based on category and save them to a file
    Returns list of generated titles
    """
    # Prepare the title generation prompt
    excluded = json.dumps(excluded_titles) if excluded_titles else "[]"
    if excluded_titles:
        title_prompt = f"{category} in {language} language. Exclude {excluded}."
    else:
        title_prompt = f"{category} in {language} language."
    
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
        
        # Remove duplicates and excluded titles
        unique_titles = list(set(titles_data['titles']) - set(excluded_titles or []))
        
        # Create directory for storing stories if it doesn't exist
        os.makedirs('generated_stories', exist_ok=True)
        
        # Save titles to a file
        with open('generated_stories/titles.txt', 'w', encoding='utf-8') as f:
            f.write(f"Category: {category}\n")
            f.write("\n".join(unique_titles))
            
        return unique_titles
        
    except Exception as e:
        print(f"Error in title generation: {str(e)}")
        return []

def generate_stories_from_titles(
    titles: List[str],
    language: str = "English",
    age: int = 5,
    story_type: str = "fiction"
) -> List[str]:
    """
    Generate stories for each title in the provided list
    Returns list of successfully generated story titles
    """
    generated_stories = []
    
    for title in titles:
        # Get random generation options
        options = get_random_generation_options(age, story_type)
        options.language = language
        
        # Generate story using Azure GPT-4

        system_prompt = ExistingStory.format(**options.__dict__)
        story_response = call_azure_gpt4(
            prompt=title,
            system_prompt=system_prompt
        )
        
        if not story_response:
            raise ValueError("Failed to generate story")
        
        # Save story to individual file
        filename = f'generated_stories/{title.replace(" ", "_")}.txt'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Title: {title}\n\n")
            f.write(story_response)
        
        generated_stories.append(title)
            
    
    return generated_stories

def generate_titles_and_stories(
    category: str,
    excluded_titles: List[str] = None,
    language: str = "English",
    age: int = 6,
    story_type: str = "fiction"
) -> Dict[str, List[str]]:
    """
    Generate story titles and their corresponding stories based on category
    """
    # First generate and save titles
    generated_titles = generate_and_save_titles(category, excluded_titles, language)
    
    # Then generate stories for each title
    generated_stories = generate_stories_from_titles(generated_titles, language, age, story_type)
    
    return {
        "category": category,
        "generated_titles": generated_stories
    }

if __name__ == "__main__":
    # generate_titles_and_stories(
    #     category="Fairy Tales",
    #     language="English",
    # )
    titles = json.load(open('generated_stories/titles.json'))['titles']
    generate_stories_from_titles(titles, language="English", age=5, story_type="Fiction")