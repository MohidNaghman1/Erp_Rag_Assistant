import streamlit as st

def load_custom_css():
    """
    Loads the custom CSS styles for the Streamlit app.
    This function injects a <style> block into the Streamlit app's HTML.
    """
    css = """
    /* Superior University AI Dashboard - Enhanced UI Styles */

    /* Main App Styling */
    .main > div {
        padding-top: 2rem;
    }

    /* Custom Header */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }

    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }

    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
    }

    /* Login Form Styling */
    .login-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        margin: 2rem auto;
        max-width: 500px;
    }

    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }

    .login-header h2 {
        color: #4a5568;
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }

    .login-header p {
        color: #718096;
        font-size: 1.1rem;
    }

    /* Sidebar Styling */
    .sidebar-content {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        color: white;
        transition: all 0.3s ease;
    }
    
    .sidebar-content:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }

    .sidebar-content h3 {
        margin-top: 0;
        color: white;
        font-size: 1.3rem;
    }

    .sidebar-content p {
        color: rgba(255,255,255,0.9);
        margin: 0.5rem 0;
    }
    
    /* Metric Cards */
    .metric-row {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin-bottom: 2rem;
    }

    .metric-card {
        flex: 1;
        min-width: 200px;
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 4px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }

    .metric-card h3 {
        color: #4a5568;
        margin: 0 0 0.5rem 0;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .metric-card .value {
        color: #667eea;
        font-size: 2rem;
        font-weight: bold;
        margin: 0;
    }


    /* Next Class Card */
    .next-class-card {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }

    .next-class-card h4 {
        color: white;
        margin: 0 0 0.5rem 0;
    }

    .next-class-card p {
        color: rgba(255,255,255,0.9);
        margin: 0.25rem 0;
    }
    
    /* Animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .fade-in {
        animation: fadeIn 0.5s ease-out forwards;
    }
    
    /* Hide Streamlit Menu and Footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }

    /* Button, Input, and other Streamlit specific overrides */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        color: white !important;
    }
    
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        padding: 1.5rem 0.75rem;
        font-size: 1rem;
    }

    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
    }
    """
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def create_welcome_header(student_name):
    """
    Creates the main welcome header for the dashboard.
    
    Args:
        student_name (str): The name of the student to display.
    """
    header_html = f"""
    <div class="main-header fade-in">
        <h1>Welcome, {student_name}!</h1>
        <p>Your AI-powered university assistant is ready to help.</p>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

# In styles/ui_components.py

# In styles/ui_components.py

def create_login_form(default_roll_no="", default_password="", existing_whatsapp_number=""):
    """
    Renders a styled login form container and pre-fills it with default values.
    
    Args:
        default_roll_no (str): The default roll number to display.
        default_password (str): The default password to display.
        existing_whatsapp_number (str): The pre-existing WhatsApp number to show in the field.

    Returns:
        tuple: A tuple containing the current values of (roll_no, password, parent_whatsapp, login_button_clicked).
    """
    login_html_start = """
    <div class="login-container fade-in">
        <div class="login-header">
            <h2>Superior University AI Portal</h2>
            <p>Please log in to access your dashboard.</p>
        </div>
    """
    st.markdown(login_html_start, unsafe_allow_html=True)

    # Use the default values passed into the function
    roll_no = st.text_input(
        "🎓 Roll Number", 
        value=default_roll_no, 
        key="login_user"
    )
    password = st.text_input(
        "🔒 Password", 
        type="password", 
        value=default_password, 
        key="login_pass"
    )
    
    parent_whatsapp = st.text_input(
        "📱 Parent's WhatsApp Number (for alerts, optional)", 
        value=existing_whatsapp_number,
        key="login_whatsapp"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    login_button = st.button("🚀 Login & Fetch Data", use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    return roll_no, password, parent_whatsapp, login_button

def create_sidebar_content(title, content):
    """
    Creates a styled content block in the sidebar.
    
    Args:
        title (str): The title for the sidebar block.
        content (str): The paragraph content for the block.
    """
    sidebar_html = f"""
    <div class="sidebar-content fade-in">
        <h3>{title}</h3>
        <p>{content}</p>
    </div>
    """
    st.sidebar.markdown(sidebar_html, unsafe_allow_html=True)


def create_metric_cards(metrics):
    """
    Creates a full row of styled metric cards from a list of dictionaries.
    This function correctly builds a single HTML block and renders it once.

    Args:
        metrics (list): A list of dictionaries, where each dict has 'label' and 'value'.
                        Example: [{'label': 'GPA', 'value': '3.85'}, ...]
    """
    
    # 1. Start with an empty string to hold the HTML for all the individual cards.
    cards_html = ""

    # 2. Loop through the list of metric data you provided.
    for metric in metrics:
        label = metric.get('label', '')
        value = metric.get('value', '')
        
        # 3. For each metric, create the HTML for one card and add it to our string.
        cards_html += f"""
        <div class="metric-card fade-in">
            <h3>{label}</h3>
            <p class="value">{value}</p>
        </div>
        """

    # 4. After the loop, wrap all the generated cards in the parent 'metric-row' div.
    #    This div uses 'display: flex' to align the cards horizontally.
    full_html = f'<div class="metric-row">{cards_html}</div>'

    # 5. Render the complete HTML block in one single command.
    st.markdown(full_html, unsafe_allow_html=True)

# In styles/ui_components.py

def create_next_class_card(course, time, location):
    """
    Creates a card displaying information about the next class.
    (This version does NOT include a professor/instructor).

    Args:
        course (str): The name of the course.
        time (str): The time of the class.
        location (str): The location/venue of the class.
    """
    card_html = f"""
    <div class="next-class-card fade-in">
        <h4>Next Up: {course}</h4>
        <p><strong>Time:</strong> {time}</p>
        <p><strong>Location:</strong> {location}</p>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)