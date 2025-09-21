import streamlit as st
import google.generativeai as genai
import sqlite3
import json
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def get_chat_response(user_input, chat_history):
    model = genai.GenerativeModel('gemini-pro')
    
    # Create context from chat history
    context = "\n".join([f"User: {msg['user']}\nAssistant: {msg['assistant']}" 
                        for msg in chat_history[-5:]])  # Last 5 messages for context
    
    prompt = f"""
    You are an automotive service assistant. Help the user with their vehicle-related queries.
    Be professional, helpful, and provide accurate information.
    
    Previous conversation:
    {context}
    
    User: {user_input}
    
    Provide a helpful response considering:
    1. Common vehicle problems and solutions
    2. Maintenance tips
    3. Service recommendations
    4. Booking assistance
    5. Emergency guidance if needed
    
    If the query requires immediate attention, suggest contacting emergency services.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"I apologize, but I'm having trouble processing your request. Please try again or contact our support team. Error: {str(e)}"

def show_support():
    st.header("24/7 Service Support")
    
    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Chat interface
    st.write("Hello! I'm your automotive service assistant. How can I help you today?")
    
    # Quick action buttons
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📅 Book Service"):
            st.session_state.chat_history.append({
                "user": "How can I book a service?",
                "assistant": "To book a service, you can:\n1. Go to the 'Book Service' page\n2. Select your vehicle type\n3. Choose your preferred date and time\n4. Describe your vehicle's issue\n\nWould you like me to guide you through the process?"
            })
    with col2:
        if st.button("🚗 Vehicle Issues"):
            st.session_state.chat_history.append({
                "user": "What are common vehicle issues?",
                "assistant": "Common vehicle issues include:\n1. Engine not starting\n2. Unusual noises\n3. Brake problems\n4. Battery issues\n5. Transmission problems\n\nCan you describe the specific issue you're experiencing?"
            })
    with col3:
        if st.button("💰 Service Costs"):
            st.session_state.chat_history.append({
                "user": "What are your service costs?",
                "assistant": "Our service costs vary depending on the type of service and vehicle. Here are some estimates:\n1. General Service: ₹2,000-₹6,000\n2. Oil Change: ₹500-₹1,000\n3. Brake Service: ₹1,000-₹3,000\n4. Engine Tune-up: ₹2,000-₹5,000\n\nWould you like a specific cost estimate?"
            })
    with col4:
        if st.button("🆘 Emergency Help"):
            st.session_state.chat_history.append({
                "user": "I need emergency help!",
                "assistant": "For emergency assistance:\n1. Call our 24/7 helpline: 9988776655\n2. Use our roadside assistance service\n3. If you're in immediate danger, call emergency services\n\nCan you describe your emergency situation?"
            })
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(message["user"])
        with st.chat_message("assistant"):
            st.write(message["assistant"])
    
    # Chat input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Get and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_chat_response(user_input, st.session_state.chat_history)
                st.write(response)
        
        # Update chat history
        st.session_state.chat_history.append({
            "user": user_input,
            "assistant": response
        })
    
    # Helpful tips sidebar
    with st.sidebar:
        st.subheader("Quick Tips")
        st.info("""
        🔧 Regular Maintenance Tips:
        - Check oil levels monthly
        - Inspect tire pressure
        - Monitor warning lights
        - Schedule regular services
        
        🚨 Warning Signs:
        - Unusual noises
        - Vibrations
        - Warning lights
        - Reduced performance
        
        📞 Emergency Contacts:
        - Service Center: 9988776655
        - Email: uchihabyte.git@gmail.com
        - Location: Hyderabad, Telangana
        - Emergency: 911
        """) 