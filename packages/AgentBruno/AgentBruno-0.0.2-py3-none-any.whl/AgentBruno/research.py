# AgentBruno/research.py
import asyncio
import re
import pinecone
import json

from typing import List, TypedDict, Optional, Annotated
from langchain_core.pydantic_v1 import BaseModel, Field, constr
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.retrievers import WikipediaRetriever
from langchain_core.runnables import RunnableLambda, chain as as_runnable, RunnableConfig
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage, AnyMessage
from langgraph.graph import StateGraph, END
from langchain_core.prompts import MessagesPlaceholder
from langchain.vectorstores import Pinecone
from langchain_community.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper
from langchain_core.tools import tool
from langchain_community.vectorstores import SKLearnVectorStore
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Pydantic models for handling subsections, sections, and outlines

class Subsection(BaseModel):
    """
    Represents a subsection of a section.
    """
    subsection_title: str = Field(..., title="Title of the subsection")
    description: str = Field(..., title="Content of the subsection")

    @property
    def as_str(self) -> str:
        """
        Generates a string representation of the subsection.
        """
        return f"### {self.subsection_title}\n\n{self.description}".strip()

class Section(BaseModel):
    """
    Represents a section of a Wikipedia page.
    """
    section_title: str = Field(..., title="Title of the section")
    description: str = Field(..., title="Content of the section")
    subsections: Optional[List[Subsection]] = Field(
        default=None,
        title="Titles and descriptions for each subsection of the Wikipedia page.",
    )

    @property
    def as_str(self) -> str:
        """
        Generates a string representation of the section, including its subsections if any.
        """
        subsections = "\n\n".join(
            f"### {subsection.subsection_title}\n\n{subsection.description}"
            for subsection in self.subsections or []
        )
        return f"## {self.section_title}\n\n{self.description}\n\n{subsections}".strip()

class Outline(BaseModel):
    """
    Represents an outline of a Wikipedia page.
    """
    page_title: str = Field(..., title="Title of the Wikipedia page")
    sections: List[Section] = Field(
        default_factory=list,
        title="Titles and descriptions for each section of the Wikipedia page.",
    )

    @property
    def as_str(self) -> str:
        """
        Generates a string representation of the outline, including its sections.
        """
        sections = "\n\n".join(section.as_str for section in self.sections)
        return f"# {self.page_title}\n\n{sections}".strip()

# Pydantic models used by the writer

class WikiSection(BaseModel):
    """
    Represents a section of content for a Wikipedia page.
    """
    section_title: str = Field(..., title="Title of the section")
    content: str = Field(..., title="Full content of the section")
    subsections: Optional[List[Subsection]] = Field(
        default=None,
        title="Titles and descriptions for each subsection of the Wikipedia page.",
    )
    citations: List[str] = Field(default_factory=list)

    @property
    def as_str(self) -> str:
        """
        Generates a string representation of the section, including its subsections and citations.
        """
        subsections = "\n\n".join(
            subsection.as_str for subsection in self.subsections or []
        )
        citations = "\n".join([f" [{i}] {cit}" for i, cit in enumerate(self.citations)])
        return (
            f"## {self.section_title}\n\n{self.content}\n\n{subsections}".strip()
            + f"\n\n{citations}".strip()
        )

# Pydantic models used in perspectives

class Editor(BaseModel):
    """
    Represents an editor with their affiliation, name, role, and description.
    """
    affiliation: str = Field(
        description="Primary affiliation of the editor.",
    )
    name: constr(regex=r'^[a-zA-Z0-9_-]{1,64}$') = Field(
        description="Name of the editor."
    )
    role: str = Field(
        description="Role of the editor in the context of the topic.",
    )
    description: str = Field(
        description="Description of the editor's focus, concerns, and motives.",
    )

    @property
    def persona(self) -> str:
        """
        Generates a string representation of the editor's persona.
        """
        return f"Name: {self.name}\nRole: {self.role}\nAffiliation: {self.affiliation}\nDescription: {self.description}\n"

class Perspectives(BaseModel):
    """
    Represents perspectives with a list of editors.
    """
    editors: List[Editor] = Field(
        description="Comprehensive list of editors with their roles and affiliations.",
    )

class RelatedSubjects(BaseModel):
    """
    Represents related subjects as background research.
    """
    topics: List[str] = Field(
        description="Comprehensive list of related subjects as background research.",
    )

def add_messages(left, right):
    """
    Concatenates two lists of messages.

    Args:
        left: The first list of messages.
        right: The second list of messages.

    Returns:
        The concatenated list of messages.
    """
    if not isinstance(left, list):
        left = [left]
    if not isinstance(right, list):
        right = [right]
    return left + right

def update_references(references, new_references):
    """
    Updates the references dictionary with new references.

    Args:
        references: The existing references dictionary.
        new_references: The new references to add.

    Returns:
        The updated references dictionary.
    """
    if not references:
        references = {}
    references.update(new_references)
    return references

def update_editor(editor, new_editor):
    """
    Updates the editor information if not already set.

    Args:
        editor: The existing editor information.
        new_editor: The new editor information.

    Returns:
        The updated editor information.
    """
    # Can only set at the outset
    if not editor:
        return new_editor
    return editor

class InterviewState(TypedDict):
    """
    Represents the state of an interview, including messages, references, and editor information.
    """
    messages: Annotated[List[AnyMessage], add_messages]  # List of interview messages
    references: Annotated[Optional[dict], update_references]  # Optional dictionary of references
    editor: Annotated[Optional[Editor], update_editor]  # Optional editor information

# Additional TypedDict used in ResearchState

class ResearchState(TypedDict):
    """
    Represents the state of research, including topic, outline, editors, interview results, sections, and article.
    """
    topic: str
    outline: Outline
    editors: List[Editor]
    interview_results: List[InterviewState]
    sections: List[WikiSection]
    article: str
    open_ai_key: str
    pinecone_api_key: str
    pinecone_envo: str 
    pinecone_index: str
    vectorstore: SKLearnVectorStore

async def initialize_research(state: ResearchState):
    """
    Initializes the research state by generating an outline and selecting editors based on a provided topic.

    Args:
        state (ResearchState): The current research state containing the topic and other information.

    Returns:
        dict: The updated research state including the generated outline and selected editors.
    """
    
    topic = state["topic"]
    #print("I'm in initialize_research topic: ", topic)
    
    open_ai_api_key = state["open_ai_key"]
    fast_llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key = open_ai_api_key, temperature=0)
       
    # Define chat prompts and chains for generating an outline, expanding related topics, and selecting editors
    
    # Chat prompts for generating an outline
    direct_gen_outline_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a Wikipedia writer. Write an outline for a Wikipedia page about a user-provided topic. The Wikipedia page will be read by consultants and senior executives working for energy and utility sectors for insights. Be comprehensive and specific.",
            ),
            ("user", f"{topic}"),
        ]
    )
    
    generate_outline_direct = direct_gen_outline_prompt | fast_llm.with_structured_output(
        Outline
    )

    # Chat prompts for expanding related topics
    gen_related_topics_prompt = ChatPromptTemplate.from_template(
        """I'm writing a Wikipedia page for a topic mentioned below. Please identify and recommend some Wikipedia pages on closely related subjects. \n
        I'm looking for examples that provide insights to consultants and executives into interesting aspects specifically associated with this topic, or examples that help me understand the typical content and structure included in Wikipedia pages.
        Also remember that this Wikipedia page will be read by consultants and senior executives as insights working for energy and utility sector. 
        Please list as many subjects and urls as you can.
        
        Topic of interest: {topic}
        """
    )
    
    expand_chain = gen_related_topics_prompt | fast_llm.with_structured_output(
        RelatedSubjects
    )
    
    # Chat prompts for selecting editors
    gen_perspectives_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You need to select a diverse (and distinct) group of Wikipedia editors who will work together to create a comprehensive article on the topic. Each of them represents a different perspective, role, or affiliation related to this topic.\
                You can use other Wikipedia pages of related topics for inspiration. For each editor, add a description of what they will focus on.
                Wiki page outlines of related topics for inspiration:
                {examples}""",
            ),
            ("user", "Topic of interest: {topic}"),
        ]
    )
    
    gen_perspectives_chain = gen_perspectives_prompt | fast_llm.with_structured_output(
        Perspectives
    )
    
    # Initialize WikipediaRetriever
    wikipedia_retriever = WikipediaRetriever(load_all_available_meta=True, top_k_results=1)
    
    # Function for formatting retrieved documents
    def format_doc(doc, max_length=1000):
        related = "- ".join(doc.metadata["categories"])
        return f"### {doc.metadata['title']}\n\nSummary: {doc.page_content}\n\nRelated\n{related}"[
            :max_length
        ]
    
    # Function for formatting a list of documents
    def format_docs(docs):
        return "\n\n".join(format_doc(doc) for doc in docs)
    
    # Define coroutine for surveying related subjects and selecting editors
    @as_runnable
    async def survey_subjects(topic: str):
        related_subjects = await expand_chain.ainvoke({"topic": topic})
        retrieved_docs = await wikipedia_retriever.abatch(
            related_subjects.topics, return_exceptions=True
        )
        all_docs = []
        for docs in retrieved_docs:
            if isinstance(docs, BaseException):
                continue
            all_docs.extend(docs)
        formatted = format_docs(all_docs)
        return await gen_perspectives_chain.ainvoke({"examples": formatted, "topic": topic})
    
    # Invoke chat chains for generating outline and selecting editors concurrently
    coros = (
        generate_outline_direct.ainvoke({"topic": topic}),
        survey_subjects.ainvoke(topic),
    )
    results = await asyncio.gather(*coros)
    
    # Return updated research state with generated outline and selected editors
    return {
        **state,
        "outline": results[0],
        "editors": results[1].editors,
    }
# End of initialize_research

# Start of conduct_interviews
def sanitize_name(name):
    # Define the pattern for valid names
    pattern = r'^[a-zA-Z0-9_-]{1,64}$'

    # Check if the name matches the pattern
    if re.match(pattern, name):
        return name
    else:
        # If the name doesn't match the pattern, replace invalid characters with underscores
        return re.sub(r'[^a-zA-Z0-9_-]', '_', name)

async def conduct_interviews(state: ResearchState):
    """
    Conducts interviews with selected editors for the given research state.

    Args:
        state (ResearchState): The current research state containing the topic, outline, and selected editors.

    Returns:
        dict: The updated research state including the interview results.
    """
    topic = state["topic"]
    
    open_ai_api_key = state["open_ai_key"]
    fast_llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key = open_ai_api_key, temperature=0)
    pinecone_api_key = state["pinecone_api_key"]
    pinecone_envo = state["pinecone_envo"]
    pinecone_index = state["pinecone_index"]
    
    # print("****************")
    # print(pinecone_index)
    # print("****************")
    
    # Start generate question logic
    gen_qn_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an experienced Wikipedia writer and want to edit a specific page. \
            Besides your identity as a Wikipedia writer, you have a specific focus when researching the topic.
            You can assume that this Wikipedia page will be read by consultants and senior executives working in energy and utility sectors for insights.  
            These readers are interested in reading the market trends, facts and figures, regulations, policies and standards, challenges and risk and possible solutions around the topics.
            
            Now, you are chatting with an expert to get information. Ask good questions to get more useful and detailed information.
            
            When you have no more questions to ask, say "Thank you so much for your help!" to end the conversation.\
            Please only ask one question at a time and don't ask what you have asked before.\
            Your questions should be related to the topic you want to write.
            Be comprehensive and curious, gaining as much unique insight from the expert as possible.\
        
            Stay true to your specific perspective:
            {persona}""",
        ),
                MessagesPlaceholder(variable_name="messages", optional=True),
    ]
    )

    def tag_with_name(ai_message: AIMessage, name: str):
        ai_message.name = name
        return ai_message

    def swap_roles(state: InterviewState, name: str):
        converted = []
        for message in state["messages"]:
            if isinstance(message, AIMessage) and message.name != name:
                message = HumanMessage(**message.dict(exclude={"type"}))
            converted.append(message)
        return {"messages": converted}
    
    @as_runnable
    async def generate_question(state: InterviewState):
        editor = state["editor"]
        gn_chain = (
            RunnableLambda(swap_roles).bind(name=editor.name)
            | gen_qn_prompt.partial(persona=editor.persona)
            | fast_llm
            | RunnableLambda(tag_with_name).bind(name=editor.name)
        )
        result = await gn_chain.ainvoke(state)
        return {"messages": [result]}
    
    class Queries(BaseModel):
        queries: List[str] = Field(
            description="Comprehensive list of search engine queries to answer the user's questions.",
        )
    
    gen_queries_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful research assistant. Query the search engine to answer the user's questions.",
            ),
            MessagesPlaceholder(variable_name="messages", optional=True),
        ]
    )
    gen_queries_chain = gen_queries_prompt | fast_llm.with_structured_output(Queries, include_raw=True)
    
    
    class AnswerWithCitations(BaseModel):
        answer: str = Field(
            description="Comprehensive answer to the user's question with citations.",
        )
        cited_urls: List[str] = Field(
            description="List of urls cited in the answer.",
        )
    
        @property
        def as_str(self) -> str:
            return f"{self.answer}\n\nCitations:\n\n" + "\n".join(
                f"[{i+1}]: {url}" for i, url in enumerate(self.cited_urls)
            )
    
    
    gen_answer_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an expert who can use information effectively. You are chatting with a Wikipedia writer who wants to write a Wikipedia page on the topic you know. You have gathered the related information and will now use the information to form a response. \
                Assume that this Wikipedia page will be read by consultants and senior executives working in energy and utility sectors for insights.  
                Readers are interested in reading about the trends in markets, facts and figures, regulations, policies and standards, challenges and risk and solutions around the topics.
    
                Make your response as informative as possible and make sure every sentence is supported by the gathered information.
                Each response must be backed up by a citation from a reliable source, formatted as a footnote, reproducing the URLS after your response.""",
            ),
            MessagesPlaceholder(variable_name="messages", optional=True),
        ]
    )
    
    gen_answer_chain = gen_answer_prompt | fast_llm.with_structured_output(
        AnswerWithCitations, include_raw=True
    ).with_config(run_name="GenerateAnswer")
        
    @tool
    async def search_knowledge_catalogue(query: str):
        """Search pinecone vector database"""
        pinecone.init(
        api_key= pinecone_api_key, 
        environment= pinecone_envo
        )
        # print('************')
        # print('Inside search_knowledge_catalogue ', pinecone_index)
        # print('************')

        index = pinecone.Index(pinecone_index)
        embeddings = OpenAIEmbeddings(openai_api_key = open_ai_api_key)
        vectorstore = Pinecone(index, embeddings, "text")
    
        results_1 = vectorstore.similarity_search_with_score(query)

        # Filter results based on the threshold
        results = [doc for doc, score in results_1 if score >= 0.7]
        return [{"content": r.page_content, "url": f"Document: {r.metadata['document_title']}, Date Published: {r.metadata['date_published']}, Page Number: {r.metadata['page_number']}"} for r in results]

    @tool
    async def search_engine(query: str):
        """Search engine to the internet."""
        results = DuckDuckGoSearchAPIWrapper()._ddgs_text(query)
        processed_results = [{"content": r["body"], "url": r["href"]} for r in results]

        return processed_results
    
    async def gen_answer(
        state: InterviewState,
        config: Optional[RunnableConfig] = None,
        name: str = "Subject_Matter_Expert",
        max_str_len: int = 15000
    ):
        name = sanitize_name(name)
        swapped_state = swap_roles(state, name)  # Convert all other AI messages
        queries = await gen_queries_chain.ainvoke(swapped_state)
        
            
        query_results = await search_engine.abatch(
            queries["parsed"].queries, config, return_exceptions=True
        )

        successful_results = [
            res for res in query_results if not isinstance(res, Exception)
        ]
        
        ## Logic to fetch data from Agent Bruno vectorstore
        if pinecone_index != '':
            #print("********** Pinecone index is provided.********")
            vector_results = await search_knowledge_catalogue.abatch(queries["parsed"].queries)
            successful_results.extend(vector_results)
        
        all_query_results = {
            res["url"]: res["content"] for results in successful_results for res in results
        }

        # We could be more precise about handling max token length if we wanted to here
        dumped = json.dumps(all_query_results)[:max_str_len]
        ai_message: AIMessage = queries["raw"]
        tool_call = queries["raw"].additional_kwargs["tool_calls"][0]
        tool_id = tool_call["id"]
        tool_message = ToolMessage(tool_call_id=tool_id, content=dumped)
        swapped_state["messages"].extend([ai_message, tool_message])
        # Only update the shared state with the final answer to avoid
        # polluting the dialogue history with intermediate messages
        generated = await gen_answer_chain.ainvoke(swapped_state)

        cited_urls = set(generated["parsed"].cited_urls)
        # Save the retrieved information to a the shared state for future reference
        cited_references = {k: v for k, v in all_query_results.items() if k in cited_urls}
        formatted_message = AIMessage(name=name, content=generated["parsed"].as_str)
                
        return {"messages": [formatted_message], "references": cited_references}
    
    # End logic for generating answers
    
    # Start logic for routing messages
    max_num_turns = 5
    

    def route_messages(state: InterviewState, name: str = "Subject_Matter_Expert"):
        messages = state["messages"]
        #name = sanitize_name(name)
        num_responses = len(
            [m for m in messages if isinstance(m, AIMessage) and m.name == name]
        )
        if num_responses >= max_num_turns:
            return END
        last_question = messages[-2]
        if last_question.content.endswith("Thank you so much for your help!"):
            return END
        return "ask_question"
    
    # End logic for routing messages
    
    
    builder = StateGraph(InterviewState)
    
    builder.add_node("ask_question", generate_question)
    builder.add_node("answer_question", gen_answer)
    builder.add_conditional_edges("answer_question", route_messages)
    builder.add_edge("ask_question", "answer_question")
    
    builder.set_entry_point("ask_question")
    interview_graph = builder.compile().with_config(run_name="Conduct Interviews")
    
    initial_states = [
        {
            "editor": editor,
            "messages": [
                AIMessage(
                    content=f"So you said you were writing an article on {topic}?",
                    name=sanitize_name("Subject_Matter_Expert"),
                )
            ],
        }
        for editor in state["editors"]
    ]
    
    config = {"recursion_limit": 100}
    
    interview_results = await interview_graph.abatch(initial_states, config=config)


    return {
        **state,
        "interview_results": interview_results,
    }

# End of conduct_interviews
async def refine_outline(state: ResearchState):
    """
    Refines the outline of the Wikipedia page based on conversations with subject-matter experts.

    Args:
        state (ResearchState): The current research state containing the topic, old outline, and interview results.

    Returns:
        dict: The updated research state including the refined outline.
    """
    
    # Function to format conversation messages for display
    def format_conversation(interview_state):
        messages = interview_state["messages"]
        convo = "\n".join(f"{m.name}: {m.content}" for m in messages)
        return f'Conversation with {interview_state["editor"].name}\n\n' + convo

    # Extract conversation messages from interview results
    convos = "\n\n".join(
        [
            format_conversation(interview_state)
            for interview_state in state["interview_results"]
        ]
    )

    # Define prompt for refining the outline
    refine_outline_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a Wikipedia writer. You have gathered information from experts and search engines. Now, you are refining the outline of the Wikipedia page. \
                You need to make sure that the outline is comprehensive and specific. \
                Topic you are writing about: {topic} 
                
                Old outline:
                
                {old_outline}""",
            ),
            (
                "user",
                "Refine the outline based on your conversations with subject-matter experts:\n\nConversations:\n\n{conversations}\n\nWrite the refined Wikipedia outline:",
            ),
        ]
    )

    open_ai_api_key = state["open_ai_key"]
    long_context_llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key = open_ai_api_key, temperature=0)
    
    # Use Turbo model for generating the refined outline
    refine_outline_chain = refine_outline_prompt | long_context_llm.with_structured_output(
        Outline
    )
    
    # Invoke the refinement chain to generate the updated outline
    updated_outline = await refine_outline_chain.ainvoke(
        {
            "topic": state["topic"],
            "old_outline": state["outline"].as_str,
            "conversations": convos,
        }
    )
    return {**state, "outline": updated_outline}
# End of refine_outline

# Start of index_references


async def index_references(state: ResearchState):
    """
    Indexes the reference documents obtained from interviews into the vector store.

    Args:
        state (ResearchState): The current research state containing the interview results.

    Returns:
        ResearchState: The unchanged research state.
    """
    all_docs = []
    
    open_ai_api_key = state["open_ai_key"]
    
    embeddings = OpenAIEmbeddings(openai_api_key = open_ai_api_key)
    
    vectorstore = SKLearnVectorStore(embeddings)
    
    
    # Iterate through each interview result to extract reference documents
    for interview_state in state["interview_results"]:
        # Extract reference documents from the interview state and create Document objects
        reference_docs = [
            Document(page_content=v, metadata={"source": k})
            for k, v in interview_state["references"].items()
        ]
        # Add reference documents to the list of all documents
        all_docs.extend(reference_docs)
    
    # Check if there are any reference documents
    if len(all_docs) > 0:
        # If reference documents exist, add them to the vector store
        
        print("*****index_references****** : ", len(all_docs))
        
        await vectorstore.aadd_documents(all_docs)


        
    else:
        # If there are no reference documents, handle it as an error
        #print('If there are no reference documents, handle as error --> Logic to be written')
        return 'Problem referencing index. There are no reference documents to wirte this article. Try again.'
        
    #return state
    return {
        **state,
        "vectorstore": vectorstore,
    }

# End of index_references

async def write_sections(state: ResearchState):
    """
    Writes WikiSections based on the provided outline and topic in the research state.

    Args:
        state (ResearchState): The current research state containing the outline and topic.

    Returns:
        dict: The updated research state including the written sections.
    """
    # Extract the outline from the state
    outline = state["outline"]

    open_ai_api_key = state["open_ai_key"]
    long_context_llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key = open_ai_api_key, temperature=0)
    vectorstore = state["vectorstore"]
    
    # Define the prompt template for writing WikiSections
    section_writer_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert Wikipedia writer. Complete your assigned WikiSection from the following outline:\n\n"
                "Just remember that you are writing this page for consultants and executive working for energy and utility sectors."
                "{outline}\n\nCite your sources, using the following references:\n\n<Documents>\n{docs}\n<Documents>",
            ),
            ("user", "Write the full WikiSection for the {section} section."),
        ]
    )
    # Initialize the retriever for retrieving documents from the vector store
    retriever = vectorstore.as_retriever(k=10)
        
    # Define the retrieve function to retrieve documents related to the section topic
    async def retrieve(inputs: dict):
        # Retrieve documents related to the section topic
        docs = await retriever.ainvoke(inputs["topic"] + ": " + inputs["section"])
        # Format the retrieved documents
        formatted = "\n".join(
            [
                f'<Document href="{doc.metadata["source"]}"/>\n{doc.page_content}\n</Document>'
                for doc in docs
            ]
        )
        print("****write_section*****")
        print(formatted)
        print("*********")
        return {"docs": formatted, **inputs}

    # Define the section writer pipeline
    section_writer = (
        retrieve
        | section_writer_prompt
        | long_context_llm.with_structured_output(WikiSection)
    )
    
    # Write WikiSections for each section in the outline
    sections = await section_writer.abatch(
        [
            {
                "outline": state["outline"],
                "section": section.section_title,
                "topic": state["topic"],
            }
            for section in outline.sections
        ]
    )

    # Return the updated state with the written sections
    return {
        **state,
        "sections": sections,
    }

async def write_article(state: ResearchState):
    """
    Generates the complete wiki article based on the given section drafts and topic.

    Args:
        state (ResearchState): The current research state containing the topic and section drafts.

    Returns:
        dict: The updated research state including the generated article.
    """
    # Extract the topic and sections from the state

    topic = state["topic"]
    sections = state["sections"]

    # Concatenate the section drafts to form the article draft
    draft = "\n\n".join([section.as_str for section in sections])
    
    # Define the prompt for the article writer
    writer_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert Wikipedia author. Write the complete wiki article on {topic} using the following section drafts:\n\n"
                "{draft}\n\nStrictly follow Wikipedia format guidelines.",
            ),
            (
                "user",
                "Write the complete Wiki article using markdown format. Organize citations using footnotes like '[1]',"
                " avoiding duplicates in the footer. Include URLs in the footer.",
            ),
        ]
    )
    
    open_ai_api_key = state["open_ai_key"]
    long_context_llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key = open_ai_api_key, temperature=0)
    
    # Define the writer pipeline
    writer = writer_prompt | long_context_llm | StrOutputParser()
    
    # Invoke the writer to generate the article
    article = await writer.ainvoke({"topic": topic, "draft": draft})

    # Return the updated state with the generated article
    return {
        **state,
        "article": article,
    }

# End of write_sections