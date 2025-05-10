import streamlit as st
import requests

st.title("Smart Research Paper Finder")

query = st.text_input("Enter your search query:")
if st.button("Search") and query:
    with st.spinner("Searching..."):
        try:
            response = requests.get(
                "http://127.0.0.1:8000/search",
                params={"query": query}
            )
            papers = response.json()

            # Iterate through each paper in the result
            for i, paper in enumerate(papers):
                # Display each paper inside an expandable section
                with st.expander(f"{paper['title']}"):
                    st.markdown(f"**Authors:** {', '.join(paper['authors'])}")
                    st.markdown(f"**Year:** {paper['year']}")
                    st.markdown(paper["abstract"])

                    # Add a "Recommend Similar Papers" button for each paper
                    if st.button(f"🔍 Recommend Similar Papers", key=f"recommend_{i}"):
                        with st.spinner("Loading recommendations..."):
                            try:
                                # Send POST request to /recommend endpoint with paper_id
                                rec_response = requests.post(
                                    "http://127.0.0.1:8000/recommend",
                                    json={"paper_id": paper["id"]}  # Make sure your backend includes "id"
                                )

                                # Parse recommended papers
                                recs = rec_response.json().get("recommendations", [])

                                st.subheader("📚 Recommended Papers")
                                for rec in recs:
                                    st.markdown(f"**{rec['metadata']['title']}**")
                                    st.markdown(f"*{', '.join(rec['metadata'].get('authors', []))}*")
                                    st.markdown(rec['metadata'].get("abstract", "")[:300] + "...")
                                    st.markdown("---")
                            except Exception as rec_e:
                                st.error(f"Recommendation failed: {rec_e}")

        except Exception as e:
            st.error(f"Error: {e}")


if st.button("Ping FastAPI"):
    try:
        response = requests.get("http://localhost:8000/ping")
        st.write("Response:", response.json())
    except Exception as e:
        st.error(f"Failed to connect: {e}")
