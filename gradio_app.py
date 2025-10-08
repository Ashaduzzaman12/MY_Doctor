# AI Doctor – Vision + Voice Assistant

# Uncomment if not using pipenv
# from dotenv import load_dotenv
# load_dotenv()

import os
import gradio as gr
from Brain_of_doctor import encode_image, analyze_image_with_query
from Voice_patient import transcribe_with_groq
from voice_of_doctor import text_to_speech_with_elevenlabs

# Load API key
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Doctor’s “personality” / system instruction
system_prompt = """You have to act as a professional doctor, 
I know you are not but this is for educational purposes. 
What's in this image? Do you find anything wrong with it medically? 
If you make a differential, suggest some remedies for them. 
Do not add any numbers or special characters in your response. 
Your response should be in one short paragraph, written naturally, 
like a doctor speaking to a patient. Start your answer directly with 
'With what I see, I think you have...' Avoid saying 'In the image I see' 
or referring to yourself as an AI model. Keep it concise (max two sentences)."""


# ---------- MAIN PIPELINE ----------
def process_inputs(audio_filepath, image_filepath):
    # 1️⃣ Handle missing audio safely
    if not audio_filepath:
        return "No voice input detected.", "Please record or upload your voice.", None

    # 2️⃣ Convert speech → text
    try:
        speech_to_text_output = transcribe_with_groq(
            stt_model="whisper-large-v3",
            audio_filepath=audio_filepath,
            GROQ_API_KEY=GROQ_API_KEY
        )
    except Exception as e:
        return f"Speech-to-text failed: {e}", "Unable to transcribe audio.", None

    # 3️⃣ Handle optional image input
    if image_filepath:
        try:
            doctor_response = analyze_image_with_query(
                query=f"{system_prompt} {speech_to_text_output}",
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                encoded_image=encode_image(image_filepath)
            )
        except Exception as e:
            doctor_response = f"Image analysis failed: {e}"
    else:
        doctor_response = "I can’t see an image, but based on what you said, I can still give advice if you describe your symptoms."

    # 4️⃣ Generate spoken response
    output_audio_path = "final_response.mp3"
    try:
        text_to_speech_with_elevenlabs(
            input_text=doctor_response,
            output_filepath=output_audio_path,
            voice_name="Rachel"
        )
    except Exception as e:
        print(f"TTS generation failed: {e}")
        output_audio_path = None

    # 5️⃣ Return outputs for Gradio
    return speech_to_text_output, doctor_response, output_audio_path


# ---------- GRADIO UI ----------
iface = gr.Interface(
    fn=process_inputs,
    inputs=[
        gr.Audio(sources=["microphone"], type="filepath", label="🎙️ Speak your question"),
        gr.Image(type="filepath", label="🩻 Upload or take a picture")
    ],
    outputs=[
        gr.Textbox(label="🗣️ Speech-to-Text Output"),
        gr.Textbox(label="🧑‍⚕️ Doctor’s Response"),
        gr.Audio(label="🔊 Doctor’s Voice Reply")
    ],
    title="🩺My_Doctor The Personal AI",
    description="Speak your symptoms and optionally upload an image. The AI doctor listens, looks, and responds like a real physician."
)

if __name__ == "__main__":
    iface.launch(debug=True, share=True)
