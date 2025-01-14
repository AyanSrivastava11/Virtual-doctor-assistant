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
    {"name": "Ayan Srivastava", "role": "Data Scientist", "image": "https://media.licdn.com/dms/image/v2/D4D03AQG8LaH9lnxJ8Q/profile-displayphoto-shrink_800_800/profile-displayphoto-shrink_800_800/0/1689078172220?e=1742428800&v=beta&t=OBgBT8goDJYkk4mksWOj12bbyB2I6GhDrzQg7B52ZJI", "linkedin": "https://www.linkedin.com/in/ayan-srivastava-017a89259/", "github": "https://github.com/AyanSrivastava11"},

    {"name": "Aditi Singh", "role": "Data Analyst", "image": "https://media.licdn.com/dms/image/v2/D4D03AQEz1Pq8446DEQ/profile-displayphoto-shrink_800_800/B4DZRlMFVeHIAc-/0/1736864454743?e=1742428800&v=beta&t=FXPSyIoxLXC0yBd3yG8XZC65cqG7xBfPJi_Oxcn8esc","linkedin":"https://www.linkedin.com/in/aditi-singh-266456253/", "github": "https://github.com/AyanSrivastava11"},

    {"name": "Aditi Gupta", "role": "Front End Developer", "image": "https://media.licdn.com/dms/image/v2/D5603AQGnk1vrfCWxwA/profile-displayphoto-shrink_800_800/B56ZRlLwIRHoAg-/0/1736864369350?e=1742428800&v=beta&t=nYcibn1X6pmI11F_xGaAe7Jkyx-LOdLFFFGEN3YZtWk", "linkedin": "https://www.linkedin.com/in/guptaaditi18/?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app", "github": "https://github.com/Aditi-code123"},
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
