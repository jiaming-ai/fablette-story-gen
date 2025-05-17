from tts.azure_tts import generate_ssml, generate_basic
import json

story = json.load(open("generated_stories/African_Folktales_(Nigeria)_6.json"))[0]

generate_ssml(story)
# generate_basic(story)
