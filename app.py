import streamlit as st
import groq
from typing import Dict, List
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Initialize Groq client
class AIDoctor:
    def __init__(self):
        # Check if API key is available
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Please make sure it's set in your .env file"
            )
        
        # Initialize Groq client
        self.client = groq.Groq(api_key=api_key)
        
        # System prompt for the AI doctor
        self.system_prompt = """You are an AI Medical Assistant. Your role is to:
        1. Ask relevant questions about symptoms
        2. Provide preliminary assessments
        3. Offer general health advice
        4. Recommend when to seek professional medical help
        
        Important: Always include a disclaimer that you are an AI and not a replacement 
        for professional medical advice. For any serious concerns, always recommend 
        consulting with a healthcare provider."""

    def get_response(self, conversation_history: List[Dict[str, str]]) -> str:
        try:
            # Prepare the messages for the API call
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(conversation_history)
            
            # Make the API call to Groq
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model="mixtral-8x7b-32768",  # Using Mixtral model for better performance
                temperature=0.7,
                max_tokens=1024,
                top_p=0.95,
            )
            
            return chat_completion.choices[0].message.content
        
        except Exception as e:
            return f"Error: {str(e)}"

class StreamlitApp:
    def __init__(self):
        self.ai_doctor = AIDoctor()
        
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'conversation_history' not in st.session_state:
            st.session_state.conversation_history = []
        if 'user_name' not in st.session_state:
            st.session_state.user_name = None

    def display_header(self):
        """Display the app header and description"""
        st.title("🏥 AI Doctor Assistant")
        st.markdown("""
        Welcome to the AI Doctor Assistant! I'm here to:
        * Discuss your health concerns
        * Provide general health information
        * Help you decide if you should see a doctor
        
        **Note:** This is an AI assistant and not a replacement for professional medical advice.
        """)

    def display_disclaimer(self):
        """Display medical disclaimer"""
        with st.expander("📋 Important Disclaimer", expanded=False):
            st.warning("""
            This AI Doctor Assistant is for informational purposes only and is not a substitute 
            for professional medical advice, diagnosis, or treatment. Always seek the advice of 
            your physician or other qualified health provider with any questions you may have 
            regarding a medical condition.
            
            In case of emergency, please call your local emergency services immediately.
            """)

    def get_user_info(self):
        """Get user information if not already provided"""
        if not st.session_state.user_name:
            with st.form("user_info_form"):
                name = st.text_input("What's your name?")
                submit = st.form_submit_button("Start Consultation")
                if submit and name:
                    st.session_state.user_name = name
                    return True
            return False
        return True

    def display_chat_interface(self):
        """Display the chat interface"""
        # Display conversation history
        for message in st.session_state.conversation_history:
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                st.write(f"👤 **You:** {content}")
            else:
                st.write(f"👨‍⚕️ **AI Doctor:** {content}")

        # Chat input
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_area("Describe your symptoms or ask a health question:", 
                                    height=100)
            submit = st.form_submit_button("Send")
            
            if submit and user_input:
                # Add user message to history
                st.session_state.conversation_history.append(
                    {"role": "user", "content": user_input}
                )
                
                # Get AI response
                ai_response = self.ai_doctor.get_response(
                    st.session_state.conversation_history
                )
                
                # Add AI response to history
                st.session_state.conversation_history.append(
                    {"role": "assistant", "content": ai_response}
                )
                
                # Rerun to update the display
                st.rerun()

    def add_sidebar_features(self):
        """Add sidebar features like consultation history and settings"""
        with st.sidebar:
            st.header("📊 Consultation Information")
            if st.session_state.user_name:
                st.write(f"Patient: {st.session_state.user_name}")
                st.write(f"Session started: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            
            if st.button("Start New Consultation"):
                st.session_state.conversation_history = []
                st.rerun()

            # Export conversation
            if st.session_state.conversation_history:
                conversation_text = "\n".join([
                    f"{msg['role']}: {msg['content']}" 
                    for msg in st.session_state.conversation_history
                ])
                st.download_button(
                    label="Export Consultation",
                    data=conversation_text,
                    file_name="ai_doctor_consultation.txt",
                    mime="text/plain"
                )

    def run(self):
        """Run the Streamlit app"""
        self.initialize_session_state()
        self.display_header()
        self.display_disclaimer()
        
        if self.get_user_info():
            self.add_sidebar_features()
            self.display_chat_interface()

def main():
    # Set page config
    st.set_page_config(
        page_title="AI Doctor Assistant",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Run the app
    app = StreamlitApp()
    app.run()

if __name__ == "__main__":
    main()
