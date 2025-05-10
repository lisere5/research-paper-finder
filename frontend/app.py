import streamlit as st
import requests

st.set_page_config(page_title="Smart Research Paper Finder", layout="wide")
st.title("📚 Smart Research Paper Finder")

query = st.text_input("Enter your search query:")
if st.button("Search") and query:
    with st.spinner("🔍 Searching..."):
        try:
            response = requests.get(
                "http://127.0.0.1:8000/search",
                params={"query": query}
            )
            data = response.json()
            papers = data["papers"]

            if not papers:
                st.warning("No results found.")
            else:
                for paper in papers:
                    with st.container():
                        st.markdown(
                            f"""
                            <div style="border:1px solid #ccc; border-radius:10px; padding:16px; margin-bottom:10px; background-color:#f9f9f9;">
                                <h4 style="margin-bottom:8px;">{paper['title']}</h4>
                                <p><strong>Authors:</strong> {', '.join(paper['authors'])}</p>
                                <p><strong>Published Date:</strong> {paper.get('date', 'N/A')}</p>
                                <p><strong>Relevance Score:</strong> {paper['score']:.3f}</p>
                                <p>{paper['abstract']}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
        except Exception as e:
            st.error(f"Error: {e}")


if st.button("Ping FastAPI"):
    try:
        response = requests.get("http://localhost:8000/ping")
        st.success(f"Response: {response.json()}")
    except Exception as e:
        st.error(f"Failed to connect: {e}")
