import streamlit as st
import sqlite3
import os
from dotenv import load_dotenv
from datetime import datetime
import plotly.express as px
import pandas as pd
import uuid
import google.generativeai as genai
from typing import Dict, List, Optional
import time
import hashlib

# Load environment variables
load_dotenv('api.env')

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    st.error("Gemini API key not found. Please check your api.env file.")
    st.stop()

try:
    genai.configure(api_key=GEMINI_API_KEY)
    # Initialize Gemini model with gemini-1.5-flash
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Error initializing Gemini API: {str(e)}")
    st.stop()

def get_auto_assist_response(prompt: str, context: Optional[Dict] = None) -> str:
    """
    Get AI-powered suggestions and insights using Gemini API.
    
    Args:
        prompt (str): The user's input or query
        context (Dict, optional): Additional context for better responses
        
    Returns:
        str: AI-generated response
    """
    try:
        # Prepare the full prompt with context
        full_prompt = f"""
        You are an automotive service expert AI assistant. Provide clear, concise responses in bullet points.
        
        Context: {context if context else 'No additional context provided'}
        
        User Query: {prompt}
        
        Please provide your response in this format:
        • Main point 1\n\n
        • Main point 2\n\n
        • Main point 3\n\n
        
        Keep each point brief and easy to understand.
        Make sure each bullet point is on a separate line with a blank line between them.
        """
        
        # Generate response with error handling
        try:
            response = model.generate_content(full_prompt)
            if response and hasattr(response, 'text'):
                return response.text
            else:
                return "I apologize, but I received an invalid response from the AI service. Please try again later."
        except Exception as e:
            st.error(f"Error generating AI response: {str(e)}")
            return "I apologize, but I'm currently unable to provide AI assistance. Please try again later or contact our support team."
    except Exception as e:
        return f"Error getting AI response: {str(e)}"

def get_service_recommendations(vehicle_type: str, vehicle_model: str, service_history: List[Dict]) -> str:
    """
    Get AI-powered service recommendations based on vehicle details and history.
    
    Args:
        vehicle_type (str): Type of vehicle (Car/Motorcycle)
        vehicle_model (str): Model of the vehicle
        service_history (List[Dict]): List of previous service records
        
    Returns:
        str: AI-generated service recommendations
    """
    try:
        prompt = f"""
        Based on the following vehicle information, provide service recommendations in bullet points:
        
        Vehicle Type: {vehicle_type}
        Vehicle Model: {vehicle_model}
        Service History: {service_history}
        
        Please provide your response in this format:
        
        Recommended Maintenance:\n\n
        • Item 1\n\n
        • Item 2\n\n
        
        Common Issues to Watch:\n\n
        • Issue 1\n\n
        • Issue 2\n\n
        
        Preventive Tips:\n\n
        • Tip 1\n\n
        • Tip 2\n\n
        
        Keep each point brief and actionable.
        Make sure each bullet point is on a separate line with a blank line between them.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error getting service recommendations: {str(e)}"

def get_diagnostic_insights(symptoms: str, vehicle_details: Dict) -> str:
    """
    Get AI-powered diagnostic insights based on reported symptoms.
    
    Args:
        symptoms (str): Reported vehicle symptoms/issues
        vehicle_details (Dict): Vehicle information
        
    Returns:
        str: AI-generated diagnostic insights
    """
    try:
        prompt = f"""
        Based on the following symptoms and vehicle details, provide diagnostic insights in bullet points:
        
        Symptoms: {symptoms}
        Vehicle Details: {vehicle_details}
        
        Please provide your response in this format:
        
        Likely Causes:\n\n
        • Cause 1\n\n
        • Cause 2\n\n
        
        Severity Assessment:\n\n
        • Level: [Low/Medium/High]\n\n
        • Immediate Action Required: [Yes/No]\n\n
        
        Recommended Actions:\n\n
        • Action 1\n\n
        • Action 2\n\n
        
        Safety Considerations:\n\n
        • Consideration 1\n\n
        • Consideration 2\n\n
        
        Keep each point clear and concise.
        Make sure each bullet point is on a separate line with a blank line between them.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error getting diagnostic insights: {str(e)}"

def get_staff_assistance(task: str, context: Dict) -> str:
    """
    Get AI-powered assistance for staff members.
    
    Args:
        task (str): The task or query from staff
        context (Dict): Additional context about the task
        
    Returns:
        str: AI-generated assistance
    """
    try:
        prompt = f"""
        As a service center staff assistant, provide guidance in bullet points:
        
        Task: {task}
        Context: {context}
        
        Please provide your response in this format:
        
        Step-by-Step Guidance:\n\n
        • Step 1\n\n
        • Step 2\n\n
        
        Best Practices:\n\n
        • Practice 1\n\n
        • Practice 2\n\n
        
        Common Pitfalls:\n\n
        • Pitfall 1\n\n
        • Pitfall 2\n\n
        
        Quality Check Points:\n\n
        • Check 1\n\n
        • Check 2\n\n
        
        Keep each point brief and practical.
        Make sure each bullet point is on a separate line with a blank line between them.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error getting staff assistance: {str(e)}"

# Configure page with dark theme
st.set_page_config(
    page_title="AUTO ASSIST AND BOOKING SYSTEM",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load external CSS
with open('static/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize database
def init_db():
    # Main database for other features
    conn = sqlite3.connect('vehicle_service.db')
    c = conn.cursor()
    
    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id TEXT PRIMARY KEY,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  role TEXT NOT NULL,
                  email TEXT UNIQUE,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Create staff and bookings tables
    c.execute('''CREATE TABLE IF NOT EXISTS staff
                 (staff_id TEXT PRIMARY KEY,
                  name TEXT NOT NULL,
                  duty TEXT NOT NULL,
                  salary REAL NOT NULL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS bookings
                 (booking_id TEXT PRIMARY KEY,
                  customer_name TEXT NOT NULL,
                  vehicle_type TEXT NOT NULL,
                  vehicle_number TEXT NOT NULL,
                  service_type TEXT NOT NULL,
                  booking_date DATE NOT NULL,
                  time_slot TEXT NOT NULL,
                  status TEXT NOT NULL,
                  description TEXT,
                  last_service_date DATE,
                  last_service_km INTEGER,
                  service_items TEXT,
                  additional_notes TEXT)''')
    
    conn.commit()
    conn.close()
    
    # Separate database for inventory
    init_inventory_db()

def init_inventory_db():
    """Initialize the inventory database"""
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    
    # Create inventory table
    c.execute('''CREATE TABLE IF NOT EXISTS inventory
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL, 
                  category TEXT NOT NULL, 
                  quantity INTEGER DEFAULT 0, 
                  price REAL DEFAULT 0.0,
                  min_stock INTEGER DEFAULT 0, 
                  description TEXT DEFAULT '', 
                  status TEXT DEFAULT 'In Stock',
                  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Create inventory history table
    c.execute('''CREATE TABLE IF NOT EXISTS inventory_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  inventory_id INTEGER,
                  action TEXT,
                  old_quantity INTEGER,
                  new_quantity INTEGER,
                  old_price REAL,
                  new_price REAL,
                  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (inventory_id) REFERENCES inventory(id))''')
    
    conn.commit()
    conn.close()

def delete_inventory_item(item_id):
    """Delete an inventory item and add to history"""
    try:
        conn = sqlite3.connect('inventory.db')
        c = conn.cursor()
        
        # Get item details before deletion
        c.execute("SELECT * FROM inventory WHERE id = ?", (item_id,))
        item = c.fetchone()
        
        if item:
            # Add to history
            c.execute("""
                INSERT INTO inventory_history (
                    inventory_id, action, old_quantity, new_quantity,
                    old_price, new_price
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                item_id,
                "DELETE",
                item[3],  # quantity
                0,
                item[4],  # price
                0
            ))
            
            # Delete the item
            c.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
            conn.commit()
            return True, "Item deleted successfully"
        else:
            return False, "Item not found"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def validate_inventory_csv(df):
    """Validate the CSV data for inventory import"""
    required_columns = ['name', 'category', 'quantity', 'price', 'min_stock']
    optional_columns = ['description']
    
    # Check required columns
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return False, f"Missing required columns: {', '.join(missing_columns)}"
    
    # Validate data types
    try:
        df['quantity'] = pd.to_numeric(df['quantity'], errors='raise')
        df['price'] = pd.to_numeric(df['price'], errors='raise')
        df['min_stock'] = pd.to_numeric(df['min_stock'], errors='raise')
    except ValueError:
        return False, "Invalid numeric values in quantity, price, or min_stock columns"
    
    # Validate non-negative values
    if (df['quantity'] < 0).any() or (df['price'] < 0).any() or (df['min_stock'] < 0).any():
        return False, "Negative values found in quantity, price, or min_stock columns"
    
    # Validate required fields are not empty
    if df['name'].isnull().any() or df['category'].isnull().any():
        return False, "Empty values found in name or category columns"
    
    return True, "CSV validation successful"

def import_inventory_from_csv(df):
    """Import inventory items from validated CSV data"""
    try:
        conn = sqlite3.connect('inventory.db')
        c = conn.cursor()
        
        success_count = 0
        error_count = 0
        errors = []
        
        for _, row in df.iterrows():
            try:
                # Insert into inventory
                c.execute("""
                    INSERT INTO inventory (
                        name, category, quantity, price, 
                        min_stock, description, status, last_updated
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    row['name'],
                    row['category'],
                    int(row['quantity']),
                    float(row['price']),
                    int(row['min_stock']),
                    row.get('description', ''),
                    'In Stock' if int(row['quantity']) > 0 else 'Out of Stock'
                ))
                
                # Get the inserted item's ID
                item_id = c.lastrowid
                
                # Add to history
                c.execute("""
                    INSERT INTO inventory_history (
                        inventory_id, action, new_quantity, new_price
                    ) VALUES (?, ?, ?, ?)
                """, (
                    item_id,
                    "ADD",
                    int(row['quantity']),
                    float(row['price'])
                ))
                
                success_count += 1
            except Exception as e:
                error_count += 1
                errors.append(f"Error importing {row['name']}: {str(e)}")
        
        conn.commit()
        conn.close()
        
        return True, {
            "success_count": success_count,
            "error_count": error_count,
            "errors": errors
        }
    except Exception as e:
        return False, str(e)

def show_admin_dashboard():
    st.title("Admin Dashboard")
    
    # Add logout button in the top right
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()
    
    # Create tabs for different admin functions
    tabs = st.tabs(["Staff Management", "Inventory Management", "Booking Management", "AI Assistant"])
    
    with tabs[0]:  # Staff Management
        st.header("Staff Management")
        st.write("Here you can manage staff members")
        
        # Add staff form
        with st.form("add_staff_form"):
            staff_name = st.text_input("Staff Name")
            staff_duty = st.selectbox("Duty", ["Mechanic", "Helper", "Manager", "Receptionist"])
            staff_salary = st.number_input("Salary", min_value=0.0, step=1000.0)
            submit_staff = st.form_submit_button("Add Staff")
            
            if submit_staff and staff_name and staff_salary > 0:
                conn = sqlite3.connect('vehicle_service.db')
                c = conn.cursor()
                c.execute("INSERT INTO staff (staff_id, name, duty, salary) VALUES (?, ?, ?, ?)",
                         (str(uuid.uuid4()), staff_name, staff_duty, staff_salary))
                conn.commit()
                conn.close()
                st.success("Staff member added successfully!")
        
        # Display staff list
        conn = sqlite3.connect('vehicle_service.db')
        staff_df = pd.read_sql_query("SELECT * FROM staff", conn)
        conn.close()
        
        if not staff_df.empty:
            st.write("Current Staff Members:")
            st.dataframe(staff_df)
    
    with tabs[1]:  # Inventory Management
        st.header("Inventory Management")
        st.write("Manage your inventory here")
        
        # Create tabs for different inventory functions
        inventory_tabs = st.tabs(["Add Items", "View Inventory", "Stock Alerts", "Analytics"])
        
        with inventory_tabs[0]:  # Add Items
            st.subheader("Add New Inventory Item")
            
            # Add bulk upload option
            st.markdown("### Bulk Import")
            st.markdown("""
            Import multiple items using a CSV file. The CSV should have the following columns:
            - name (required): Item name
            - category (required): Item category
            - quantity (required): Initial quantity
            - price (required): Item price
            - min_stock (required): Minimum stock level
            - description (optional): Item description
            """)
            
            uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file)
                    
                    # Show preview
                    st.write("Preview of uploaded data:")
                    st.dataframe(df.head())
                    
                    # Validate CSV
                    is_valid, message = validate_inventory_csv(df)
                    if is_valid:
                        if st.button("Import Items"):
                            with st.spinner("Importing items..."):
                                success, result = import_inventory_from_csv(df)
                                if success:
                                    st.success(f"""
                                    Import completed:
                                    - Successfully imported: {result['success_count']} items
                                    - Failed to import: {result['error_count']} items
                                    """)
                                    if result['errors']:
                                        st.warning("Errors encountered:")
                                        for error in result['errors']:
                                            st.error(error)
                                    st.rerun()
                                else:
                                    st.error(f"Import failed: {result}")
                    else:
                        st.error(f"CSV validation failed: {message}")
                except Exception as e:
                    st.error(f"Error reading CSV file: {str(e)}")
            
            st.markdown("### Add Single Item")
            with st.form("add_inventory_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    item_name = st.text_input("Item Name", placeholder="Enter item name")
                    category = st.selectbox("Category", [
                        "Engine Parts", "Brake Parts", "Electrical Parts",
                        "Body Parts", "Filters", "Fluids", "Tools", "Accessories"
                    ])
                    quantity = st.number_input("Quantity", min_value=0, step=1)
                
                with col2:
                    price = st.number_input("Price (₹)", min_value=0.0, step=0.01)
                    min_stock = st.number_input("Minimum Stock Level", min_value=0, step=1)
                    status = st.selectbox("Status", ["In Stock", "Low Stock", "Out of Stock"])
                
                description = st.text_area("Description", placeholder="Enter item description")
                
                submit_inventory = st.form_submit_button("Add Item")
                
                if submit_inventory:
                    try:
                        if not item_name or not category:
                            st.error("Item name and category are required!")
                            return
                        
                        conn = sqlite3.connect('inventory.db')
                        c = conn.cursor()
                        
                        # Insert into inventory
                        c.execute("""
                            INSERT INTO inventory (
                                name, category, quantity, price, 
                                min_stock, description, status, last_updated
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                        """, (
                            item_name, category, quantity, price,
                            min_stock, description, status
                        ))
                        
                        # Get the inserted item's ID
                        item_id = c.lastrowid
                        
                        # Add to history
                        c.execute("""
                            INSERT INTO inventory_history (
                                inventory_id, action, new_quantity, new_price
                            ) VALUES (?, ?, ?, ?)
                        """, (
                            item_id, "ADD", quantity, price
                        ))
                        
                        conn.commit()
                        conn.close()
                        st.success("Item added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding item: {str(e)}")
        
        with inventory_tabs[1]:  # View Inventory
            st.subheader("Current Inventory")
            
            # Search and filter options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                search_query = st.text_input("🔍 Search Items", placeholder="Search by name, category, or description")
            
            with col2:
                category_filter = st.selectbox(
                    "Filter by Category",
                    ["All Categories"] + [
                        "Engine Parts", "Brake Parts", "Electrical Parts",
                        "Body Parts", "Filters", "Fluids", "Tools", "Accessories"
                    ]
                )
            
            with col3:
                col3_1, col3_2 = st.columns([3, 1])
                with col3_1:
                    status_filter = st.selectbox(
                        "Filter by Status",
                        ["All", "In Stock", "Low Stock", "Out of Stock"]
                    )
                with col3_2:
                    if st.button("🗑️ Clear", help="Clear all inventory items"):
                        if st.warning("⚠️ Are you sure you want to clear all inventory items? This action cannot be undone."):
                            success, message = clear_inventory()
                            if success:
                                st.success(message)
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"Error clearing inventory: {message}")
            
            # Export option
            if st.button("📥 Export to CSV"):
                try:
                    inventory_df = get_inventory_data()
                    if not inventory_df.empty:
                        csv = inventory_df.to_csv(index=False)
                        st.download_button(
                            "Download CSV",
                            csv,
                            "inventory.csv",
                            "text/csv",
                            key='download-csv'
                        )
                    else:
                        st.warning("No inventory data to export")
                except Exception as e:
                    st.error(f"Error exporting data: {str(e)}")
            
            # Get and display inventory data
            inventory_df = get_inventory_data()
            
            if not inventory_df.empty:
                # Apply filters
                filtered_df = apply_inventory_filters(inventory_df, search_query, category_filter, status_filter)
                
                if filtered_df.empty:
                    st.info("No items match your search criteria")
                else:
                    # Display inventory in a table format
                    st.dataframe(
                        filtered_df[['name', 'category', 'quantity', 'price', 'status', 'last_updated']],
                        column_config={
                            "name": "Item Name",
                            "category": "Category",
                            "quantity": "Quantity",
                            "price": st.column_config.NumberColumn("Price (₹)", format="₹%.2f"),
                            "status": "Status",
                            "last_updated": "Last Updated"
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                    
                    # Display detailed view for each item
                    for _, item in filtered_df.iterrows():
                        st.markdown("---")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"### {item['name']} ({item['category']})")
                            st.markdown(f"**Quantity:** {item['quantity']}")
                            st.markdown(f"**Price:** ₹{item['price']}")
                            st.markdown(f"**Status:** {item['status']}")
                        
                        with col2:
                            st.markdown(f"**Min Stock:** {item['min_stock']}")
                            st.markdown(f"**Description:** {item.get('description', 'No description available')}")
                            st.markdown(f"**Last Updated:** {item['last_updated']}")
                        
                        # Update quantity and price
                        col3, col4 = st.columns(2)
                        with col3:
                            new_quantity = st.number_input(
                                f"Update Quantity",
                                min_value=0,
                                value=item['quantity'],
                                key=f"update_qty_{item['id']}"
                            )
                        with col4:
                            new_price = st.number_input(
                                f"Update Price",
                                min_value=0.0,
                                value=item['price'],
                                key=f"update_price_{item['id']}"
                            )
                        
                        # Action buttons
                        col5, col6, col7 = st.columns(3)
                        with col5:
                            if new_quantity != item['quantity'] or new_price != item['price']:
                                if st.button("Update", key=f"update_btn_{item['id']}"):
                                    try:
                                        conn = sqlite3.connect('inventory.db')
                                        c = conn.cursor()
                                        
                                        # Update inventory
                                        c.execute("""
                                            UPDATE inventory 
                                            SET quantity = ?, price = ?, status = ?, last_updated = CURRENT_TIMESTAMP
                                            WHERE id = ?
                                        """, (
                                            new_quantity,
                                            new_price,
                                            "In Stock" if new_quantity > 0 else "Out of Stock",
                                            item['id']
                                        ))
                                        
                                        # Add to history
                                        c.execute("""
                                            INSERT INTO inventory_history (
                                                inventory_id, action, 
                                                old_quantity, new_quantity,
                                                old_price, new_price
                                            ) VALUES (?, ?, ?, ?, ?, ?)
                                        """, (
                                            item['id'],
                                            "UPDATE",
                                            item['quantity'],
                                            new_quantity,
                                            item['price'],
                                            new_price
                                        ))
                                        
                                        conn.commit()
                                        conn.close()
                                        
                                        # Show success message
                                        st.success(f"Item '{item['name']}' updated successfully!")
                                        # Refresh the page after a short delay
                                        time.sleep(1)
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error updating item: {str(e)}")
                        
                        with col6:
                            if st.button("Delete", key=f"delete_btn_{item['id']}"):
                                if st.warning("Are you sure you want to delete this item?"):
                                    success, message = delete_inventory_item(item['id'])
                                    if success:
                                        st.success(f"Item '{item['name']}' deleted successfully!")
                                        # Refresh the page after a short delay
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error(message)
                        
                        with col7:
                            if st.button("View History", key=f"history_btn_{item['id']}"):
                                try:
                                    conn = sqlite3.connect('inventory.db')
                                    history_df = pd.read_sql_query(
                                        "SELECT * FROM inventory_history WHERE inventory_id = ? ORDER BY timestamp DESC",
                                        conn,
                                        params=(item['id'],)
                                    )
                                    conn.close()
                                    
                                    if not history_df.empty:
                                        st.write("Item History:")
                                        st.dataframe(history_df)
                                    else:
                                        st.info("No history available for this item.")
                                except Exception as e:
                                    st.error(f"Error loading history: {str(e)}")
            else:
                st.info("No inventory items found. Add some items to get started!")

        with inventory_tabs[2]:  # Stock Alerts
            st.subheader("Stock Alerts")
            
            try:
                conn = sqlite3.connect('vehicle_service.db')
                inventory_df = pd.read_sql_query("SELECT * FROM inventory", conn)
                conn.close()
                
                if not inventory_df.empty:
                    # Calculate stock status
                    inventory_df['stock_status'] = inventory_df.apply(
                        lambda row: "Low Stock" if row['quantity'] <= row['min_stock'] 
                        else "Out of Stock" if row['quantity'] == 0 
                        else "In Stock",
                        axis=1
                    )
                    
                    # Display alerts
                    low_stock = inventory_df[inventory_df['stock_status'] == "Low Stock"]
                    out_of_stock = inventory_df[inventory_df['stock_status'] == "Out of Stock"]
                    
                    if not low_stock.empty:
                        st.warning("### ⚠️ Low Stock Items")
                        for _, item in low_stock.iterrows():
                            st.markdown(f"""
                            - **{item['name']}** ({item['category']})
                              - Current Stock: {item['quantity']}
                              - Minimum Required: {item['min_stock']}
                              - Last Updated: {item['last_updated']}
                            """)
                    
                    if not out_of_stock.empty:
                        st.error("### ❌ Out of Stock Items")
                        for _, item in out_of_stock.iterrows():
                            st.markdown(f"""
                            - **{item['name']}** ({item['category']})
                              - Last Price: ₹{item['price']}
                              - Last Updated: {item['last_updated']}
                            """)
                    
                    if low_stock.empty and out_of_stock.empty:
                        st.success("All items are well stocked! 🎉")
                else:
                    st.info("No inventory items found. Add some items to get started!")
            except Exception as e:
                st.error(f"Error loading stock alerts: {str(e)}")
                st.info("Please try refreshing the page or contact support if the issue persists.")

        with inventory_tabs[3]:  # Analytics
            st.subheader("Inventory Analytics")
            
            try:
                conn = sqlite3.connect('inventory.db')
                inventory_df = pd.read_sql_query("SELECT * FROM inventory", conn)
                conn.close()
                
                if not inventory_df.empty:
                    # Calculate stock status
                    inventory_df['stock_status'] = inventory_df.apply(
                        lambda row: "Low Stock" if row['quantity'] <= row['min_stock'] and row['quantity'] > 0
                        else "Out of Stock" if row['quantity'] == 0
                        else "In Stock",
                        axis=1
                    )
                    
                    # Create metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Items", len(inventory_df))
                    
                    with col2:
                        total_value = (inventory_df['quantity'] * inventory_df['price']).sum()
                        st.metric("Total Inventory Value", f"₹{total_value:,.2f}")
                    
                    with col3:
                        low_stock_count = len(inventory_df[inventory_df['stock_status'] == "Low Stock"])
                        st.metric("Low Stock Items", low_stock_count)
                    
                    with col4:
                        out_of_stock_count = len(inventory_df[inventory_df['stock_status'] == "Out of Stock"])
                        st.metric("Out of Stock Items", out_of_stock_count)
                    
                    # Create visualizations
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Category distribution
                        category_counts = inventory_df['category'].value_counts()
                        fig1 = px.pie(
                            values=category_counts.values,
                            names=category_counts.index,
                            title="Inventory by Category"
                        )
                        st.plotly_chart(fig1)
                    
                    with col2:
                        # Stock status distribution
                        status_counts = inventory_df['stock_status'].value_counts()
                        fig2 = px.bar(
                            x=status_counts.index,
                            y=status_counts.values,
                            title="Stock Status Distribution",
                            labels={'x': 'Status', 'y': 'Count'}
                        )
                        st.plotly_chart(fig2)
                    
                    # Top items by value
                    st.subheader("Top Items by Value")
                    inventory_df['total_value'] = inventory_df['quantity'] * inventory_df['price']
                    top_items = inventory_df.nlargest(5, 'total_value')
                    
                    fig3 = px.bar(
                        top_items,
                        x='name',
                        y='total_value',
                        title="Top 5 Items by Inventory Value",
                        labels={'name': 'Item', 'total_value': 'Value (₹)'}
                    )
                    st.plotly_chart(fig3)
                    
                    # Recent updates
                    st.subheader("Recent Updates")
                    try:
                        conn = sqlite3.connect('inventory.db')
                        recent_updates = pd.read_sql_query(
                            """
                            SELECT 
                                h.timestamp,
                                i.name,
                                h.action,
                                h.old_quantity,
                                h.new_quantity,
                                h.old_price,
                                h.new_price
                            FROM inventory_history h
                            JOIN inventory i ON h.inventory_id = i.id
                            ORDER BY h.timestamp DESC LIMIT 10
                            """,
                            conn
                        )
                        conn.close()
                        
                        if not recent_updates.empty:
                            st.dataframe(
                                recent_updates,
                                column_config={
                                    "timestamp": "Time",
                                    "name": "Item Name",
                                    "action": "Action",
                                    "old_quantity": "Old Quantity",
                                    "new_quantity": "New Quantity",
                                    "old_price": st.column_config.NumberColumn("Old Price (₹)", format="₹%.2f"),
                                    "new_price": st.column_config.NumberColumn("New Price (₹)", format="₹%.2f")
                                },
                                hide_index=True
                            )
                        else:
                            st.info("No recent updates found.")
                    except Exception as e:
                        st.error(f"Error loading recent updates: {str(e)}")
                else:
                    st.info("No inventory items found. Add some items to get started!")
            except Exception as e:
                st.error(f"Error loading analytics: {str(e)}")
                st.info("Please try refreshing the page or contact support if the issue persists.")
    
    with tabs[2]:  # Booking Management
        st.header("Booking Management")
        st.write("Manage service bookings here")
        
        # Display current bookings
        conn = sqlite3.connect('vehicle_service.db')
        bookings_df = pd.read_sql_query("SELECT * FROM bookings", conn)
        conn.close()
        
        if not bookings_df.empty:
            st.write("Current Bookings:")
            st.dataframe(bookings_df)
            
            # Update booking status
            with st.form("update_booking_status"):
                booking_id = st.selectbox("Select Booking ID", bookings_df['booking_id'].tolist())
                new_status = st.selectbox("New Status", ["Pending", "In Progress", "Completed", "Cancelled"])
                submit_status = st.form_submit_button("Update Status")
                
                if submit_status:
                    conn = sqlite3.connect('vehicle_service.db')
                    c = conn.cursor()
                    c.execute("UPDATE bookings SET status = ? WHERE booking_id = ?",
                             (new_status, booking_id))
                    conn.commit()
                    conn.close()
                    st.success("Booking status updated successfully!")
    
    with tabs[3]:  # AI Assistant
        st.header("AI Assistant")
        st.write("Get AI-powered assistance for your tasks")
        
        # Create tabs for different AI assistance features
        ai_tabs = st.tabs(["General Assistance", "Symptom Checker", "Quick Actions"])
        
        with ai_tabs[0]:  # General Assistance
            # Task input
            task = st.text_area("Describe your task or question")
            
            if task:
                # Get context from database
                conn = sqlite3.connect('vehicle_service.db')
                staff_df = pd.read_sql_query("SELECT * FROM staff", conn)
                inventory_df = pd.read_sql_query("SELECT * FROM inventory", conn)
                bookings_df = pd.read_sql_query("SELECT * FROM bookings", conn)
                conn.close()
                
                context = {
                    "staff_count": len(staff_df),
                    "inventory_items": len(inventory_df),
                    "active_bookings": len(bookings_df[bookings_df['status'] != 'Completed']),
                    "recent_bookings": bookings_df.tail(5).to_dict('records')
                }
                
                if st.button("Get AI Assistance"):
                    with st.spinner("Getting AI assistance..."):
                        assistance = get_staff_assistance(task, context)
                        st.info("AI Assistance:")
                        st.write(assistance)
        
        with ai_tabs[1]:  # Symptom Checker
            st.subheader("Vehicle Symptom Checker")
            
            # Vehicle Type Selection
            vehicle_type = st.selectbox("Select Vehicle Type", ["Car", "Motorcycle"])
            
            # Vehicle Details
            col1, col2 = st.columns(2)
            with col1:
                vehicle_brand = st.selectbox("Select Brand", 
                    sorted(car_models.keys()) if vehicle_type == "Car" else sorted(bike_models.keys()))
            with col2:
                vehicle_model = st.selectbox("Select Model", 
                    sorted(car_models[vehicle_brand]) if vehicle_type == "Car" else sorted(bike_models[vehicle_brand]))
            
            # Vehicle Age and Usage
            col3, col4 = st.columns(2)
            with col3:
                vehicle_age = st.number_input("Vehicle Age (years)", min_value=0, max_value=50, value=0)
            with col4:
                mileage = st.number_input("Current Mileage (KM)", min_value=0, value=0)
            
            # Last Service Details
            col5, col6 = st.columns(2)
            with col5:
                last_service_date = st.date_input("Last Service Date (if any)", value=None)
            with col6:
                last_service_km = st.number_input("Last Service Mileage (KM)", min_value=0, value=0)
            
            # Symptoms Input
            st.subheader("Describe the Symptoms")
            symptoms = st.text_area(
                "Please describe any issues, sounds, or behaviors you've noticed with your vehicle. "
                "Be as detailed as possible about when and how these symptoms occur.",
                height=150
            )
            
            # Additional Context
            st.subheader("Additional Context")
            additional_context = st.text_area(
                "Any additional information that might help diagnose the issue "
                "(e.g., recent repairs, modifications, or unusual driving conditions)",
                height=100
            )
            
            if st.button("Get Diagnostic Analysis"):
                if not symptoms:
                    st.warning("Please describe the symptoms you're experiencing.")
                else:
                    with st.spinner("Analyzing symptoms..."):
                        vehicle_details = {
                            "type": vehicle_type,
                            "brand": vehicle_brand,
                            "model": vehicle_model,
                            "age": vehicle_age,
                            "mileage": mileage,
                            "last_service_date": last_service_date,
                            "last_service_km": last_service_km,
                            "additional_context": additional_context
                        }
                        
                        # Get diagnostic insights
                        diagnosis = get_diagnostic_insights(symptoms, vehicle_details)
                        
                        # Display results in an organized way
                        st.markdown("### Diagnostic Analysis")
                        st.write(diagnosis)
                        
                        # Add a section for preventive maintenance tips
                        st.markdown("### Preventive Maintenance Tips")
                        maintenance_prompt = f"""
                        Based on the vehicle details and symptoms:
                        Vehicle: {vehicle_brand} {vehicle_model}
                        Age: {vehicle_age} years
                        Mileage: {mileage} KM
                        Symptoms: {symptoms}
                        
                        Please provide:
                        1. Preventive maintenance recommendations
                        2. Regular maintenance schedule
                        3. Warning signs to watch for
                        4. Cost-effective maintenance tips
                        """
                        
                        maintenance_tips = get_auto_assist_response(maintenance_prompt)
                        st.write(maintenance_tips)
        
        with ai_tabs[2]:  # Quick Actions
            st.subheader("Quick Actions")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Get Staff Performance Insights"):
                    with st.spinner("Analyzing staff performance..."):
                        context = {
                            "staff_data": staff_df.to_dict('records'),
                            "bookings_data": bookings_df.to_dict('records')
                        }
                        insights = get_auto_assist_response(
                            "Analyze staff performance and provide insights for improvement",
                            context
                        )
                        st.info("Staff Performance Insights:")
                        st.write(insights)
            
            with col2:
                if st.button("Get Inventory Optimization Suggestions"):
                    with st.spinner("Analyzing inventory..."):
                        context = {
                            "inventory_data": inventory_df.to_dict('records'),
                            "bookings_data": bookings_df.to_dict('records')
                        }
                        suggestions = get_auto_assist_response(
                            "Analyze inventory levels and provide optimization suggestions",
                            context
                        )
                        st.info("Inventory Optimization Suggestions:")
                        st.write(suggestions)

def show_booking_history(customer_name=None):
    st.header("Your Booking History")
    
    # Dark theme container for the entire section
    st.markdown("""
        <style>
        .booking-history-container {
            background-color: #0f172a;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .booking-card {
            background-color: #1e293b;
            padding: 20px;
            border-radius: 8px;
            margin: 10px 0;
            border: 1px solid #334155;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .booking-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            border-bottom: 1px solid #334155;
            padding-bottom: 10px;
        }
        .status-pending {
            background-color: #854d0e;
            color: #fef3c7;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.875rem;
        }
        .status-in-progress {
            background-color: #1d4ed8;
            color: #e0f2fe;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.875rem;
        }
        .status-completed {
            background-color: #15803d;
            color: #dcfce7;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.875rem;
        }
        .status-cancelled {
            background-color: #991b1b;
            color: #fee2e2;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.875rem;
        }
        .booking-details {
            color: #94a3b8;
            font-size: 0.95rem;
            line-height: 1.5;
        }
        .service-tag {
            background-color: #334155;
            color: #e2e8f0;
            padding: 4px 8px;
            border-radius: 4px;
            margin: 2px;
            display: inline-block;
            font-size: 0.875rem;
        }
        .vehicle-info {
            background-color: #334155;
            padding: 10px;
            border-radius: 6px;
            margin: 10px 0;
        }
        </style>
    """, unsafe_allow_html=True)

    if not customer_name:
        customer_name = st.text_input("Enter your name to view bookings", 
                                    placeholder="Enter your full name as used during booking")
    
    if customer_name:
        conn = sqlite3.connect('vehicle_service.db')
        customer_bookings = pd.read_sql_query(
            """
            SELECT * FROM bookings 
            WHERE customer_name=? 
            ORDER BY 
                CASE 
                    WHEN status = 'In Progress' THEN 1
                    WHEN status = 'Pending' THEN 2
                    WHEN status = 'Completed' THEN 3
                    WHEN status = 'Cancelled' THEN 4
                END,
                booking_date DESC
            """, 
            conn, 
            params=(customer_name,)
        )
        conn.close()
        
        if not customer_bookings.empty:
            # Group bookings by status
            active_bookings = customer_bookings[customer_bookings['status'].isin(['Pending', 'In Progress'])]
            completed_bookings = customer_bookings[customer_bookings['status'] == 'Completed']
            cancelled_bookings = customer_bookings[customer_bookings['status'] == 'Cancelled']
            
            st.markdown('<div class="booking-history-container">', unsafe_allow_html=True)
            
            # Display active bookings first
            if not active_bookings.empty:
                st.subheader("🔄 Active Bookings")
                for _, booking in active_bookings.iterrows():
                    display_booking_card(booking)
            
            # Display completed bookings
            if not completed_bookings.empty:
                st.subheader("✅ Completed Services")
                for _, booking in completed_bookings.iterrows():
                    display_booking_card(booking)
            
            # Display cancelled bookings
            if not cancelled_bookings.empty:
                st.subheader("❌ Cancelled Bookings")
                for _, booking in cancelled_bookings.iterrows():
                    display_booking_card(booking)
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("You have no bookings yet. Would you like to [book a service](/book_service)?")
    else:
        st.info("Please enter your name to view your booking history")

def display_booking_card(booking):
    # Convert service items from string to list if it exists
    service_items = booking['service_items'].split(',') if booking['service_items'] else []
    
    # Create the last service info string conditionally
    last_service_info = ""
    if booking["last_service_date"] and booking["last_service_km"]:
        last_service_info = f'<p><strong>Last Service:</strong> {booking["last_service_date"]} ({booking["last_service_km"]} KM)</p>'
    
    st.markdown(f"""
        <div class="booking-card">
            <div class="booking-header">
                <div>
                    <h3 style="color: #e2e8f0; margin: 0;">Booking #{booking['booking_id']}</h3>
                    <p style="color: #94a3b8; margin: 5px 0;">
                        {booking['booking_date']} | {booking['time_slot']}
                    </p>
                </div>
                <span class="status-{booking['status'].lower().replace(' ', '-')}">
                    {booking['status']}
                </span>
            </div>
            
            <div class="vehicle-info">
                <p style="color: #e2e8f0; margin: 0;">
                    🚗 {booking['vehicle_type']} | 
                    📝 {booking['vehicle_number']}
                </p>
            </div>
            
            <div class="booking-details">
                <p><strong>Service Type:</strong> {booking['service_type']}</p>
                
                {f'<div style="margin: 10px 0;"><strong>Service Items:</strong><br/>' + 
                ''.join([f'<span class="service-tag">{item.strip()}</span>' for item in service_items]) + 
                '</div>' if service_items else ''}
                
                {f'<p><strong>Description:</strong><br/>{booking["description"]}</p>' 
                if booking["description"] else ''}
                
                {f'<p><strong>Additional Notes:</strong><br/>{booking["additional_notes"]}</p>'
                if booking["additional_notes"] else ''}
                
                {last_service_info}
            </div>
        </div>
    """, unsafe_allow_html=True)

def get_vehicle_data():
    return {
        "Car": {
            "Categories": [
                "Hatchback",
                "Sedan",
                "SUV",
                "MPV",
                "Electric",
                "Pickup"
            ],
            "Models": {
                "Hatchback": [
                    "Alto", "WagonR", "Swift", "Baleno", "Celerio", "S-Presso", "Ignis",
                    "Tiago", "Altroz", "Punch", "Nano",
                    "i10", "i20", "Grand i10", "Santro",
                    "Jazz", "Brio", "Amaze",
                    "Sonet",
                    "Polo", "Virtus"
                ],
                "Sedan": [
                    "Dzire", "Ciaz", "SX4",
                    "Tigor", "Indigo", "Manza",
                    "Verna", "Aura", "Elantra", "Sonata",
                    "Camry", "Corolla", "Etios",
                    "City", "Civic", "Accord",
                    "Carens",
                    "Vento",
                    "Rapid", "Superb", "Octavia"
                ],
                "SUV": [
                    "Brezza", "Grand Vitara", "Ertiga", "XL6", "Jimny", "Fronx",
                    "Nexon", "Harrier", "Safari", "Gravitas",
                    "XUV700", "XUV300", "Scorpio", "Bolero", "Thar", "XUV400",
                    "Creta", "Venue", "Alcazar", "Tucson", "Kona Electric",
                    "Fortuner", "Urban Cruiser", "Land Cruiser",
                    "WR-V", "Elevate", "CR-V",
                    "Seltos", "Carnival", "EV6",
                    "Taigun", "T-Roc",
                    "Kodiaq", "Karoq",
                    "Hector", "Astor", "Gloster", "Comet"
                ],
                "MPV": [
                    "Eeco", "Omni",
                    "Innova", "Vellfire",
                    "BR-V",
                    "Starex"
                ],
                "Electric": [
                    "eVX",
                    "Nexon EV", "Tigor EV",
                    "e2o", "eVerito",
                    "bZ4X",
                    "ZS EV"
                ],
                "Pickup": [
                    "Bolero Pickup", "Jeeto", "Bolero Maxi Truck"
                ]
            },
            "Brands": [
                "Maruti Suzuki",
                "Tata",
                "Mahindra",
                "Hyundai",
                "Toyota",
                "Honda",
                "Kia",
                "Volkswagen",
                "Skoda",
                "MG"
            ]
        },
        "Motorcycle": {
            "Categories": [
                "Commuter",
                "Sports",
                "Scooter",
                "Adventure",
                "Classic",
                "Cruiser",
                "Modern Classic",
                "Naked",
                "Perak",
                "Bobber"
            ],
            "Models": {
                "Commuter": [
                    "Shine", "Unicorn", "Livo", "SP 125", "CB Shine", "Dream Yuga",
                    "Pulsar 150", "Platina", "CT 100", "Pulsar 125", "Pulsar NS160",
                    "Apache RTR 160", "Sport", "Star City", "Radeon",
                    "FZ", "FZ-S", "FZ-X", "FZ25",
                    "Intruder", "Access 125",
                    "Splendor", "HF Deluxe", "Passion", "Glamour", "Xtreme"
                ],
                "Sports": [
                    "CBR 150R", "CBR 250R", "CBR 650R", "CB300R",
                    "Pulsar 220F", "Dominar 400", "Pulsar NS200", "Pulsar RS200",
                    "Apache RR 310", "Apache RTR 200", "Apache RTR 180",
                    "R15", "MT-15", "MT-03",
                    "Gixxer", "Gixxer SF", "V-Strom 250",
                    "Xtreme 160R", "Karizma", "Xpulse",
                    "S1000RR", "M1000RR"
                ],
                "Scooter": [
                    "Activa", "Dio", "Jazz", "Grazia", "Aviator",
                    "Chetak", "Platina 110",
                    "Jupiter", "NTorq", "Scooty Pep+", "Scooty Zest",
                    "Fascino", "Ray ZR", "Aerox 155",
                    "Maestro Edge", "Pleasure+", "Destini"
                ],
                "Adventure": [
                    "CB200X", "CB500X",
                    "Adventure 400",
                    "Himalayan", "Scram 411",
                    "Adventure 390", "Adventure 250", "390 Adventure",
                    "V-Strom 650",
                    "GS 310", "F850GS"
                ],
                "Classic": [
                    "Classic 350", "Classic 500", "Classic 650",
                    "Jawa", "Jawa 42"
                ],
                "Cruiser": [
                    "Meteor 350", "Thunderbird", "Super Meteor 650"
                ],
                "Modern Classic": [
                    "Interceptor 650", "Continental GT 650"
                ],
                "Naked": [
                    "Duke 125", "Duke 250",
                    "G310R"
                ],
                "Perak": [
                    "Perak"
                ],
                "Bobber": [
                    "42 Bobber"
                ]
            },
            "Brands": [
                "Honda",
                "Bajaj",
                "TVS",
                "Royal Enfield",
                "KTM",
                "Yamaha",
                "Suzuki",
                "Hero",
                "Jawa",
                "BMW"
            ]
        }
    }

# Create car_models and bike_models dictionaries
vehicle_data = get_vehicle_data()
car_models = {}
bike_models = {}

# Populate car_models
for brand in vehicle_data["Car"]["Brands"]:
    car_models[brand] = []
    for category in vehicle_data["Car"]["Categories"]:
        car_models[brand].extend(vehicle_data["Car"]["Models"][category])

# Populate bike_models
for brand in vehicle_data["Motorcycle"]["Brands"]:
    bike_models[brand] = []
    for category in vehicle_data["Motorcycle"]["Categories"]:
        bike_models[brand].extend(vehicle_data["Motorcycle"]["Models"][category])

def search_vehicle(query, vehicle_type=None):
    """Search for vehicles based on query string and optional vehicle type"""
    vehicle_data = get_vehicle_data()
    results = []
    
    # Determine which vehicle types to search
    search_types = [vehicle_type] if vehicle_type else vehicle_data.keys()
    
    for v_type in search_types:
        if v_type not in vehicle_data:
            continue
            
        for brand, categories in vehicle_data[v_type].items():
            for category, models in categories.items():
                for model in models:
                    # Search in brand, category, and model names
                    if (query.lower() in brand.lower() or 
                        query.lower() in category.lower() or 
                        query.lower() in model.lower()):
                        results.append({
                            'type': v_type,
                            'brand': brand,
                            'category': category,
                            'model': model
                        })
    return results

def get_repair_types():
    return {
        "Car": {
            "Engine": [
                "Engine Overhaul",
                "Piston Replacement",
                "Cylinder Head Repair",
                "Timing Belt Replacement",
                "Engine Mount Replacement"
            ],
            "Transmission": [
                "Clutch Replacement",
                "Gearbox Repair",
                "Automatic Transmission Service",
                "Differential Repair",
                "Drive Shaft Replacement"
            ],
            "Brakes": [
                "Brake Pad Replacement",
                "Brake Disc Replacement",
                "Brake Caliper Repair",
                "Brake Line Replacement",
                "ABS System Repair"
            ],
            "Suspension": [
                "Shock Absorber Replacement",
                "Spring Replacement",
                "Control Arm Replacement",
                "Ball Joint Replacement",
                "Wheel Bearing Replacement"
            ],
            "Electrical": [
                "Battery Replacement",
                "Alternator Repair",
                "Starter Motor Replacement",
                "ECU Repair",
                "Wiring Harness Repair"
            ],
            "AC": [
                "AC Compressor Replacement",
                "AC Condenser Repair",
                "AC Evaporator Replacement",
                "AC Gas Refill",
                "AC Control Unit Repair"
            ],
            "Body": [
                "Dent Removal",
                "Paint Work",
                "Panel Replacement",
                "Glass Replacement",
                "Bumper Repair"
            ]
        },
        "Motorcycle": {
            "Engine": [
                "Engine Overhaul",
                "Piston Replacement",
                "Cylinder Head Repair",
                "Valve Adjustment",
                "Engine Mount Replacement"
            ],
            "Transmission": [
                "Clutch Replacement",
                "Gearbox Repair",
                "Chain & Sprocket Replacement",
                "Primary Drive Repair",
                "Gear Shifter Repair"
            ],
            "Brakes": [
                "Brake Pad Replacement",
                "Brake Disc Replacement",
                "Brake Caliper Repair",
                "Brake Line Replacement",
                "ABS System Repair"
            ],
            "Suspension": [
                "Front Fork Repair",
                "Rear Shock Replacement",
                "Swing Arm Repair",
                "Wheel Bearing Replacement",
                "Steering Head Bearing Replacement"
            ],
            "Electrical": [
                "Battery Replacement",
                "Alternator Repair",
                "Starter Motor Replacement",
                "ECU Repair",
                "Wiring Harness Repair"
            ],
            "Body": [
                "Fairing Repair",
                "Paint Work",
                "Panel Replacement",
                "Mirror Replacement",
                "Seat Repair"
            ]
        }
    }

def show_initial_booking_form():
    st.header("Book a Service")
    with st.form("initial_booking_form"):
        customer_name = st.text_input("Your Name")
        vehicle_number = st.text_input("Vehicle Number")
        
        # Vehicle Type Selection
        vehicle_type = st.selectbox("Vehicle Type", ["Car", "Motorcycle"])
        
        # Last service details
        col1, col2 = st.columns(2)
        with col1:
            last_service_date = st.date_input("Last Service Date (if any)", value=None)
        with col2:
            last_service_km = st.number_input("Odometer Reading (KM)", min_value=0)
        
        submit_initial = st.form_submit_button("Continue to Service Selection")
        
        if submit_initial and customer_name and vehicle_number:
            # Store the initial details in session state
            st.session_state.booking_details = {
                'customer_name': customer_name,
                'vehicle_number': vehicle_number,
                'vehicle_type': vehicle_type,
                'last_service_date': last_service_date,
                'last_service_km': last_service_km
            }
            st.session_state.current_page = 'car_service' if vehicle_type == "Car" else 'bike_service'
            st.rerun()

def show_car_service_form():
    st.header("Car Service Booking")
    
    # Get booking details from session state
    booking_details = st.session_state.get('booking_details', {})
    
    # Vehicle Brand and Model Selection
    vehicle_brand = st.selectbox("Select Car Brand", sorted(car_models.keys()))
    vehicle_model = st.selectbox("Select Car Model", sorted(car_models[vehicle_brand]))
    
    # Service Type Selection
    service_type = st.selectbox("Service Type", ["Regular Maintenance", "Repair", "Washing"])
    
    # Auto-assist feature for service recommendations
    if st.button("Get AI Service Recommendations"):
        with st.spinner("Getting personalized recommendations..."):
            # Get service history from database
            conn = sqlite3.connect('vehicle_service.db')
            service_history = pd.read_sql_query(
                "SELECT * FROM bookings WHERE vehicle_type='Car' AND vehicle_number=?",
                conn,
                params=(booking_details.get('vehicle_number', ''),)
            ).to_dict('records')
            conn.close()
            
            recommendations = get_service_recommendations(
                "Car",
                f"{vehicle_brand} {vehicle_model}",
                service_history
            )
            st.info("AI Service Recommendations:")
            st.write(recommendations)
    
    # Service Items Selection based on service type
    service_items = []
    if service_type == "Regular Maintenance":
        service_items = st.multiselect(
            "Select Maintenance Items",
            ["Engine Oil Change", "Oil Filter Replacement", "Air Filter Cleaning", 
             "Brake Check", "Wheel Alignment", "Battery Check", "Tire Rotation"]
        )
    elif service_type == "Repair":
        # Add symptoms input for AI diagnosis
        symptoms = st.text_area("Describe the issues or symptoms you're experiencing")
        if symptoms:
            if st.button("Get AI Diagnosis"):
                with st.spinner("Analyzing symptoms..."):
                    vehicle_details = {
                        "brand": vehicle_brand,
                        "model": vehicle_model,
                        "last_service": booking_details.get('last_service_date'),
                        "last_service_km": booking_details.get('last_service_km')
                    }
                    diagnosis = get_diagnostic_insights(symptoms, vehicle_details)
                    st.info("AI Diagnostic Insights:")
                    st.write(diagnosis)
        
        service_items = st.multiselect(
            "Select Repair Items",
            ["Engine Repair", "Transmission Service", "Brake System Repair",
             "Suspension Work", "Electrical Systems", "AC Service & Repair"]
        )
    elif service_type == "Washing":
        service_items = st.multiselect(
            "Select Washing Package",
            ["Basic Wash", "Premium Wash", "Deep Cleaning"]
        )
    
    # Time Slot Selection
    time_slot = st.selectbox("Preferred Time Slot", 
                           ["09:00 AM - 11:00 AM", 
                            "11:00 AM - 01:00 PM",
                            "02:00 PM - 04:00 PM",
                            "04:00 PM - 06:00 PM"])
    
    additional_notes = st.text_area("Additional Notes (Optional)")
    
    # Auto-assist for additional notes
    if additional_notes:
        if st.button("Get AI Suggestions"):
            with st.spinner("Analyzing your notes..."):
                context = {
                    "vehicle": f"{vehicle_brand} {vehicle_model}",
                    "service_type": service_type,
                    "selected_items": service_items
                }
                suggestions = get_auto_assist_response(additional_notes, context)
                st.info("AI Suggestions:")
                st.write(suggestions)
    
    # Booking form
    with st.form("car_booking_form"):
        submit_booking = st.form_submit_button("Book Service")
        
        if submit_booking:
            try:
                # Prepare service description
                service_description = f"Vehicle: {vehicle_brand} {vehicle_model}\n"
                if booking_details.get('last_service_date'):
                    service_description += f"Last Service: {booking_details['last_service_date']}, {booking_details['last_service_km']} KM\n"
                if service_items:
                    service_description += f"Service Items: {', '.join(service_items)}\n"
                if additional_notes:
                    service_description += f"Additional Notes: {additional_notes}"
                
                conn = sqlite3.connect('vehicle_service.db')
                c = conn.cursor()
                
                # Insert booking into database
                c.execute("""
                    INSERT INTO bookings (
                        booking_id, customer_name, vehicle_type, vehicle_number,
                        service_type, booking_date, time_slot, status, description,
                        last_service_date, last_service_km, service_items, additional_notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(uuid.uuid4()),
                    booking_details['customer_name'],
                    'Car',
                    booking_details['vehicle_number'],
                    service_type,
                    datetime.now().date(),
                    time_slot,
                    'Pending',
                    service_description,
                    booking_details.get('last_service_date'),
                    booking_details.get('last_service_km'),
                    ','.join(service_items) if service_items else None,
                    additional_notes
                ))
                
                conn.commit()
                conn.close()
                
                st.success("Service booked successfully!")
                st.session_state.current_page = 'home'
                st.rerun()
                
            except Exception as e:
                st.error(f"Error booking service: {str(e)}")

def show_bike_service_form():
    st.header("Motorcycle Service Booking")
    
    # Get booking details from session state
    booking_details = st.session_state.get('booking_details', {})
    
    # Vehicle Brand and Model Selection
    vehicle_brand = st.selectbox("Select Bike Brand", sorted(bike_models.keys()))
    vehicle_model = st.selectbox("Select Bike Model", sorted(bike_models[vehicle_brand]))
    
    # Service Type Selection
    service_type = st.selectbox("Service Type", ["Regular Maintenance", "Repair", "Washing"])
    
    # Auto-assist feature for service recommendations
    if st.button("Get AI Service Recommendations"):
        with st.spinner("Getting personalized recommendations..."):
            # Get service history from database
            conn = sqlite3.connect('vehicle_service.db')
            service_history = pd.read_sql_query(
                "SELECT * FROM bookings WHERE vehicle_type='Motorcycle' AND vehicle_number=?",
                conn,
                params=(booking_details.get('vehicle_number', ''),)
            ).to_dict('records')
            conn.close()
            
            recommendations = get_service_recommendations(
                "Motorcycle",
                f"{vehicle_brand} {vehicle_model}",
                service_history
            )
            st.info("AI Service Recommendations:")
            st.write(recommendations)
    
    # Service Items Selection based on service type
    service_items = []
    if service_type == "Regular Maintenance":
        service_items = st.multiselect(
            "Select Maintenance Items",
            ["Engine Oil Change", "Oil Filter Replacement", "Air Filter Cleaning",
             "Chain Cleaning", "Brake Adjustment", "Battery Check", "Tire Pressure Check"]
        )
    elif service_type == "Repair":
        # Add symptoms input for AI diagnosis
        symptoms = st.text_area("Describe the issues or symptoms you're experiencing")
        if symptoms:
            if st.button("Get AI Diagnosis"):
                with st.spinner("Analyzing symptoms..."):
                    vehicle_details = {
                        "brand": vehicle_brand,
                        "model": vehicle_model,
                        "last_service": booking_details.get('last_service_date'),
                        "last_service_km": booking_details.get('last_service_km')
                    }
                    diagnosis = get_diagnostic_insights(symptoms, vehicle_details)
                    st.info("AI Diagnostic Insights:")
                    st.write(diagnosis)
        
        service_items = st.multiselect(
            "Select Repair Items",
            ["Engine Work", "Chain & Sprocket Replacement", "Clutch Repair",
             "Brake System Service", "Electrical Repairs", "Tire Services"]
        )
    elif service_type == "Washing":
        service_items = st.multiselect(
            "Select Washing Package",
            ["Basic Wash", "Premium Wash", "Deep Cleaning"]
        )
    
    # Time Slot Selection
    time_slot = st.selectbox("Preferred Time Slot", 
                           ["09:00 AM - 11:00 AM", 
                            "11:00 AM - 01:00 PM",
                            "02:00 PM - 04:00 PM",
                            "04:00 PM - 06:00 PM"])
    
    additional_notes = st.text_area("Additional Notes (Optional)")
    
    # Auto-assist for additional notes
    if additional_notes:
        if st.button("Get AI Suggestions"):
            with st.spinner("Analyzing your notes..."):
                context = {
                    "vehicle": f"{vehicle_brand} {vehicle_model}",
                    "service_type": service_type,
                    "selected_items": service_items
                }
                suggestions = get_auto_assist_response(additional_notes, context)
                st.info("AI Suggestions:")
                st.write(suggestions)
    
    # Booking form
    with st.form("bike_booking_form"):
        submit_booking = st.form_submit_button("Book Service")
        
        if submit_booking:
            try:
                # Prepare service description
                service_description = f"Vehicle: {vehicle_brand} {vehicle_model}\n"
                if booking_details.get('last_service_date'):
                    service_description += f"Last Service: {booking_details['last_service_date']}, {booking_details['last_service_km']} KM\n"
                if service_items:
                    service_description += f"Service Items: {', '.join(service_items)}\n"
                if additional_notes:
                    service_description += f"Additional Notes: {additional_notes}"
                
                conn = sqlite3.connect('vehicle_service.db')
                c = conn.cursor()
                
                # Insert booking into database
                c.execute("""
                    INSERT INTO bookings (
                        booking_id, customer_name, vehicle_type, vehicle_number,
                        service_type, booking_date, time_slot, status, description,
                        last_service_date, last_service_km, service_items, additional_notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(uuid.uuid4()),
                    booking_details['customer_name'],
                    'Motorcycle',
                    booking_details['vehicle_number'],
                    service_type,
                    datetime.now().date(),
                    time_slot,
                    'Pending',
                    service_description,
                    booking_details.get('last_service_date'),
                    booking_details.get('last_service_km'),
                    ','.join(service_items) if service_items else None,
                    additional_notes
                ))
                
                conn.commit()
                conn.close()
                
                st.success("Service booked successfully!")
                st.session_state.current_page = 'home'
                st.rerun()
                
            except Exception as e:
                st.error(f"Error booking service: {str(e)}")

def show_customer_dashboard():
    # Add custom font
    st.markdown("""
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)
    
    # Create columns for logo and title
    col1, col2 = st.columns([1, 4])
    
    with col1:
        # Add logo image
        st.image("static/images/Logo.png", width=250)

    
    with col2:
        st.markdown("""
            <div class="title-container">
                <h1 class="main-title">AUTO ASSIST AND BOOKING SYSTEM</h1>
            </div>
        """, unsafe_allow_html=True)
    
    # Add logout button in the top right
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()
    
    # Initialize the current page in session state if not exists
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    
    # Back button for all pages except home
    if st.session_state.current_page != 'home':
        if st.button('🏠 Back to Home', use_container_width=True):
            st.session_state.current_page = 'home'
            st.rerun()
    
    # Show the appropriate page based on current_page
    if st.session_state.current_page == 'home':
        # Welcome message
        st.markdown("### Welcome to AUTO ASSIST AND BOOKING SYSTEM")
        st.write("Select a service to proceed:")
        
        # Create three rows of cards with 2 cards each
        row1_col1, row1_col2 = st.columns(2)
        row2_col1, row2_col2 = st.columns(2)
        row3_col1, row3_col2 = st.columns(2)
        
        with row1_col1:
            st.markdown("""
            <div class="service-card">
                <img src="https://www.holidaymonk.com/wp-content/uploads/2022/05/Car-Rental-in-India.webp" style="width: 100%; height: 200px; object-fit: cover">
                <h3>📝 Book Service</h3>
                <p>Schedule a new service appointment for your vehicle</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Book Service", key="book_service", use_container_width=True):
                st.session_state.current_page = 'book_service'
                st.rerun()
        
        with row1_col2:
            st.markdown("""
            <div class="service-card">
                <img src="https://www.shutterstock.com/image-vector/black-color-analog-flip-board-260nw-2278609195.jpg" style="width: 100%; height: 200px; object-fit: cover">
                <h3>📋 Booking History</h3>
                <p>View your past and upcoming service bookings</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("View History", key="booking_history", use_container_width=True):
                st.session_state.current_page = 'booking_history'
                st.rerun()
        
        with row2_col1:
            st.markdown("""
            <div class="service-card">
                <img src="https://t4.ftcdn.net/jpg/07/81/64/13/360_F_781641329_zKW0q4jlSJXtyAnX5hqCMhW1BgC0ygQe.jpg" style="width: 100%; height: 150px; object-fit: cover; ">
                <h3>🔍 Service Status</h3>
                <p>Track the status of your current service</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Check Status", key="service_status", use_container_width=True):
                st.session_state.current_page = 'service_status'
                st.rerun()
        
        with row2_col2:
            st.markdown("""
            <div class="service-card">
                <img src="https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=500" style="width: 100%; height: 150px; object-fit: cover; border-radius: 10px 10px 0 0;">
                <h3>💰 Cost Calculator</h3>
                <p>Estimate the cost of your service</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Calculate Cost", key="cost_calculator", use_container_width=True):
                st.session_state.current_page = 'cost_calculator'
                st.rerun()
        
        with row3_col1:
            st.markdown("""
            <div class="service-card">
                <img src="https://imageio.forbes.com/specials-images/imageserve/656e010c1eacbfe7918ca848/AI-Customer-Service/960x0.png?format=png&width=960" style="width: 100%; height: 150px; object-fit: cover; border-radius: 10px 10px 0 0;">
                <h3>💬 AI Chat Support</h3>
                <p>Get instant help from our AI chatbot</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Start Chat", key="chat_support", use_container_width=True):
                st.session_state.current_page = 'chat_support'
                st.rerun()
        
        with row3_col2:
            st.markdown("""
            <div class="service-card">
                <img src="https://media.istockphoto.com/id/1357693643/photo/master-repairman-repairing-motorcycle-with-wrench-closeup.jpg?s=612x612&w=0&k=20&c=N6r16Hzkm8qrqvu-Nz12Ne-gcqGxOqTU7Jd4iCmot_E=" style="width: 100%; height: 150px; object-fit: cover; border-radius: 10px 10px 0 0;">
                <h3>ℹ️ Service Information</h3>
                <p>View our service packages and offerings</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("View Services", key="service_info", use_container_width=True):
                st.session_state.current_page = 'service_info'
                st.rerun()
        
        # Display service highlights at the bottom
        st.markdown("---")
        st.markdown("## Our Premium Services")
        st.markdown("Experience excellence in vehicle care with our comprehensive service packages")
        
        # Create tabs for different service categories
        service_tabs = st.tabs(["🚗 Car Services", "🏍️ Bike Services", "💧 Washing Packages"])
        
        with service_tabs[0]:  # Car Services
            st.markdown("### Car Maintenance & Services")
            
            # Add image column layout
            img_col, content_col = st.columns([1, 2])
            with img_col:
                st.image("https://www.shutterstock.com/image-photo/portrait-shot-handsome-mechanic-working-600nw-1711144648.jpg",
                        caption="Professional Car Services",
                        use_container_width=True)
                st.image("https://media.istockphoto.com/id/1350239751/photo/car-diagnostic-service-and-electronics-repair.jpg?s=612x612&w=0&k=20&c=6xSgzMp9KJJ8lN0hC1UcuqXuuZMLNFCgCkcju-Q0BTU=",
                        caption="Engine Diagnostics",
                        use_container_width=True)
                st.image("https://media.istockphoto.com/id/522394158/photo/car-service-procedure.jpg?s=612x612&w=0&k=20&c=SXPyg7yMw0Uc4LuI59lchMouvjJ3z6r5oNKO7mdnHCc=",
                        caption="Brake Service",
                        use_container_width=True)
            
            with content_col:
                # Regular Maintenance
                with st.expander("Regular Maintenance", expanded=True):
                    st.markdown("""
                    #### Basic Service Package
                    - Engine Oil Change
                    - Oil Filter Replacement
                    - Air Filter Cleaning
                    - General Inspection
                    """)
                    st.markdown("""<div style='background-color: #1e293b; padding: 5px 15px; border-radius: 15px; 
                        text-align: center; width: fit-content; margin: 5px 0; border: 1px solid #334155; 
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                        <p style='color: #e2e8f0; margin: 0; font-size: 15px;'>Starting at <span style='color: #60a5fa; font-weight: 600;'>₹2,000</span></p>
                    </div>""", unsafe_allow_html=True)
                    
                    st.markdown("""
                    #### Standard Service Package
                    - All Basic Service Items
                    - Brake System Check
                    - Wheel Alignment
                    - Battery Check
                    - Tire Rotation
                    """)
                    st.markdown("""<div style='background-color: #1e293b; padding: 5px 15px; border-radius: 15px; 
                        text-align: center; width: fit-content; margin: 5px 0; border: 1px solid #334155; 
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                        <p style='color: #e2e8f0; margin: 0; font-size: 15px;'>Starting at <span style='color: #60a5fa; font-weight: 600;'>₹4,000</span></p>
                    </div>""", unsafe_allow_html=True)
                    
                    st.markdown("""
                    #### Premium Service Package
                    - All Standard Service Items
                    - Complete Diagnostics
                    - Detailed Inspection
                    - Interior Cleaning
                    - Performance Check
                    """)
                    st.markdown("""<div style='background-color: #1e293b; padding: 5px 15px; border-radius: 15px; 
                        text-align: center; width: fit-content; margin: 5px 0; border: 1px solid #334155; 
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                        <p style='color: #e2e8f0; margin: 0; font-size: 15px;'>Starting at <span style='color: #60a5fa; font-weight: 600;'>₹6,000</span></p>
                    </div>""", unsafe_allow_html=True)
                
                # Repair Services
                with st.expander("Repair Services", expanded=True):
                    st.markdown("""
                    #### Engine & Transmission
                    - Engine Diagnostics
                    - Engine Overhaul
                    - Transmission Service
                    - Clutch Replacement
                    """)
                    
                    st.markdown("""
                    #### Electrical & AC
                    - Electrical System Repair
                    - AC Service & Repair
                    - Battery Replacement
                    - Wiring Harness Repair
                    """)
                    
                    st.markdown("""
                    #### Brakes & Suspension
                    - Brake System Service
                    - Suspension Work
                    - Wheel Alignment
                    - Shock Absorber Replacement
                    """)
                
                # Body Work
                with st.expander("Body Work", expanded=True):
                    st.markdown("""
                    #### Paint & Dent Work
                    - Paint Work
                    - Dent Removal
                    - Panel Replacement
                    - Glass Repair
                    """)
                    
                    st.markdown("""
                    #### Interior Work
                    - Upholstery Repair
                    - Dashboard Repair
                    - Carpet Replacement
                    - Interior Detailing
                    """)
        
        with service_tabs[1]:  # Bike Services
            st.markdown("### Bike Maintenance & Services")
            
            # Add image column layout
            img_col, content_col = st.columns([1, 2])
            with img_col:
                st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQtr_rx-dAiQPgS0XwEq-0_CuLy7Uahslx-ng&s",
                        caption="Professional Bike Services",
                        use_container_width=True)
                st.image("https://wallup.net/wp-content/uploads/2019/09/744652-thunderbike-custom-chopper-bobber-bike-1tbike-motorbike-motorcycle-tuning.jpg",
                        caption="Performance Tuning",
                        use_container_width=True)
                st.image("https://media.istockphoto.com/id/1954221485/photo/repairman-checking-scheme-of-motorcycle.jpg?s=612x612&w=0&k=20&c=w9o4m-YmpJalFxi0dGL3HDUwTacqt7uSQaxAtRIb3_k=",
                        caption="Bike Maintenance",
                        use_container_width=True)
            
            with content_col:
                # Periodic Services
                with st.expander("Periodic Services", expanded=True):
                    st.markdown("""
                    #### Basic Service Package
                    - Engine Oil Change
                    - Chain Lubrication
                    - Basic Inspection
                    - Tire Pressure Check
                    """)
                    st.markdown("""<div style='background-color: #1e293b; padding: 5px 15px; border-radius: 15px; 
                        text-align: center; width: fit-content; margin: 5px 0; border: 1px solid #334155; 
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                        <p style='color: #e2e8f0; margin: 0; font-size: 15px;'>Starting at <span style='color: #60a5fa; font-weight: 600;'>₹1,000</span></p>
                    </div>""", unsafe_allow_html=True)
                    
                    st.markdown("""
                    #### Standard Service Package
                    - All Basic Service Items
                    - Air Filter Cleaning
                    - Brake Adjustment
                    - Chain Adjustment
                    - Battery Check
                    """)
                    st.markdown("""<div style='background-color: #1e293b; padding: 5px 15px; border-radius: 15px; 
                        text-align: center; width: fit-content; margin: 5px 0; border: 1px solid #334155; 
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                        <p style='color: #e2e8f0; margin: 0; font-size: 15px;'>Starting at <span style='color: #60a5fa; font-weight: 600;'>₹2,000</span></p>
                    </div>""", unsafe_allow_html=True)
                    
                    st.markdown("""
                    #### Premium Service Package
                    - All Standard Service Items
                    - Complete Diagnostics
                    - Deep Cleaning
                    - Performance Tuning
                    - Carburetor Tuning
                    """)
                    st.markdown("""<div style='background-color: #1e293b; padding: 5px 15px; border-radius: 15px; 
                        text-align: center; width: fit-content; margin: 5px 0; border: 1px solid #334155; 
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                        <p style='color: #e2e8f0; margin: 0; font-size: 15px;'>Starting at <span style='color: #60a5fa; font-weight: 600;'>₹3,000</span></p>
                    </div>""", unsafe_allow_html=True)
                
                # Repairs & Parts
                with st.expander("Repairs & Parts", expanded=True):
                    st.markdown("""
                    #### Engine & Transmission
                    - Engine Overhaul
                    - Parts Replacement
                    - Chain & Sprocket Set
                    - Clutch Repair
                    """)
                    
                    st.markdown("""
                    #### Electrical & Performance
                    - Electrical Work
                    - Performance Tuning
                    - ECU Remapping
                    - Exhaust System
                    """)
                
                # Customization
                with st.expander("Customization", expanded=True):
                    st.markdown("""
                    #### Performance Upgrades
                    - Performance Kits
                    - Exhaust Systems
                    - Air Filters
                    - ECU Tuning
                    """)
                    
                    st.markdown("""
                    #### Cosmetic Modifications
                    - Paint Jobs
                    - Accessory Installation
                    - LED Kits
                    - Custom Graphics
                    """)
        
        with service_tabs[2]:  # Washing Packages
            st.markdown("### Washing & Detailing Services")
            
            # Add image column layout
            img_col, content_col = st.columns([1, 2])
            with img_col:
                st.image("https://5.imimg.com/data5/SELLER/Default/2022/2/WL/EW/HO/71120205/5-shampoo-copy-jpg.jpg",
                        caption="Professional Washing Services",
                        use_container_width=True)
                st.image("https://cavallistables.com/wp-content/uploads/2020/09/professional-car-detailing-1200x675.jpg",
                        caption="Interior Detailing",
                        use_container_width=True)
                st.image("https://media.istockphoto.com/id/958873882/photo/repair.jpg?s=612x612&w=0&k=20&c=ZWNKfZAKTr16vQjOE9VcXkToQaf3TzzV0eD-GJVCI5U=",
                        caption="Exterior Polishing",
                        use_container_width=True)
            
            with content_col:
                # Car Wash Packages
                with st.expander("Car Wash Packages", expanded=True):
                    st.markdown("""
                    #### Basic Wash - ₹500
                    - Exterior Wash
                    - Tire Cleaning
                    - Basic Interior
                    - Window Cleaning
                    """)
                    st.markdown("""<div style='background-color: #1e293b; padding: 5px 15px; border-radius: 15px; 
                        text-align: center; width: fit-content; margin: 5px 0; border: 1px solid #334155; 
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                        <p style='color: #e2e8f0; margin: 0; font-size: 15px;'><span style='color: #60a5fa; font-weight: 600;'>₹500</span></p>
                    </div>""", unsafe_allow_html=True)
                    
                    st.markdown("""
                    #### Premium Wash
                    - All Basic Services
                    - Interior Detailing
                    - Dashboard Polishing
                    - Seat Cleaning
                    - Carpet Cleaning
                    - Waxing & Polishing
                    """)
                    st.markdown("""<div style='background-color: #1e293b; padding: 5px 15px; border-radius: 15px; 
                        text-align: center; width: fit-content; margin: 5px 0; border: 1px solid #334155; 
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                        <p style='color: #e2e8f0; margin: 0; font-size: 15px;'><span style='color: #60a5fa; font-weight: 600;'>₹1,000</span></p>
                    </div>""", unsafe_allow_html=True)
                    
                    st.markdown("""
                    #### Deep Cleaning
                    - All Premium Services
                    - Engine Bay Cleaning
                    - Underbody Wash
                    - Ceramic Coating
                    - Leather Treatment
                    - Odor Removal
                    """)
                    st.markdown("""<div style='background-color: #1e293b; padding: 5px 15px; border-radius: 15px; 
                        text-align: center; width: fit-content; margin: 5px 0; border: 1px solid #334155; 
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                        <p style='color: #e2e8f0; margin: 0; font-size: 15px;'><span style='color: #60a5fa; font-weight: 600;'>₹2,000</span></p>
                    </div>""", unsafe_allow_html=True)
                
                # Bike Wash Packages
                with st.expander("Bike Wash Packages", expanded=True):
                    st.markdown("""
                    #### Basic Wash - ₹200
                    - Exterior Wash
                    - Chain Cleaning
                    - Basic Inspection
                    - Tire Cleaning
                    """)
                    
                    st.markdown("""
                    #### Premium Wash - ₹500
                    - All Basic Services
                    - Deep Cleaning
                    - Polishing
                    - Chain Lubrication
                    - Tire Dressing
                    """)
                    
                    st.markdown("""
                    #### Deep Cleaning - ₹1,000
                    - All Premium Services
                    - Engine Cleaning
                    - Metal Polishing
                    - Ceramic Coating
                    - Paint Protection
                    """)

    elif st.session_state.current_page == 'book_service':
        show_initial_booking_form()
    
    elif st.session_state.current_page == 'car_service':
        show_car_service_form()
    
    elif st.session_state.current_page == 'bike_service':
        show_bike_service_form()
    
    elif st.session_state.current_page == 'booking_history':
        show_booking_history(st.session_state.get('customer_name', None))
    
    elif st.session_state.current_page == 'service_status':
        show_service_status()
    
    elif st.session_state.current_page == 'cost_calculator':
        show_service_calculator()
    
    elif st.session_state.current_page == 'chat_support':
        show_chatbot()
    
    elif st.session_state.current_page == 'service_info':
        st.header("Service Information")
        
        # Add custom CSS for service cards and animations
        st.markdown("""
        <style>
        /* Toggle Button Styles */
        div[data-testid="stRadio"] > div {
            display: flex;
            justify-content: center;
            gap: 1rem;
            padding: 0.5rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 50px;
            margin: 1rem 0;
        }
        div[data-testid="stRadio"] > div > label {
            padding: 0.75rem 2rem !important;
            border-radius: 25px !important;
            background: transparent !important;
            color: #60a5fa !important;
            font-weight: 600 !important;
            border: 2px solid #60a5fa !important;
            transition: all 0.3s ease !important;
            cursor: pointer !important;
            margin: 0 !important;
            min-width: 150px !important;
            text-align: center !important;
        }
        div[data-testid="stRadio"] > div > label:hover {
            background: rgba(96, 165, 250, 0.1) !important;
            transform: translateY(-2px) !important;
        }
        div[data-testid="stRadio"] > div > label[data-checked="true"] {
            background: #60a5fa !important;
            color: white !important;
            box-shadow: 0 4px 12px rgba(96, 165, 250, 0.3) !important;
        }
        </style>
        """, unsafe_allow_html=True)

        # Vehicle Type Toggle
        vehicle_type = st.radio(
            "Select Vehicle Type",
            ["Car Services", "Bike Services"],
            horizontal=True,
            label_visibility="collapsed"
        )

        if vehicle_type == "Car Services":
            st.subheader("🚗 Car Services")
            car_services_tab1, car_services_tab2, car_services_tab3 = st.tabs(["Regular Maintenance", "Repairs", "Washing Services"])
            
            with car_services_tab1:
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown("""
                    <div class="service-card">
                        <div class="service-header">
                            <h3>Basic Service Package</h3>
                            <span class="service-badge">Most Popular</span>
                        </div>
                        <div class="service-price">Starting at ₹2,000</div>
                        <div class="service-features">
                            <ul>
                                <li>Engine Oil Change with Premium Oil</li>
                                <li>Oil Filter Replacement</li>
                                <li>Comprehensive General Inspection</li>
                                <li>Battery Health Check</li>
                                <li>Tire Pressure & Condition Check</li>
                                <li>Basic Fluid Level Check</li>
                            </ul>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div class="service-card">
                        <div class="service-header">
                            <h3>Standard Service Package</h3>
                            <span class="service-badge">Recommended</span>
                        </div>
                        <div class="service-price">Starting at ₹4,000</div>
                        <div class="service-features">
                            <ul>
                                <li>All Basic Service Items</li>
                                <li>Air Filter Cleaning & Replacement</li>
                                <li>Complete Brake System Check</li>
                                <li>Precision Wheel Alignment</li>
                                <li>Comprehensive Fluid Level Check</li>
                                <li>Belt & Hose Inspection</li>
                                <li>Exhaust System Check</li>
                            </ul>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div class="service-card">
                        <div class="service-header">
                            <h3>Premium Service Package</h3>
                            <span class="service-badge">Best Value</span>
                        </div>
                        <div class="service-price">Starting at ₹6,000</div>
                        <div class="service-features">
                            <ul>
                                <li>All Standard Service Items</li>
                                <li>Advanced Computer Diagnostics</li>
                                <li>Detailed 50-Point Inspection</li>
                                <li>Professional Interior Cleaning</li>
                                <li>Performance Optimization</li>
                                <li>Complete AC System Service</li>
                                <li>Fuel System Cleaning</li>
                                <li>Transmission Fluid Check</li>
                            </ul>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.image("https://images.unsplash.com/photo-1580273916550-e323be2ae537?w=500", caption="Professional Car Service", use_column_width=True)
                    st.image("https://images.unsplash.com/photo-1607860108855-64acf2078ed9?w=500", caption="Engine Maintenance", use_column_width=True)
                    st.image("https://images.unsplash.com/photo-1607860108855-64acf2078ed9?w=500", caption="Premium Service", use_column_width=True)
            
            with car_services_tab2:
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown("""
                    <div class="service-card">
                        <h3>Engine & Transmission</h3>
                        <div class="service-features">
                            <ul>
                                <li>Advanced Engine Diagnostics & Repair</li>
                                <li>Complete Engine Overhaul</li>
                                <li>Transmission Service & Repair</li>
                                <li>Clutch System Replacement</li>
                                <li>Timing Belt & Chain Service</li>
                                <li>Engine Mount Replacement</li>
                            </ul>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div class="service-card">
                        <h3>Electrical & AC</h3>
                        <div class="service-features">
                            <ul>
                                <li>Complete Electrical System Repair</li>
                                <li>AC System Service & Repair</li>
                                <li>Battery & Charging System Service</li>
                                <li>Wiring Harness Repair</li>
                                <li>Alternator & Starter Service</li>
                                <li>ECU Diagnostics & Repair</li>
                            </ul>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div class="service-card">
                        <h3>Brakes & Suspension</h3>
                        <div class="service-features">
                            <ul>
                                <li>Complete Brake System Service</li>
                                <li>Advanced Suspension Work</li>
                                <li>Precision Wheel Alignment</li>
                                <li>Shock Absorber Replacement</li>
                                <li>Steering System Service</li>
                                <li>Brake Fluid Flush</li>
                            </ul>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.image("https://images.unsplash.com/photo-1607860108855-64acf2078ed9?w=500", caption="Engine Repair", use_column_width=True)
                    st.image("https://images.unsplash.com/photo-1607860108855-64acf2078ed9?w=500", caption="Electrical System", use_column_width=True)
                    st.image("https://images.unsplash.com/photo-1607860108855-64acf2078ed9?w=500", caption="Brake Service", use_column_width=True)
            
            with car_services_tab3:
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown("""
                    <div class="service-card">
                        <h3>Basic Wash</h3>
                        <div class="service-price">₹500</div>
                        <div class="service-features">
                            <ul>
                                <li>Exterior Hand Wash</li>
                                <li>Window Cleaning</li>
                                <li>Tire & Wheel Cleaning</li>
                                <li>Basic Interior Vacuum</li>
                                <li>Dashboard Wipe</li>
                            </ul>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div class="service-card">
                        <h3>Premium Wash</h3>
                        <div class="service-price">₹1,000</div>
                        <div class="service-features">
                            <ul>
                                <li>All Basic Wash Items</li>
                                <li>Interior Deep Cleaning</li>
                                <li>Dashboard & Console Polish</li>
                                <li>Leather Seat Cleaning</li>
                                <li>Air Freshener</li>
                                <li>Door Jamb Cleaning</li>
                            </ul>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div class="service-card">
                        <h3>Deep Cleaning</h3>
                        <div class="service-price">₹2,000</div>
                        <div class="service-features">
                            <ul>
                                <li>All Premium Wash Items</li>
                                <li>Engine Bay Cleaning</li>
                                <li>Paint Protection Treatment</li>
                                <li>Professional Waxing</li>
                                <li>Stain Removal</li>
                                <li>Odor Treatment</li>
                                <li>Interior Sanitization</li>
                            </ul>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.image("https://images.unsplash.com/photo-1607860108855-64acf2078ed9?w=500", caption="Basic Wash", use_column_width=True)
                    st.image("https://images.unsplash.com/photo-1607860108855-64acf2078ed9?w=500", caption="Premium Wash", use_column_width=True)
                    st.image("https://images.unsplash.com/photo-1607860108855-64acf2078ed9?w=500", caption="Deep Cleaning", use_column_width=True)

        else:  # Bike Services
            st.subheader("🏍️ Bike Services")
            bike_services_tab1, bike_services_tab2, bike_services_tab3 = st.tabs(["Regular Maintenance", "Repairs", "Washing Services"])
            
            with bike_services_tab1:
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown("""
                    <div class="service-card">
                        <div class="service-header">
                            <h3>Basic Service Package</h3>
                            <span class="service-badge">Most Popular</span>
                        </div>
                        <div class="service-price">Starting at ₹1,000</div>
                        <div class="service-features">
                            <ul>
                                <li>Engine Oil Change</li>
                                <li>Oil Filter Replacement</li>
                                <li>Chain Cleaning & Lubrication</li>
                                <li>Basic Inspection</li>
                                <li>Tire Pressure Check</li>
                                <li>Battery Check</li>
                            </ul>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div class="service-card">
                        <div class="service-header">
                            <h3>Standard Service Package</h3>
                            <span class="service-badge">Recommended</span>
                        </div>
                        <div class="service-price">Starting at ₹2,000</div>
                        <div class="service-features">
                            <ul>
                                <li>All Basic Service Items</li>
                                <li>Air Filter Cleaning</li>
                                <li>Brake Adjustment</li>
                                <li>Carburetor Tuning</li>
                                <li>Battery Check</li>
                                <li>Spark Plug Replacement</li>
                                <li>Chain Tension Check</li>
                            </ul>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div class="service-card">
                        <div class="service-header">
                            <h3>Premium Service Package</h3>
                            <span class="service-badge">Best Value</span>
                        </div>
                        <div class="service-price">Starting at ₹3,000</div>
                        <div class="service-features">
                            <ul>
                                <li>All Standard Service Items</li>
                                <li>Complete Diagnostics</li>
                                <li>Detailed Inspection</li>
                                <li>Performance Tuning</li>
                                <li>Electrical System Check</li>
                                <li>Fuel System Cleaning</li>
                                <li>Valve Clearance Check</li>
                            </ul>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.image("https://images.unsplash.com/photo-1607860108855-64acf2078ed9?w=500", caption="Basic Bike Service", use_column_width=True)
                    st.image("https://images.unsplash.com/photo-1607860108855-64acf2078ed9?w=500", caption="Standard Service", use_column_width=True)
                    st.image("https://images.unsplash.com/photo-1607860108855-64acf2078ed9?w=500", caption="Premium Service", use_column_width=True)
            
            with bike_services_tab2:
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown("""
                    <div class="service-card">
                        <h3>Engine & Transmission</h3>
                        <div class="service-features">
                            <ul>
                                <li>Engine Overhaul</li>
                                <li>Clutch Service</li>
                                <li>Gearbox Repair</li>
                                <li>Chain & Sprocket Replacement</li>
                                <li>Engine Tuning</li>
                            </ul>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div class="service-card">
                        <h3>Electrical & Performance</h3>
                        <div class="service-features">
                            <ul>
                                <li>Electrical System Repair</li>
                                <li>Battery Replacement</li>
                                <li>Starter Motor Service</li>
                                <li>Performance Tuning</li>
                                <li>ECU Remapping</li>
                            </ul>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div class="service-card">
                        <h3>Brakes & Suspension</h3>
                        <div class="service-features">
                            <ul>
                                <li>Brake System Service</li>
                                <li>Suspension Work</li>
                                <li>Wheel Alignment</li>
                                <li>Fork Service</li>
                                <li>Shock Absorber Replacement</li>
                            </ul>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.image("https://images.unsplash.com/photo-1607860108855-64acf2078ed9?w=500", caption="Engine Service", use_column_width=True)
                    st.image("https://images.unsplash.com/photo-1607860108855-64acf2078ed9?w=500", caption="Electrical System", use_column_width=True)
                    st.image("https://images.unsplash.com/photo-1607860108855-64acf2078ed9?w=500", caption="Brake Service", use_column_width=True)
            
            with bike_services_tab3:
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown("""
                    <div class="service-card">
                        <h3>Basic Wash</h3>
                        <div class="service-price">₹300</div>
                        <div class="service-features">
                            <ul>
                                <li>Exterior Wash</li>
                                <li>Chain Cleaning</li>
                                <li>Basic Polish</li>
                            </ul>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div class="service-card">
                        <h3>Premium Wash</h3>
                        <div class="service-price">₹600</div>
                        <div class="service-features">
                            <ul>
                                <li>All Basic Wash Items</li>
                                <li>Detailed Polish</li>
                                <li>Chain Lubrication</li>
                                <li>Metal Parts Polish</li>
                            </ul>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div class="service-card">
                        <h3>Deep Cleaning</h3>
                        <div class="service-price">₹1,000</div>
                        <div class="service-features">
                            <ul>
                                <li>All Premium Wash Items</li>
                                <li>Engine Bay Cleaning</li>
                                <li>Paint Protection</li>
                                <li>Waxing</li>
                                <li>Rust Treatment</li>
                            </ul>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.image("https://images.unsplash.com/photo-1607860108855-64acf2078ed9?w=500", caption="Basic Wash", use_column_width=True)
                    st.image("https://images.unsplash.com/photo-1607860108855-64acf2078ed9?w=500", caption="Premium Wash", use_column_width=True)
                    st.image("https://images.unsplash.com/photo-1607860108855-64acf2078ed9?w=500", caption="Deep Cleaning", use_column_width=True)

        # Additional Information
        st.markdown("---")
        st.subheader("Additional Information")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            ### Service Guarantee
            - All services come with a 30-day warranty
            - Free re-service if issues persist
            - Quality assured by certified technicians
            - Genuine parts used in all repairs
            - 100% satisfaction guarantee
            """)
        
        with col2:
            st.markdown("""
            ### Why Choose Us?
            - State-of-the-art equipment
            - Certified technicians
            - Transparent pricing
            - Quick turnaround time
            - 24/7 customer support
            - Convenient online booking
            """)
        
        st.markdown("""
        ### Booking Process
        1. Select your vehicle type
        2. Choose service package
        3. Pick preferred date and time
        4. Get instant confirmation
        5. Track service status online
        6. Receive service completion notification
        """)

        # Service Benefits
        st.markdown("---")
        st.subheader("Service Benefits")
        
        benefits_col1, benefits_col2, benefits_col3 = st.columns(3)
        
        with benefits_col1:
            st.markdown("""
            ### 🛠️ Quality Service
            - Expert technicians
            - Latest diagnostic tools
            - Genuine spare parts
            - Quality workmanship
            """)
        
        with benefits_col2:
            st.markdown("""
            ### 💰 Value for Money
            - Competitive pricing
            - Transparent costs
            - No hidden charges
            - Service packages
            """)
        
        with benefits_col3:
            st.markdown("""
            ### ⏱️ Time Saving
            - Quick service
            - Online booking
            - Status tracking
            - Pick-up & delivery
            """)

def show_service_calculator():
    # Add custom CSS for the calculator
    st.markdown("""
        <style>
        .calculator-header {
            background-color: #0f172a;
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            color: white;
            text-align: center;
            border: 1px solid #1e293b;
        }
        .calculator-header h1 {
            color: white;
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
        .calculator-header p {
            color: #94a3b8;
            font-size: 1.1rem;
        }
        .service-option {
            background-color: #1e293b;
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid #334155;
            margin-bottom: 1rem;
        }
        .cost-summary {
            background-color: #0f172a;
            padding: 1.5rem;
            border-radius: 15px;
            color: white;
            border: 1px solid #1e293b;
        }
        .cost-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 1rem;
            padding: 0.5rem 0;
            border-bottom: 1px solid #334155;
            color: #e2e8f0;
        }
        .total-cost {
            font-size: 1.5rem;
            font-weight: bold;
            color: #60a5fa;
            text-align: center;
            padding: 1rem;
            background-color: #1e293b;
            border-radius: 10px;
            margin-top: 1rem;
            border: 1px solid #334155;
        }
        .service-checkbox {
            padding: 8px;
            margin: 4px 0;
            border-radius: 5px;
        }
        .service-checkbox:hover {
            background-color: #1e293b;
        }
        .dark-card {
            background-color: #1e293b;
            padding: 1.5rem;
            border-radius: 15px;
            border: 1px solid #334155;
            margin-bottom: 1rem;
            color: #e2e8f0;
        }
        .dark-card h3 {
            color: #e2e8f0;
            margin-bottom: 1rem;
        }
        .disclaimer {
            background-color: #1e293b;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            border: 1px solid #334155;
        }
        .disclaimer p {
            color: #94a3b8;
            font-size: 0.9rem;
            margin: 0;
        }
        .disclaimer ul {
            color: #94a3b8;
            margin: 0.5rem 0;
            padding-left: 1.5rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Calculator Header
    st.markdown("""
        <div class="calculator-header">
            <h1>💰 Service Cost Calculator</h1>
            <p>Get an instant estimate for your vehicle service</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for the main layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Vehicle Selection Section
        st.markdown("""
            <div class="dark-card">
                <h3>Vehicle Details</h3>
            </div>
        """, unsafe_allow_html=True)
        
        # Vehicle Type Selection with icons
        vehicle_type = st.selectbox(
            "Select Vehicle Type",
            ["Car", "Motorcycle"],
            format_func=lambda x: f"🚗 {x}" if x == "Car" else f"🏍️ {x}"
        )
        
        # Service Type Selection with icons
        service_type = st.selectbox(
            "Select Service Type",
            ["Regular Maintenance", "Repair", "Washing", "Inspection"],
            format_func=lambda x: {
                "Regular Maintenance": "🔧 Regular Maintenance",
                "Repair": "🔨 Repair",
                "Washing": "💧 Washing",
                "Inspection": "🔍 Inspection"
            }[x]
        )
        
        # Get repair types for the selected vehicle type
        repair_types = get_repair_types()
        
        # Calculate base cost based on vehicle type and service type
        base_cost = 0
        if vehicle_type == "Car":
            if service_type == "Regular Maintenance":
                base_cost = 2000
            elif service_type == "Washing":
                base_cost = 500
            elif service_type == "Inspection":
                base_cost = 1000
        else:  # Motorcycle
            if service_type == "Regular Maintenance":
                base_cost = 1000
            elif service_type == "Washing":
                base_cost = 200
            elif service_type == "Inspection":
                base_cost = 500
        
        # Additional costs based on service type
        additional_cost = 0
        selected_items = []
        
        st.markdown("""
            <div class="dark-card">
                <h3>Service Options</h3>
            </div>
        """, unsafe_allow_html=True)
        
        if service_type == "Regular Maintenance":
            # Create columns for maintenance items
            maint_col1, maint_col2 = st.columns(2)
            
            with maint_col1:
                if vehicle_type == "Car":
                    items = [
                        ("Engine Oil Change", 500, "🛢️"),
                        ("Oil Filter Replacement", 300, "🔍"),
                        ("Air Filter Cleaning", 400, "💨"),
                        ("Brake Check", 600, "🛑"),
                        ("Wheel Alignment", 800, "⚙️")
                    ]
                else:
                    items = [
                        ("Engine Oil Change", 300, "🛢️"),
                        ("Oil Filter Replacement", 200, "🔍"),
                        ("Air Filter Cleaning", 250, "💨"),
                        ("Chain Cleaning", 200, "⛓️"),
                        ("Brake Adjustment", 300, "🛑")
                    ]
                
                for item, cost, icon in items:
                    if st.checkbox(f"{icon} {item}", help=f"Cost: ₹{cost}"):
                        additional_cost += cost
                        selected_items.append((item, cost))
        
        elif service_type == "Repair":
            # Repair Categories
            repair_categories = list(repair_types[vehicle_type].keys())
            selected_category = st.selectbox(
                "Select Repair Category",
                repair_categories,
                format_func=lambda x: f"🔧 {x}"
            )
            
            # Repair Items with costs
            repair_items = repair_types[vehicle_type][selected_category]
            repair_costs = {
                "Engine": 5000,
                "Transmission": 4000,
                "Brake": 2000,
                "Suspension": 3000,
                "Electrical": 1500,
                "AC": 2500,
                "Body": 1000
            }
            
            for item in repair_items:
                cost = repair_costs.get(selected_category, 1000)
                if st.checkbox(f"🔧 {item}", help=f"Cost: ₹{cost}"):
                    additional_cost += cost
                    selected_items.append((item, cost))
        
        elif service_type == "Washing":
            if vehicle_type == "Car":
                packages = [
                    ("Basic Wash", 500, ["Exterior Wash", "Tire Cleaning", "Basic Interior"], "🧹"),
                    ("Premium Wash", 1000, ["All Basic Services", "Interior Detailing", "Waxing"], "✨"),
                    ("Deep Cleaning", 2000, ["All Premium Services", "Engine Bay Cleaning", "Ceramic Coating"], "🌟")
                ]
            else:
                packages = [
                    ("Basic Wash", 200, ["Exterior Wash", "Chain Cleaning"], "🧹"),
                    ("Premium Wash", 500, ["All Basic Services", "Deep Cleaning", "Polishing"], "✨"),
                    ("Deep Cleaning", 1000, ["All Premium Services", "Engine Cleaning", "Ceramic Coating"], "🌟")
                ]
            
            selected_package = st.radio(
                "Select Washing Package",
                [p[0] for p in packages],
                format_func=lambda x: f"{next(p[3] for p in packages if p[0] == x)} {x}"
            )
            
            for package, cost, services, icon in packages:
                if package == selected_package:
                    additional_cost = cost
                    selected_items = [(service, 0) for service in services]
                    break
    
    with col2:
        # Cost Summary Card
        st.markdown("""
            <div class="cost-summary">
                <h3 style='color: #e2e8f0; margin-bottom: 1rem; text-align: center;'>Cost Summary</h3>
                <div class="cost-item">
                    <span>Base Service Cost</span>
                    <span>₹{}</span>
                </div>
                <div class="cost-item">
                    <span>Additional Services</span>
                    <span>₹{}</span>
                </div>
                <div class="total-cost">
                    Total Estimate: ₹{}
                </div>
            </div>
        """.format(base_cost, additional_cost, base_cost + additional_cost), unsafe_allow_html=True)
        
        # Selected Services List
        if selected_items:
            st.markdown("""
                <div class="dark-card">
                    <h3>Selected Services</h3>
                </div>
            """, unsafe_allow_html=True)
            for item, cost in selected_items:
                if cost > 0:
                    st.markdown(f"<div style='color: #e2e8f0;'>- {item} (₹{cost})</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='color: #e2e8f0;'>- {item}</div>", unsafe_allow_html=True)
        
        # Disclaimer
        st.markdown("""
            <div class="disclaimer">
                <p>
                    <strong style='color: #e2e8f0;'>Note:</strong> This is an estimated cost. Final cost may vary based on:
                    <ul>
                        <li>Actual service requirements</li>
                        <li>Parts needed</li>
                        <li>Additional issues found during inspection</li>
                        <li>Vehicle condition</li>
                    </ul>
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Book Now Button with custom styling
        st.markdown("""
            <style>
            div[data-testid="stButton"] > button {
                background-color: #3b82f6;
                color: white;
                padding: 0.75rem 2rem;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                width: 100%;
            }
            div[data-testid="stButton"] > button:hover {
                background-color: #2563eb;
            }
            </style>
        """, unsafe_allow_html=True)
        
        if st.button("📝 Book This Service", key="book_service_btn", use_container_width=True):
            st.session_state.current_page = 'book_service'
            st.rerun()

def show_chatbot():
    st.header("AI Chat Support")
    
    # Initialize chat history in session state if it doesn't exist
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Quick Assist Features
    st.subheader("Quick Assist")
    st.write("Click on a common query to get instant assistance:")
    
    # Create columns for quick assist buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📅 How do I book a service?", use_container_width=True):
            prompt = "How do I book a service appointment?"
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            response = generate_chat_response(prompt)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
        
        if st.button("💰 What are your service prices?", use_container_width=True):
            prompt = "What are your service prices and packages?"
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            response = generate_chat_response(prompt)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
        
        if st.button("⏰ What are your working hours?", use_container_width=True):
            prompt = "What are your service center working hours?"
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            response = generate_chat_response(prompt)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col2:
        if st.button("🔧 What services do you offer?", use_container_width=True):
            prompt = "What types of services do you offer for vehicles?"
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            response = generate_chat_response(prompt)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
        
        if st.button("❓ How do I check my service status?", use_container_width=True):
            prompt = "How can I check the status of my service booking?"
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            response = generate_chat_response(prompt)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
        
        if st.button("📞 How can I contact support?", use_container_width=True):
            prompt = "What are your contact details and support options?"
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            response = generate_chat_response(prompt)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
    
    st.markdown("---")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("How can I help you today?"):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate response using Gemini AI
        response = generate_chat_response(prompt)
        
        # Add assistant response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.write(response)
    
    # Add a clear chat button
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

def generate_chat_response(prompt):
    """Generate a response using Gemini AI based on the user's prompt"""
    try:
        # Prepare the context for Gemini AI
        context = {
            "service_info": {
                "services": {
                    "regular_maintenance": {
                        "car": {
                            "basic": "₹2,000",
                            "standard": "₹4,000",
                            "premium": "₹6,000"
                        },
                        "bike": {
                            "basic": "₹1,000",
                            "standard": "₹2,000",
                            "premium": "₹3,000"
                        }
                    },
                    "washing": {
                        "car": {
                            "basic": "₹500",
                            "premium": "₹1,000",
                            "deep_cleaning": "₹2,000"
                        },
                        "bike": {
                            "basic": "₹200",
                            "premium": "₹500",
                            "deep_cleaning": "₹1,000"
                        }
                    }
                },
                "working_hours": "8:00 AM to 9:00 PM, Monday through Saturday",
                "location": "Hyderabad, Telangana",
                "contact": {
                    "phone": "9063358346",
                    "email": "shaheedmohiuddin99@gmail.com"
                }
            }
        }
        
        # Create a detailed prompt for Gemini AI
        full_prompt = f"""
        You are an automotive service center AI assistant. Provide helpful, accurate, and friendly responses.
        
        Context about our service center:
        {context}
        
        Previous conversation history:
        {st.session_state.chat_history}
        
        User's current query: {prompt}
        
        Please provide a response that is:
        1. Relevant to the user's query
        2. Helpful and informative
        3. Professional yet friendly
        4. Includes specific details when relevant
        5. Suggests next steps or related information when appropriate
        
        If the query is about vehicle problems, provide:
        1. Quick diagnosis
        2. Simple solutions
        3. When to visit the service center
        
        Format your response in a clear, easy-to-read way using bullet points or numbered lists when appropriate.
        """
        
        # Generate response using Gemini AI
        response = model.generate_content(full_prompt)
        
        if response and hasattr(response, 'text'):
            return response.text
        else:
            return "I apologize, but I'm having trouble generating a response right now. Please try rephrasing your question or contact our support team directly."
            
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}. Please try again or contact our support team for assistance."

def get_inventory_data():
    """Get inventory data with proper error handling"""
    try:
        conn = sqlite3.connect('inventory.db')
        inventory_df = pd.read_sql_query("""
            SELECT 
                id, name, category, quantity, price, 
                min_stock, description, status,
                COALESCE(last_updated, CURRENT_TIMESTAMP) as last_updated
            FROM inventory
        """, conn)
        conn.close()
        return inventory_df
    except Exception as e:
        st.error(f"Error loading inventory: {str(e)}")
        return pd.DataFrame()

def apply_inventory_filters(df, search_query, category_filter, status_filter):
    """Apply filters to inventory data"""
    if df.empty:
        return df
        
    # Apply search filter
    if search_query:
        search_query = search_query.lower()
        df = df[
            df['name'].str.lower().str.contains(search_query) |
            df['category'].str.lower().str.contains(search_query) |
            df['description'].str.lower().str.contains(search_query)
        ]
    
    # Apply category filter
    if category_filter != "All Categories":
        df = df[df['category'] == category_filter]
    
    # Apply status filter
    if status_filter != "All":
        df = df[df['status'] == status_filter]
    
    return df

def clear_inventory():
    """Clear all inventory items and their history"""
    try:
        conn = sqlite3.connect('inventory.db')
        c = conn.cursor()
        
        # First clear the history table (due to foreign key constraint)
        c.execute("DELETE FROM inventory_history")
        # Then clear the inventory table
        c.execute("DELETE FROM inventory")
        
        conn.commit()
        conn.close()
        return True, "Inventory cleared successfully"
    except Exception as e:
        return False, str(e)

def show_service_status():
    st.header("Service Status")
    
    # Get customer name from session state or prompt for input
    customer_name = st.session_state.get('customer_name')
    if not customer_name:
        customer_name = st.text_input("Enter your name to view service status")
    
    if customer_name:
        try:
            # Connect to database
            conn = sqlite3.connect('vehicle_service.db')
            c = conn.cursor()
            
            # Get customer's bookings
            c.execute("""
                SELECT * FROM bookings 
                WHERE customer_name = ? 
                ORDER BY booking_date DESC
            """, (customer_name,))
            
            bookings = c.fetchall()
            conn.close()
            
            if bookings:
                # Separate active and completed bookings
                active_bookings = [b for b in bookings if b[7] not in ['Completed', 'Cancelled']]
                completed_bookings = [b for b in bookings if b[7] in ['Completed', 'Cancelled']]
                
                # Display active bookings
                if active_bookings:
                    st.subheader("Active Bookings")
                    for booking in active_bookings:
                        with st.expander(f"Booking ID: {booking[0]} - {booking[4]} ({booking[6]})"):
                            st.write(f"**Vehicle Type:** {booking[2]}")
                            st.write(f"**Vehicle Number:** {booking[3]}")
                            st.write(f"**Service Type:** {booking[4]}")
                            st.write(f"**Booking Date:** {booking[5]}")
                            st.write(f"**Time Slot:** {booking[6]}")
                            st.write(f"**Status:** {booking[7]}")
                            if booking[8]:  # Description
                                st.write(f"**Description:** {booking[8]}")
                
                # Display completed bookings
                if completed_bookings:
                    st.subheader("Completed Bookings")
                    for booking in completed_bookings:
                        with st.expander(f"Booking ID: {booking[0]} - {booking[4]} ({booking[6]})"):
                            st.write(f"**Vehicle Type:** {booking[2]}")
                            st.write(f"**Vehicle Number:** {booking[3]}")
                            st.write(f"**Service Type:** {booking[4]}")
                            st.write(f"**Booking Date:** {booking[5]}")
                            st.write(f"**Time Slot:** {booking[6]}")
                            st.write(f"**Status:** {booking[7]}")
                            if booking[8]:  # Description
                                st.write(f"**Description:** {booking[8]}")
                
                # Admin interface for updating status
                if st.session_state.get('current_view') == 'admin':
                    st.subheader("Update Booking Status")
                    booking_id = st.selectbox(
                        "Select Booking",
                        [b[0] for b in bookings],
                        format_func=lambda x: f"Booking ID: {x}"
                    )
                    new_status = st.selectbox(
                        "New Status",
                        ["Pending", "In Progress", "Completed", "Cancelled"]
                    )
                    
                    if st.button("Update Status"):
                        try:
                            conn = sqlite3.connect('vehicle_service.db')
                            c = conn.cursor()
                            c.execute(
                                "UPDATE bookings SET status = ? WHERE booking_id = ?",
                                (new_status, booking_id)
                            )
                            conn.commit()
                            conn.close()
                            st.success("Status updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error updating status: {str(e)}")
            else:
                st.info("No bookings found for this customer.")
        
        except Exception as e:
            st.error(f"Error retrieving booking information: {str(e)}")
    else:
        st.info("Please enter your name to view service status.")

def hash_password(password):
    """Hash a password using a secure algorithm"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verify a password against its hash"""
    return hash_password(password) == hashed

def register_user(username, password, role, email=None):
    """Register a new user"""
    try:
        conn = sqlite3.connect('vehicle_service.db')
        c = conn.cursor()
        
        # Check if username already exists
        c.execute("SELECT username FROM users WHERE username = ?", (username,))
        if c.fetchone():
            return False, "Username already exists"
        
        # Check if email already exists (if provided)
        if email:
            c.execute("SELECT email FROM users WHERE email = ?", (email,))
            if c.fetchone():
                return False, "Email already registered"
        
        # Hash password and insert user
        hashed_password = hash_password(password)
        user_id = str(uuid.uuid4())
        
        c.execute("""
            INSERT INTO users (user_id, username, password, role, email)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, username, hashed_password, role, email))
        
        conn.commit()
        return True, "User registered successfully"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def authenticate_user(username, password):
    """Authenticate a user"""
    try:
        conn = sqlite3.connect('vehicle_service.db')
        c = conn.cursor()
        
        # Get user details
        c.execute("""
            SELECT user_id, username, password, role, email
            FROM users WHERE username = ?
        """, (username,))
        
        user = c.fetchone()
        if not user:
            return False, "User not found"
        
        # Verify password
        if not verify_password(password, user[2]):
            return False, "Invalid password"
        
        return True, {
            "user_id": user[0],
            "username": user[1],
            "role": user[3],
            "email": user[4]
        }
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def show_login_page():
    """Show the login page"""
    # Create columns for logo and title
    col1, col2 = st.columns([1, 4])
    
    with col1:
        # Add logo image
        st.image("D:\smart_vehicle_services_System-main\Smart_Vehicle_Services_System-main\static\images\Logo.png", width=500)

    
    with col2:
        st.title("AUTO ASSIST AND BOOKING SYSTEM")
    
    # Simple toggle button for role selection
    role = st.toggle("👨‍💼 Admin Mode", value=False, help="Toggle for Admin/Customer access")
    st.session_state['selected_role'] = 'admin' if role else 'customer'
    
    st.markdown(f"### {st.session_state['selected_role'].title()} Login")
    
    # Create tabs for login and registration
    login_tab, register_tab = st.tabs(["Login", "Register"])
    
    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if not username or not password:
                    st.error("Please fill in all fields")
                else:
                    success, result = authenticate_user(username, password)
                    if success:
                        if result['role'] != st.session_state['selected_role']:
                            st.error(f"Invalid role. Please use {st.session_state['selected_role']} login.")
                        else:
                            st.session_state['authenticated'] = True
                            st.session_state['user'] = result
                            st.session_state['current_view'] = result['role']
                            st.rerun()
                    else:
                        st.error(result)
    
    with register_tab:
        with st.form("register_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            email = st.text_input("Email (optional)")
            submit = st.form_submit_button("Register")
            
            if submit:
                if not username or not password or not confirm_password:
                    st.error("Please fill in all required fields")
                elif password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    success, message = register_user(username, password, st.session_state['selected_role'], email)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
    
def main():
    init_db()
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    
    # Show login page if not authenticated
    if not st.session_state.get('authenticated'):
        show_login_page()
        return
    
    # Show the appropriate dashboard based on user role
    if st.session_state['current_view'] == 'admin':
        show_admin_dashboard()
    elif st.session_state['current_view'] == 'customer':
        show_customer_dashboard()

if __name__ == "__main__":
    main() 