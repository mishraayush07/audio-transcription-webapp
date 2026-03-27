from transformers import pipeline

print("Loading summarization model...")

summarizer = pipeline(
    "summarization",
    model="t5-small"
)

print("Summarization model loaded")

def summarize_text(text):

    if not text:
        return "No summary available."

    # T5 requires prefix
    text = "summarize: " + text

    result = summarizer(
        text,
        max_length=80,
        min_length=25,
        do_sample=False
    )

    return result[0]["summary_text"]