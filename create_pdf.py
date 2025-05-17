import json
from reportlab.lib.pagesizes import letter, inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def create_pdf_from_json(json_file_path, output_pdf_path):
    """
    Read children's stories from a JSON file and create a PDF file for each story.

    Args:
        json_file_path (str): Path to the JSON file.
        output_pdf_path (str): Path to the output PDF file.
    """
    # Register a font that supports Chinese characters
    # You'll need to download and provide the path to a suitable font file
    pdfmetrics.registerFont(TTFont('NotoSans', 'data/Noto_Sans_SC/static/NotoSansSC-Regular.ttf'))
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            stories = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found {json_file_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON file {json_file_path}, please check if the file format is correct.")
        return

    doc = SimpleDocTemplate(
        output_pdf_path, 
        pagesize=letter,
        leftMargin=1.5*inch,  # Default is 1 inch
        rightMargin=1.5*inch  # Default is 1 inch
    )
    story_elements = []
    styles = getSampleStyleSheet()

    # Title style: centered, bold, larger font
    title_style = ParagraphStyle(
        'StoryTitle',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        fontName='NotoSans',
        fontSize=18,
        spaceAfter=12
    )

    # Language style: bold, slightly smaller font for language names
    language_style = ParagraphStyle(
        'LanguageStyle',
        parent=styles['Normal'],
        fontName='NotoSans',
        fontSize=10,  # Reduced font size for the entire line
        spaceBefore=12,  # Increased space before
        spaceAfter=12,   # Increased space after
        alignment=TA_CENTER  # Center-align the language header
    )

    # Text style: normal font for story content
    text_style = ParagraphStyle(
        'TextStyle',
        parent=styles['Normal'],
        fontName='NotoSans',
        fontSize=12,
        leading=14
    )

    for story_data in stories:
        story_title = story_data.get('title', 'Untitled')  # Get title, use "Untitled" if not found
        translations = story_data.get('translations', [])  # Get translations list, use empty list if not found

        # Add title to story_elements list
        story_elements.append(Paragraph(story_title, title_style))
        story_elements.append(Spacer(1, 0.2*inch))  # Add some space after title

        for translation in translations:
            language = translation.get('language', 'Unknown Language')
            text = translation.get('text', 'No text')
            
            # Add check to ensure text is a string
            if text is None:
                text = 'No text'
            
            # Replace \n with <br/> for proper line breaks in PDF
            text = text.replace('\n', '<br/>')

            # Add language name with decorative separator
            separator = "～～～～～ <b>{}</b> ～～～～～"
            formatted_language = separator.format(language)
            story_elements.append(Paragraph(formatted_language, language_style))
            story_elements.append(Paragraph(text, text_style))
            story_elements.append(Spacer(1, 0.1*inch))

        # Ensure each story starts on a new page, except for the first story
        if stories.index(story_data) < len(stories) - 1:  # If not the last story
            story_elements.append(PageBreak())  # Replace empty Paragraph with PageBreak
            story_elements.append(Spacer(1, 0.5*inch))  # Add more space between stories

    try:
        doc.build(story_elements)
        print(f"PDF file '{output_pdf_path}' created successfully!")
    except Exception as e:
        print(f"Error occurred while creating PDF file: {e}")


if __name__ == '__main__':
    create_pdf_from_json("generated_stories/Fairy_Tales_7.json", "generated_stories/FairyTales.pdf")