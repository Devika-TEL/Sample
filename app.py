import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI 
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure 
os.getenv('GOOGLE_API_KEY')

def get_ai_response(prompt):
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)
        response = llm.invoke(prompt).content
        return response
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    st.title('Text Case Converter & AI Assistant')
    
    # Input text box
    user_input = st.text_input('Enter your text:', 'Hello World')
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Original case conversion
        if st.button('Convert to Uppercase'):
            st.write('Converted text:', user_input.upper())
    
    with col2:
        # AI enhancement
        if st.button('Enhance with AI'):
            prompt = f"Improve this text while maintaining its core meaning: '{user_input}'"
            ai_response = get_ai_response(prompt)
            st.write('AI Enhanced:', ai_response)
    
    # Add usage notes
    st.markdown('---')
    st.markdown('''
    *Instructions:*
    - Enter text and click "Convert to Uppercase" for simple case conversion
    - Click "Enhance with AI" to get an AI-enhanced version of your text
    ''')

if __name__ == '__main__':
    main()
