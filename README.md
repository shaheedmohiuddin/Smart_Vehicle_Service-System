# Vehicle Services System🏎️

A comprehensive vehicle service management system built with Streamlit and Python, featuring AI-powered assistance and automated booking management.

## 🌟 Features

### For Customers
- **Service Booking**
  - Easy booking interface for cars and motorcycles
  - Multiple service types (Regular Maintenance, Repair, Washing)
  - Flexible time slot selection
  - Service history tracking

- **Premium Services**
  - Car Services
    - Professional maintenance and repair
    - Expert body work solutions
    - High-end service packages
  - Bike Services
    - Periodic maintenance packages
    - Professional repair services
    - Custom modification options
  - Washing Packages
    - Premium car washing services
    - Specialized bike cleaning
    - Detailed interior and exterior care

- **AI-Powered Assistance**
  - Smart service recommendations
  - Diagnostic insights
  - Chat support
  - Cost estimation

- **Service Management**
  - Real-time service status tracking
  - Booking history
  - Service cost calculator
  - Detailed service information

### For Administrators
- **Staff Management**
  - Staff member registration
  - Duty assignment
  - Performance tracking

- **Inventory Management**
  - Stock tracking
  - Low stock alerts
  - Inventory analytics
  - Bulk import/export

- **Booking Management**
  - Service status updates
  - Customer booking overview
  - Service scheduling

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Uchiha_byte/Smart_Vehicle_Services_System.git
cd Smart_Vehicle_Services_System
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create an `api.env` file in the root directory and add your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

4. Run the application:
```bash
streamlit run app.py
```

## 💻 Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: SQLite
- **AI Integration**: Google Gemini AI
- **Data Visualization**: Plotly
- **Data Processing**: Pandas

## 📁 Project Structure

```
Vehicle_Services_System/
├── app.py                 # Main application file
├── api.env               # Environment variables
├── requirements.txt      # Project dependencies
├── vehicle_service.db    # Main database
├── inventory.db         # Inventory database
└── static/
    └── style.css        # Custom styling
```

## 🔧 Configuration

### Database Setup
The system uses two SQLite databases:
- `vehicle_service.db`: Stores user data, bookings, and staff information
- `inventory.db`: Manages inventory items and their history

### Environment Variables
Create an `api.env` file with the following:
```
GEMINI_API_KEY=your_gemini_api_key
```

## 👥 User Roles

### Customer
- Book services
- View booking history
- Track service status
- Use AI assistance
- Calculate service costs

### Administrator
- Manage staff
- Monitor inventory
- Update service status
- View analytics
- Access AI-powered insights

## 🔐 Security Features

- Password hashing
- Role-based access control
- Secure session management
- Input validation

## 📊 Features in Detail

### Service Booking
- Vehicle type selection (Car/Motorcycle)
- Service type selection
- Time slot booking
- Additional notes and requirements

### AI Integration
- Service recommendations
- Diagnostic insights
- Chat support
- Staff assistance

### Inventory Management
- Stock tracking
- Low stock alerts
- Inventory analytics
- Bulk operations

### Analytics Dashboard
- Service statistics
- Inventory insights
- Staff performance metrics
- Revenue tracking

### Premium Services Implementation
- **Interactive UI**
  - Expandable service sections
  - Two-column layout design
  - High-quality service images
  - Detailed service descriptions
- **Service Categories**
  - Car Services: Comprehensive maintenance, repair, and body work options
  - Bike Services: Professional maintenance, repairs, and customization
  - Washing Packages: Specialized cleaning services for both cars and bikes
- **Visual Integration**
  - Professional imagery from Unsplash
  - Visual representation of each service type
  - Clean and modern design aesthetic

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

- GitHub: (https://github.com/Uchiha_byte)
- Email: uchihabyte.git@gmail.com

## 🙏 Acknowledgments

- Google Gemini AI for providing the AI capabilities
- Streamlit for the web framework
