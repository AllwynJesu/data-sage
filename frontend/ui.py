import pandas as pd
import altair as alt
import streamlit as st
from typing import Dict, List, Any


# Simulated backend calls
def get_data_sources() -> List[Dict[str, Any]]:
    return [
        {"id": 1, "display_name": "Production Database"},
        {"id": 2, "display_name": "Development Database"},
    ]


def create_data_source(db_credentials: Dict[str, Any]) -> Dict[str, Any]:
    # Placeholder for actual creation logic
    return {"id": 3, "display_name": db_credentials.get("name", "New Data Source")}


def backend_call(data_source_id: int):
    pass


def create_chart(visual_config):
    df = pd.DataFrame(visual_config.data)
    if isinstance(visual_config.y_axis, list):
        long_data = pd.melt(
            df,
            id_vars=[visual_config.x_axis]
            + [col for col in df.columns if col not in visual_config.y_axis],
            value_vars=visual_config.y_axis,
            var_name="Metric",
            value_name="Value",
        )
    else:
        long_data = df

    chart_types = {
        "Bar Chart": alt.Chart(long_data).mark_bar(),
        "Line Chart": alt.Chart(long_data).mark_line(),
        "Pie Chart": alt.Chart(long_data).mark_arc(),
    }

    if visual_config.chart_type not in chart_types:
        st.error(f"Unsupported chart type: {visual_config.chart_type}")
        return None

    chart = (
        chart_types[visual_config.chart_type]
        .encode(
            x=alt.X(visual_config.x_axis),
            y=alt.Y(
                "Value"
                if isinstance(visual_config.y_axis, list)
                else visual_config.y_axis
            ),
            color=alt.Color(
                "Metric" if isinstance(visual_config.y_axis, list) else None
            ),
            tooltip=visual_config.other_options.tooltip,
        )
        .properties(width=800, height=400)
    )

    return chart


# Streamlit App
st.set_page_config(
    page_title="Data Sage",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Header Section ---
st.markdown(
    """
    <h1 style='text-align: center; font-size: 2.5rem;'>🔮 Data Sage</h1>
    <p style='text-align: center; font-size: 1rem; color: gray;'>Empowering data insights with SQL and visualization</p>
    """,
    unsafe_allow_html=True,
)

# --- Data Source Selection ---
st.markdown("### 🗄️ Select or Add a Data Source")
data_sources = get_data_sources()
selected_source = st.selectbox(
    "Choose a Data Source:",
    options=["None"] + [ds["display_name"] for ds in data_sources],
    index=0,
)

if selected_source != "None":
    st.success(f"✅ Using selected data source: {selected_source}")
    db_config = None  # Disable DB credentials
else:
    st.warning("⚠️ No data source selected. Provide credentials to add a new one.")
    db_config = {}

    with st.expander("➕ Add a New Data Source", expanded=True):
        # Fields in rows and columns
        col1, col2 = st.columns(2)
        with col1:
            db_name = st.text_input("Database Name")
            db_host = st.text_input("Host", value="localhost")
            db_user = st.text_input("Username", value="admin")
        with col2:
            # Additional dropdown for dialect
            db_dialect = st.selectbox(
                "Database Dialect",
                options=["PostgreSQL", "MySQL", "Oracle"],
            )
            db_port = st.text_input("Port", value="6432")
            # Password in full row for better UX
            db_password = st.text_input("Password", type="password")

        # File Upload with Help Icon
        st.markdown("### 📂 Upload SQL Log File")
        uploaded_file = st.file_uploader(
            "Upload a file containing SQL queries executed by the application or database logs.",
            type=["txt", "log", "csv"],
            help=(
                "This file should contain all SQL queries executed on the database. "
                "You can collect this information from application/database logs."
            ),
        )

        # Create button
        if st.button("Create Data Source"):
            if (
                db_name
                and db_host
                and db_port
                and db_user
                and db_password
                and db_dialect
            ):
                if uploaded_file:
                    sql_log_content = uploaded_file.read().decode("utf-8")
                    new_source = create_data_source(
                        {
                            "name": db_name,
                            "host": db_host,
                            "port": db_port,
                            "user": db_user,
                            "password": db_password,
                            "dialect": db_dialect,
                            "sql_logs": sql_log_content,
                        }
                    )
                    st.success(
                        f"Data Source '{new_source['display_name']}' created successfully!"
                    )
                    st.experimental_rerun()
                else:
                    st.error("Please upload a SQL log file to proceed.")
            else:
                st.error("All fields are required to create a data source.")

# --- User Query Section ---
st.markdown("### 💬 Ask Your Question")
query_input = st.text_area(
    "Enter your question in natural language:",
    placeholder="e.g., Get customers who placed multiple orders",
    height=150,
    disabled=(selected_source == "None"),  # Disable input if no data source
)

execute_button = st.button("Fetch Results", disabled=(selected_source == "None"))

if execute_button:
    with st.spinner("Processing your query..."):
        if selected_source == "None":
            st.error("Please select or create a data source to execute your query.")
        else:
            db_config = None  # Simulate data source usage
            result = backend_call(None)

            if result.get("is_error"):
                st.error(f"❌ {result['error_explanation']}")
            else:
                st.success("✅ Query executed successfully!")
                st.markdown("#### SQL Query")
                st.code(result["sql"], language="sql")

                st.markdown("#### Explanation")
                st.write(result["explanation"])

                st.markdown("#### Data")
                if result["data"]:
                    st.dataframe(result["data"])
                    llm_output = ""
                    # llm_output = visualizer_chain.invoke(
                    #     {"sql": result["sql"], "data": result["data"]}
                    # )
                    if llm_output.is_visualization_possible:
                        chart = create_chart(llm_output)
                        if chart:
                            st.altair_chart(chart, use_container_width=True)
                    else:
                        st.error("Visualization not possible.")
                else:
                    st.info("No data found for the query.")

# --- Footer ---
st.markdown("---")
st.markdown(
    """
    <p style='text-align: center; color: gray;'>Authored by Allwyn Jesu</p>
    """,
    unsafe_allow_html=True,
)
