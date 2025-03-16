

# 🤖 TalentScout - AI Hiring Assistant

## 📌 Project Overview

TalentScout is an AI-powered **hiring assistant chatbot** designed to **conduct technical screenings** for candidates based on their **tech stack, experience, and desired positions**.  
It dynamically generates **3-5 technical questions**, engages in **follow-ups**, and evaluates responses to provide an interactive interview experience.

---

## 🛠️ Installation Instructions

### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/Tarun304/AI-Hiring-Assistant-Chatbot.git
cd AI-Hiring-Assistant-Chatbot

```

### **2️⃣ Set Up a Virtual Environment (Optional but Recommended)**

```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

```

### **3️⃣ Install Dependencies**

```bash
pip install -r requirements.txt

```

### **4️⃣ Set Up Google Gemini API Key**

1.  Get your **Google Gemini API Key** from [Google Cloud Console](https://console.cloud.google.com/)
2.  Create a `.env` file in the project directory:

```bash
touch .env

```

3.  Add your API key inside `.env`:

```bash
GOOGLE_API_KEY=your_google_gemini_api_key_here

```

### **5️⃣ Run the Application**

```bash
streamlit run app.py

```

----------

## 🎯 Usage Guide

1.  Open the **Streamlit Web Interface** in your browser.
2.  **Fill in your details** (Name, Email, Experience, Tech Stack, etc.).
3.  Click on **"Start Interview"** to begin the technical screening.
4.  Answer the **AI-generated technical questions**.
5.  The AI will **ask up to 2 follow-ups per question** before moving on.
6.  To **exit the chatbot**, simply type **"Thank you", "Goodbye", "End interview"**, etc.
7.  The chatbot will conclude the interview and **reset if needed**.

----------

## ⚙️ Technical Details

### **🛠️ Libraries & Tools Used**

-   **Python 3.x**: Core programming language
-   **Streamlit**: Frontend UI for chatbot
-   **LangChain**: LLM integration and conversational memory
-   **Google Gemini API**: AI-powered model for generating questions & responses
-   **Dotenv**: Managing API keys securely
-   **Random**: For fallback question selection

### **🧠 Architectural Overview**

-   **Candidate Info Collection**: Sidebar form collects details (name, experience, tech stack).
-   **Dynamic Question Generation**: AI generates **3-5 questions** based on tech expertise.
-   **Follow-Up Handling**: AI engages in **max 2 follow-ups per question** before moving forward.
-   **Exit Detection**: AI **dynamically detects when the user wants to exit**.
-   **Memory Handling**: Uses `ConversationBufferMemory` to track conversation state.

----------

## ✍️ Prompt Designs

Prompts are designed to ensure:

-   **Context-Aware Questioning**: AI generates questions **based on tech stack & experience**.
-   **Structured Follow-Ups**: Encourages **in-depth responses** before moving forward.
-   **Exit Detection**: Dynamically determines if a candidate wants to end the chat.

### **Prompt for Question Generation**

```plaintext
You are a technical interviewer for TalentScout recruitment agency.

The candidate has {experience} years of experience and is skilled in: {tech_stack}.

They are looking for positions as: {desired_positions}.

Generate exactly {num_questions} technical questions to assess their knowledge. The questions should:

1. Be of increasing difficulty (start easy, end challenging)

2. Cover different aspects of their tech stack

3. Include some practical scenario-based questions

4. Be clear and concise

Format each question as:

1. Question 1

2. Question 2

...and so on.

Only provide {num_questions} questions, nothing else.

```
### **Prompt to Detect Exit Dynamically**

```plaintext
Analyze this user message and determine if they want to end the interview.

If yes, return ONLY the word 'exit'.

If no, return ONLY the word 'continue'.

  

User message: "{user_input}"

```
### **Prompt to Evaluate Follow up Response**

```plaintext
You are a technical interviewer evaluating a follow-up response.

Candidate: {st.session_state.candidate_info['name']} with {st.session_state.candidate_info['experience']} years of experience

Tech stack: {st.session_state.candidate_info['tech_stack']}

Current technical topic: {st.session_state.questions[current_q_index]}

Follow-up response from candidate: {user_input}

Current follow-up count: {st.session_state.followup_count} (max allowed: 2)

Based on this response:

1. Briefly acknowledge their answer (1-2 sentences)

2. Make ONE decision:

a. If the candidate has now demonstrated sufficient knowledge on this topic, respond with "MOVE_TO_NEXT_QUESTION" at the end of your response

b. If the candidate still shows limited understanding AND we haven't reached the maximum follow-ups (2), provide brief feedback and respond with "NEEDS_MORE_DEPTH" at the end of your response

c. If we've already asked 2 follow-ups or are at the limit, respond with "MOVE_TO_NEXT_QUESTION" regardless of answer quality

Your response should be professional and constructive. Don't include the decision marker in the visible text to the candidate.

```
### **Prompt to Evaluate Candidate Response**

```plaintext
You are a technical interviewer evaluating a candidate response.

Candidate: {st.session_state.candidate_info['name']} with {st.session_state.candidate_info['experience']} years of experience

Tech stack: {st.session_state.candidate_info['tech_stack']}

Current question: {st.session_state.questions[current_q_index]}

Candidate response: {user_input}

Based on this response, make ONE decision:

1. If the answer shows good understanding, acknowledge it positively and respond with "COMPLETE_ANSWER" at the end of your response

2. If the answer is superficial or incomplete, acknowledge what they said, ask ONE specific follow-up question to probe deeper, and respond with "NEEDS_FOLLOWUP" at the end

3. If the answer is completely off-topic or incorrect, provide gentle correction and respond with "NEEDS_FOLLOWUP" at the end

Your response should be professional and constructive. Don't include the decision marker in the visible text to the candidate.

```
### **Prompt to Move To The Next Base Question**

```plaintext
You are a technical interviewer moving to the next question.

  

Create a natural transition to the next question that:

1. Briefly acknowledges we're moving to a new topic (1 sentence)

2. Presents the next question clearly, **without numbering it explicitly** (e.g., do NOT include "Question 2:")

  

The next question is: "{st.session_state.questions[next_index]}". If it starts with a number, rewrite it naturally without a number.

```
### **Prompt for Conclusion**

```plaintext
You are a technical interviewer concluding a screening interview.

The candidate ({st.session_state.candidate_info['name']}) has completed all technical questions about {st.session_state.candidate_info['tech_stack']}.

Provide a brief, positive conclusion to the interview that:

1. Thanks them for their time

2. Mentions that the TalentScout team will review their responses

3. Gives them an idea of next steps (without making specific promises)

4. Ends professionally

Keep it under 4 sentences.

```

----------

## 🏆 Challenges & Solutions


### **1️⃣ Issue: AI Generating Too Many Follow-Ups**
- **Problem**: AI sometimes kept asking too many follow-up questions.
- **Solution**: We **capped follow-ups at 2 per question** by:
  - Tracking the follow-up count using `st.session_state.followup_count`.
  - If the count reached **2**, the chatbot **automatically moved to the next question**.
  - Ensured that after the second follow-up, the AI would **only acknowledge the response** and **not generate another follow up question** and move to the next actual base question.




### **2️⃣ Issue: AI Numbering Questions Incorrectly**
- **Problem**: Sometimes the AI prefixed "Question 2: " when transitioning.
- **Solution**: Updated the next question prompt to **explicitly remove numbers**:
  - AI was instructed **not to add explicit numbering** (e.g., "Question 2:").
  - Ensured a smooth, conversational transition between questions.


### **3️⃣ Issue: Unclear Exit Handling**
- **Problem**: The chatbot wasn't always detecting user exits.
- **Solution**: Used **dynamic LLM-based exit detection** instead of a static keyword list:
  - **Prompt explicitly asks the AI to determine exit intent**.
  - AI **returns only "exit" or "continue"**, reducing misinterpretation.
  - If "exit" is returned, the chatbot **stops immediately** and displays a farewell message.

----------


```
