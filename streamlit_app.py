# streamlit_app.py
import streamlit as st
import requests
import pandas as pd
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"  # Change if hosted
ENDPOINTS = {
    "Create Subscription": "/api/v1/subscriptions/",
    "Ingest Webhook": "/api/v1/ingest/{subscription_id}",
    "Check Delivery Status": "/api/v1/status/delivery/{delivery_id}"
}

# Helper functions
def call_api(method, endpoint, data=None):
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        else:
            response = requests.post(url, json=data)
        return response.json(), response.status_code
    except Exception as e:
        return {"error": str(e)}, 500

# Streamlit UI
st.set_page_config(layout="wide")
st.title("Webhook Delivery Service Dashboard")

# Sidebar - Service Selection
service = st.sidebar.selectbox(
    "Select Service",
    list(ENDPOINTS.keys())
)

# Main Content Area
if service == "Create Subscription":
    st.header("Create New Subscription")
    with st.form("create_sub"):
        target_url = st.text_input("Target URL", 
                                 "https://webhook.site/your-unique-url")
        secret = st.text_input("Secret Key", "test-secret-123")
        event_types = st.multiselect(
            "Event Types",
            ["payment.success", "order.created", "user.updated"],
            default=["payment.success"]
        )
        
        if st.form_submit_button("Create Subscription"):
            data = {
                "target_url": target_url,
                "secret": secret,
                "event_types": event_types
            }
            result, status = call_api("POST", ENDPOINTS[service], data)
            
            if status == 200:
                st.success("Subscription Created!")
                st.json(result)
                st.session_state.last_subscription = result["id"]
            else:
                st.error(f"Error {status}: {result.get('detail', 'Unknown error')}")

elif service == "Ingest Webhook":
    st.header("Ingest Webhook")
    with st.form("ingest_webhook"):
        subscription_id = st.text_input(
            "Subscription ID",
            st.session_state.get("last_subscription", "")
        )
        payload = st.text_area(
            "Payload (JSON)",
            json.dumps({"event": "payment.success", "amount": 100}, indent=2)
        )
        
        if st.form_submit_button("Send Webhook"):
            try:
                payload_json = json.loads(payload)
                endpoint = ENDPOINTS[service].format(subscription_id=subscription_id)
                result, status = call_api("POST", endpoint, payload_json)
                
                if status == 202:
                    st.success("Webhook Accepted!")
                    st.json(result)
                    st.session_state.last_delivery = result["delivery_id"]
                else:
                    st.error(f"Error {status}: {result.get('detail', 'Unknown error')}")
            except json.JSONDecodeError:
                st.error("Invalid JSON payload")

else:  # Delivery Status
    st.header("Check Delivery Status")
    with st.form("check_status"):
        delivery_id = st.text_input(
            "Delivery ID",
            st.session_state.get("last_delivery", "")
        )
        
        if st.form_submit_button("Check Status"):
            endpoint = ENDPOINTS[service].format(delivery_id=delivery_id)
            result, status = call_api("GET", endpoint)
            
            if status == 200:
                st.success("Delivery Found")
                st.json(result)
            else:
                st.error(f"Error {status}: {result.get('detail', 'Unknown error')}")

# Database Inspection Section
st.sidebar.markdown("---")
st.sidebar.header("Database Inspection")

if st.sidebar.button("View Recent Deliveries"):
    try:
        # Replace with your actual DB connection
        import psycopg2
        conn = psycopg2.connect("host=34.41.72.59 dbname=webhook-db user=postgres password=segwise123")
        df = pd.read_sql("""
            SELECT id, status, status_code, created_at 
            FROM delivery_logs 
            ORDER BY created_at DESC 
            LIMIT 20
        """, conn)
        st.dataframe(df)
    except Exception as e:
        st.error(f"DB Error: {str(e)}")

if st.sidebar.button("View Active Subscriptions"):
    try:
        import psycopg2
        conn = psycopg2.connect("host=34.41.72.59 dbname=webhook-db user=postgres password=segwise123")
        df = pd.read_sql("""
            SELECT id, target_url, is_active, created_at 
            FROM subscriptions 
            WHERE is_active = true
            LIMIT 20
        """, conn)
        st.dataframe(df)
    except Exception as e:
        st.error(f"DB Error: {str(e)}")

# Redis Monitoring
st.sidebar.header("Redis Monitoring")
if st.sidebar.button("Check Celery Queue"):
    try:
        import redis
        # Fixed URL - added port 15996 after the colon
        r = redis.Redis.from_url("redis://default:GRhoCbTJb8HTZAxa430RUAeTrDMQBI1M@redis-15996.fcrce190.us-east-1-1.ec2.redns.redis-cloud.com:15996")
        
        # Add timeout to prevent infinite waiting
        queue_length = r.llen("celery")
        st.info(f"Pending tasks in queue: {queue_length}")
        
        if queue_length > 0:
            sample_task = r.lrange("celery", 0, 0)[0]
            st.text_area("Sample Task", sample_task.decode('utf-8'))
    except redis.exceptions.ConnectionError as e:
        st.error(f"Redis Connection Error: {str(e)}")
    except redis.exceptions.TimeoutError as e:
        st.error(f"Redis Timeout Error: {str(e)}")
    except Exception as e:
        st.error(f"Redis Error: {str(e)}")