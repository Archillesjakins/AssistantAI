import streamlit as st
from openassist import OpenAssist



def main():
    
    manager = OpenAssist()

    st.title("Archie AI Assistant")
    
    previous_response = manager.get_previous_response()
    st.text("Archie")
    st.write(previous_response, value=previous_response, height=100, max_chars=None, key='previous_response')
    st.markdown("---")

    # Get user input
    user_input = st.text_area("Ask anything...", height=100, max_chars=None)

    if st.button("Run Assistant"):
        
        manager.create_message(user_input)

        run = manager.run_assistant()

        manager.wait_for_run_completion(run.id)

        st.write(manager.get_summary())
        

if __name__ == "__main__":
    main()
