import streamlit as st
import requests
from datetime import datetime
from itertools import islice
from urllib.parse import urlparse, parse_qs

st.set_page_config(page_title="Smart Research Paper Finder", layout="wide")


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


# Detailed view of research paper
query_params = st.query_params
paper_id = query_params.get("paper_id")

if paper_id:
    paper_id = paper_id[0] if isinstance(paper_id, list) else paper_id

    if st.button("← Back to Search"):
        st.query_params.clear()
        st.rerun()

    try:
        with st.spinner("🧠 Compiling information..."):
            response = requests.get(f"http://127.0.0.1:8000/details", params={"paper_id": paper_id})
            paper = response.json()
    except Exception as e:
        st.error(f"Could not load paper details: {e}")
        st.stop()

    # Paper card
    st.markdown(
        f"""
        <div style="border:1px solid #ccc; border-radius:10px; padding:24px; margin-bottom:32px; background-color:#f9f9f9; width:100%;">
            <h2>{paper['title']}</h2>
            <p><strong>Authors:</strong> {', '.join(paper['authors'])}</p>
            <p><strong>Published Date:</strong> {paper.get('date', 'N/A')}</p>
            <p><strong>Journal:</strong> {paper['journal']}</p>
            <p><a href="{paper['link']}" target="_blank">📄 View Full Paper</a></p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 🧱 Side-by-side Abstract and Summary
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(
            f"""
            <div style="border:1px solid #ccc; border-radius:10px; padding:20px; background-color:#f0f0f0;">
                <h4>📄 Abstract</h4>
                <p>{paper['abstract']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div style="border:1px solid #ccc; border-radius:10px; padding:20px; background-color:#f0f0f0;">
                <h4>🧠 LLM Summary</h4>
                <p>{paper['llm_summary']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 🧠 Relevant papers row
    st.markdown("### 🔁 Relevant Papers")

    relevant_docs = paper.get("relevant_docs", [])[:5]  # Limit to 5

    cols = st.columns(len(relevant_docs))  # Horizontal layout

    for col, doc in zip(cols, relevant_docs):
        with col:
            st.markdown(
                f"""
                <div style="border:1px solid #ccc; border-radius:10px; padding:16px; background-color:#f9f9f9; height:100%;">
                    <h4 style="font-size:16px;">
                        <a href="?paper_id={doc['id']}" style="text-decoration: none; color: inherit;">
                            {doc['title']}
                        </a>
                    </h4>
                    <p style="font-size:12px;"><strong>Authors:</strong> {', '.join(doc['authors'])}</p>
                    <p style="font-size:12px;"><strong>Date:</strong> {doc.get('date', 'N/A')}</p>
                    <p style="font-size:12px;"><strong>Journal:</strong> {doc['journal']}</p>
                    <p style="font-size:12px;"><strong>Score:</strong> {doc['score']:.3f}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.stop()

# Main page
# st.set_page_config(page_title="Smart Research Paper Finder", layout="wide")
st.title("📚 Smart Research Paper Finder")

st.markdown("""
<style>
.big-search-box input {
    font-size: 20px !important;
    height: 50px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("## 🔎 Enter Your Search Query")

# Place input and button in columns
query_col, button_col = st.columns([10, 1])

with query_col:
    query = st.text_input(
        "Search",
        key="main_query",
        placeholder="e.g. graph neural networks",
        label_visibility="collapsed"
    )

with button_col:
    search_clicked = st.button("Search")

# Initialize session state
for key in ["author_filters", "journal_filters"]:
    if key not in st.session_state:
        st.session_state[key] = []

# --- Constants ---
MIN_YEAR = 1970
MAX_YEAR = datetime.now().year
YEARS = [""] + list(range(MIN_YEAR, MAX_YEAR + 1))
MONTHS = [""] + [f"{m:02d}" for m in range(1, 13)]

# --- Top Row: Date, Author, Journal Filters ---
col_date, col_author, col_journal = st.columns(3)

# --- 📅 Date Filter ---
with col_date:
    st.markdown("**📅 Filter by Publication Date**")

    start_col1, start_col2 = st.columns(2)

    with start_col1:
        st.markdown(
            '<div style="font-size: 0.8rem; color: black; margin-top: -6px; margin-left: 8px;">Start Year</div>',
            unsafe_allow_html=True
        )
        start_year = st.selectbox("Start Year", YEARS, key="start_year", label_visibility="collapsed")
        st.markdown(
            '<div style="font-size: 0.8rem; color: black; margin-top: -6px; margin-left: 8px;">End Year</div>',
            unsafe_allow_html=True
        )
    with start_col2:
        st.markdown(
            '<div style="font-size: 0.8rem; color: black; margin-top: -6px; margin-left: 8px;">Start Month</div>',
            unsafe_allow_html=True
        )
        start_month = st.selectbox("Start Month", MONTHS, key="start_month", label_visibility="collapsed")
        st.markdown(
            '<div style="font-size: 0.8rem; color: black; margin-top: -6px; margin-left: 8px;">End Month</div>',
            unsafe_allow_html=True
        )

    end_col1, end_col2 = st.columns(2)
    with end_col1:
        end_year = st.selectbox("End Year", YEARS, key="end_year", label_visibility="collapsed")
    with end_col2:
        end_month = st.selectbox("End Month", MONTHS, key="end_month", label_visibility="collapsed")

# --- 👤 Author Filter ---
with col_author:
    st.markdown("**👤 Filter by Author**")

    with st.form("author_form", clear_on_submit=True):
        input_col, button_col = st.columns([6, 1])  # Adjust width ratio as needed

        with input_col:
            author_input = st.text_input("", placeholder="Add author", label_visibility="collapsed")

        with button_col:
            submitted = st.form_submit_button("➕")

        if submitted and author_input.strip() and author_input not in st.session_state.author_filters:
            st.session_state.author_filters.append(author_input.strip())

    for row in chunks(st.session_state.author_filters, 4):
        cols = st.columns(4)
        for i, author in enumerate(row):
            with cols[i]:
                if st.button(f"✖️ {author}", key=f"del_author_{author}"):
                    st.session_state.author_filters.remove(author)

# --- 📘 Journal Filter ---
with col_journal:
    st.markdown("**📘 Filter by Journal**")

    with st.form("journal_form", clear_on_submit=True):
        input_col, button_col = st.columns([6, 1])  # Adjust width ratio as needed

        with input_col:
            journal_input = st.text_input("", placeholder="Add journal", label_visibility="collapsed")

        with button_col:
            submitted = st.form_submit_button("➕")

        if submitted and journal_input.strip() and journal_input not in st.session_state.journal_filters:
            st.session_state.journal_filters.append(journal_input.strip())

    for row in chunks(st.session_state.journal_filters, 2):
        cols = st.columns(2)
        for i, journal in enumerate(row):
            with cols[i]:
                if st.button(f"✖️ {journal}", key=f"del_journal_{journal}"):
                    st.session_state.journal_filters.remove(journal)

author_param = ",".join(st.session_state.author_filters) if st.session_state.author_filters else None
journal_param = ",".join(st.session_state.journal_filters) if st.session_state.journal_filters else None

params = {
    "query": query,
}

# Only include filters if they're not empty
if author_param:
    params["authors"] = author_param
if journal_param:
    params["journal"] = journal_param
if start_year:
    params["start_year"] = start_year
    if start_month:
        params["start_month"] = start_month
if end_year:
    params['end_year'] = end_year
    if end_month:
        params["end_month"] = end_month

if search_clicked and query:
    with st.spinner("🔍 Searching..."):
        try:
            response = requests.get(
                "http://127.0.0.1:8000/search",
                params=params
            )

            data = response.json()
            papers = data["papers"]

            if not papers:
                st.warning("No results found.")
            else:
                for paper in papers:
                    paper_id = paper.get("id") or str(hash(paper["title"]))

                    with st.container():
                        st.markdown(
                            f"""
                            <div style="margin-bottom: 24px;">
                                <a href="/?paper_id={paper['id']}" target="_blank">
                                    <button style="
                                        width: 100%;
                                        text-align: left;
                                        background-color: #f9f9f9;
                                        border: 1px solid #ccc;
                                        padding: 16px;
                                        border-radius: 10px;
                                        cursor: pointer;
                                    ">
                                        <h4>{paper['title']}</h4>
                                        <p><strong>Authors:</strong> {', '.join(paper['authors'])}</p>
                                        <p><strong>Date:</strong> {paper.get('date', 'N/A')}</p>
                                        <p><strong>Journal:</strong> {paper['journal']}</p>
                                        <p><strong>Relevance Score:</strong> {paper['score']:.3f}</p>
                                        <p>{paper['abstract']}</p>
                                    </button>
                                </a>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

        except Exception as e:
            st.error(f"Error: {e}")
