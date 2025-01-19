# app.py
import streamlit as st

def main():
    st.title('Text Case Converter')
    
    # Input text box
    user_input = st.text_input('Enter your text:', 'Hello World')
    
    # Convert button
    if st.button('Convert to Uppercase'):
        # Display the converted text
        st.write('Converted text:', user_input.upper())
        
    # Add a note about usage
    st.markdown('---')
    st.markdown('*Enter any text and click the button to convert it to uppercase.*')

if __name__ == '__main__':
    main()
