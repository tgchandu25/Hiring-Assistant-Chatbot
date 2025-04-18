
# System Architecture: Hiring Assistant Chatbot

## 1. User Interaction Flow
- Candidate interacts with a chatbot UI built using Gradio.
- Step-by-step prompts collect user data (name, email, tech stack, etc.).
- On collecting tech stack, questions are dynamically generated using OpenAI.

## 2. Language Handling
- Uses `langdetect` to identify language from tech stack input.
- GPT prompt switches language context based on detection.

## 3. Technical Questions
- GPT-3.5-turbo generates 3–5 questions per tech using prompt engineering.
- These questions are shown back to the user.

## 4. Data Persistence
- All user responses, questions, and answers are saved to JSON.
- JSONs stored in a folder `responses/`.

## 5. Deployment
- Designed for Hugging Face Spaces using latest Gradio version.
