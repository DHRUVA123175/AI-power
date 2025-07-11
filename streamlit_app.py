import openai
import os
import streamlit as st
from dotenv import load_dotenv
from pathlib import Path
import razorpay
import json

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Razorpay credentials
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# Streamlit UI
st.set_page_config(page_title="AI Business Plan Generator", layout="wide")
st.title("📊 AI Business Plan Generator")
st.write("Generate a professional business plan for your startup or project using AI.")

# Session state
if 'paid' not in st.session_state:
    st.session_state.paid = False

# Collect inputs
idea = st.text_area("Business Idea", "An AI-powered app that generates investor-ready business plans for startups.")
industry = st.text_input("Industry", "SaaS / Artificial Intelligence")
audience = st.text_input("Target Audience", "Startup founders, freelancers, small business owners")
funding = st.text_input("Funding Needs", "$50,000")
goals = st.text_area("Business Goals", "To simplify and speed up the business planning process using AI")

# Razorpay payment logic
if not st.session_state.paid:
    st.subheader("💳 Payment")
    if st.button("🔒 Pay ₹99 to Generate Plan"):
        order_data = {
            'amount': 9900,  # Amount in paise (₹99)
            'currency': 'INR',
            'payment_capture': '1'
        }
        order = client.order.create(data=order_data)

        st.markdown("""
        <form action="https://api.razorpay.com/v1/checkout/embedded" method="POST">
            <input type="hidden" name="key_id" value="{key}"/>
            <input type="hidden" name="order_id" value="{order_id}"/>
            <input type="hidden" name="name" value="AI Business Plan Generator"/>
            <input type="hidden" name="description" value="Generate business plan using AI"/>
            <input type="hidden" name="amount" value="9900"/>
            <input type="hidden" name="prefill[name]" value="Dhruva"/>
            <input type="hidden" name="prefill[email]" value="test@example.com"/>
            <input type="hidden" name="theme[color]" value="#3399cc"/>
            <input type="submit" value="Pay with Razorpay"/>
        </form>
        """.format(key=RAZORPAY_KEY_ID, order_id=order['id']), unsafe_allow_html=True)
        st.stop()
else:
    st.success("✅ Payment Successful. You may now generate your plan.")

# Temporary button for testing purposes
if st.button("✅ I have completed payment"):
    st.session_state.paid = True

# Generate plan if paid
if st.session_state.paid and st.button("🚀 Generate Business Plan"):
    prompt = f"""
    You are an expert business consultant and startup strategist. Using the details below, generate a comprehensive and structured business plan that is suitable for presentation to investors, banks, or stakeholders.

    Inputs:
    - Business Idea: {idea}
    - Industry: {industry}
    - Target Audience: {audience}
    - Funding Needs: {funding}
    - Business Goals: {goals}

    The business plan should be well-organized and include the following sections:

    1. Executive Summary
    2. Company Description
    3. Market Analysis
    4. Product/Service Overview
    5. Marketing & Sales Strategy
    6. Operational Plan
    7. Financial Projections
    8. Competitor Analysis
    9. Funding Requirements & Usage
    10. Conclusion & Future Vision

    Make sure the tone is professional, insightful, and tailored for a serious business proposal. Add bullet points or tables wherever needed.
    """

    with st.spinner("Generating your business plan..."):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional business strategist."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3000
        )

        business_plan = response['choices'][0]['message']['content']
        st.subheader("📄 Generated Business Plan")
        st.write(business_plan)

        # Save to file
        with open("business_plan.txt", "w", encoding="utf-8") as f:
            f.write(business_plan)

        with open("business_plan.txt", "r") as file:
            st.download_button(label="📥 Download Plan as TXT",
                               data=file,
                               file_name="business_plan.txt")
