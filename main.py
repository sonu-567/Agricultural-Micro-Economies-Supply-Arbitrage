
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# ==========================================
# 0. STREAMLIT PAGE CONFIG & STYLING
# ==========================================
st.set_page_config(
    page_title="AgriTrade AI Platform",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern Tech Theme
st.markdown("""
<style>
    .main-header { font-size: 2.2rem; color: #1e4d2b; font-weight: 700; font-family: 'Segoe UI', sans-serif; }
    .sub-header { font-size: 1.1rem; color: #4a7c59; margin-bottom: 20px; }
    .card { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; margin-bottom: 15px; }
    .ai-badge { background-color: #e6f4ea; color: #137333; padding: 4px 12px; border-radius: 16px; font-weight: 600; font-size: 0.85rem; border: 1px solid #ceead6; }
    .metric-value { font-size: 1.8rem; font-weight: 700; color: #1e293b; }
    .metric-label { font-size: 0.9rem; color: #64748b; font-weight: 500; }
    .risk-high { color: #dc2626; font-weight: bold; }
    .risk-med { color: #d97706; font-weight: bold; }
    .risk-low { color: #16a34a; font-weight: bold; }
    .stButton>button { background-color: #1e4d2b; color: white; border-radius: 8px; font-weight: 600; border: none; }
    .stButton>button:hover { background-color: #2e7d32; color: white; }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 1. SYNTHETIC DATA GENERATOR & INITIALIZATION
# ==========================================
@st.cache_data
def load_initial_data():
    np.random.seed(42)
    random.seed(42)
    
    crops_list = ["Tomato", "Potato", "Onion", "Wheat", "Maize"]
    villages = ["Deoghar North", "Deoghar South", "Ranchi Rural", "Patna East", "Gaya Central"]
    
    # 20 Farmers Data
    farmers = []
    for i in range(1, 21):
        village = random.choice(villages)
        crop = random.choice(crops_list)
        qty = round(random.uniform(2000, 12000), -2)
        farmers.append({
            "id": f"FARM-{100+i}",
            "name": f"Farmer {chr(65 + i%26)}{i}",
            "village": village,
            "latitude": 24.4826 + random.uniform(-0.15, 0.15),
            "longitude": 86.6999 + random.uniform(-0.15, 0.15),
            "farm_size_acres": round(random.uniform(1.5, 8.0), 1),
            "crop": crop,
            "current_stock_kg": qty,
            "expected_yield_kg": round(qty * random.uniform(1.1, 1.4), -2),
            "harvest_date": (datetime.now() + timedelta(days=random.randint(1, 10))).strftime("%Y-%m-%d"),
            "quality_grade": random.choice(["Grade A", "Grade B", "Grade A"]),
            "cost_per_kg": round(random.uniform(8.0, 13.0), 1)
        })
    df_farmers = pd.DataFrame(farmers)

    # 5 Markets Data
    markets = [
        {"id": "MKT-1", "name": "Local Village Market", "distance_km": 5, "transport_cost_per_kg": 0.8, "handling_cost_per_kg": 0.5, "demand_level": "Medium"},
        {"id": "MKT-2", "name": "District Agricultural Mandi", "distance_km": 35, "transport_cost_per_kg": 2.2, "handling_cost_per_kg": 0.8, "demand_level": "High"},
        {"id": "MKT-3", "name": "Capital Terminal Market", "distance_km": 110, "transport_cost_per_kg": 4.5, "handling_cost_per_kg": 1.2, "demand_level": "Very High"},
        {"id": "MKT-4", "name": "Regional Processing Hub", "distance_km": 65, "transport_cost_per_kg": 3.0, "handling_cost_per_kg": 1.0, "demand_level": "High"},
        {"id": "MKT-5", "name": "Interstate Export Terminal", "distance_km": 210, "transport_cost_per_kg": 7.0, "handling_cost_per_kg": 1.5, "demand_level": "Extreme"}
    ]
    df_markets = pd.DataFrame(markets)
    
    # Prices matrix per crop per market
    base_prices = {"Tomato": 14, "Potato": 12, "Onion": 18, "Wheat": 22, "Maize": 16}
    price_records = []
    for crop in crops_list:
        base = base_prices[crop]
        for mkt in markets:
            multiplier = 1.0 + (mkt["distance_km"] / 150.0) + random.uniform(-0.05, 0.15)
            price_records.append({
                "crop": crop,
                "market_id": mkt["id"],
                "market_name": mkt["name"],
                "selling_price_per_kg": round(base * multiplier, 1)
            })
    df_prices = pd.DataFrame(price_records)

    # Storage Data
    storages = [
        {"id": "STR-1", "name": "Deoghar Cold Chain Ltd", "type": "Cold Storage", "distance_km": 8, "capacity_kg": 50000, "available_kg": 18000, "cost_per_kg_day": 0.15, "spoilage_reduction": 0.95},
        {"id": "STR-2", "name": "Community Granary Hub", "type": "Warehouse", "distance_km": 4, "capacity_kg": 100000, "available_kg": 45000, "cost_per_kg_day": 0.05, "spoilage_reduction": 0.70},
        {"id": "STR-3", "name": "State Logistics Park", "type": "Cold Storage", "distance_km": 40, "capacity_kg": 200000, "available_kg": 90000, "cost_per_kg_day": 0.12, "spoilage_reduction": 0.98}
    ]
    df_storages = pd.DataFrame(storages)

    # Buyers Data
    buyers = [
        {"id": "BUY-1", "name": "AgriCorp Fresh Ltd", "crop": "Tomato", "required_qty_kg": 15000, "quality": "Grade A", "offered_price": 22.5, "distance_km": 45, "date_needed": "In 3 Days"},
        {"id": "BUY-2", "name": "Metro Mega Retail", "crop": "Tomato", "required_qty_kg": 8000, "quality": "Grade B", "offered_price": 19.0, "distance_km": 15, "date_needed": "Immediate"},
        {"id": "BUY-3", "name": "Golden Granary Exports", "crop": "Wheat", "required_qty_kg": 40000, "quality": "Grade A", "offered_price": 26.0, "distance_km": 120, "date_needed": "In 5 Days"},
        {"id": "BUY-4", "name": "National Food Processors", "crop": "Potato", "required_qty_kg": 25000, "quality": "Grade B", "offered_price": 16.5, "distance_km": 30, "date_needed": "In 2 Days"},
        {"id": "BUY-5", "name": "BioFeed Industries", "crop": "Maize", "required_qty_kg": 18000, "quality": "Grade B", "offered_price": 18.5, "distance_km": 50, "date_needed": "In 4 Days"}
    ]
    df_buyers = pd.DataFrame(buyers)

    return df_farmers, df_markets, df_prices, df_storages, df_buyers

if "farmers" not in st.session_state:
    df_farmers, df_markets, df_prices, df_storages, df_buyers = load_initial_data()
    st.session_state.farmers = df_farmers
    st.session_state.markets = df_markets
    st.session_state.prices = df_prices
    st.session_state.storages = df_storages
    st.session_state.buyers = df_buyers
    st.session_state.notifications = [
        {"id": 1, "time": "10 mins ago", "type": "warning", "msg": "⚠️ Heavy rainfall (82% prob) expected in Deoghar region in 48 hrs. Harvest alert issued."},
        {"id": 2, "time": "1 hr ago", "type": "success", "msg": "📈 Capital Terminal Market tomato prices surged +18% due to supply shortage."},
        {"id": 3, "time": "3 hrs ago", "type": "info", "msg": "🤝 New high-volume buyer offer posted for Grade A Tomato (15,000 kg @ ₹22.5/kg)."}
    ]

# ==========================================
# 2. AGENT-BASED AI ENGINE MODULES
# ==========================================

class CropIntelligenceAgent:
    @staticmethod
    def analyze_supply(df_farmers, target_crop):
        crop_data = df_farmers[df_farmers["crop"] == target_crop]
        total_stock = crop_data["current_stock_kg"].sum()
        total_expected = crop_data["expected_yield_kg"].sum()
        surplus_status = "SURPLUS" if total_stock > 25000 else "BALANCED"
        return {
            "total_farmers": len(crop_data),
            "total_current_stock": total_stock,
            "total_expected_yield": total_expected,
            "status": surplus_status,
            "avg_quality_a_ratio": round((crop_data["quality_grade"] == "Grade A").mean() * 100, 1)
        }


class WeatherRiskAgent:
    @staticmethod
    def evaluate_risk(village):
        # Simulated weather API outputs
        weather_conditions = {
            "Deoghar North": {"temp": 29, "rain_prob": 82, "humidity": 88, "wind": 18, "forecast": "Torrential Downpour in 48h"},
            "Deoghar South": {"temp": 30, "rain_prob": 75, "humidity": 82, "wind": 15, "forecast": "Heavy Showers"},
            "Ranchi Rural": {"temp": 24, "rain_prob": 20, "humidity": 60, "wind": 10, "forecast": "Clear Skies"},
            "Patna East": {"temp": 33, "rain_prob": 45, "humidity": 70, "wind": 12, "forecast": "Moderate Humidity & Light Rain"},
            "Gaya Central": {"temp": 35, "rain_prob": 10, "humidity": 40, "wind": 8, "forecast": "Hot & Dry"}
        }
        w = weather_conditions.get(village, {"temp": 28, "rain_prob": 30, "humidity": 65, "wind": 10, "forecast": "Fair"})
        
        if w["rain_prob"] > 70:
            risk_level = "HIGH"
            harvest_recommendation = "HARVEST IMMEDIATELY (Within 24-48 hrs)"
            risk_color = "🔴"
            reason = f"High rainfall probability ({w['rain_prob']}%) poses extreme risk of crop rot and waterlogging."
        elif w["rain_prob"] > 40:
            risk_level = "MEDIUM"
            harvest_recommendation = "MONITOR CLOSELY (Harvest in 3-5 days)"
            risk_color = "🟡"
            reason = "Moderate precipitation risk. Post-harvest drying facilities may be required."
        else:
            risk_level = "LOW"
            harvest_recommendation = "OPTIMAL HARVEST TIMELINE (Normal schedule)"
            risk_color = "🟢"
            reason = "Favorable weather conditions predicted for next 7 days."
            
        # Added 'village' to the returned dictionary
        return {
            "village": village, 
            **w, 
            "risk_level": risk_level, 
            "risk_color": risk_color, 
            "harvest_recommendation": harvest_recommendation, 
            "reason": reason
        }    
    
class MarketIntelligenceAgent:
    @staticmethod
    def calculate_market_arbitrage(crop, qty_kg, df_markets, df_prices, crop_perishability_days=5):
        crop_prices = df_prices[df_prices["crop"] == crop]
        merged = pd.merge(df_markets, crop_prices, left_on="id", right_on="market_id")
        
        results = []
        for _, row in merged.iterrows():
            gross_revenue = row["selling_price_per_kg"] * qty_kg
            transport_cost = row["transport_cost_per_kg"] * qty_kg
            handling_cost = row["handling_cost_per_kg"] * qty_kg
            
            # Expected loss penalty based on distance & perishability
            loss_pct = min(0.15, (row["distance_km"] / 100.0) * (1.0 / crop_perishability_days))
            expected_loss_val = gross_revenue * loss_pct
            
            net_return = gross_revenue - transport_cost - handling_cost - expected_loss_val
            net_return_per_kg = net_return / qty_kg if qty_kg > 0 else 0
            
            results.append({
                "market_id": row["id"],
                "market_name": row["name"],
                "distance_km": row["distance_km"],
                "demand_level": row["demand_level"],
                "gross_price_per_kg": row["selling_price_per_kg"],
                "transport_cost_total": transport_cost,
                "handling_cost_total": handling_cost,
                "expected_loss_val": expected_loss_val,
                "net_return_total": net_return,
                "net_return_per_kg": round(net_return_per_kg, 2)
            })
        
        df_res = pd.DataFrame(results).sort_values(by="net_return_total", ascending=False)
        return df_res

class LogisticsOptimizationAgent:
    @staticmethod
    def optimize_pooling(df_farmers, target_village, target_crop):
        group = df_farmers[(df_farmers["village"] == target_village) & (df_farmers["crop"] == target_crop)]
        total_volume = group["current_stock_kg"].sum()
        num_farmers = len(group)
        
        # Vehicle selection logic
        if total_volume <= 3000:
            truck_type = "Small Light Commercial Vehicle (3 Ton)"
            solo_rate = 3.5
            pooled_rate = 2.0
        elif total_volume <= 10000:
            truck_type = "Medium Duty Truck (10 Ton)"
            solo_rate = 2.8
            pooled_rate = 1.4
        else:
            truck_type = "Heavy Duty Multi-Axle Truck (25 Ton)"
            solo_rate = 2.2
            pooled_rate = 0.9
            
        distance = 110 # To Capital Terminal Market
        solo_cost_total = sum([f["current_stock_kg"] * solo_rate * (distance/100) for _, f in group.iterrows()])
        pooled_cost_total = total_volume * pooled_rate * (distance/100)
        savings = max(0, solo_cost_total - pooled_cost_total)
        
        return {
            "num_farmers": num_farmers,
            "total_volume_kg": total_volume,
            "recommended_truck": truck_type,
            "solo_cost_total": round(solo_cost_total, 2),
            "pooled_cost_total": round(pooled_cost_total, 2),
            "cost_savings_total": round(savings, 2),
            "savings_pct": round((savings / solo_cost_total * 100) if solo_cost_total > 0 else 0, 1)
        }

class SmartStorageAgent:
    @staticmethod
    def evaluate_storage_vs_sell(current_price_per_kg, qty_kg, df_storages, expected_price_increase_pct=0.25, holding_days=15):
        best_storage = df_storages.sort_values(by="cost_per_kg_day").iloc[0]
        
        sell_now_revenue = current_price_per_kg * qty_kg
        
        expected_future_price = current_price_per_kg * (1 + expected_price_increase_pct)
        storage_fee = best_storage["cost_per_kg_day"] * holding_days * qty_kg
        spoilage_loss = (1 - best_storage["spoilage_reduction"]) * expected_future_price * qty_kg
        
        net_stored_revenue = (expected_future_price * qty_kg) - storage_fee - spoilage_loss
        profit_delta = net_stored_revenue - sell_now_revenue
        
        should_store = profit_delta > 0
        
        return {
            "should_store": should_store,
            "storage_facility": best_storage["name"],
            "holding_days": holding_days,
            "sell_now_revenue": round(sell_now_revenue, 2),
            "net_stored_revenue": round(net_stored_revenue, 2),
            "storage_costs": round(storage_fee, 2),
            "spoilage_risk_val": round(spoilage_loss, 2),
            "net_benefit": round(profit_delta, 2)
        }

class BuyerDiscoveryAgent:
    @staticmethod
    def match_buyers(crop, qty_kg, quality, df_buyers):
        crop_buyers = df_buyers[df_buyers["crop"] == crop].copy()
        if crop_buyers.empty:
            return crop_buyers
            
        scores = []
        for _, row in crop_buyers.iterrows():
            # Scoring algorithm (0 to 100%)
            qty_match = min(1.0, qty_kg / row["required_qty_kg"]) * 40
            quality_match = 30 if row["quality"] == quality else 15
            price_score = min(30, (row["offered_price"] / 25.0) * 30)
            total_score = round(qty_match + quality_match + price_score, 1)
            scores.append(min(99.0, total_score))
            
        crop_buyers["match_score_pct"] = scores
        return crop_buyers.sort_values(by="match_score_pct", ascending=False)

class DecisionEngine:
    @staticmethod
    def generate_unified_strategy(farmer_row, df_markets, df_prices, df_storages, df_buyers):
        crop = farmer_row["crop"]
        qty = farmer_row["current_stock_kg"]
        village = farmer_row["village"]
        quality = farmer_row["quality_grade"]
        
        w_res = WeatherRiskAgent.evaluate_risk(village)
        m_res = MarketIntelligenceAgent.calculate_market_arbitrage(crop, qty, df_markets, df_prices)
        best_market = m_res.iloc[0]
        
        s_res = SmartStorageAgent.evaluate_storage_vs_sell(best_market["gross_price_per_kg"], qty, df_storages)
        buyer_matches = BuyerDiscoveryAgent.match_buyers(crop, qty, quality, df_buyers)
        
        # Decision logic aggregation
        if w_res["risk_level"] == "HIGH":
            primary_action = f"Harvest & Transport to {best_market['market_name']} immediately."
            storage_action = "Avoid long-term storage on-farm due to extreme rainfall risk."
        elif s_res["should_store"]:
            primary_action = f"Store {round(qty*0.4)} kg in {s_res['storage_facility']}; sell {round(qty*0.6)} kg now."
            storage_action = f"Hold stock for {s_res['holding_days']} days for projected revenue upside."
        else:
            primary_action = f"Ship entire stock to {best_market['market_name']} via Pooled Shipment."
            storage_action = "Direct sell recommended; market prices currently peaked."

        baseline_rev = qty * df_prices[(df_prices["crop"] == crop) & (df_prices["market_name"] == "Local Village Market")]["selling_price_per_kg"].values[0]
        opt_net_rev = best_market["net_return_total"]
        added_value = max(0, opt_net_rev - baseline_rev)

        explanations = [
            f"✓ Gross price at {best_market['market_name']} is ₹{best_market['gross_price_per_kg']}/kg (vs Local ₹{df_prices[(df_prices['crop']==crop) & (df_prices['market_name']=='Local Village Market')]['selling_price_per_kg'].values[0]}/kg).",
            f"✓ Net profit margin remains superior (+₹{best_market['net_return_per_kg']}/kg net) after accounting for ₹{round(best_market['transport_cost_total'],0)} transport expenses.",
            f"✓ Weather Risk: {w_res['risk_level']} ({w_res['reason']}).",
            f"✓ Pooling transport with village collective reduces freight overhead by up to 45%."
        ]

        return {
            "primary_action": primary_action,
            "storage_action": storage_action,
            "best_market_name": best_market["market_name"],
            "expected_net_return": best_market["net_return_total"],
            "added_value": added_value,
            "risk_status": w_res["risk_level"],
            "explanations": explanations,
            "top_buyer": buyer_matches.iloc[0]["name"] if not buyer_matches.empty else "Open Market Bidding"
        }


# ==========================================
# 3. SIDEBAR NAVIGATION & USER ROLE SELECTOR
# ==========================================
st.sidebar.image("https://img.icons8.com/color/96/000000/tractor.png", width=64)
st.sidebar.title("AgriTrade AI")
st.sidebar.caption("Agentic Agricultural Economy Platform")

user_role = st.sidebar.selectbox("👤 Select User Role / Context", ["Farmer", "Farmer Collective / Co-op", "Buyer", "System Administrator"])
selected_farmer_id = "FARM-101"

if user_role == "Farmer":
    st.sidebar.divider()
    selected_farmer_id = st.sidebar.selectbox("Select Active Farmer Account", st.session_state.farmers["id"].tolist())

navigation = st.sidebar.radio("📌 Navigation Menu", [
    "Executive Dashboard",
    "Farmer Personal Center",
    "AI Decision Engine & Arbitrage",
    "Weather Risk Intelligence",
    "Market Comparison & Prices",
    "Logistics & Pooling Optimizer",
    "Smart Storage Planner",
    "Buyer Match & AI Negotiation",
    "Collective Management",
    "Analytics & System Database"
])

st.sidebar.divider()
st.sidebar.info("💡 **AI Network Status:** 9/9 Agents Active\n\n*Connected to Regional Ag-Mandi API Data Hub*")


# ==========================================
# 4. VIEW MODULES
# ==========================================

# --- VIEW 1: EXECUTIVE DASHBOARD ---
if navigation == "Executive Dashboard":
    st.markdown("<div class='main-header'>🌾 AgriTrade AI – Command Center</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Real-Time Supply, Risk & Multi-Market Economic Arbitrage Overview</div>", unsafe_allow_html=True)
    
    # Top Metrics
    total_farmers = len(st.session_state.farmers)
    total_stock_tons = round(st.session_state.farmers["current_stock_kg"].sum() / 1000, 1)
    total_expected_tons = round(st.session_state.farmers["expected_yield_kg"].sum() / 1000, 1)
    
    # Calculate macro economic metrics
    total_baseline_val = 0
    total_optimized_val = 0
    for _, f in st.session_state.farmers.iterrows():
        opt = DecisionEngine.generate_unified_strategy(f, st.session_state.markets, st.session_state.prices, st.session_state.storages, st.session_state.buyers)
        total_baseline_val += f["current_stock_kg"] * 14.0 # Base local rate
        total_optimized_val += opt["expected_net_return"]
        
    added_rev = max(0, total_optimized_val - total_baseline_val)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown("<div class='card'><div class='metric-label'>Total Registered Farmers</div><div class='metric-value'>{}</div></div>".format(total_farmers), unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='card'><div class='metric-label'>Available Crop Stock</div><div class='metric-value'>{} T</div></div>".format(total_stock_tons), unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='card'><div class='metric-label'>Expected Harvest</div><div class='metric-value'>{} T</div></div>".format(total_expected_tons), unsafe_allow_html=True)
    with col4:
        st.markdown("<div class='card'><div class='metric-label'>Est. Market Net Value</div><div class='metric-value'>₹{:,.0f}</div></div>".format(total_optimized_val), unsafe_allow_html=True)
    with col5:
        st.markdown("<div class='card'><div class='metric-label'>AI-Unlocked Added Revenue</div><div class='metric-value' style='color:#16a34a;'>+₹{:,.0f}</div></div>".format(added_rev), unsafe_allow_html=True)

    st.markdown("---")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("🗺️ Regional Crop Stock & Weather Risk Distribution")
        # Map Display using Plotly Scatter Geo / Mapbox representation
        df_f = st.session_state.farmers.copy()
        
        # Determine risks for visual color
        df_f["Risk_Level"] = df_f["village"].apply(lambda v: WeatherRiskAgent.evaluate_risk(v)["risk_level"])
        
        fig_map = px.scatter_mapbox(
            df_f,
            lat="latitude",
            lon="longitude",
            color="Risk_Level",
            size="current_stock_kg",
            hover_name="name",
            hover_data=["crop", "village", "current_stock_kg", "quality_grade"],
            color_discrete_map={"HIGH": "red", "MEDIUM": "orange", "LOW": "green"},
            zoom=8,
            height=420
        )
        fig_map.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)

    with col_right:
        st.subheader("🔔 Live System Intelligence Notifications")
        for note in st.session_state.notifications:
            if note["type"] == "warning":
                st.warning(f"**[{note['time']}]** {note['msg']}")
            elif note["type"] == "success":
                st.success(f"**[{note['time']}]** {note['msg']}")
            else:
                st.info(f"**[{note['time']}]** {note['msg']}")

    st.markdown("---")
    
    # Analytics Breakdown Chart
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.subheader("📊 Crop Supply Volume by Village")
        fig_bar = px.bar(df_f, x="village", y="current_stock_kg", color="crop", barmode="group", title="Current Available Stock (kg)")
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col_c2:
        st.subheader("📈 Multi-Market Price Spread Comparison")
        fig_line = px.line(st.session_state.prices, x="market_name", y="selling_price_per_kg", color="crop", markers=True, title="Gross Selling Price per Market (₹/kg)")
        st.plotly_chart(fig_line, use_container_width=True)


# --- VIEW 2: FARMER PERSONAL CENTER ---
elif navigation == "Farmer Personal Center":
    farmer = st.session_state.farmers[st.session_state.farmers["id"] == selected_farmer_id].iloc[0]
    
    st.markdown(f"<div class='main-header'>👨‍🌾 Farmer Command Dashboard – {farmer['name']}</div>", unsafe_allow_html=True)
    st.markdown(f"<span class='ai-badge'>Location: {farmer['village']}</span> &nbsp; <span class='ai-badge'>Farm Size: {farmer['farm_size_acres']} Acres</span>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Farmer Summary Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Crop Type", farmer["crop"])
    with col2:
        st.metric("Current Available Stock", f"{farmer['current_stock_kg']:,} kg")
    with col3:
        st.metric("Expected Harvest Yield", f"{farmer['expected_yield_kg']:,} kg")
    with col4:
        st.metric("Quality Rating", farmer["quality_grade"])

    st.markdown("---")
    
    # AI Recommendation Card for this Farmer
    st.subheader("🤖 Personalized Agentic Strategy Recommendation")
    
    strat = DecisionEngine.generate_unified_strategy(farmer, st.session_state.markets, st.session_state.prices, st.session_state.storages, st.session_state.buyers)
    
    with st.container():
        st.markdown(f"""
        <div class="card" style="border-left: 6px solid #16a34a;">
            <h3>Strategic Recommendation: <span style="color:#1e4d2b;">{strat['primary_action']}</span></h3>
            <p><strong>Storage & Inventory Advice:</strong> {strat['storage_action']}</p>
            <h4 style="color:#16a34a;">Expected Additional Net Revenue: +₹{strat['added_value']:,.2f}</h4>
        </div>
        """, unsafe_allow_html=True)

        col_act1, col_act2, col_act3 = st.columns([1, 1, 3])
        with col_act1:
            if st.button("✅ Accept AI Recommendation", key="btn_acc"):
                st.success("Recommendation accepted! Action tasks routed to logistics and buyer dispatch.")
        with col_act2:
            if st.button("❌ Reject / Manual Mode", key="btn_rej"):
                st.info("Switched to manual dispatch mode.")

    st.markdown("---")
    
    # Crop Input Form
    with st.expander("📝 Update Crop Stock & Harvest Info"):
        with st.form("update_crop_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                new_crop = st.selectbox("Crop Type", ["Tomato", "Potato", "Onion", "Wheat", "Maize"], index=["Tomato", "Potato", "Onion", "Wheat", "Maize"].index(farmer["crop"]))
                new_stock = st.number_input("Available Stock (kg)", value=float(farmer["current_stock_kg"]), step=100.0)
            with c2:
                new_yield = st.number_input("Expected Harvest Yield (kg)", value=float(farmer["expected_yield_kg"]), step=100.0)
                new_quality = st.selectbox("Quality Grade", ["Grade A", "Grade B", "Grade C"], index=["Grade A", "Grade B", "Grade C"].index(farmer["quality_grade"]))
            with c3:
                new_date = st.date_input("Expected Harvest Date", datetime.strptime(farmer["harvest_date"], "%Y-%m-%d"))
                submitted = st.form_submit_button("Save Farm Data")
                if submitted:
                    st.session_state.farmers.loc[st.session_state.farmers["id"] == selected_farmer_id, "crop"] = new_crop
                    st.session_state.farmers.loc[st.session_state.farmers["id"] == selected_farmer_id, "current_stock_kg"] = new_stock
                    st.session_state.farmers.loc[st.session_state.farmers["id"] == selected_farmer_id, "expected_yield_kg"] = new_yield
                    st.session_state.farmers.loc[st.session_state.farmers["id"] == selected_farmer_id, "quality_grade"] = new_quality
                    st.session_state.farmers.loc[st.session_state.farmers["id"] == selected_farmer_id, "harvest_date"] = new_date.strftime("%Y-%m-%d")
                    st.success("Farm profile updated successfully!")
                    st.rerun()


# --- VIEW 3: AI DECISION ENGINE & ARBITRAGE ---
elif navigation == "AI Decision Engine & Arbitrage":
    st.markdown("<div class='main-header'>🧠 Multi-Agent Decision Engine & Supply Arbitrage</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Continuous multi-factor analysis synthesizing risk, price, freight, and storage</div>", unsafe_allow_html=True)

    farmer_sel = st.selectbox("Select Target Farmer Profile for Analysis", st.session_state.farmers["name"].tolist())
    farmer_row = st.session_state.farmers[st.session_state.farmers["name"] == farmer_sel].iloc[0]

    st.markdown("---")
    st.subheader("🔄 Multi-Agent Workflow Pipeline Execution")

    # Workflow Visual Representation
    col_a, col_b, col_c, col_d, col_e = st.columns(5)
    col_a.metric("1. Crop Agent", f"{farmer_row['crop']} ({farmer_row['current_stock_kg']:,} kg)")
    w_eval = WeatherRiskAgent.evaluate_risk(farmer_row["village"])
    col_b.metric("2. Weather Risk", f"{w_eval['risk_color']} {w_eval['risk_level']}")
    m_eval = MarketIntelligenceAgent.calculate_market_arbitrage(farmer_row["crop"], farmer_row["current_stock_kg"], st.session_state.markets, st.session_state.prices).iloc[0]
    col_c.metric("3. Arbitrage Market", m_eval["market_name"])
    l_eval = LogisticsOptimizationAgent.optimize_pooling(st.session_state.farmers, farmer_row["village"], farmer_row["crop"])
    col_d.metric("4. Logistics Pooling", f"-{l_eval['savings_pct']}% Freight Cost")
    s_eval = SmartStorageAgent.evaluate_storage_vs_sell(m_eval["gross_price_per_kg"], farmer_row["current_stock_kg"], st.session_state.storages)
    col_e.metric("5. Smart Storage", "Store Partial" if s_eval["should_store"] else "Sell Direct")

    st.markdown("---")
    
    # Detailed Arbitrage Breakdown Table
    st.subheader(f"💡 Net Value Arbitrage Analysis ({farmer_row['crop']} - {farmer_row['current_stock_kg']:,} kg)")
    arbitrage_df = MarketIntelligenceAgent.calculate_market_arbitrage(farmer_row["crop"], farmer_row["current_stock_kg"], st.session_state.markets, st.session_state.prices)
    
    st.dataframe(
        arbitrage_df[["market_name", "distance_km", "gross_price_per_kg", "transport_cost_total", "handling_cost_total", "expected_loss_val", "net_return_total", "net_return_per_kg"]],
        column_config={
            "market_name": "Target Market",
            "distance_km": "Distance (km)",
            "gross_price_per_kg": "Price (₹/kg)",
            "transport_cost_total": "Transport Cost (₹)",
            "handling_cost_total": "Handling Cost (₹)",
            "expected_loss_val": "Est. Spoilage (₹)",
            "net_return_total": "Net Return Total (₹)",
            "net_return_per_kg": "Net Return (₹/kg)"
        },
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    
    # AI Explainability Section
    st.subheader("💬 AI Explainability & Reasoning Engine")
    strat = DecisionEngine.generate_unified_strategy(farmer_row, st.session_state.markets, st.session_state.prices, st.session_state.storages, st.session_state.buyers)
    
    for exp in strat["explanations"]:
        st.write(f"- {exp}")


# --- VIEW 4: WEATHER RISK INTELLIGENCE ---
elif navigation == "Weather Risk Intelligence":
    st.markdown("<div class='main-header'>🌦️ Hyper-Local Weather Risk Agent</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Predictive Agricultural Risk & Extreme Weather Harvesting Advisories</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    
    with col1:
        sel_village = st.selectbox("Select Village Cluster", ["Deoghar North", "Deoghar South", "Ranchi Rural", "Patna East", "Gaya Central"])
        w_data = WeatherRiskAgent.evaluate_risk(sel_village)
        
        st.markdown(f"""
        <div class="card">
            <h3>Village: {sel_village}</h3>
            <h4>Risk Level: {w_data['risk_color']} {w_data['risk_level']}</h4>
            <p><strong>Forecast:</strong> {w_data['forecast']}</p>
            <p><strong>Temperature:</strong> {w_data['temp']}°C</p>
            <p><strong>Rainfall Probability:</strong> {w_data['rain_prob']}%</p>
            <p><strong>Relative Humidity:</strong> {w_data['humidity']}%</p>
            <hr>
            <p><strong>Harvest Action Advisory:</strong><br><span style="color:#d97706; font-weight:bold;">{w_data['harvest_recommendation']}</span></p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.subheader("🌦️ Regional Rainfall Probability Forecast")
        villages_list = ["Deoghar North", "Deoghar South", "Ranchi Rural", "Patna East", "Gaya Central"]
        risk_summary = [WeatherRiskAgent.evaluate_risk(v) for v in villages_list]
        df_w = pd.DataFrame(risk_summary)
        
        fig_w = px.bar(df_w, x="village", y="rain_prob", color="risk_level",
                       color_discrete_map={"HIGH": "red", "MEDIUM": "orange", "LOW": "green"},
                       labels={"rain_prob": "Rain Probability (%)", "village": "Village Hub"},
                       title="Micro-Climate Rain Risk across Regions")
        st.plotly_chart(fig_w, use_container_width=True)

    st.markdown("---")
    st.subheader("⚠️ High Weather-Risk Action Recommendations")
    high_risk_farmers = st.session_state.farmers[st.session_state.farmers["village"].isin(
        [v for v in villages_list if WeatherRiskAgent.evaluate_risk(v)["risk_level"] == "HIGH"]
    )]
    
    st.dataframe(
        high_risk_farmers[["name", "village", "crop", "current_stock_kg", "harvest_date"]],
        use_container_width=True,
        hide_index=True
    )


# --- VIEW 5: MARKET COMPARISON & PRICES ---
elif navigation == "Market Comparison & Prices":
    st.markdown("<div class='main-header'>📈 Real-Time Market Intelligence & Price Spread</div>", unsafe_allow_html=True)

    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        selected_crop = st.selectbox("Select Target Crop for Market Analysis", ["Tomato", "Potato", "Onion", "Wheat", "Maize"])
    with col_filter2:
        sample_qty = st.number_input("Simulated Batch Quantity (kg)", value=5000, step=1000)

    arbitrage_df = MarketIntelligenceAgent.calculate_market_arbitrage(selected_crop, sample_qty, st.session_state.markets, st.session_state.prices)

    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        fig_gross = px.bar(arbitrage_df, x="market_name", y="gross_price_per_kg", color="market_name", title=f"Gross Market Price per kg for {selected_crop} (₹)")
        st.plotly_chart(fig_gross, use_container_width=True)
    
    with col_chart2:
        fig_net = px.bar(arbitrage_df, x="market_name", y="net_return_per_kg", color="net_return_per_kg", color_continuous_scale="Viridis", title="Net Return per kg (After Logistics & Loss) (₹)")
        st.plotly_chart(fig_net, use_container_width=True)

    st.markdown("---")
    st.subheader("🏆 Market Arbitrage Ranking")
    st.dataframe(arbitrage_df, use_container_width=True, hide_index=True)


# --- VIEW 6: LOGISTICS & POOLING OPTIMIZER ---
elif navigation == "Logistics & Pooling Optimizer":
    st.markdown("<div class='main-header'>🚚 Logistics Optimization & Freight Pooling Agent</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Combine micro-shipments to unlock economies of scale and cut transport costs</div>", unsafe_allow_html=True)

    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        target_v = st.selectbox("Select Farming Village Cluster", st.session_state.farmers["village"].unique())
    with col_sel2:
        target_c = st.selectbox("Select Crop", st.session_state.farmers["crop"].unique())

    pooling_res = LogisticsOptimizationAgent.optimize_pooling(st.session_state.farmers, target_v, target_c)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Participating Farmers", pooling_res["num_farmers"])
    c2.metric("Total Pooled Cargo Volume", f"{pooling_res['total_volume_kg']:,} kg")
    c3.metric("Solo Logistics Cost", f"₹{pooling_res['solo_cost_total']:,}")
    c4.metric("Pooled Logistics Cost", f"₹{pooling_res['pooled_cost_total']:,}", delta=f"-{pooling_res['savings_pct']}% Savings")

    st.markdown("---")
    st.subheader(f"🚛 Recommended Dispatch Route: {target_v} ➔ Capital Terminal Market")
    st.info(f"**Recommended Fleet Assignment:** {pooling_res['recommended_truck']}")

    # Display Farmers participating in this pooled route
    pooled_farmers = st.session_state.farmers[(st.session_state.farmers["village"] == target_v) & (st.session_state.farmers["crop"] == target_c)]
    
    st.subheader("Participating Cargo Manifest")
    st.dataframe(pooled_farmers[["id", "name", "village", "current_stock_kg", "quality_grade"]], use_container_width=True, hide_index=True)


# --- VIEW 7: SMART STORAGE PLANNER ---
elif navigation == "Smart Storage Planner":
    st.markdown("<div class='main-header'>🏪 Smart Storage & Inventory Agent</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        crop_sel = st.selectbox("Crop Type", ["Tomato", "Potato", "Onion", "Wheat", "Maize"])
        qty_input = st.number_input("Cargo Quantity (kg)", value=10000, step=1000)
    with c2:
        curr_price = st.number_input("Current Spot Market Price (₹/kg)", value=16.0, step=0.5)
        days_hold = st.slider("Target Holding Duration (Days)", 5, 60, 15)
    with c3:
        exp_increase = st.slider("Expected Price Appreciation (%)", 0, 50, 20) / 100.0

    st.markdown("---")
    
    storage_res = SmartStorageAgent.evaluate_storage_vs_sell(curr_price, qty_input, st.session_state.storages, exp_increase, days_hold)

    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.markdown(f"""
        <div class="card">
            <h3>Immediate Sale Scenario</h3>
            <h2>Gross Revenue: ₹{storage_res['sell_now_revenue']:,.2f}</h2>
            <p>Zero storage fees, zero holding risk.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_res2:
        card_border = "#16a34a" if storage_res["should_store"] else "#dc2626"
        st.markdown(f"""
        <div class="card" style="border-left: 6px solid {card_border};">
            <h3>Storage & Deferred Sale Scenario ({storage_res['storage_facility']})</h3>
            <h2>Net Revenue: ₹{storage_res['net_stored_revenue']:,.2f}</h2>
            <p><strong>Storage Cost:</strong> ₹{storage_res['storage_costs']:,.2f}</p>
            <p><strong>Est. Spoilage Loss:</strong> ₹{storage_res['spoilage_risk_val']:,.2f}</p>
            <h3>Net Advantage: <span style="color:{card_border};">₹{storage_res['net_benefit']:,.2f}</span></h3>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("🏛️ Storage Facility Availability Directory")
    st.dataframe(st.session_state.storages, use_container_width=True, hide_index=True)


# --- VIEW 8: BUYER MATCH & AI NEGOTIATION ---
elif navigation == "Buyer Match & AI Negotiation":
    st.markdown("<div class='main-header'>🤝 Buyer Discovery & AI Negotiation Simulator</div>", unsafe_allow_html=True)

    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        sel_farmer_id = st.selectbox("Select Farmer", st.session_state.farmers["id"].tolist(), key="buyer_farmer_sel")
        farmer = st.session_state.farmers[st.session_state.farmers["id"] == sel_farmer_id].iloc[0]
    
    matches = BuyerDiscoveryAgent.match_buyers(farmer["crop"], farmer["current_stock_kg"], farmer["quality_grade"], st.session_state.buyers)
    
    if matches.empty:
        st.warning(f"No direct commercial buyers found matching requirements for {farmer['crop']}.")
    else:
        st.subheader(f"🎯 Top Buyer Matches for {farmer['name']} ({farmer['crop']} - {farmer['current_stock_kg']} kg)")
        
        top_buyer = matches.iloc[0]
        
        col_b1, col_b2 = st.columns([1, 1])
        with col_b1:
            st.dataframe(matches[["name", "required_qty_kg", "quality", "offered_price", "match_score_pct"]], use_container_width=True, hide_index=True)
            
        with col_b2:
            st.markdown(f"""
            <div class="card" style="border-left: 6px solid #2563eb;">
                <h3>Selected Buyer: {top_buyer['name']}</h3>
                <p><strong>Initial Buyer Offer:</strong> ₹{top_buyer['offered_price']}/kg</p>
                <p><strong>Required Quantity:</strong> {top_buyer['required_qty_kg']:,} kg</p>
                <p><strong>Match AI Score:</strong> {top_buyer['match_score_pct']}%</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("💬 Interactive AI Negotiation Simulation")
            
            # Interactive Negotiation logic
            min_target_price = farmer["cost_per_kg"] + 4.0
            rec_target_price = top_buyer["offered_price"] + 1.5
            
            st.write(f"**AI Guidance:** Minimum breakeven threshold: **₹{farmer['cost_per_kg'] + 2.0}/kg**. Recommended Counter-Offer: **₹{rec_target_price}/kg**.")
            
            user_offer = st.number_input("Enter Your Counter-Offer Price (₹/kg)", value=float(rec_target_price), step=0.5)
            
            if st.button("Submit Counter-Offer"):
                if user_offer <= top_buyer["offered_price"]:
                    st.success(f"🎉 Buyer {top_buyer['name']} ACCEPTED your offer immediately at ₹{user_offer}/kg!")
                elif user_offer <= top_buyer["offered_price"] + 2.0:
                    st.info(f"🤝 Buyer counter-negotiated and agreed to split at ₹{round((user_offer + top_buyer['offered_price'])/2, 2)}/kg!")
                else:
                    st.error(f"❌ Buyer REJECTED your offer of ₹{user_offer}/kg as above market ceiling. Current best offer stands at ₹{top_buyer['offered_price'] + 0.5}/kg.")


# --- VIEW 9: COLLECTIVE MANAGEMENT ---
elif navigation == "Collective Management":
    st.markdown("<div class='main-header'>👥 Farmer Collective / Co-operative Management</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <h2>Active Collective: Deoghar Tomato & Vegetable Co-op</h2>
        <p>Empowering smallholders through pooled bargaining, bulk logistics, and unified cold chain access.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Active Members", len(st.session_state.farmers))
    c2.metric("Combined Tomato Inventory", f"{st.session_state.farmers[st.session_state.farmers['crop']=='Tomato']['current_stock_kg'].sum():,} kg")
    c3.metric("Avg Regional Spot Rate", "₹16.5 / kg")
    c4.metric("Co-op Bargaining Power Price", "₹22.0 / kg", delta="+33%")

    st.markdown("---")
    st.subheader("📦 Co-op Collective Inventory Aggregation")
    
    df_agg = st.session_state.farmers.groupby("crop").agg(
        Total_Farmers=("id", "count"),
        Total_Current_Stock_kg=("current_stock_kg", "sum"),
        Total_Expected_Yield_kg=("expected_yield_kg", "sum")
    ).reset_index()

    st.dataframe(df_agg, use_container_width=True, hide_index=True)


# --- VIEW 10: ANALYTICS & DATABASE ---
elif navigation == "Analytics & System Database":
    st.markdown("<div class='main-header'>📊 Platform Analytics & System Database</div>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.columns(3)
    
    st.subheader("💾 Live Platform Relational Tables")
    
    table_choice = st.selectbox("Select Database Table to Inspect", ["Farmers Data", "Markets Data", "Price Matrix", "Storages Directory", "Buyers Directory"])
    
    if table_choice == "Farmers Data":
        st.dataframe(st.session_state.farmers, use_container_width=True)
    elif table_choice == "Markets Data":
        st.dataframe(st.session_state.markets, use_container_width=True)
    elif table_choice == "Price Matrix":
        st.dataframe(st.session_state.prices, use_container_width=True)
    elif table_choice == "Storages Directory":
        st.dataframe(st.session_state.storages, use_container_width=True)
    elif table_choice == "Buyers Directory":
        st.dataframe(st.session_state.buyers, use_container_width=True)  