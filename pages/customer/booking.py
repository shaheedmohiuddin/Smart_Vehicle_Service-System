import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

def get_service_recommendation(vehicle_type, problem_description):
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"""
    As an automotive expert, analyze the following vehicle issue:
    Vehicle Type: {vehicle_type}
    Problem Description: {problem_description}
    
    Provide a JSON response with:
    1. Potential causes
    2. Recommended services
    3. Estimated time required
    4. Estimated cost range
    5. Priority level (Emergency/High/Medium/Low)
    6. Additional recommendations
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return str(e)

def show_booking_form():
    st.header("Book a Service")
    
    # AI-powered problem diagnosis
    with st.expander("🤖 AI Problem Diagnosis", expanded=True):
        vehicle_type = st.selectbox(
            "Vehicle Type",
            ["Car", "Bike", "SUV", "Commercial Vehicle"]
        )
        
        problem_description = st.text_area(
            "Describe your vehicle's problem",
            placeholder="E.g., Strange noise when braking, Engine not starting smoothly..."
        )
        
        if problem_description:
            with st.spinner("Analyzing your problem..."):
                recommendation = get_service_recommendation(vehicle_type, problem_description)
                st.info("AI Analysis Result:")
                st.json(recommendation)
    
    # Booking Form
    with st.form("service_booking_form"):
        st.subheader("Service Booking Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            customer_name = st.text_input("Full Name")
            vehicle_number = st.text_input("Vehicle Number")
            service_type = st.multiselect(
                "Service Required",
                [
                    "General Service",
                    "Oil Change",
                    "Brake Service",
                    "Engine Tune-up",
                    "Tire Service",
                    "Battery Service",
                    "AC Service",
                    "Other"
                ]
            )
        
        with col2:
            # Date selection (exclude past dates and next 30 days)
            min_date = datetime.now().date()
            max_date = min_date + timedelta(days=30)
            date = st.date_input(
                "Preferred Date",
                min_value=min_date,
                max_value=max_date
            )
            
            # Time slot selection
            available_slots = [
                "09:00 AM", "10:00 AM", "11:00 AM",
                "12:00 PM", "02:00 PM", "03:00 PM",
                "04:00 PM", "05:00 PM"
            ]
            time_slot = st.selectbox("Preferred Time", available_slots)
            
            # Check slot availability
            conn = sqlite3.connect('vehicle_service.db')
            c = conn.cursor()
            c.execute("""
                SELECT COUNT(*) FROM bookings 
                WHERE booking_date=? AND time_slot=?
            """, (date, time_slot))
            slot_count = c.fetchone()[0]
            conn.close()
            
            if slot_count >= 3:  # Assuming max 3 bookings per slot
                st.error("⚠️ This slot is fully booked. Please select another time.")
            else:
                st.success(f"✅ {3 - slot_count} slots available")
        
        # Additional details
        st.text_area(
            "Additional Notes",
            placeholder="Any specific requirements or concerns..."
        )
        
        # Terms and conditions
        st.checkbox(
            "I agree to the terms and conditions",
            help="Click to read our terms and conditions"
        )
        
        submitted = st.form_submit_button("Book Service")
        
        if submitted:
            if not all([customer_name, vehicle_number, service_type, date, time_slot]):
                st.error("Please fill in all required fields.")
            else:
                try:
                    conn = sqlite3.connect('vehicle_service.db')
                    c = conn.cursor()
                    
                    # Generate booking ID
                    booking_id = f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    
                    c.execute("""
                        INSERT INTO bookings 
                        (booking_id, customer_name, vehicle_type, vehicle_number,
                         service_type, booking_date, time_slot, status, description)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        booking_id, customer_name, vehicle_type, vehicle_number,
                        ", ".join(service_type), date, time_slot, "Pending",
                        problem_description
                    ))
                    
                    conn.commit()
                    
                    # Success message with booking details
                    st.success("🎉 Service booked successfully!")
                    st.info(f"""
                        Booking Details:
                        - Booking ID: {booking_id}
                        - Date: {date}
                        - Time: {time_slot}
                        
                        We'll send you a confirmation email shortly.
                    """)
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                finally:
                    conn.close()

def show_my_bookings():
    st.header("My Bookings")
    
    conn = sqlite3.connect('vehicle_service.db')
    df = pd.read_sql_query("SELECT * FROM bookings", conn)
    conn.close()
    
    if not df.empty:
        # Filter options
        status_filter = st.multiselect(
            "Filter by Status",
            options=df['status'].unique(),
            default=df['status'].unique()
        )
        
        filtered_df = df[df['status'].isin(status_filter)]
        
        if not filtered_df.empty:
            st.dataframe(
                filtered_df,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "booking_id": st.column_config.TextColumn("Booking ID"),
                    "status": st.column_config.SelectboxColumn(
                        "Status",
                        options=["Pending", "Confirmed", "In Progress", "Completed", "Cancelled"]
                    )
                }
            )
        else:
            st.info("No bookings found with selected filters.")
    else:
        st.info("No bookings found.") 