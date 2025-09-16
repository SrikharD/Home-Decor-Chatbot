"""
Home Decor Chatbot - Streamlit Application
"""
import streamlit as st
import time
import logging
import re
from datetime import datetime
from src import RAGSystem

# Configure page
st.set_page_config(
    page_title="Home Decor Chatbot",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set up logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def _validate_and_clean_response(response: str) -> str:
    """Validate and clean response text for display issues"""
    if not response:
        return "I apologize, but I couldn't generate a proper response."

    # Check for malformed text patterns
    words = response.split()
    single_char_count = sum(1 for word in words if len(word) == 1 and word.isalpha())

    # If more than 15% of words are single characters, likely malformed
    if len(words) > 0 and (single_char_count / len(words)) > 0.15:
        # Try to fix by removing spaces between single characters
        cleaned = re.sub(r'\b([a-zA-Z])\s+([a-zA-Z])\s+([a-zA-Z])', r'\1\2\3', response)
        cleaned = re.sub(r'\b([a-zA-Z])\s+([a-zA-Z])', r'\1\2', cleaned)
        return cleaned

    # Check for price formatting issues
    response = re.sub(r'(\$?\d+\.?\d*)\)([a-zA-Z])', r'\1) \2', response)

    # Fix spacing around punctuation
    response = re.sub(r'\s+([,.!?;:])', r'\1', response)
    response = re.sub(r'([,.!?;:])\s*', r'\1 ', response)

    return response.strip()


@st.cache_resource
def initialize_system():
    """Initialize RAG system"""
    try:
        with st.spinner("Initializing system..."):
            return RAGSystem()
    except Exception as e:
        st.error(f"Failed to initialize system: {str(e)}")
        st.error("Please ensure Amazon Bedrock access is configured.")
        return None


def main():
    """Main application"""
    st.title("Home Decor Assistant")
    st.markdown("Find the perfect furniture and decor for your space")
    
    # Initialize system
    rag_system = initialize_system()
    
    if rag_system is None:
        st.error("Cannot start chatbot - system initialization failed")
        st.stop()
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! I'm your home decor assistant. How can I help you today?",
                "timestamp": datetime.now()
            }
        ]

    # Sidebar - Hidden metrics in expandable menu
    with st.sidebar:
        with st.expander("Performance Metrics"):
            # Calculate metrics
            response_times = [
                msg.get("response_time", 0)
                for msg in st.session_state.messages
                if msg.get("role") == "assistant" and "response_time" in msg
            ]
            avg_time = sum(response_times) / len(response_times) if response_times else 0
            total_queries = len([msg for msg in st.session_state.messages if msg.get("role") == "user"])

            st.metric("Avg Response Time", f"{avg_time:.1f}s")
            st.metric("Total Queries", total_queries)

        with st.expander("System Status"):
            st.metric("Products Loaded", len(rag_system.products))
            st.metric("LLM Status", "Bedrock Llama3 70B")
            st.metric("Data Source", "S3 Bucket")

    # Example queries
    st.subheader("Try these examples:")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Modern bedroom lighting"):
            st.session_state.example_query = "I need modern lighting for my bedroom"
    
    with col2:
        if st.button("Comfortable living room chairs"):
            st.session_state.example_query = "Show me comfortable chairs for my living room"
    
    with col3:
        if st.button("Dining room furniture"):
            st.session_state.example_query = "What dining room furniture do you have?"

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and "response_time" in message:
                st.caption(f"Response time: {message['response_time']:.1f}s")

    # Generate response for the latest user message if needed
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        latest_message = st.session_state.messages[-1]

        with st.chat_message("assistant"):
            with st.spinner("Processing..."):
                start_time = time.time()

                try:
                    response = rag_system.query(latest_message["content"])
                    end_time = time.time()
                    response_time = end_time - start_time

                    # Additional text validation and cleanup
                    if response:
                        # Basic validation - if response looks malformed, clean it
                        cleaned_response = _validate_and_clean_response(response)
                        st.markdown(cleaned_response)
                    else:
                        st.markdown("I apologize, but I couldn't generate a proper response. Please try rephrasing your question.")

                    st.caption(f"Response time: {response_time:.1f}s")

                    # Add to session state (store cleaned response)
                    final_response = cleaned_response if response else "I apologize, but I couldn't generate a proper response. Please try rephrasing your question."
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": final_response,
                        "response_time": response_time,
                        "timestamp": datetime.now()
                    })

                    # Rerun to update the display
                    st.rerun()

                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "timestamp": datetime.now()
                    })

                    st.rerun()

    # Chat input - always available
    prompt = st.chat_input("Ask about home decor...")

    # Handle example query
    if hasattr(st.session_state, 'example_query'):
        prompt = st.session_state.example_query
        del st.session_state.example_query

    # Process user input
    if prompt:
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now()
        })

        # Rerun to show user message immediately
        st.rerun()

    # System status removed from main screen - now in sidebar menu


if __name__ == "__main__":
    main()
