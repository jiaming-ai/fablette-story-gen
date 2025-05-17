
# import os
# from supabase import create_client, Client

# url: str = os.environ.get("SUPABASE_URL")
# key: str = os.environ.get("SUPABASE_KEY")
# supabase: Client = create_client(url, key)


async def insert_story(supabase, story: dict) -> dict:
    """
    Insert a new story into the database.
    
    Args:
        supabase: Supabase client instance
        story (dict): Story data with the following structure:
            {
                'id': UUID,  # Optional if using default gen_random_uuid()
                'author_id': UUID,
                'age': int,  # Optional
                'level': str,  # Optional, max 50 chars
                'cover_img': str,  # Optional
                'translations': [{
                    'lang': str,  # One of the language_enum values
                    'title': str,
                    'text': dict,
                    'description': str,  # Optional
                    'tags': list[str],  # Optional
                    'audio': str,  # Optional
                }]
            }
    
    Returns:
        dict: The inserted story data
    """
    try:
        # Insert the main story record
        story_data = {
            'author_id': story['author_id'],
            'age': story.get('age'),
            'level': story.get('level'),
            'cover_img': story.get('cover_img')
        }
        
        # If id is provided, include it in the data
        if 'id' in story:
            story_data['id'] = story['id']
            
        result = await supabase.table('story').insert(story_data).execute()
        inserted_story = result.data[0]
        
        # Insert translations if provided
        if 'translations' in story:
            translations = [
                {
                    'slid': inserted_story['id'],
                    'lang': trans['lang'],
                    'title': trans['title'],
                    'text': trans['text'],
                    'description': trans.get('description'),
                    'tags': trans.get('tags'),
                    'audio': trans.get('audio')
                }
                for trans in story['translations']
            ]
            
            await supabase.table('story_translation').insert(translations).execute()
            
        return inserted_story
        
    except Exception as e:
        raise Exception(f"Failed to insert story: {str(e)}")
