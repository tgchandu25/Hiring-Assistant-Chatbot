import os
import json
import gradio as gr
from datetime import datetime
import langdetect
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")

# Session state
session = {
    "step": 0,
    "info_keys": ["name", "email", "phone", "experience", "position", "location", "tech_stack"],
    "prompts": [
        "What is your full name?",
        "Please enter your email address.",
        "What is your phone number?",
        "How many years of experience do you have?",
        "What position(s) are you applying for?",
        "Where are you currently located?",
        "List your tech stack (languages, frameworks, tools)."
    ],
    "candidate": {},
    "questions": "",
    "answers": []
}

# Save responses
def save_json(data):
    path = "logs"
    os.makedirs(path, exist_ok=True)
    file = os.path.join(path, "responses.json")
    data["timestamp"] = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    try:
        if os.path.exists(file):
            with open(file, "r") as f:
                all_data = json.load(f)
        else:
            all_data = []
        all_data.append(data)
        with open(file, "w") as f:
            json.dump(all_data, f, indent=2)
    except Exception as e:
        print("Error saving:", e)

# GPT-based question generator
def generate_questions(tech_stack, language="English"):
    system = f"""
    You are a multilingual technical interviewer. Respond in {language}.
    Generate 3 to 5 intermediate-level technical interview questions for each technology in: {tech_stack}.
    Format clearly by technology.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": tech_stack}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating questions: {e}"

# Reset for new candidate
def reset():
    session["step"] = 0
    session["candidate"] = {}
    session["questions"] = ""
    session["answers"] = []

# Chatbot response logic
def chatbot_response(message):
    message = message.strip()

    if message.lower() in ["exit", "quit", "bye"]:
        save_json({
            "candidate_info": session["candidate"],
            "tech_questions": session["questions"],
            "answers": session["answers"]
        })
        reset()
        return {"role": "assistant", "content": "Thank you! Your responses have been saved. We'll be in touch."}

    if session["step"] < len(session["prompts"]):
        key = session["info_keys"][session["step"]]
        session["candidate"][key] = message
        session["step"] += 1
        if session["step"] < len(session["prompts"]):
            return {"role": "assistant", "content": session["prompts"][session["step"]]}
        else:
            tech_stack = session["candidate"]["tech_stack"]
            try:
                lang_code = langdetect.detect(tech_stack)
            except:
                lang_code = "en"
            lang_map = {"en": "English", "hi": "Hindi", "es": "Spanish", "fr": "French", "de": "German"}
            lang_name = lang_map.get(lang_code, "English")
            questions = generate_questions(tech_stack, lang_name)
            session["questions"] = questions
            return {"role": "assistant", "content": f"Thank you! Based on your tech stack, here are your technical questions:\n\n{questions}\n\nPlease answer them one at a time. Type 'exit' to finish."}

    session["answers"].append(message)
    return {"role": "assistant", "content": "Answer noted. You can continue answering or type 'exit' to finish."}

# Gradio interface
with gr.Blocks() as app:
    chatbot_ui = gr.Chatbot(label="🤖 TalentScout Hiring Assistant", type="messages", show_copy_button=True)
    user_input = gr.Textbox(placeholder="Type your response here...", show_label=False)
    state = gr.State([])

    # Submit
    def respond(message, history):
        response = chatbot_response(message)
        history.append({"role": "user", "content": message})
        history.append(response)
        return history, ""

    # Auto greet on launch
    def greet():
        greeting = {
            "role": "assistant",
            "content": "👋 Hello! Welcome to TalentScout — your smart hiring assistant.\n\n" + session["prompts"][0]
        }
        return [greeting], ""

    # Clear button logic
    def clear():
        reset()
        greeting = {
            "role": "assistant",
            "content": "👋 Hello! Welcome to TalentScout — your smart hiring assistant.\n\n" + session["prompts"][0]
        }
        return [greeting], ""

    gr.Markdown("### Please follow the prompts. Type 'exit' anytime to finish.")
    clear_btn = gr.Button("Clear Chat")

    # Download button
    def download_file():
        return "logs/responses.json"

    download_btn = gr.DownloadButton(label="⬇️ Download All Responses", value=download_file)

    user_input.submit(respond, [user_input, state], [chatbot_ui, user_input])
    clear_btn.click(clear, None, [chatbot_ui, user_input])
    app.load(greet, None, [chatbot_ui, user_input])

app.launch()
