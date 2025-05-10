import streamlit as st
import requests

st.title("Smart Research Paper Finder")

query = st.text_input("Enter your search query:")

# New filter inputs
author_filter = st.text_input("Filter by author name (optional):")
journal_filter = st.text_input("Filter by journal name (optional):")
# Year range selector (optional)
start_year, end_year = st.slider("Filter by publication year range (optional):", 2000, 2025, (2015, 2025))

if st.button("Search") and query:
    with st.spinner("Searching..."):
        try:
            response = requests.get(
                "http://127.0.0.1:8000/search",
                params={
                    "query": query,
                    "author": author_filter,
                    "journal": journal_filter,
                    "start_year": start_year,
                    "end_year": end_year
                }
            )
            papers = response.json()
            for paper in papers:
                st.markdown(f"### {paper['title']}")
                st.markdown(f"**Authors:** {', '.join(paper['authors'])}")
                st.markdown(f"**Year:** {paper['year']}")
                st.markdown(f"{paper['abstract']}")
                st.markdown("---")
        except Exception as e:
            st.error(f"Error: {e}")


if st.button("Ping FastAPI"):
    try:
        response = requests.get("http://localhost:8000/ping")
        st.write("Response:", response.json())
    except Exception as e:
        st.error(f"Failed to connect: {e}")
