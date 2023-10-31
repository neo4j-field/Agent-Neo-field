import streamlit as st
from urllib.error import URLError
from communicator import Communicator
from streamlit_feedback import streamlit_feedback
import time
import uuid
import os

# Usually, these values will be the same for both projects
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
# Replace "YOUR API KEY" with the API key you created
os.environ["LANGCHAIN_API_KEY"] = st.secrets['langsmith_api_key']
# Make sure to use the correct project name
os.environ["LANGCHAIN_PROJECT"] = "agent-neo"

llm_avatar = 'resources/images/neo4j_icon_white.png'
user_avatar = '👤'

INITIAL_MESSAGE = [
    {
        "role": "assistant",
        "avatar": llm_avatar,
        "content": """
                    Hey there, I'm Agent Neo!
                    What Graph Data Science question can I answer for you?
                    """,
    },
]

RESET_MESSAGE = [
    {
        "role": "assistant",
        "avatar": llm_avatar,
        "content": """
                    Our chat history has been reset.
                    What Graph Data Science question can I answer for you?
                    """,
    },
]

with open("ui/sidebar.md", "r") as sidebar_file:
    sidebar_content = sidebar_file.read()

with open("ui/bloglist.md", "r") as sidebar_file:
    blog_list = sidebar_file.read()

try:
    st.markdown("""
    <style>
    .sidebar-font {
        font-size:14px !important;
        color:#FAFAFA !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("Agent Neo")
    st.sidebar.write("# Agent Neo", 1.0)
    # st.sidebar.markdown("Read more: [The Practical Benefits to Grounding an LLM in a Knowledge Graph](https://medium.com/@bukowski.daniel/the-practical-benefits-to-grounding-an-llm-in-a-knowledge-graph-919918eb493)")

    # init session if first visit
    if len(st.session_state.keys()) == 0:
        st.session_state["messages"] = INITIAL_MESSAGE
        st.session_state["history"] = []
    if 'session_id' not in st.session_state:
        st.session_state['session_id'] = 's-'+str(uuid.uuid4())

    with st.sidebar.expander("Parameters"):
        # give options for llm
        llm = st.radio("Select LLM", ("chat-bison 2k", "chat-bison 32k", "GPT-4 8k", "GPT-4 32k"), index=2, 
                            help="""
                                    Selecting a different LLM will reset the chat. Default is GPT-4 8k.
                                    """)
        
        # select temperature
        temperature = st.slider("Select Temperature", 0.0, 1.0, 0.7, step=0.05, 
                                        help='''
                                            Temperature sets the amount of "creativity" the LLM has 
                                            in developing its responses. Chat must be reset to have an effect.
                                            ''')
        
        # Add slider to select the number of documents to use as context
        use_context = st.toggle('Use Grounding?', value=True, help='Use the Neo4j knowledge graph to ground Agent Neo.')
        if use_context:
            st.session_state['num_documents_for_context'] = st.slider('Select Number of Context Documents', 1, 10, 10, 
                                                                        help='''
                                                                                More documents could provide better context for a response 
                                                                                at the cost of longer prompts and processing time. This
                                                                                value can vary throughout a conversation.
                                                                                ''',
                                                                                disabled=not use_context)
        else:
            st.session_state['num_documents_for_context'] = 0
    
    # display app description in sidebar
    with st.sidebar.expander("Description"):
        st.markdown(sidebar_content)

    with st.sidebar.expander("Read More"):
        st.markdown(blog_list)

    # Add a reset button
    # st.sidebar.caption('<p class="sidebar-font">Reset Chat & Memory</p>', unsafe_allow_html=True)
    if st.sidebar.button("Reset Conversation", type="secondary", 
                        #  help='''
                        #       Effectively reset the session. A new Neo4j driver is created and the LLM history is cleared.
                        #       ''',
                        use_container_width=True):
        for key in st.session_state.keys():
            if key != 'session_id':
                del st.session_state[key]
        st.session_state["messages"] = RESET_MESSAGE
        st.session_state["history"] = []
        st.session_state['temperature'] = temperature

    
    # init Communicator object
    if 'communicator' not in st.session_state:
        st.session_state['communicator'] = Communicator()

    # Initialize the chat messages history
    if "messages" not in st.session_state:
        st.session_state["messages"] = INITIAL_MESSAGE
        st.chat_message("assistant", avatar=llm_avatar).markdown(INITIAL_MESSAGE['content'])

    # Initialize the LLM conversation
    if "llm_conversation" not in st.session_state:
        st.session_state['temperature'] = temperature
        st.session_state['llm_conversation'] = st.session_state['communicator'].create_conversation(llm)

    # handle llm switching
    if 'prev_llm' not in st.session_state:
        st.session_state['prev_llm'] = llm

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=message['avatar']):
            st.markdown(message["content"])

    if st.session_state['prev_llm'] != llm:
        print("switching llm...")
        message = f"Excuse me while I switch to my {llm} brain and wipe my memory..."
        st.chat_message("assistant", avatar=llm_avatar).markdown(message)
        st.session_state.messages.append({"role": "assistant", "avatar": llm_avatar, "content": message})
        # on switch, restart the internal llm conversation history with new llm
        st.session_state['llm_conversation'] = st.session_state['communicator'].create_conversation(llm)
        st.session_state['prev_llm'] = llm

    # Prompt for user input and save and display
    if question := st.chat_input():
        st.session_state.messages.append({"role": "user", "avatar": user_avatar, "content": question})
        st.chat_message("user", avatar=user_avatar).markdown(question)

#       start prompt timer
        prompt_timer_start = time.perf_counter()
        prompt, context_idxs = st.session_state['communicator'].create_prompt(question)
        prompt_timer_response = "\n\nPrompt creation took "+str(round(time.perf_counter() - prompt_timer_start, 4))+" seconds."
        
        # create new log chain in neo4j database if fresh conversation
        # and log first user message
        # if only initial message and user message OR
        # if 2 consecutive assistant followed by new user message in history
        if len(st.session_state['messages']) <= 2 or st.session_state['messages'][-3]['role'] == 'assistant':
            st.session_state['communicator'].log_new_conversation(llm=llm, user_input=question)

        # otherwise log user message to neo4j database
        else:
            st.session_state['communicator'].log_user(user_input=question)


        with st.chat_message('assistant', avatar=llm_avatar):
            message_placeholder = st.empty()
            message_placeholder.status('thinking...')

            # start "thinking" timer
            run_timer_start = time.perf_counter()
            response = st.session_state['llm_conversation'].run(prompt)
            run_timer_response = "\n\nThis thought took "+str(round(time.perf_counter() - run_timer_start, 4))+" seconds."

            message_placeholder.markdown(response+prompt_timer_response+run_timer_response)

            # log LLM response to neo4j database
            st.session_state['communicator'].log_assistant(assistant_output=response, context_indices=context_idxs)

        st.session_state.messages.append({"role": "assistant", 'avatar':llm_avatar, "content": response+prompt_timer_response+run_timer_response})

    # rate buttons appear after each llm response
    if len(st.session_state['messages']) > 2 and st.session_state['messages'][-1]['role'] == 'assistant':
        
        streamlit_feedback(
            feedback_type="thumbs",
            optional_text_label="[Required] Please provide an explanation",
            align='flex-start',
            on_submit=st.session_state['communicator'].rate_message,
            key='rating_options'+str(len(st.session_state['messages']))
        )

    # print('\n', st.session_state['llm_memory'].moving_summary_buffer)

except URLError as e:
    st.error(
        """
        **This app requires internet access.**
        Connection error: %s
    """
        % e.reason
    )

except Exception as e:
    print(e)
    st.error(
        """
        Error occurred: %s
        """
        % e
    )