import streamlit as st
import requests
import pandas as pd
import json
import time
from datetime import datetime
from streamlit_extras.let_it_rain import rain
from streamlit_mermaid import st_mermaid
import psycopg2
import redis
import os

st.set_page_config(
    layout="wide",
    page_title="Webhook HQ",
    page_icon="🚀",
    initial_sidebar_state="expanded"
)

# Secrets (Create .env file)
BASE_URL = os.getenv("BASE_URL", "https://segwise-webhook-service.onrender.com")

# Constants
ENDPOINTS = {
    "Create Subscription": "/api/v1/subscriptions/",
    "Ingest Webhook": "/api/v1/ingest/{subscription_id}",
    "Check Delivery Status": "/api/v1/status/delivery/{delivery_id}"
}

# Helper Functions
@st.cache_data(ttl=60)
def fetch_deliveries():
    conn = psycopg2.connect("host=34.45.129.153 dbname=segwise-webhook-db user=postgres password=vSaVzzRqQn")
    return pd.read_sql("SELECT id, status, status_code, created_at FROM delivery_logs ORDER BY created_at DESC LIMIT 100", conn)

@st.cache_data(ttl=60)
def fetch_subscriptions():
    conn = psycopg2.connect("host=34.45.129.153 dbname=segwise-webhook-db user=postgres password=vSaVzzRqQn")
    return pd.read_sql("SELECT id, target_url, is_active, created_at FROM subscriptions WHERE is_active = true", conn)

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

# UI - Header
st.title("🚀 Webhook HQ")
st.caption("Real-time Webhook Management Dashboard")

# Updated Live Metrics (Tere Schema ke Hisab se)
@st.cache_data(ttl=60)  # Auto-refresh every 60 sec / 1 min
def get_live_metrics():
    conn = psycopg2.connect("host=34.45.129.153 dbname=segwise-webhook-db user=postgres password=vSaVzzRqQn")
    cursor = conn.cursor()
    
    # 1. Total Deliveries (DeliveryLogs se)
    cursor.execute("SELECT COUNT(*) FROM delivery_logs")
    total_deliveries = cursor.fetchone()[0]
    
    # # 2. Success Rate (status='success' vs total)
    # cursor.execute("""
    #     SELECT 
    #         ROUND(100.0 * 
    #             SUM(CASE WHEN status='success' THEN 1 ELSE 0 END) / 
    #             COUNT(*), 
    #         1) 
    #     FROM delivery_logs
    # """)
    # success_rate = cursor.fetchone()[0] or 0  # Handle divide-by-zero
    
    
    
    # 4. Active Subs (Subscription table se)
    cursor.execute("SELECT COUNT(*) FROM subscriptions WHERE is_active=true")
    active_subs = cursor.fetchone()[0]
    
    conn.close()
    return total_deliveries, active_subs
#, success_rate

# UI Display
total, subs = get_live_metrics() # , success
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Deliveries", f"{total:,}", 
              help="Total webhooks attempted")
# with col2:
#     st.metric("Success Rate", f"{success}%", 
#               delta=f"{success - 95}% vs target" if success else None,
#               help="Successful deliveries percentage")
with col2:
    st.metric("Active Subs", subs, 
              help="Currently active webhook subscriptions")

# Service Selection
service = st.sidebar.radio(
    "SERVICES",
    list(ENDPOINTS.keys()),
    index=0
)

# Main Service Panels
if service == "Create Subscription":
    st.subheader("📝 New Subscription")
    with st.form("create_sub"):
        target_url = st.text_input("Target URL", "https://webhook.site/...")
        secret = st.text_input("Secret Key", type="password")
        event_types = st.multiselect(
            "Event Types",
            ["payment.success", "order.created", "user.updated"],
            default=["payment.success"]
        )
        
        if st.form_submit_button("✨ Create"):
            data = {
                "target_url": target_url,
                "secret": secret,
                "event_types": event_types
            }
            result, status = call_api("POST", ENDPOINTS[service], data)
            
            if status == 200:
                rain(emoji="🎉", font_size=12, falling_speed=3, animation_length=5)
                st.session_state.last_subscription = result["id"]
                st.success("Subscription Created!")
                st.json(result)
            else:
                st.error(f"Error {status}: {result.get('detail', 'Unknown error')}")

elif service == "Ingest Webhook":
    st.subheader("⚡ Webhook Simulator")

    st.markdown("""
    🎯 **Recruiter Test URL:**  
    `https://hook.eu2.make.com/oa7dkj27u6dsx5lcnj7siwcldjg4uj1v` (Copy this to test - no setup needed!)  
    """)

    sub_id = st.text_input(
        "Subscription ID",
        st.session_state.get("last_subscription", ""),
        key="webhook_sub_id"
    )
    payload = st.text_area(
        "Payload (JSON)",
        json.dumps({"event": "payment.success", "amount": 100, "user": "demo"}, indent=2),
        key="webhook_payload"
    )
    
    if st.button("🚀 Fire Webhook", key="fire_webhook"):
        try:
            payload_json = json.loads(payload)
            endpoint = ENDPOINTS[service].format(subscription_id=sub_id)
            
            # Use a container for status that won't conflict with forms
            status_container = st.empty()
            with status_container:
                with st.status("Launching webhook...", state="running") as status:
                    time.sleep(0.5)
                    result, status_code = call_api("POST", endpoint, payload_json)
                    
                    if status_code == 202:
                        status.update(label="✅ Delivered!", state="complete")
                        st.session_state.last_delivery = result["delivery_id"]
                        st.balloons()
                        st.json(result)
                    else:
                        status.update(label=f"❌ Failed ({status_code})", state="error")
                        st.error(result.get("detail", "Unknown error"))
        except json.JSONDecodeError:
            st.error("Invalid JSON payload")

else:  # Delivery Status
    st.subheader("🔍 Delivery Inspector")
    delivery_id = st.text_input(
        "Delivery ID",
        st.session_state.get("last_delivery", ""),
        key="delivery_id_input"
    )
    
    if st.button("🕵️ Investigate", key="investigate_delivery"):
        endpoint = ENDPOINTS[service].format(delivery_id=delivery_id)
        
        # Use spinner outside of any form/expander
        with st.spinner("Fetching delivery logs..."):
            result, status = call_api("GET", endpoint)
            time.sleep(0.3)
            
            if status == 200:
                st.success("Delivery Found")
                st.json(result)
            else:
                st.error(f"Error {status}: {result.get('detail', 'Unknown error')}")

# Database Explorer (Sidebar)
st.sidebar.markdown("---")
st.sidebar.header("🔍 Database Explorer")

if st.sidebar.button("📊 Live Delivery Logs"):
    with st.spinner("Loading real-time data..."):
        df = fetch_deliveries()
        st.dataframe(
            df.style.applymap(
                lambda x: "color: green" if x == "success" else "color: red",
                subset=["status"]
            ),
            use_container_width=True
        )
        st.download_button("💾 Export CSV", df.to_csv(), "deliveries.csv")

if st.sidebar.button("📌 Active Subscriptions"):
    df = fetch_subscriptions()
    st.dataframe(
        df.style.applymap(
            lambda x: "background-color: #C5AF22FF" if x else "background-color: #FFD972FF",
            subset=["is_active"]
        ),
        hide_index=True
    )

# Redis Monitoring
st.sidebar.header("Redis Monitoring")
if st.sidebar.button("Check Celery Queue"):
    try:
        import redis
        r = redis.Redis.from_url("redis://default:MV6QUhIJKDkE1Auf2BYhBQEnP6YzIisv@redis-16388.c279.us-central1-1.gce.redns.redis-cloud.com:16388")
        
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

st.markdown("---")
st.subheader("⚙️ Webhook Flow Diagram")

mermaid_code1 = """
sequenceDiagram
    participant Client
    participant API
    participant Redis
    participant Worker
    participant TargetURL
    
    Client->>API: POST /ingest/{id} (Webhook)
    API->>Redis: Queue Task
    Redis->>Worker: Deliver Webhook
    Worker->>TargetURL: POST Payload
    TargetURL-->>Worker: 200 OK
    Worker->>DB: Log Delivery
"""

st_mermaid(mermaid_code1, height=300)

st.markdown("---")
st.subheader("📊 Database Schema")

mermaid_code2 = """
erDiagram
    SUBSCRIPTIONS ||--o{ DELIVERY_LOGS : has
    SUBSCRIPTIONS {
        uuid id PK
        string target_url
        string secret
        json event_types
    }
    DELIVERY_LOGS {
        uuid id PK
        uuid subscription_id FK
        integer attempt_number
        integer status_code
        text status
    }
"""
st_mermaid(mermaid_code2, height=300)
st.markdown("---")

st.markdown(
    """
    <style>
        .footer {
            text-align: center;
            font-size: 14px;
            color: #888;
            margin-top: 20px;
        }
    </style>
    <div class="footer">
        Made with ❤️ by Manoj for Segwise Backend Webhook Assessment
    </div>
    """,
    unsafe_allow_html=True
)