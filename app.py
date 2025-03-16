import streamlit as st
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationChain
from dotenv import load_dotenv
import os
import random

load_dotenv()

# Set up Streamlit UI
st.set_page_config(page_title="TalentScout - AI Hiring Assistant", layout="wide")
st.title("🤖 TalentScout Hiring Assistant")
st.markdown("This chatbot will conduct an initial technical screening based on your profile and tech stack.")

# Load Google Gemini API Key
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    st.error("No API key found. Please set your GOOGLE_API_KEY in the .env file.")
    st.stop()

os.environ['GOOGLE_API_KEY'] = api_key

# Initialize Chat Model (Google Gemini)
try:
    chat_model = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
except Exception as e:
    st.error(f"Error initializing the chat model: {str(e)}")
    st.stop()

# Initialize session state variables
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(return_messages=True)
    
if "conversation" not in st.session_state:
    try:
        st.session_state.conversation = ConversationChain(
            llm=chat_model,
            memory=st.session_state.memory,
            verbose=False  # Set to True for debugging
        )
    except Exception as e:
        st.error(f"Error creating conversation chain: {str(e)}")
        st.stop()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        ("🤖 TalentScout", "Welcome to TalentScout! I'm your AI interview assistant. Please provide your details in the sidebar to begin the technical screening process.")
    ]

# Initialize session state variables to manage chatbot behavior
if "chat_started" not in st.session_state:
    st.session_state.chat_started = False

if "chat_exited" not in st.session_state:
    st.session_state.chat_exited = False

if "candidate_info" not in st.session_state:
    st.session_state.candidate_info = {}

if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 0

if "questions" not in st.session_state:
    st.session_state.questions = []

if "awaiting_followup" not in st.session_state:
    st.session_state.awaiting_followup = False

if "followup_count" not in st.session_state:
    st.session_state.followup_count = 0

if "current_question_answered" not in st.session_state:
    st.session_state.current_question_answered = False

# Sidebar - User Input Form with validation
with st.sidebar:
    st.subheader("📝 Candidate Information")
    st.markdown("Please fill out all required fields (*) to begin the interview.")
    
    name = st.text_input("Full Name*")
    email = st.text_input("Email Address*")
    phone = st.text_input("Phone Number*")
    experience = st.number_input("Years of Experience*", min_value=0, max_value=50, value=0)
    desired_positions = st.text_area("Desired Position(s)*")
    location = st.text_input("Current Location*")
    tech_stack = st.text_area("Tech Stack* (e.g., Python, Django, React, SQL)")
    
    # Form validation before enabling the Start button
    required_fields = [name, email, phone, desired_positions, location, tech_stack]
    all_filled = all(field.strip() for field in required_fields)
    
    if not all_filled:
        st.warning("Please fill out all required fields to continue.")
    
    start_chat = st.button("Start Interview", disabled=not all_filled)
    
    if start_chat and all_filled:
        # Determine number of questions based on tech stack complexity
        tech_count = len([t for t in tech_stack.split(',') if t.strip()])
        # Determine number of questions (3-5) based on tech stack size
        # More tech skills = more questions (up to 5)
        num_questions = min(max(3, min(tech_count, 5)), 5)
        
        # Store the candidate information
        st.session_state.candidate_info = {
            "name": name,
            "email": email,
            "phone": phone,
            "experience": experience,
            "desired_positions": desired_positions,
            "location": location,
            "tech_stack": tech_stack,
            "num_questions": num_questions  # Store the number of questions
        }
        
        # Reset chat state
        st.session_state.chat_started = True
        st.session_state.chat_exited = False
        st.session_state.chat_history = []
        st.session_state.memory.clear()
        st.session_state.current_question_index = 0
        st.session_state.awaiting_followup = False
        st.session_state.followup_count = 0
        st.session_state.current_question_answered = False
        
        # Add greeting message
        greeting = f"Hello {name}! I'm the TalentScout AI interviewer. Based on your profile, I'll be asking you some technical questions related to your skills in {tech_stack}. Let's begin!"
        st.session_state.chat_history.append(("🤖 TalentScout", greeting))
        
        # Generate technical questions based on tech stack
        try:
            question_prompt = f"""
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
            """
            
            response = st.session_state.conversation.predict(input=question_prompt)
            
            # Process and store questions
            questions_list = []
            for line in response.split('\n'):
                if line.strip() and any(line.strip().startswith(f"{i}.") for i in range(1, 10)):
                    # Extract just the question text (remove the number prefix)
                    question_text = line.strip()
                    if '. ' in question_text:
                        question_text = question_text[question_text.find('. ')+2:]
                    questions_list.append(question_text)
            
            # Ensure we have exactly the determined number of questions
            if len(questions_list) < num_questions:
                # If we have fewer than determined, generate some generic fallback questions
                tech_list = [tech.strip() for tech in tech_stack.split(',') if tech.strip()]
                while len(questions_list) < num_questions and tech_list:
                    tech = random.choice(tech_list)
                    questions_list.append(f"Can you describe your experience with {tech} and how you've applied it in real projects?")
                    tech_list.remove(tech)
            elif len(questions_list) > num_questions:
                # If we have more than determined, trim the list
                questions_list = questions_list[:num_questions]
            
            st.session_state.questions = questions_list
            
            # Ask the first question
            if questions_list:
                first_question = f"Let's start with the first question:\n\n{questions_list[0]}"
                st.session_state.chat_history.append(("🤖 TalentScout", first_question))
                st.session_state.current_question_index = 0  # Start at 0 since we've asked the first question
                st.session_state.current_question_answered = False  # First question hasn't been answered yet
            
        except Exception as e:
            error_msg = f"An error occurred while generating questions: {str(e)}"
            st.session_state.chat_history.append(("🤖 TalentScout", error_msg))

# Main chat interface
st.subheader("💬 Interview Session")

# Display chat history
chat_container = st.container()
with chat_container:
    for sender, message in st.session_state.chat_history:
        with st.chat_message("assistant" if sender == "🤖 TalentScout" else "user"):
            st.write(message)

# User input area - only show if chat has started and not exited
if st.session_state.chat_started and not st.session_state.chat_exited:
    user_input = st.chat_input("Your response...", key="chat_input")
    
    if user_input:
        st.session_state.chat_history.append(("👤 You", user_input))

        # Dynamically detect exit using LLM
        exit_prompt = f"""
        Analyze this user message and determine if they want to end the interview. 
        If yes, return ONLY the word 'exit'.
        If no, return ONLY the word 'continue'.

        User message: "{user_input}"
        """
        exit_response = st.session_state.conversation.predict(input=exit_prompt).strip().lower()

        if exit_response == "exit":
            st.session_state.chat_history.append(("🤖 TalentScout", "Thank you for your time! We'll review your responses and get back to you soon. Have a great day!"))
            st.session_state.chat_exited = True
            st.rerun()
        
        # Process the response and continue the interview
        try:
            current_q_index = st.session_state.current_question_index
            follow_up_needed = False
            move_to_next = False
            
            # Handle the response based on our current state
            if st.session_state.awaiting_followup:
                # This is a response to our follow-up question
                evaluation_prompt = f"""
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
                """
                
                response = st.session_state.conversation.predict(input=evaluation_prompt)
                
                # Check for decision markers and remove them
                if "MOVE_TO_NEXT_QUESTION" in response:
                    response = response.replace("MOVE_TO_NEXT_QUESTION", "").strip()
                    move_to_next = True
                    st.session_state.awaiting_followup = False
                    st.session_state.followup_count = 0  # Reset count for next question
                elif "NEEDS_MORE_DEPTH" in response:
                    response = response.replace("NEEDS_MORE_DEPTH", "").strip()
                    st.session_state.followup_count += 1
    
                    # Modified logic: Don't move to next question immediately after 2nd follow-up
                    if st.session_state.followup_count >= 2:
                        # Just acknowledge and wait for user's response
                        st.session_state.awaiting_followup = True  # Keep this true to await final response
                    else:
                        # Continue with follow-up
                        st.session_state.awaiting_followup = True
                else:
                    # No decision marker found, default to moving on
                    move_to_next = True
                    st.session_state.awaiting_followup = False
                    st.session_state.followup_count = 0
                
            else:
                # This is the first response to the current question
                st.session_state.current_question_answered = True
                
                evaluation_prompt = f"""
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
                """
                
                response = st.session_state.conversation.predict(input=evaluation_prompt)
                
                # Check for decision markers and remove them
                if "COMPLETE_ANSWER" in response:
                    response = response.replace("COMPLETE_ANSWER", "").strip()
                    move_to_next = True
                elif "NEEDS_FOLLOWUP" in response:
                    response = response.replace("NEEDS_FOLLOWUP", "").strip()
                    follow_up_needed = True
                    st.session_state.awaiting_followup = True
                    st.session_state.followup_count = 1  # This is our first follow-up
                else:
                    # No decision marker found, default to moving on
                    move_to_next = True
            
            # Send interviewer's response to the candidate
            st.session_state.chat_history.append(("🤖 TalentScout", response))
            
            # If we need to move to the next question
            if move_to_next:
                st.session_state.current_question_index += 1
                next_index = st.session_state.current_question_index
                
                # Check if we've gone through all questions
                if next_index < len(st.session_state.questions):
                    # Send the next question after a brief pause
                    next_q_prompt = f"""
                    You are a technical interviewer moving to the next question.

                    Create a natural transition to the next question that:
                    1. Briefly acknowledges we're moving to a new topic (1 sentence)
                    2. Presents the next question clearly, **without numbering it explicitly** (e.g., do NOT include "Question 2:")

                    The next question is: "{st.session_state.questions[next_index]}". If it starts with a number, rewrite it naturally without a number.
                    """

                    
                    next_question_msg = st.session_state.conversation.predict(input=next_q_prompt)
                    st.session_state.chat_history.append(("🤖 TalentScout", next_question_msg))
                    st.session_state.current_question_answered = False
                else:
                    # We've completed all questions, wrap up the interview
                    conclusion_prompt = f"""
                    You are a technical interviewer concluding a screening interview.
                    The candidate ({st.session_state.candidate_info['name']}) has completed all technical questions about {st.session_state.candidate_info['tech_stack']}.
                    
                    Provide a brief, positive conclusion to the interview that:
                    1. Thanks them for their time
                    2. Mentions that the TalentScout team will review their responses
                    3. Gives them an idea of next steps (without making specific promises)
                    4. Ends professionally
                    
                    Keep it under 4 sentences.
                    """
                    
                    conclusion = st.session_state.conversation.predict(input=conclusion_prompt)
                    st.session_state.chat_history.append(("🤖 TalentScout", conclusion))
                    st.session_state.chat_exited = True
            
        except Exception as e:
            error_msg = f"I apologize, but I encountered an error processing your response. Let me try to continue with our interview. Could you please tell me more about your experience with {st.session_state.candidate_info['tech_stack']}?"
            st.session_state.chat_history.append(("🤖 TalentScout", error_msg))
        
        st.rerun()

      