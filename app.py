import streamlit as st
from groq import Groq
from streamlit_option_menu import option_menu
from fpdf import FPDF
import time

# Set page configuration
st.set_page_config(page_title="Virtual Doctor Assistant", page_icon="🩺", layout="wide")

# Initialize Groq API
groq_api_key = st.secrets["groq_api_key"]
client = Groq(api_key=groq_api_key)

# Initialize session state for navigation if not exists
if 'page' not in st.session_state:
    st.session_state.page = "Home"

# Sidebar navigation
with st.sidebar:
    st.image("Green and White Modern Medical Logo.png", use_column_width=True)
    selected = option_menu(
        menu_title="Navigation",
        options=["Home", "Doctor Chat", "Nutrition", "About"],
        icons=["house", "chat-dots", "apple", "info-circle"],
        menu_icon="list",
        default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": "#0f0c29"},
            "icon": {"color": "#f5f0e1", "font-size": "25px"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "4px", "--hover-color": "#ffc13b"},
            "nav-link-selected": {"background-color": "#ff6e40"},
        }
    )
    if selected:
        st.session_state.page = selected

# Global CSS styles
st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 100% , #24243e );
    }
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 100% , #24243e);
    }
    .stButton>button {
        background-color: #ff6e40;
        color: #f5f0e1;
        border: none;
        padding: 10px 24px;
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #ffc13b;
        color: #1e3d59;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .tip-container {
    border: 3px solid #ff5733; /* Example of a bright color (orange-red) */
    color: #f5f0e1;
    padding: 20px;
    border-radius: 10px;
    font-size: 18px;
    font-weight: bold;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin: 20px 0;
    }
    @media (max-width: 768px) {
        .tip-container {
            font-size: 16px;
            padding: 15px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Helper functions
def get_ai_response(prompt, system_role):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": prompt},
            ],
            model="llama3-70b-8192",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error in AI response: {str(e)}")
        return "I'm sorry, I couldn't generate a response at this time."

def get_nutrition_plan(age, weight, height, goal, duration):
    bmi = weight / ((height / 100) ** 2)
    prompt = f"Create a nutrition and exercise plan for a {age}-year-old person with a BMI of {bmi:.1f}, aiming to {goal} over {duration}. Include daily meal plans and exercise routines."
    return get_ai_response(prompt, "You are a knowledgeable nutritionist and fitness expert.")

def generate_pdf(content, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, content)
    pdf.output(filename)
    st.success(f"PDF report generated successfully: {filename}")

# Home Page
def home():
    st.title("Virtual Doctor Assistant 🩺")
    st.markdown("""
        <div style="display: flex; justify-content: center;">
            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRglA8ded1nak4g53q-jAchwheavelVAUysgg&s" width="500" >
        </div>
    """, unsafe_allow_html=True)
    st.write("Let our smart AI provide virtual healthcare solutions right at your fingertips!")

    tips = [
        "Fuel Your Body Right: Eat colorful fruits and veggies.",
        "Keep Moving: Exercise daily for 30 minutes!",
        "Stay Hydrated: Drink 2-3 liters of water every day.",
    ]
    tip_index = 0
    tip_container = st.empty()

    while True:
        with tip_container:
            st.markdown(
                f'<div class="tip-container">{tips[tip_index]}</div>',
                unsafe_allow_html=True,
            )
        tip_index = (tip_index + 1) % len(tips)
        time.sleep(6)

# Doctor Chat
def doctor_chat():
    st.title("Doctor Chat 👨‍⚕️")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Enter symptoms:"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        response = get_ai_response(prompt, "You are an AI doctor providing helpful advice.")
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# Nutrition Planner
def nutrition():
    st.title("Nutrition Planner 🥗")
    age = st.number_input("Age", min_value=1, max_value=120, value=30)
    weight = st.number_input("Weight (kg)", min_value=1.0, max_value=300.0, value=70.0)
    height = st.number_input("Height (cm)", min_value=50, max_value=250, value=170)
    goal = st.selectbox("Goal", ["lose weight", "gain weight", "maintain weight"])
    duration = st.selectbox("Plan Duration", ["1 week", "2 weeks", "1 month"])

    if st.button("Generate Nutrition Plan"):
        plan = get_nutrition_plan(age, weight, height, goal, duration)
        st.session_state.nutrition_plan = plan
        st.markdown(plan)

        if st.button("Download PDF Report"):
            filename = "nutrition_plan_report.pdf"
            generate_pdf(st.session_state.nutrition_plan, filename)
            with open(filename, "rb") as f:
                st.download_button("Download Nutrition Plan", f, file_name=filename)

# About Us
def about():
    st.title("About Us 👥")
    st.write("We are a team of passionate developers working on innovative healthcare solutions.")
    team_members = [
    {"name": "Ayan Srivastava", "role": "Data Scientist", "image": "https://media.licdn.com/dms/image/v2/D5635AQE5pi8FGnqPvw/profile-framedphoto-shrink_400_400/profile-framedphoto-shrink_400_400/0/1712780768563?e=1736964000&v=beta&t=D_sC5MFkvmwXOI1N8ItByLm4wN3ZNns7PTRWdH4wLkI", "linkedin": "https://www.linkedin.com/in/ayan-srivastava-017a89259/", "github": "https://github.com/AyanSrivastava11"},

    {"name": "Aditi Singh", "role": "Data Analyst", "image": "data:image/jpeg;base64,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", "linkedin": "https://www.linkedin.com/in/aditi-singh-266456253/", "github": "https://github.com/AyanSrivastava11"},

    {"name": "Aditi Gupta", "role": "Front end developer", "image": "https://media.licdn.com/dms/image/v2/D4E03AQFyK8SIQkAFpA/profile-displayphoto-shrink_800_800/profile-displayphoto-shrink_800_800/0/1688370356823?e=1735776000&v=beta&t=1Uo6GsirXGHBxUzxrjJ77x6xBB4uduHmV5uyDaRK5Nw", "linkedin": "https://www.linkedin.com/in/guptaaditi18/", "github": "#"},
]

    cols = st.columns(3)
    for idx, member in enumerate(team_members):
        with cols[idx % 3]:
            st.markdown(f'<div style="text-align: center;"><img src="{member["image"]}" style="width: 200px; height: 200px; border-radius: 50%; margin-right:1000px; margin-top:50px;" /></div>', unsafe_allow_html=True)
            st.subheader(member["name"])
            st.write(member["role"])
            st.write(f"[LinkedIn]({member['linkedin']}) | [GitHub]({member['github']})")


# Page Routing
if st.session_state.page == "Home":
    home()
elif st.session_state.page == "Doctor Chat":
    doctor_chat()
elif st.session_state.page == "Nutrition":
    nutrition()
elif st.session_state.page == "About":
    about()
