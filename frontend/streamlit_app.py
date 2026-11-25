import streamlit as st
import httpx
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="RepoPilot",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 RepoPilot")
st.subheader("AI-Powered Codebase Intelligence Platform")

st.write(
    "Analyze Python repositories, explore dependencies, "
    "and ask questions about your codebase using AI."
)

st.sidebar.title("🚀 RepoPilot")

selected_page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Repository Analysis",
        "Symbol Explorer",
        "Dependency Explorer",
        "AI Code Assistant"
    ]
)

st.divider()

st.subheader(selected_page)
if selected_page == "Dashboard":

    st.title("Repository Dashboard")

    st.write(
        "Welcome to RepoPilot! Monitor your repository "
        "analysis and codebase insights."
    )

    analysis = st.session_state.get("analysis_result")

    if analysis:

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Files",
            analysis["total_files"]
        )

        col2.metric(
            "Successful Files",
            analysis["successful_files"]
        )

        col3.metric(
            "Symbols Saved",
            analysis["symbols_saved"]
        )

        col4.metric(
            "Relationships Saved",
            analysis["relationships_saved"]
        )

    else:
        st.info(
            "No repository analyzed yet. "
            "Go to Repository Analysis to get started."
        )
elif selected_page == "Repository Analysis":

    st.title("Repository Analysis")

    st.write(
        "Enter the local path of a Python repository "
        "to analyze its code structure and dependencies."
    )

    repo_path = st.text_input(
        "Repository Path",
        placeholder=r"C:\Users\YourName\Projects\MyRepository"
    )

    analyze_button = st.button(
        "Analyze Repository",
        type="primary"
    )

    if analyze_button:

        if not repo_path.strip():
            st.warning("Please enter a repository path.")

        else:
            try:
                with st.spinner("Analyzing repository..."):

                    response = httpx.post(
                        f"{API_URL}/analyze",
                        json={"repo_path": repo_path},
                        timeout=120
                    )

                    response.raise_for_status()

                    result = response.json()

                    st.session_state["analysis_result"] = result

                st.success("Repository analyzed successfully!")

            except httpx.HTTPStatusError as error:
                st.error(
                    f"Analysis failed: {error.response.text}"
                )

            except httpx.RequestError:
                st.error(
                    "Could not connect to FastAPI. "
                    "Please make sure the backend server is running."
                )


elif selected_page == "Symbol Explorer":

    st.title("Symbol Explorer")

    st.write(
        "Search for functions and classes "
        "in your analyzed repository."
    )

    symbol_name = st.text_input(
        "Enter function or class name",
        placeholder="Example: login"
    )

    search_button = st.button(
        "Search Symbols",
        type="primary"
    )

    if search_button:

        if not symbol_name.strip():
            st.warning("Please enter a symbol name.")

        elif not st.session_state.get("analysis_result"):
            st.warning("Please analyze a repository first.")

        else:
            try:
                with st.spinner("Searching symbols..."):

                    response = httpx.get(
                        f"{API_URL}/symbols",
                        params={"name": symbol_name},
                        timeout=30
                    )

                    response.raise_for_status()
                    symbols = response.json()

                # Extract matching symbols from API response
                if isinstance(symbols, dict):

                    matches = symbols.get("matches", [])
                    searched_name = symbols.get("name", symbol_name)

                else:
                    matches = symbols
                    searched_name = symbol_name

                if matches:

                    st.success(
                        f"Found {len(matches)} symbol(s)."
                    )

                    # Convert API results into readable rows
                    formatted_symbols = []

                    for match in matches:

                        formatted_symbols.append({
                            "Symbol Name": searched_name,
                            "File Path": match["file_path"],
                            "Start Line": match["start_line"],
                            "End Line": match["end_line"]
                        })

                    st.dataframe(
                        formatted_symbols,
                        use_container_width=True,
                        hide_index=True
                    )

                else:
                    st.info("No matching symbols found.")

            except httpx.HTTPStatusError as error:
                st.error(
                    f"Search failed: {error.response.text}"
                )

            except httpx.RequestError:
                st.error("Could not connect to FastAPI.")

            except (KeyError, TypeError, AttributeError) as error:
                st.error(
                    f"Unexpected API response structure: {error}"
                )



elif selected_page == "Dependency Explorer":

    st.title("Dependency Explorer")

    st.write(
        "Explore function callers, dependencies, "
        "and potential impact across your repository."
    )

    function_name = st.text_input(
        "Enter function name",
        placeholder="Example: start_application"
    )

    analysis_type = st.selectbox(
        "Select analysis type",
        [
            "Find Callers",
            "Find Dependencies",
            "Impact Analysis"
        ]
    )

    analyze_dependency = st.button(
        "Analyze Dependencies",
        type="primary"
    )

    if analyze_dependency:

        if not function_name.strip():
            st.warning("Please enter a function name.")

        elif not st.session_state.get("analysis_result"):
            st.warning("Please analyze a repository first.")

        else:
            try:
                endpoint_map = {
                    "Find Callers": "callers",
                    "Find Dependencies": "dependencies",
                    "Impact Analysis": "impact"
                }

                endpoint = endpoint_map[analysis_type]

                with st.spinner("Analyzing dependencies..."):

                    response = httpx.get(
                        f"{API_URL}/{endpoint}/{function_name}",
                        timeout=30
                    )

                    response.raise_for_status()
                    api_data = response.json()

                st.success(f"{analysis_type} completed!")

                # Extract the function name and result list
                searched_function = api_data.get(
                    "function",
                    function_name
                )

                result_items = api_data.get("results", [])

                formatted_results = []

                # Process each matching function in the repository
                for item in result_items:

                    source_file = item.get(
                        "file_path",
                        "Not available"
                    )

                    # Choose the correct relationship list
                    if analysis_type == "Find Callers":

                        related_items = item.get("callers", [])
                        relationship = "Called by"
                        related_label = "Caller"

                    elif analysis_type == "Find Dependencies":

                        related_items = item.get("dependencies", [])
                        relationship = "Calls"
                        related_label = "Dependency"

                    else:

                        related_items = item.get(
                            "affected_functions", []
                        )
                        relationship = "Affected by changes"
                        related_label = "Affected Function"

                    # Create a separate table row for each relationship
                    for related in related_items:

                        formatted_results.append({
                            "Function": searched_function,
                            "Source File": source_file,
                            "Relationship": relationship,
                            related_label: related.get(
                                "name",
                                "Unknown"
                            ),
                            "Related File": related.get(
                                "file_path",
                                "Not available"
                            ),
                            "Related Start Line": related.get(
                                "start_line",
                                "Not available"
                            )
                        })

                if formatted_results:

                    st.subheader("Results")

                    st.dataframe(
                        formatted_results,
                        use_container_width=True,
                        hide_index=True
                    )

                else:
                    st.info(
                        "No relationships found for this function."
                    )

            except httpx.HTTPStatusError as error:
                st.error(
                    f"Analysis failed: {error.response.text}"
                )

            except httpx.RequestError:
                st.error(
                    "Could not connect to FastAPI."
                )

            except (KeyError, TypeError, AttributeError) as error:
                st.error(
                    f"Unexpected API response structure: {error}"
                )

elif selected_page == "AI Code Assistant":

    st.title("AI Code Assistant")

    st.write(
        "Ask questions about your Python codebase "
        "and get AI-powered answers with source references."
    )

    question = st.text_area(
        "Ask a question about your repository",
        placeholder="Example: Which login function does start_application call?",
        height=120
    )

    ask_button = st.button(
        "Ask RepoPilot",
        type="primary"
    )

    if ask_button:

        if not question.strip():
            st.warning("Please enter a question.")

        elif not st.session_state.get("analysis_result"):
            st.warning("Please analyze a repository first.")

        else:
            try:
                repository_id = st.session_state["analysis_result"]["repository_id"]

                with st.spinner("RepoPilot is analyzing your code..."):

                    response = httpx.post(
                        f"{API_URL}/ask",
                        json={
                            "repository_id": repository_id,
                            "question": question,
                            "top_k": 5
                        },
                        timeout=120
                    )

                    response.raise_for_status()
                    result = response.json()

                st.success("Answer generated successfully!")

                st.subheader("AI Answer")
                st.markdown(result["answer"])

                st.subheader("Source References")

                for source in result["sources"]:

                    with st.expander(
                        f"{source['symbol_name']} — {source['file_path']}"
                    ):
                        st.write(f"**File:** {source['file_path']}")
                        st.write(
                            f"**Lines:** {source['start_line']}-{source['end_line']}"
                        )
                        st.write(
                            f"**Similarity:** {source['similarity']:.4f}"
                        )

            except httpx.HTTPStatusError as error:
                st.error(f"Question failed: {error.response.text}")

            except httpx.RequestError:
                st.error("Could not connect to FastAPI.")