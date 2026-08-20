import streamlit as st
import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from graph import graph
from state import FarmInput


st.set_page_config(
    page_title="Farm Management Agent",
    page_icon="🌾",
    layout="wide"
)

st.title("🌾 Farm Management Agent")
st.write("Enter farm conditions to generate a farm management plan.")


with st.form("farm_input"):

    st.header("Farm Information")

    col1, col2, col3 = st.columns(3)

    with col1:
        land_acres = st.number_input(
            "Land (acres)",
            min_value=0.1,
            value=10.0
        )

    with col2:
        capital = st.number_input(
            "Available Capital (₹)",
            min_value=0.0,
            value=500000.0
        )

    with col3:
        water = st.number_input(
            "Available Water (liters)",
            min_value=0.0,
            value=500000.0
        )

    st.header("Soil Conditions")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        soil_n = st.number_input(
            "Nitrogen (N)",
            min_value=0.0,
            value=45.0
        )

    with col2:
        soil_p = st.number_input(
            "Phosphorus (P)",
            min_value=0.0,
            value=20.0
        )

    with col3:
        soil_k = st.number_input(
            "Potassium (K)",
            min_value=0.0,
            value=40.0
        )

    with col4:
        soil_ph = st.number_input(
            "Soil pH",
            min_value=0.0,
            max_value=14.0,
            value=6.8
        )

    with col5:
        soil_moisture = st.number_input(
            "Soil Moisture (%)",
            min_value=0.0,
            max_value=100.0,
            value=32.0
        )

    st.header("Weather")

    col1, col2 = st.columns(2)

    with col1:
        temperature = st.number_input(
            "Temperature (°C)",
            value=24.0
        )

    with col2:
        rainfall = st.number_input(
            "Rainfall Forecast (mm)",
            min_value=0.0,
            value=5.0
        )

    st.header("Livestock")

    col1, col2 = st.columns(2)

    with col1:
        livestock_type = st.selectbox(
            "Animal Type",
            ["cattle", "goat", "sheep"]
        )

    with col2:
        livestock_count = st.number_input(
            "Number of Animals",
            min_value=0,
            value=20
        )

    st.header("Labor")

    available_workers = st.number_input(
        "Available Workers",
        min_value=0,
        value=8
    )

    submitted = st.form_submit_button(
        "🌱 Generate Farm Plan"
    )


if submitted:

    try:

        validated_input = FarmInput(
            land_acres=land_acres,
            available_water_liters=water,
            capital=capital,

            soil_n=soil_n,
            soil_p=soil_p,
            soil_k=soil_k,
            soil_ph=soil_ph,
            soil_moisture=soil_moisture,

            temperature=temperature,
            rainfall_forecast_mm=rainfall,

            current_crop="",
            crop_growth_stage="",
            planting_date="",

            livestock_type=livestock_type,
            livestock_count=livestock_count,

            available_workers=available_workers,

            decisions={}
        )

        farm_data = validated_input.model_dump()

        result = graph.invoke(farm_data)

        plan = result["decisions"]["final_plan"]

        st.success("Farm plan generated successfully!")

        st.header("🌾 Final Farm Plan")

        # Crop
        st.subheader("🌱 Crop Recommendation")

        crop = plan["crop"]

        st.write(
            f"**Recommended Crop:** "
            f"{crop['recommended_crop']}"
        )

        st.write("**Crop Scores:**")

        for crop_name, score in crop["rule_based_scores"].items():
            st.write(
            f"- {crop_name}: {score}"
        )

        # Planting
        st.subheader("📅 Planting Schedule")

        planting = plan["planting"]

        for event, date in planting.items():
            st.write(
                f"**{event.replace('_', ' ').title()}:** "
                f"{date}"
            )

        # Irrigation
        st.subheader("💧 Irrigation")

        irrigation = plan["irrigation"]

        st.write(
            f"**Decision:** "
            f"{irrigation['decision']}"
        )

        st.write(
            f"**Amount:** "
            f"{irrigation['amount_mm']} mm"
        )

        st.write(
            f"**Reason:** "
            f"{irrigation['reason']}"
        )

        # Fertilization
        st.subheader("🧪 Fertilization")

        fertilization = plan["fertilization"]

        st.write(
            f"**Crop:** "
            f"{fertilization['crop']}"
        )

        recommendation = fertilization["recommendation"]

        if isinstance(recommendation, list):

            for item in recommendation:
                st.write(f"- {item}")

        else:
            st.write(recommendation)

        # Harvest
        st.subheader("🌾 Harvesting")

        harvest = plan["harvesting"]

        st.write(
            f"**Crop:** {harvest['crop']}"
        )

        st.write(
            f"**Expected Harvest:** "
            f"{harvest['expected_harvest']}"
        )

        st.write(
            f"**Harvest Window:** "
            f"{harvest['harvest_window']}"
        )

        st.write(
            f"**Recommendation:** "
            f"{harvest['recommendation']}"
        )

        # Livestock
        st.subheader("🐄 Livestock")

        livestock = plan["livestock"]

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Animals",
            livestock["count"]
        )

        col2.metric(
            "Daily Feed",
            f"{livestock['daily_feed_kg']} kg"
        )

        col3.metric(
            "Daily Water",
            f"{livestock['daily_water_liters']} L"
        )

        st.write(
            f"**Health Risk:** "
            f"{livestock['health_risk']}"
        )

        st.write(
            f"**Recommendation:** "
            f"{livestock['recommendation']}"
        )

        # Labor
        st.subheader("👷 Labor")

        labor = plan["labor"]

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Required Workers",
            labor["required_workers"]
        )

        col2.metric(
            "Available Workers",
            labor["available_workers"]
        )

        col3.metric(
            "Shortage",
            labor["worker_shortage"]
        )

        st.write(
            f"**Recommendation:** "
            f"{labor['recommendation']}"
        )

        # Land Expansion
        st.subheader("🏞️ Land Expansion")

        land = plan["land_expansion"]

        st.write(
            f"**Recommendation:** "
            f"{land['recommendation']}"
        )

        st.write(
            f"**Additional Land:** "
            f"{land['additional_land_acres']} acres"
        )

        st.write(
            f"**Land Cost:** "
            f"₹{land['land_cost']:,}"
        )

        st.write(
            f"**Expected Additional Profit:** "
            f"₹{land['expected_additional_profit']:,}/year"
        )

        if land["payback_years"] is not None:

            st.write(
                f"**Payback Period:** "
                f"{land['payback_years']:.1f} years"
            )

        # Market
        st.subheader("📈 Market Trading")

        market = plan["market"]

        st.write(
            f"**Recommended Market:** "
            f"{market['recommended_market']}"
        )

        st.write(
            f"**Net Price:** "
            f"₹{market['net_price_per_quintal']}/quintal"
        )

        st.write(
            f"**Recommendation:** "
            f"{market['recommendation']}"
        )

    except Exception as e:

        st.error(
            f"Unable to generate farm plan: {e}"
        )