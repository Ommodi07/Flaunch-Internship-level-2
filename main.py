import streamlit as st
import groq
from typing import Dict, List
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from datetime import datetime

# Initialize Groq client
class AIDoctor:
    def _init_(self):
        # Check if API key is available
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Please make sure it's set in your .env file"
            )
        
        # Initialize Groq client
        self.client = groq.Groq(api_key=api_key)
        
        # Enhanced system prompt for more conversational interactions
        self.system_prompt = """You are a friendly and empathetic AI Medical Assistant named Dr. AI. Your communication style should be:
                1. Warm and conversational, like a caring doctor
                2. Clear and easy to understand, avoiding complex medical jargon
                3. Patient and thorough in your explanations
                4. Empathetic to the patient's concerns

                You will receive the patient's complete profile including:
                - Name (use it occasionally to make the conversation personal)
                - Age (consider age-specific health concerns and medication dosages)
                - Sex (consider sex-specific health conditions and symptoms)
                - Height and Weight (use to assess BMI and related health factors)
                - Allergies (ALWAYS check against these when suggesting medications)

                Your role is to:
                1. Start with a friendly greeting and ask about their symptoms
                2. Consider the patient's complete profile when assessing their concerns
                3. Ask relevant follow-up questions in a conversational way
                4. Calculate and consider BMI when relevant to the consultation
                5. Provide preliminary assessments in clear, simple language
                6. Offer practical health advice and lifestyle recommendations
                7. ALWAYS cross-reference any medication suggestions with their listed allergies

                When suggesting medications:
                - Focus on common, easily available over-the-counter options
                - FIRST check against the patient's listed allergies
                - Explain potential allergies and interactions in simple terms
                - Always remind about reading medication labels
                - Adjust dosage recommendations based on age and weight when relevant
                - Provide alternative options when available

                Remember to:
                - Use the patient's name in responses occasionally
                - Show understanding and empathy for their symptoms
                - Reference their age and other relevant health factors when giving advice
                - Consider sex-specific health concerns when relevant
                - Maintain continuity by referencing previous parts of the conversation
                - Ask one clear follow-up question at a time
                - End your responses with encouragement or support
                - Be extra cautious with medication recommendations for:
                * Children and elderly patients
                * Patients with multiple allergies
                * Patients with extreme BMI values

                Important: Always include a friendly reminder that you are an AI assistant and not a 
                replacement for professional medical advice. For any serious concerns, warmly recommend 
                consulting with a healthcare provider."""

    def get_response(self, conversation_history: List[Dict[str, str]], user_name: str) -> str:
        try:
            # Prepare the messages for the API call
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add user's information to the context
            user_info = {
                "role": "system", 
                "content": f"""The patient's information:
                - Name: {st.session_state.user_name}
                - Age: {st.session_state.user_age} years
                - Sex: {st.session_state.user_sex}
                - Height: {st.session_state.user_height} cm
                - Weight: {st.session_state.user_weight} kg
                - Allergies: {st.session_state.user_allergies}
                
                Please consider this information when providing medical advice and watch for any allergy concerns."""
            }
            messages.append(user_info)


            
            # Add the entire conversation history
            messages.extend(conversation_history)
            
            # Make the API call to Groq
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model="llama-3.2-11b-vision-preview",  # Using LLAMA 3.2 11B model for better performance
                temperature=0.7,
                max_tokens=1024,
                top_p=0.95,
            )
            
            return chat_completion.choices[0].message.content
        
        except Exception as e:
            return f"Error: {str(e)}"

class StreamlitApp:
    def _init_(self):
        self.ai_doctor = AIDoctor()
        
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'conversation_history' not in st.session_state:
            st.session_state.conversation_history = []
        if 'user_name' not in st.session_state:
            st.session_state.user_name = None
        if 'user_age' not in st.session_state:
            st.session_state.user_age = None
        if 'user_sex' not in st.session_state:
            st.session_state.user_sex = None
        if 'user_height' not in st.session_state:
            st.session_state.user_height = None
        if 'user_weight' not in st.session_state:
            st.session_state.user_weight = None
        if 'user_allergies' not in st.session_state:
            st.session_state.user_allergies = None



    def display_header(self):
        """Display the app header and description"""
        st.title("🏥 AI Doctor Assistant")
        st.markdown("""
        Hi! I'm Dr. AI, your friendly medical assistant. I'm here to:
        * Chat about your health concerns
        * Help understand your symptoms
        * Suggest over-the-counter remedies
        * Guide you on when to see a doctor
        
        *Note:* I'm an AI assistant here to help, but not to replace your regular doctor.
        """)

    def display_disclaimer(self):
        """Display medical disclaimer"""
        st.text("")
        st.text("")
        with st.expander("📋 Important Note", expanded=True):
            st.warning("""
            Hi there! While I'm here to help and provide information, please remember that 
            I'm an AI assistant, not a real doctor. Any advice or suggestions I provide 
            should be discussed with your healthcare provider before taking action.
            
            If you're experiencing a medical emergency, please contact emergency services 
            immediately.
            """)

    def get_user_info(self):
        """Get user information if not already provided"""
        if not st.session_state.user_name:
            with st.form("user_info_form"):
                st.markdown("### 👋 Welcome! Let's get to know each other")
                
                # Basic Information
                name = st.text_input("What should I call you?")
                
                # Age and Sex
                col1, col2 = st.columns(2)
                with col1:
                    age = st.number_input("Age (years)", min_value=0, max_value=120)
                with col2:
                    sex = st.selectbox("Sex", options=["Male", "Female", "Other"])
                
                # Height and Weight
                col3, col4 = st.columns(2)
                with col3:
                    height = st.number_input("Height (cm)", min_value=0, max_value=300, value=None)
                with col4:
                    weight = st.number_input("Weight (kg)", min_value=0, max_value=500, value=None)
                
                # Allergies
                allergies = st.text_area(
                    "Please list any medicine or food allergies (if none, write 'None')",
                    placeholder="Enter allergies here..."
                )
                
                submit = st.form_submit_button("Start Chat")
                
                if submit and name and age and sex and height and weight and allergies:
                    st.session_state.user_name = name
                    st.session_state.user_age = age
                    st.session_state.user_sex = sex
                    st.session_state.user_height = height
                    st.session_state.user_weight = weight
                    st.session_state.user_allergies = allergies
                    return True
                elif submit:
                    st.error("Please fill in all fields")
                return False
            return False
        return True
    
    def create_message_container(self, role: str, content: str):
        """Create a styled message container for chat messages"""
        if role == "user":
            with st.container():
                # User message styling
                st.markdown(
                    f"""
                    <div style="display: flex; justify-content: flex-end; margin: 1rem 0;">
                        <div style="background-color: #47b36b; padding: 0.75rem; border-radius: 15px; max-width: 80%;">
                            <p style="margin: 0; color: #000;">💬 {content}</p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            with st.container():
                # AI doctor message styling
                st.markdown(
                    f"""
                    <div style="display: flex; margin: 1rem 0;">
                        <div style="background-color: #021617; padding: 0.75rem; border-radius: 15px; max-width: 80%;">
                            <p style="margin: 0; color: #00a2cf;">👨‍⚕ {content}</p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    def display_chat_interface(self):
        """Display the enhanced chat interface"""
        # Create a container for the chat history
        chat_container = st.container()
        
        # Display conversation history with enhanced styling
        with chat_container:
            for message in st.session_state.conversation_history:
                self.create_message_container(message["role"], message["content"])

        # Chat input with styling
        st.markdown("---")
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_area(
                "Type your message here:",
                height=100,
                placeholder="Describe your symptoms or ask any health-related questions..."
            )
            col1, col2 = st.columns([5, 1])
            with col2:
                submit = st.form_submit_button("Send 📤")
            
            if submit and user_input:
                # Add user message to history
                st.session_state.conversation_history.append(
                    {"role": "user", "content": user_input}
                )
                
                # Get AI response with user's name context
                ai_response = self.ai_doctor.get_response(
                    st.session_state.conversation_history,
                    st.session_state.user_name
                )
                
                # Add AI response to history
                st.session_state.conversation_history.append(
                    {"role": "assistant", "content": ai_response}
                )
                
                # Rerun to update the display
                st.rerun()
    def create_pdf_report(self, conversation_text: str) -> bytes:
        """Create a PDF report of the chat history"""
        class PDF(FPDF):
            def header(self):
                # Add logo or header image if desired
                self.set_font('Helvetica', 'B', 15)
                self.cell(0, 10, 'AI Doctor Consultation Report', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
                self.set_y(self.get_y() + 10)

            def footer(self):
                self.set_y(-15)
                self.set_font('Helvetica', 'I', 8)
                self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, align='C')

        # Create PDF object
        pdf = PDF()
        pdf.alias_nb_pages()
        pdf.add_page()
        
        # Add patient information
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 10, 'Patient Information:', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font('helvetica', '', 11)
        pdf.cell(0, 10, f"Name: {st.session_state.user_name}", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 10, f"Age: {st.session_state.user_age} years", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 10, f"Sex: {st.session_state.user_sex}", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 10, f"Height: {st.session_state.user_height} cm", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 10, f"Weight: {st.session_state.user_weight} kg", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 10, f"Allergies: {st.session_state.user_allergies}", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # Add conversation
        pdf.set_y(pdf.get_y() + 10)
        pdf.set_font('helvetica', 'B', 12)
        pdf.cell(0, 10, 'Consultation History:', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font('helvetica', '', 11)

        # Split conversation into lines and add to PDF
        pdf.set_fill_color(245, 245, 245)  # Light gray background for messages
        for line in conversation_text.split('\n'):
            if line.strip():  # Skip empty lines
                # Add some styling based on whether it's the AI or user
                if line.startswith('You:'):
                    pdf.set_text_color(0, 100, 0)  # Dark green for user
                else:
                    pdf.set_text_color(0, 0, 139)  # Dark blue for AI
                
                # Write the message with multi-cell to handle long text
                pdf.multi_cell(0, 10, line, fill=True)
                pdf.ln(5)  # Add some space between messages
        
        # Reset text color
        pdf.set_text_color(0, 0, 0)
        
        # Add disclaimer at the end
        pdf.set_y(pdf.get_y() + 10)
        pdf.set_font('helvetica', 'I', 10)
        pdf.multi_cell(0, 10, 'Note: This is an AI-generated consultation report and should not replace professional medical advice. Please consult with a healthcare provider for proper medical diagnosis and treatment.')
    

        # Return PDF as bytes
        return bytes(pdf.output())

    def add_sidebar_features(self):
        """Add sidebar features with enhanced styling"""
        with st.sidebar:
            st.header("🗒 Patient Info:")
            
            # User information
            if st.session_state.user_name:
                st.markdown(f"""
                    <div style='background-color: #00162b; padding: 1rem; border-radius: 10px;'>
                        <p style='margin: 0;'>👤 <strong>Patient:</strong> {st.session_state.user_name}</p>
                        <p style='margin: 0;'>📅 <strong>Age:</strong> {st.session_state.user_age} years</p>
                        <p style='margin: 0;'>⚧ <strong>Sex:</strong> {st.session_state.user_sex}</p>
                        <p style='margin: 0;'>📏 <strong>Height:</strong> {st.session_state.user_height} cm</p>
                        <p style='margin: 0;'>⚖ <strong>Weight:</strong> {st.session_state.user_weight} kg</p>
                        <p style='margin: 0;'>⚠ <strong>Allergies:</strong> {st.session_state.user_allergies}</p>
                        <p style='margin: 0;'>🕒 <strong>Started:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                    </div>
                """, unsafe_allow_html=True)


            
            st.markdown("---")
            st.header("💬 Chat Controls")
            # Chat control buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 New Chat", type="primary", use_container_width=True):
                    st.session_state.conversation_history = []
                    st.rerun()
            with col2:
                if st.button("👋 New Consultation", use_container_width=True):
                    st.session_state.conversation_history = []
                    st.session_state.user_name = None
                    st.rerun()

            # Export feature
            if st.session_state.conversation_history:
                st.markdown("---")
                st.header("📥 Save Your Chat")
                
                # Format conversation for PDF
                conversation_text = "\n".join([
                    f"{'You' if msg['role'] == 'user' else 'Dr. AI'}: {msg['content']}" 
                    for msg in st.session_state.conversation_history
                ])
                
                # Generate PDF
                pdf_bytes = self.create_pdf_report(conversation_text)
                
                # Create download button
                st.download_button(
                    label="Download Consultation Report (PDF)",
                    data=pdf_bytes,
                    file_name=f"ai_doctor_consultation_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )


    def run(self):
        """Run the Streamlit app"""
        self.initialize_session_state()
        col1, col2 = st.columns(2)
        with col1:
            self.display_header()
        with col2:
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
    
    # Add custom CSS
    st.markdown("""
        <style>
        .stTextArea textarea {
            border-radius: 10px;
        }
        
        .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        padding-left: 5rem;
        padding-right: 5rem;
        }
        
        .stButton button {
            border-radius: 20px;
        }
        
        .stMarkdown {
            line-height: 1.6;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Run the app
    app = StreamlitApp()
    app.run()

if _name_ == "_main_":
    main()