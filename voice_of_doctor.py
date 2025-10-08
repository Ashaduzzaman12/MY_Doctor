import os
import subprocess
import platform
from gtts import gTTS
from elevenlabs import save
from elevenlabs.client import ElevenLabs

ELEVENLABS_API_KEY = os.environ.get("ELEVEN_API_KEY")


# ---------- GOOGLE TTS ----------
def text_to_speech_with_gtts(input_text, output_filepath):
    """
    Convert text to speech using Google TTS and auto-play the result.
    """
    language = "en"
    audioobj = gTTS(text=input_text, lang=language, slow=False)
    audioobj.save(output_filepath)
    play_audio(output_filepath)


# ---------- ELEVENLABS TTS ----------
def text_to_speech_with_elevenlabs(input_text, output_filepath, voice_name="Rachel"):
    """
    Convert text to speech using ElevenLabs voice and auto-play the result.
    """
    if not ELEVENLABS_API_KEY:
        print("⚠️ ELEVEN_API_KEY not found. Falling back to Google TTS.")
        return text_to_speech_with_gtts(input_text, output_filepath)

    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

    try:
        audio = client.generate(
            text=input_text,
            voice=voice_name,           # ✅ default working voice
            model="eleven_turbo_v2",
            output_format="mp3_22050_32"
        )
        save(audio, output_filepath)
        play_audio(output_filepath)

    except Exception as e:
        print(f"⚠️ ElevenLabs TTS failed ({e}), using Google TTS instead.")
        text_to_speech_with_gtts(input_text, output_filepath)


# ---------- AUDIO PLAYBACK ----------
def play_audio(output_filepath):
    """
    Cross-platform audio playback utility.
    """
    os_name = platform.system()
    try:
        if os_name == "Darwin":  # macOS
            subprocess.run(["afplay", output_filepath])
        elif os_name == "Windows":
            subprocess.run([
                "powershell",
                "-c",
                f'(New-Object Media.SoundPlayer "{output_filepath}").PlaySync();'
            ])
        elif os_name == "Linux":
            subprocess.run(["aplay", output_filepath])
        else:
            raise OSError("Unsupported operating system")
    except Exception as e:
        print(f"⚠️ Error playing audio: {e}")


# ---------- TEST BLOCK ----------
if __name__ == "__main__":
    text_to_speech_with_elevenlabs(
        "Hello, I am Dr. AI. How can I assist you today?",
        "test_voice.mp3"
    )
