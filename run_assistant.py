# In run_assistant.py (at the very top of the file)
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')


import streamlit as st
import os
import json
import re
import chromadb
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from dateutil import parser
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv, set_key

# --- Import your custom modules ---
try:
    from scrapper import EnhancedErpScraper
    from utils.notifications import format_student_report, send_twilio_whatsapp_report
    from styles.ui_components import load_custom_css, create_welcome_header, create_login_form, create_sidebar_content, create_next_class_card
    # We will use st.columns for metrics, so create_metric_cards is not needed.
except ImportError as e:
    st.error(f"Fatal Error: Required modules not found. {str(e)}")
    st.stop()

# --- Configuration Constants ---
load_dotenv()
DATA_FOLDER = "data"
DATABASE_NAME = "university_db1"
COLLECTION_NAME = "university_handbook"
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'
GROQ_MODEL_NAME = "llama3-8b-8192"


# --- 2. HELPER FUNCTIONS ---

def update_env_file(key_to_update, new_value):
    set_key('.env', key_to_update, new_value)

# In run_assistant.py

def login_and_fetch_data(roll_no, password):
    """
    Handles the entire login and data fetching process.
    It runs the scraper and returns the data, designed for deployment.
    This function replaces both check_and_fetch_data and run_scraper.
    """
    # 1. Display informational messages to the user.
    st.info(
        "**Fetching live data from the ERP portal.** "
        "This may take up to 2-3 minutes. Please do not close this window."
    )
    
    # 2. Run the scraper inside a spinner to show activity.
    with st.spinner(f"🔗 Connecting to ERP and scraping data for {roll_no}..."):
        try:
            # The logic from your old `run_scraper` is now here.
            # We use the 'with' statement to ensure the browser closes properly.
            with EnhancedErpScraper(roll_no, password) as scraper:
                scraped_data = scraper.scrape_all_data()
        except Exception as e:
            # Catch any unexpected errors from the scraper itself
            st.error(f"A critical error occurred during scraping: {e}")
            return None

    # 3. Process the results.
    if scraped_data and "error" not in scraped_data:
        st.balloons()
        st.success("🎉 Live data fetched successfully!")
        return scraped_data
    else:
        # Handle errors reported by the scraper (e.g., invalid login)
        error_msg = scraped_data.get('error', 'an unknown error occurred') if scraped_data else 'an unknown error occurred'
        st.error(f"❌ Failed to fetch data. Error: {error_msg}")
        return None

@st.cache_resource
def initialize_components():
    """Initializes and caches the Persistent ChromaDB client."""
    db_path = "university_db" # Path to the folder in your repo
    
    print("--- Initializing Persistent ChromaDB Client ---")
    with st.spinner("🚀 Initializing AI Assistant..."):
        try:
            embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME, trust_remote_code=True)
            client = chromadb.PersistentClient(path="./university_db1")
            collection = client.get_collection("university_handbook")
            print(f"✅ Successfully loaded DB. Collection has {collection.count()} items.")

        except Exception as e:
            print(f"❌ FAILED to initialize PersistentClient. Error: {e}")
            st.error(f"Fatal Error: Could not load the vector database. Error: {e}")
            st.stop()
            
    return client, embedding_model

def get_next_class(timetable):
    """Finds the user's next scheduled class and returns its data or a status message."""
    now = datetime.now()
    current_day_str = now.strftime('%A')
    # current_day_str = 'Monday' # Uncomment for testing
    current_time = now.time()
    
    if current_day_str not in timetable or not timetable[current_day_str]:
        return f"No classes scheduled for today ({current_day_str})."

    today_schedule = timetable[current_day_str]
    for session in sorted(today_schedule, key=lambda x: parser.parse(x['time'].split(' - ')[0])):
        start_time_str = session['time'].split(' - ')[0]
        # Handle different time formats like '9:00AM' or '09:00 AM'
        start_time = parser.parse(start_time_str).time()
        
        if start_time > current_time:
            # Return the entire session dictionary
            return session
            
    return "✅ You have no more classes scheduled for today."
# --- 3. VISUALIZATION FUNCTIONS ---
def create_attendance_chart(attendance_data):
    """Creates an enhanced Plotly bar chart for attendance."""
    if not attendance_data:
        return go.Figure()
    
    df = pd.DataFrame(attendance_data)
    df['percentage'] = df['percentage'].astype(float)
    
    # Create color scale based on attendance percentage
    colors = ['#f56565' if x < 75 else '#48bb78' if x >= 85 else '#ed8936' for x in df['percentage']]
    
    fig = go.Figure(data=[
        go.Bar(
            y=df['course_name'],
            x=df['percentage'],
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='rgba(0,0,0,0.1)', width=1)
            ),
            text=[f'{x:.1f}%' for x in df['percentage']],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Attendance: %{x:.1f}%<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title={
            'text': '📊 Course Attendance Overview',
            'font': {'size': 20, 'color': '#4a5568'},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Attendance Percentage',
        yaxis_title='Courses',
        yaxis={'categoryorder': 'total ascending'},
        template='plotly_white',
        height=max(400, len(df) * 40),
        margin=dict(l=20, r=20, t=80, b=20),
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig



def create_gpa_chart(semester_results):
    """Creates a robust GPA/CGPA chart with corrected axes and annotations."""
    if not semester_results:
        return go.Figure()

    df = pd.DataFrame(semester_results)
    
    # Safely convert to numeric, coercing errors to NaN
    df['gpa'] = pd.to_numeric(df['gpa'], errors='coerce')
    df['cgpa'] = pd.to_numeric(df['cgpa'], errors='coerce')
    
    # Drop rows where conversion failed
    df.dropna(subset=['gpa', 'cgpa', 'term'], inplace=True)
    
    # Sort by term to ensure lines connect chronologically
    try:
        # A more robust sort if terms are like "Fall 2023"
        df['sort_key'] = df['term'].apply(lambda x: (int(x.split()[1]), 0 if x.split()[0].lower() == 'spring' else 1 if x.split()[0].lower() == 'summer' else 2))
        df.sort_values(by='sort_key', inplace=True)
    except:
        # Fallback to simple alphabetical sort
        df.sort_values(by='term', inplace=True)

    if df.empty:
        return go.Figure()

    fig = go.Figure()
    
    # Add GPA line
    fig.add_trace(go.Scatter(
        x=df['term'], y=df['gpa'], mode='lines+markers', name='Semester GPA',
        line=dict(color='#667eea', width=3), marker=dict(size=8),
        hovertemplate='<b>%{x}</b><br>GPA: %{y:.2f}<extra></extra>'
    ))
    
    # Add CGPA line (with corrected x-axis)
    fig.add_trace(go.Scatter(
        x=df['term'], y=df['cgpa'], mode='lines+markers', name='CGPA',
        line=dict(color='#48bb78', width=3, dash='dash'), marker=dict(size=8, symbol='diamond'),
        hovertemplate='<b>%{x}</b><br>CGPA: %{y:.2f}<extra></extra>'
    ))

    # Add annotations
    latest_term = df['term'].iloc[-1]
    latest_gpa = df['gpa'].iloc[-1]
    latest_cgpa = df['cgpa'].iloc[-1]
    fig.add_annotation(x=latest_term, y=latest_gpa, text=f"<b>Latest GPA: {latest_gpa:.2f}</b>", showarrow=True, arrowhead=2, ax=0, ay=-40, bgcolor="rgba(255,255,255,0.8)")
    fig.add_annotation(x=latest_term, y=latest_cgpa, text=f"<b>Current CGPA: {latest_cgpa:.2f}</b>", showarrow=True, arrowhead=2, ax=0, ay=40, bgcolor="rgba(255,255,255,0.8)")
    
    # Layout styling
    fig.update_layout(
        title={'text': '📈 Academic Performance Trend', 'x': 0.5},
        yaxis=dict(range=[0, 4.1]), height=450, hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


# --- 4. RAG FUNCTIONS ---
def format_student_data_for_prompt(student_data):
    """Creates a clean summary of the student's data for the LLM."""
    if not student_data: 
        return "No student data available."
    
    profile = student_data.get('profile', {})
    financials = student_data.get('financials', {})
    attendance = student_data.get('attendance', [])
    
    summary = f"""### Student Profile
- **Name:** {profile.get('student_name', 'N/A')}
- **Roll No:** {student_data.get('roll_no', 'N/A')}
- **Semester:** {profile.get('semester', 'N/A')}
- **CGPA:** {profile.get('cgpa', 'N/A')}
- **Academic Standing:** {profile.get('academic_standing', 'N/A')}

### Financial Status
- **Total Remaining Balance:** {financials.get('total_remaining_balance', 'N/A')}

### Attendance Summary
"""
    
    low_attendance_courses = [c for c in attendance if float(c.get('percentage', 100)) < 75]
    if low_attendance_courses:
        summary += "- **Warning:** The following courses have attendance below the 75% threshold:\n"
        summary += "".join(f"  - {course.get('course_name')}: {course.get('percentage')}%\n" for course in low_attendance_courses)
    else:
        summary += "- All course attendance records are currently above the 75% threshold.\n"
    
    return summary.strip()



def retrieve_context(client, embedding_model, user_query, formatted_student_summary, top_k=5):
    """
    Retrieves context from the persistent ChromaDB collection.
    """
    print("--- Retrieving context from persistent DB ---")
    try:
        # Ensure inputs are strings to prevent TypeErrors
        user_query = str(user_query)
        formatted_student_summary = str(formatted_student_summary)
        
        augmented_query = f"Student Summary: {formatted_student_summary}\nUser's Question: {user_query}"
        
        collection = client.get_collection(name=COLLECTION_NAME)

        # Generate the embedding for the query
        query_embedding = embedding_model.encode(augmented_query).tolist()
        
        # Perform the query
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=['documents', 'metadatas'] # Make sure to include metadatas
        )
        
        print(f"    - Found {len(results['documents'][0])} relevant documents.")
        return results

    except Exception as e:
        print(f"    ❌ FAILED during context retrieval. Error: {e}")
        # Return a default empty structure in case of error
        return {'documents': [[]], 'metadatas': [[]]}
    

def generate_response_with_groq(user_query, student_data, formatted_student_summary, conversation_history, context_docs):
    """Generates a personalized response using Groq with advanced prompt engineering."""
    context_str = "\n\n".join(f"--- Handbook Excerpt ---\n{doc}" for doc in context_docs)
    history_str = "\n".join([f"Previous {msg['role']}: {msg['content']}" for msg in conversation_history])

    system_prompt = """
    You are "Superior University's AI Assistant", a friendly, professional, and highly knowledgeable support agent.

    **Your Persona:**
    - You are helpful, accurate, and always polite.
    - You MUST address the student by their name in your response.
    - Your goal is to provide clear, actionable answers based *exclusively* on the information provided.

    **Your Core Directives:**
    1. **Synthesize ALL Information:** Use conversation history, student record summary, timetable data, and handbook excerpts.
    2. **Prioritize the New Question:** Focus on answering the user's newest question.
    3. **Handle Tables & Data:** Parse HTML tables and JSON data accurately.
    4. **NEVER Invent Information:** If information isn't available, explicitly state this.
    5. **Structure Your Answers:** Provide direct answers with clear reasoning and markdown formatting.
    """
    
    if any(keyword in user_query.lower() for keyword in ["timetable", "schedule", "my classes", "class schedule"]):
        timetable_data = student_data.get('timetable', {})
        user_prompt = f"""
        ### Conversation History
        {history_str}
        
        ### Student's Record Summary
        {formatted_student_summary}

        ### Full Timetable Data
        ```json
        {json.dumps(timetable_data, indent=2)}
        ```
        
        ### Relevant University Handbook Excerpts
        {context_str}

        ### New User Question
        {user_query}
        
        **Instruction:** Format the student's complete weekly schedule into a clean, easy-to-read markdown table.
        """
    else:
        user_prompt = f"""
        ### Conversation History
        {history_str}
        
        ### Student's Record Summary
        {formatted_student_summary}

        ### Relevant University Handbook Excerpts
        {context_str}

        ### New User Question
        {user_query}
        
        **Instruction:** Provide a helpful and accurate response based on the information above.
        """
    
    try:
        groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model=GROQ_MODEL_NAME,
            temperature=0,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"❌ An error occurred while contacting the Groq API: {e}"

# --- 5. MAIN APPLICATION ---
def main():
    """Main application function."""
    st.set_page_config(
        page_title="Superior University AI Dashboard",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    load_custom_css()

    # --- Initialize session state ---
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.student_data = None
        st.session_state.messages = []


    # In your main() function

    # --- Login Screen ---
    if not st.session_state.logged_in:
        
        # 1. Create the login form UI.
        #    (The code to get default values from .env for the form is good practice for local dev)
        default_roll_no = os.getenv("ERP_ROLL_NO", "")
        default_password = os.getenv("ERP_PASSWORD", "")
        existing_whatsapp = os.getenv("PARENT_WHATSAPP_NUMBER", "")

        roll_no_input, password_input, parent_whatsapp_input, login_button = create_login_form(
            default_roll_no=default_roll_no,
            default_password=default_password,
            existing_whatsapp_number=existing_whatsapp
        )
        
        # 2. Handle the form submission when the button is clicked.
        if login_button:
            if not roll_no_input or not password_input:
                st.error("❌ Roll Number and Password are required.")
            else:
                # --- THIS IS THE KEY CHANGE ---
                # Call the new, single function that handles scraping without file I/O.
                student_data = login_and_fetch_data(roll_no_input, password_input)
                # --- END OF KEY CHANGE ---
                
                # 3. If scraping was successful, save data to the session and proceed.
                if student_data:
                    # This logic to update the WhatsApp number is fine, but it will only
                    # work locally. On Streamlit Cloud, you cannot modify the .env file.
                    # It's better to manage this via Streamlit's Secrets manager UI.
                    if "STREAMLIT_SERVER_RUNNING" not in os.environ:
                        if parent_whatsapp_input and parent_whatsapp_input != existing_whatsapp:
                            update_env_file("PARENT_WHATSAPP_NUMBER", parent_whatsapp_input)
                            load_dotenv(override=True)
                
                    # This is your new "caching" mechanism.
                    # We save the fetched data directly into the session state.
                    st.session_state.logged_in = True
                    st.session_state.student_data = student_data
                    st.session_state.messages = [
                        {"role": "assistant", "content": f"Hello {student_data['profile']['student_name']}! 👋 How can I help?"}
                    ]
                    
                    # Rerun the script to hide the login form and show the main dashboard.
                    st.rerun()

    
    # --- Main Dashboard (Logged-in State) ---
    else:
        student_data = st.session_state.student_data
        chroma_client, embedding_model = initialize_components()
        formatted_summary = format_student_data_for_prompt(student_data)

        # --- Sidebar ---
        with st.sidebar:
            st.image("https://placehold.co/100x100/764ba2/white?text=SU", width=100)
            st.title(f"Welcome, {student_data['profile']['student_name'].split()[0]}!")

            # --- START: CORRECTED SECTION ---
            next_class_info = get_next_class(student_data.get('timetable', {}))
            
            if isinstance(next_class_info, dict): # Check if it returned class data
                 # CORRECTED: Call the function with only the arguments it now expects
                 create_next_class_card(
                    course=next_class_info.get('details', 'N/A'),
                    time=next_class_info.get('time', 'N/A'),
                    location=next_class_info.get('venue', 'N/A')
                )
            else: # It returned a string message like "No classes"
                # Use a different component for simple messages
                create_sidebar_content(
                    title="Today's Schedule",
                    content=str(next_class_info) # Ensure content is a string
                )
            st.markdown("---")
            st.subheader("📤 Actions")

            if st.button("📧 Send Report to Parent via WhatsApp"):
                parent_number = os.getenv("PARENT_WHATSAPP_NUMBER")

                if not parent_number:
                    st.error("No parent WhatsApp number saved. Please add it on the login screen.")
                else:
                    with st.spinner(f"Preparing to send report to {parent_number}..."):
                        # 1. Format the report
                        report_str = format_student_report(student_data)
                        
                        # 2. Send the message
                        result = send_twilio_whatsapp_report(student_data) 


                    # 3. Show the result
                    if "success" in result:
                        st.success(result["success"])
                    else:
                        st.error(result["error"])

            st.markdown("---")
            if st.button("🚪 Logout", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

        # --- Main Header ---
        create_welcome_header(student_name=student_data['profile']['student_name'])

      # In your app.py, inside the 'else:' block for the logged-in state

        # --- Metric Cards ---
        st.subheader("Your Academic Snapshot")

        cgpa = student_data.get('profile', {}).get('cgpa', 'N/A')
        semester = student_data.get('profile', {}).get('semester', 'N/A')
        standing = student_data.get('profile', {}).get('academic_standing', 'N/A')
        balance = student_data.get('financials', {}).get('total_remaining_balance', 'N/A')
        # Use Streamlit's built-in columns for layout. This is the most reliable way.
        col1, col2, col3, col4 = st.columns(4)

        with col1:
                st.markdown(f"""
                <div class="metric-card fade-in">
                    <h3>Current CGPA</h3>
                    <p class="value">{cgpa}</p>
                </div>
                """, unsafe_allow_html=True)

        with col2:
                st.markdown(f"""
                <div class="metric-card fade-in">
                    <h3>Semester</h3>
                    <p class="value">{semester}</p>
                </div>
                """, unsafe_allow_html=True)
                
        with col3:
                st.markdown(f"""
                <div class="metric-card fade-in">
                    <h3>Academic Standing</h3>
                    <p class="value">{standing}</p>
                </div>
                """, unsafe_allow_html=True)

        with col4:
                st.markdown(f"""
                <div class="metric-card fade-in">
                    <h3>Balance Due</h3>
                    <p class="value">{balance}</p>
                </div>
                """, unsafe_allow_html=True)
            
        # Main Tabs
        tab1, tab2, tab3, tab4 = st.tabs(["💬 AI Assistant", "📊 Academic Analytics", "📚 Enrolled Courses", "🗓️ Weekly Schedule"])
        with tab1:
            st.markdown("""
            <div class="chat-container">
                <h2>🤖 AI Assistant Chat</h2>
                <p>Ask me anything about your academic performance, university policies, or get help with your studies!</p>
            </div>
            """, unsafe_allow_html=True)
            
            # In your `main` function, inside the `else:` block for logged-in state

            formatted_summary = format_student_data_for_prompt(student_data)


            # Chat Interface
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            if prompt := st.chat_input("Ask a question..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"): 
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    with st.spinner("🔍 Analyzing with Hybrid Search..."):
                        
                        # USE HYBRID SEARCH from Block 2's logic
                        results = retrieve_context(
                            chroma_client, 
                            embedding_model, 
                            prompt, 
                            formatted_summary
                        )
                        
                        # Generate the response
                        response = generate_response_with_groq(
                            prompt, 
                            student_data, 
                            formatted_summary, 
                            st.session_state.messages[-3:-1], # Simple history
                            results['documents'][0]
                        )
                        st.markdown(response)
                        
                        # USE SOURCE DISPLAY from Block 1's logic
                        with st.expander("🔍 View Retrieved Sources"):
                            if results['documents'][0]:
                                for i, doc in enumerate(results['documents'][0]):
                                    # Assumes metadata might not be present in hybrid search result
                                    st.info(f"**Source {i+1}:**\n{doc}")
                            else:
                                st.write("No relevant documents were retrieved from the handbook.")
                
                st.session_state.messages.append({"role": "assistant", "content": response})
                        
                with st.expander("🔍 View Retrieved Sources"):
                            for i, metadata in enumerate(results['metadatas'][0]):
                                st.write(f"**Source {i+1}:** File `{metadata['source_file']}`, Page `{metadata['page_number']}`")
                                st.info(results['documents'][0][i])
                
                st.session_state.messages.append({"role": "assistant", "content": response})

    
        with tab2:
            st.header("📊 Academic Analytics")
            st.markdown("An overview of your academic performance and attendance records.")

            # --- GPA/CGPA TREND CHART ---
            if student_data.get('semester_results'):
                st.subheader("📈 GPA & CGPA Trend")
                gpa_fig = create_gpa_chart(student_data['semester_results'])
                st.plotly_chart(gpa_fig, use_container_width=True)
                st.markdown("---")
            
            # --- DETAILED SEMESTER RESULTS (NEW INTERACTIVE VIEW) ---
            if student_data.get('semester_results'):
                st.subheader("🎓 Detailed Semester Results")
                
                # Get the semester results data
                results_data = student_data['semester_results']
                
                # Loop through each semester and create an expander for it
                for semester in results_data:
                    term_name = semester.get('term', 'Unknown Semester')
                    gpa = semester.get('gpa', 'N/A')
                    cgpa = semester.get('cgpa', 'N/A')
                    courses = semester.get('courses', [])
                    
                    with st.expander(f"**{term_name}** | GPA: {gpa} | CGPA: {cgpa}"):
                        if courses:
                            # Convert the list of course dictionaries to a pandas DataFrame for nice display
                            courses_df = pd.DataFrame(courses)
                            # Rename columns for better readability
                            courses_df.columns = ["Course Name", "Credits", "Marks Obtained", "Final Grade"]
                            st.dataframe(courses_df, use_container_width=True, hide_index=True)
                        else:
                            st.write("No detailed course results found for this semester.")
                st.markdown("---")

            # --- ATTENDANCE OVERVIEW ---
            if student_data.get('attendance'):
                st.subheader("✅ Attendance Overview")
                attendance_fig = create_attendance_chart(student_data['attendance'])
                st.plotly_chart(attendance_fig, use_container_width=True)

        with tab3:
            st.header("📚 Enrolled Courses Overview")
            
            # Safely get the list of enrolled courses from the student data
            enrolled_courses = student_data.get('enrolled_courses', [])
            
            if not enrolled_courses:
                st.warning("No enrolled course data found. The scraper may need to be updated or the data is not on the portal.")
            else:
                # --- Separate the courses into two lists based on their status ---
                grading_in_progress = [c for c in enrolled_courses if c['status'] == "Grading in progress"]
                active_classes = [c for c in enrolled_courses if c['status'] == "Active Class"]
                
                # --- 1. Display the "Grading in Progress" section first ---
                if grading_in_progress:
                    st.subheader("⏳ Classes Awaiting Grades")
                    # Loop through each course in this category and display its card
                    for course in grading_in_progress:
                        # Use the correct dictionary keys: 'course_name' and 'course_code'
                        st.markdown(f"""
                        <div class="stats-card">
                            <h4>{course.get('course_name', 'N/A')}</h4>
                            <p><strong>Code:</strong> {course.get('course_code', 'N/A')} | <strong>Credits:</strong> {course.get('credits', 'N/A')}</p>
                            <p><span style="color: #ED8936; font-weight: bold;">Status: {course.get('status', 'N/A')}</span></p>
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown("---") # Add a separator line after the section
                
                # --- 2. Display the "Active Classes" section second ---
                if active_classes:
                    st.subheader("✅ Active Classes")
                    # Loop through each course in this category and display its card
                    for course in active_classes:
                        # Use the correct dictionary keys: 'course_name' and 'course_code'
                        st.markdown(f"""
                        <div class="stats-card">
                            <h4>{course.get('course_name', 'N/A')}</h4>
                            <p><strong>Code:</strong> {course.get('course_code', 'N/A')} | <strong>Credits:</strong> {course.get('credits', 'N/A')}</p>
                            <p><span style="color: #48BB78; font-weight: bold;">Status: {course.get('status', 'N/A')}</span></p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Add a helpful message if no courses were found in either category after filtering
                if not grading_in_progress and not active_classes:
                    st.info("No courses with 'Active' or 'Grading in progress' status were found.")
        with tab4:
            st.markdown("## 🗓️ Weekly Schedule")
            
            timetable = student_data.get('timetable', {})
            if timetable:
                # Create a structured weekly view
                days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                
                for day in days:
                    if day in timetable and timetable[day]:
                        st.markdown(f"### {day}")
                        
                        # Create columns for each class
                        classes = sorted(timetable[day], key=lambda x: x.get('time', ''))
                        
                        for class_info in classes:
                            with st.container():
                                st.markdown(f"""
                            <div class="schedule-card">
                                <h4>{class_info.get('details', 'Unknown Course')}</h4>
                                <p><strong>Time:</strong> {class_info.get('time', 'N/A')}</p>
                                <p><strong>Venue:</strong> {class_info.get('venue', 'N/A')}</p> 
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("---")
                    else:
                        st.markdown(f"### {day}")
                        st.info(f"No classes scheduled for {day}")
                        st.markdown("---")
            else:
                st.warning("No timetable data available.")

        # Footer
        st.markdown("---")
        st.markdown("""
        <div class="footer">
            <p>🎓 Superior University AI Dashboard</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
