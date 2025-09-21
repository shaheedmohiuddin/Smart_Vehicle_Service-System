import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px

def show_staff_management():
    st.header("Staff Management")
    
    # Create tabs for different operations
    tab1, tab2, tab3 = st.tabs(["Add Staff", "View/Edit Staff", "Staff Analytics"])
    
    # Add Staff Tab
    with tab1:
        with st.form("add_staff_form"):
            st.subheader("Add New Staff Member")
            
            staff_id = st.text_input("Staff ID", placeholder="e.g., STF001")
            name = st.text_input("Full Name")
            duty = st.selectbox("Duty", ["Mechanic", "Helper", "Manager", "Receptionist"])
            salary = st.number_input("Salary", min_value=0.0, step=100.0)
            
            submit = st.form_submit_button("Add Staff Member")
            
            if submit:
                try:
                    conn = sqlite3.connect('vehicle_service.db')
                    c = conn.cursor()
                    c.execute("INSERT INTO staff VALUES (?, ?, ?, ?)",
                            (staff_id, name, duty, salary))
                    conn.commit()
                    st.success("Staff member added successfully!")
                except sqlite3.IntegrityError:
                    st.error("Staff ID already exists!")
                finally:
                    conn.close()
    
    # View/Edit Staff Tab
    with tab2:
        st.subheader("Current Staff Members")
        
        conn = sqlite3.connect('vehicle_service.db')
        df = pd.read_sql_query("SELECT * FROM staff", conn)
        conn.close()
        
        if not df.empty:
            # Edit functionality
            edited_df = st.data_editor(
                df,
                hide_index=True,
                use_container_width=True,
                num_rows="dynamic",
                column_config={
                    "staff_id": st.column_config.TextColumn("Staff ID", disabled=True),
                    "name": st.column_config.TextColumn("Name"),
                    "duty": st.column_config.SelectboxColumn(
                        "Duty",
                        options=["Mechanic", "Helper", "Manager", "Receptionist"]
                    ),
                    "salary": st.column_config.NumberColumn("Salary")
                }
            )
            
            if st.button("Save Changes"):
                conn = sqlite3.connect('vehicle_service.db')
                c = conn.cursor()
                
                for index, row in edited_df.iterrows():
                    c.execute("""
                        UPDATE staff 
                        SET name=?, duty=?, salary=?
                        WHERE staff_id=?
                    """, (row['name'], row['duty'], row['salary'], row['staff_id']))
                
                conn.commit()
                conn.close()
                st.success("Changes saved successfully!")
        else:
            st.info("No staff members found in the database.")
    
    # Staff Analytics Tab
    with tab3:
        st.subheader("Staff Analytics")
        
        conn = sqlite3.connect('vehicle_service.db')
        df = pd.read_sql_query("SELECT * FROM staff", conn)
        conn.close()
        
        if not df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Duty distribution pie chart
                fig_duty = px.pie(df, names='duty', title='Staff Distribution by Role')
                st.plotly_chart(fig_duty, use_container_width=True)
            
            with col2:
                # Salary distribution bar chart
                fig_salary = px.bar(df, x='name', y='salary', title='Salary Distribution')
                st.plotly_chart(fig_salary, use_container_width=True)
            
            # Summary statistics
            st.subheader("Summary Statistics")
            col3, col4, col5 = st.columns(3)
            
            with col3:
                st.metric("Total Staff", len(df))
            with col4:
                st.metric("Average Salary", f"${df['salary'].mean():.2f}")
            with col5:
                st.metric("Total Monthly Payroll", f"${df['salary'].sum():.2f}")
        else:
            st.info("No data available for analytics.") 