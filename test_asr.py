from asr_model import transcribe_audio

audio_file = "uploads/mixkit-female-microphone-countdown-341.wav"

text = transcribe_audio(audio_file)

print("\nTranscription Result:\n")
print(text)