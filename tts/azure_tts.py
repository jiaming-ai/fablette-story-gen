# tts
import dotenv
import os
import azure.cognitiveservices.speech as speechsdk
import uuid
from .sml_prompt import generate_sml
dotenv.load_dotenv()

SPEECH_KEY = os.getenv("SPEECH_KEY")
SPEECH_REGION = os.getenv("SPEECH_REGION")

def generate_ssml(story):
    """
    Synthesize speech from SSML and save to a file.
    
    Args:
        story (dict): Story data
        
    Returns:
        str: Path to the generated audio file
    """
    output_dir = "generated_stories/audios"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # Configure speech service
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Ogg24Khz16BitMonoOpus
    )

    # generate ssml
    story_name = story["title"]
    story_text = story["translations"][0]["text"]
    language = story["translations"][0]["language"]
    print(f"Generating SSML for {story_name} in {language}")
    ssml = generate_sml(story_text)
    print(f"SSML: {ssml}")
    
    # Set up file output
    audio_path = f"{output_dir}/{story_name}_{language}.ogg"
    audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_path)
    
    # Create synthesizer
    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, 
        audio_config=audio_config
    )
    
    print("Synthesizing speech...")
    
    # Synthesize speech
    result = speech_synthesizer.speak_ssml_async(ssml).get()
    
    # Check result
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized successfully")
        return audio_path
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Error details: {cancellation_details.error_details}")
        raise Exception(f"Speech synthesis failed: {cancellation_details.reason}")

def generate_basic(story, voice_name=None):
    """
    Synthesize speech from plain text and save to a file.
    
    Args:
        story (dict): Story data
        voice_name (str, optional): Name of the voice to use. Defaults to "zh-CN-XiaoxiaoMultilingualNeural".
        
    Returns:
        str: Path to the generated audio file
    """
    story_name = story["title"]
    story_text = story["translations"][0]["text"]
    language = story["translations"][0]["language"]
    print(f"Generating audio for {story_name} in {language}")
    
    output_dir = "generated_stories/audios"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    audio_path = f"{output_dir}/{story_name}_{language}.ogg"
    if not voice_name:
        voice_name = "zh-CN-XiaoxiaoMultilingualNeural"
    
    # Configure speech service
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    speech_config.speech_synthesis_voice_name = voice_name
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Ogg24Khz16BitMonoOpus
    )
    
    # Generate a unique filename
    audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_path)
    
    # Create synthesizer
    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, 
        audio_config=audio_config
    )
    
    # Synthesize speech
    result = speech_synthesizer.speak_text_async(story_text).get()
    
    # Check result
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized successfully")
        return audio_path
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Error details: {cancellation_details.error_details}")
        raise Exception(f"Speech synthesis failed: {cancellation_details.reason}")




