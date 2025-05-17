SML_PROMPT = """
Your task is to generate an SSML (Speech Synthesis Markup Language) XML document that creates a high-quality, natural-sounding voiceover for a story. The SSML should reflect vivid emotions and realism by utilizing different voices and styles appropriately throughout the story.

## Instructions on Voices and Styles:
Use the provided voices and their associated styles to enhance the narrative. Different parts of the story should use distinct voices and styles for a dynamic and engaging audio experience.
--
zh-CN-XiaoyiNeural: Young lady's voice. Available styles: ["affectionate", "angry", "cheerful", "disgruntled", "embarrassed", "fearful", "gentle", "sad", "serious"].
zh-CN-XiaoxiaoNeural: Young lady's voice. Available styles: ["affectionate", "angry", "assistant", "calm", "chat", "chat-casual", "cheerful", "customerservice", "disgruntled", "excited", "fearful", "friendly", "gentle", "lyrical", "newscast", "poetry-reading", "sad", "serious", "sorry", "whispering"].
zh-CN-XiaoyouNeural: Child girl's voice. No specific styles available.
zh-CN-YunxiaNeural: Child boy's voice. Available styles: ["angry", "calm", "cheerful", "fearful", "sad"].
--
Note: the voice name should be exactly the same as in the list.
 
* Style Degree: Adjust the intensity of the styles using the styledegree attribute within the range of 0 to 2, where 0 represents a subtle expression and 2 represents a strong expression.

* Narration: Use the "zh-CN-xiaoxiaoNeural" voice for all narrative sections. Apply different styles depending on the emotion conveyed in each part.

* Characters: try to use different voices or styles for different characters in the story. Note the voice should be consistent for the same character in the story.


# General instructions
Output Format: The output should be a well-formed SSML XML document that only uses <speak>, <voice> and <<mstts:express-as> tags as shown in the following example.

Example output:
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
 <voice name="xiaoxiaoNeural">
  <mstts:express-as style="gentle" styledegree="1">
They entered a zoo and saw a tiger. Luna says
  </mstts:express-as>
 </voice>
 <voice name="xiaoxiaoNeural">
  <mstts:express-as style="excited" styledegree="2">
Wow. It's a tiger!
  </mstts:express-as>
  <mstts:express-as style="chat-casual" styledegree="0.01">
What's that?
  </mstts:express-as>
 </voice>
 <voice name="zh-CN-XiaoyouNeural">
It's a rabbit!
 </voice>
</speak> 

Use the same <speak> tag as in the example.
Specify the voice and style using the <voice> and <mstts:express-as> tags.
Maintain the provided structure without any additional text or comments.

CRITICAL OUTPUT FORMAT REQUIREMENT: Do not use any markdown, backticks, or code blocks. Your output must be a plain JSON string starting with "{" and ending with "}" - no formatting characters before or after.

Output must be exactly in this format (with no code block, no backticks, no indentation):
{"ssml":"<speak version=\"1.0\" xmlns=\"http://www.w3.org/2001/10/synthesis\" xmlns:mstts=\"https://www.w3.org/2001/mstts\" xml:lang=\"zh-CN\">...</speak>"}
"""

import json
from text.gemini_llm import call_gemini
import re

def extract_and_parse_json(text):
    """
    Extract and parse JSON from text, even if it's wrapped in code blocks or has other formatting.
    
    Args:
        text (str): Text that contains JSON
        
    Returns:
        dict: Parsed JSON object
    """
    # If the text is already valid JSON, parse it directly
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Try to extract JSON from markdown code blocks
    code_block_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
    match = re.search(code_block_pattern, text)
    if match:
        json_str = match.group(1).strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    
    # Try to find any JSON-like structure with curly braces
    json_pattern = r'({[\s\S]*?})'
    match = re.search(json_pattern, text)
    if match:
        json_str = match.group(1)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    
    raise ValueError(f"Could not extract valid JSON from text: {text[:100]}...")
  
def generate_sml(story_text):
    """
    Generate SSML markup for a story using Gemini LLM.
    
    Args:
        story_text (str): The story text to convert to SSML
        
    Returns:
        str: SSML markup for the story
    """
    
    # Use the SML_PROMPT as the system prompt
    system_prompt = SML_PROMPT
    
    # Use the story text as the user message
    user_message = story_text
    
    # Call Gemini LLM with the prompts
    ssml_output = call_gemini(system_prompt, user_message)
    ssml_output = extract_and_parse_json(ssml_output)["ssml"]
    
    return ssml_output
