

## Setup Instructions

### 1. Create and Activate a Virtual Environment

To ensure that dependencies are managed properly, it is recommended to use a virtual environment. Follow the steps below to set up and activate a virtual environment:

```sh
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```

### 2. Install Dependencies
```
pip install -r requirements.txt
```


### 3. Run audio generation AI
Download the code by run the command
```
git clone https://github.com/jiaming-ai/fablette-story-gen.git
```

You can also go to https://github.com/jiaming-ai/fablette-story-gen and download the code directly as a zip file. Then unzip it.

Note:
Put the music files in data foler as shown below

the structure is like
-root
 - generated_stories
 - data/
 - new_story_gemini.py
 - ...


The following argument can be specified when running new_story_gemini.py
- --target_langs to specify the language for translations. By default, it generate stories for English, Chinese, French and German. You can add more by specifing using this argument: --target_langs Chinese French German Japanese Spanish... English is always included so no need to add in the list.
- --titles_csv to specify the titles. See notes below.
- --age to specify the age for each stories. By default it's 5 years old.


#### Generate stories with new titles 

You can ask chatgpt to generate a CSV file that contains the following columns:
- Name
- Source
- Author
- Context: a brief description of the plot

An example looks like:

```csv
Name,Source,Author,Context
The Magical Paintbrush,New Story,Unknown,"Mia discovers a paintbrush that brings her drawings to life, but she must use it wisely!"
Benny and the Runaway Balloon,New Story,Unknown,"Benny’s favorite red balloon floats away, leading him on an adventure through the skies."
```

Save the file in data/titles/my_titles.csv

Then you can run the story generation with:
```
python new_story_gemini.py --titles_csv data/titles/my_titles.csv