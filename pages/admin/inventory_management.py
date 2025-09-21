import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime

def show_inventory_management():
    st.header("Inventory Management")
    
    tab1, tab2, tab3 = st.tabs(["Add/Update Parts", "View Inventory", "Inventory Analytics"])
    
    # Add/Update Parts Tab
    with tab1:
        with st.form("add_part_form"):
            st.subheader("Add New Part")
            
            part_id = st.text_input("Part ID", placeholder="e.g., PRT001")
            name = st.text_input("Part Name")
            quantity = st.number_input("Quantity", min_value=0, step=1)
            price = st.number_input("Price per Unit", min_value=0.0, step=1.0)
            status = "In Stock" if quantity > 0 else "Out of Stock"
            
            submit = st.form_submit_button("Add Part")
            
            if submit:
                try:
                    conn = sqlite3.connect('vehicle_service.db')
                    c = conn.cursor()
                    c.execute("INSERT INTO inventory VALUES (?, ?, ?, ?, ?)",
                            (part_id, name, quantity, price, status))
                    conn.commit()
                    st.success("Part added successfully!")
                except sqlite3.IntegrityError:
                    st.error("Part ID already exists!")
                finally:
                    conn.close()
    
    # View Inventory Tab
    with tab2:
        st.subheader("Current Inventory")
        
        conn = sqlite3.connect('vehicle_service.db')
        df = pd.read_sql_query("SELECT * FROM inventory", conn)
        conn.close()
        
        if not df.empty:
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                status_filter = st.multiselect(
                    "Filter by Status",
                    options=df['status'].unique(),
                    default=df['status'].unique()
                )
            with col2:
                min_quantity = st.number_input("Minimum Quantity", value=0)
            
            # Apply filters
            filtered_df = df[
                (df['status'].isin(status_filter)) &
                (df['quantity'] >= min_quantity)
            ]
            
            # Edit functionality
            edited_df = st.data_editor(
                filtered_df,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "part_id": st.column_config.TextColumn("Part ID", disabled=True),
                    "name": st.column_config.TextColumn("Name"),
                    "quantity": st.column_config.NumberColumn("Quantity"),
                    "price": st.column_config.NumberColumn("Price per Unit"),
                    "status": st.column_config.SelectboxColumn(
                        "Status",
                        options=["In Stock", "Out of Stock", "Low Stock"]
                    )
                }
            )
            
            if st.button("Save Changes"):
                conn = sqlite3.connect('vehicle_service.db')
                c = conn.cursor()
                
                for index, row in edited_df.iterrows():
                    c.execute("""
                        UPDATE inventory 
                        SET name=?, quantity=?, price=?, status=?
                        WHERE part_id=?
                    """, (row['name'], row['quantity'], row['price'], row['status'], row['part_id']))
                
                conn.commit()
                conn.close()
                st.success("Changes saved successfully!")
        else:
            st.info("No parts found in the inventory.")
    
    # Inventory Analytics Tab
    with tab3:
        st.subheader("Inventory Analytics")
        
        conn = sqlite3.connect('vehicle_service.db')
        df = pd.read_sql_query("SELECT * FROM inventory", conn)
        conn.close()
        
        if not df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Stock status distribution
                fig_status = px.pie(
                    df,
                    names='status',
                    title='Inventory Status Distribution',
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig_status, use_container_width=True)
            
            with col2:
                # Part quantity distribution
                fig_quantity = px.bar(
                    df,
                    x='name',
                    y='quantity',
                    title='Parts Quantity Distribution',
                    color='status'
                )
                st.plotly_chart(fig_quantity, use_container_width=True)
            
            # Summary statistics
            st.subheader("Summary Statistics")
            col3, col4, col5 = st.columns(3)
            
            with col3:
                st.metric("Total Parts", len(df))
            with col4:
                st.metric("Total Items in Stock", df['quantity'].sum())
            with col5:
                total_value = (df['quantity'] * df['price']).sum()
                st.metric("Total Inventory Value", f"${total_value:.2f}")
            
            # Low stock alerts
            st.subheader("Low Stock Alerts")
            low_stock = df[df['quantity'] <= 5]
            if not low_stock.empty:
                st.warning("The following parts are running low on stock:")
                st.dataframe(
                    low_stock[['part_id', 'name', 'quantity']],
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.success("No parts are running low on stock.") 