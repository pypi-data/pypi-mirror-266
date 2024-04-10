from .research import (
    ResearchState, 
    initialize_research,
    conduct_interviews,
    refine_outline,
    index_references,
    write_sections,
    write_article,
)
from langgraph.graph import StateGraph, END

class Storm:
       
    def __init__(self, topic, open_ai_key, pinecone_api_key='', pinecone_envo='', pinecone_index=''):
        self.topic = topic
        self.open_ai_key = open_ai_key
        self.pinecone_api_key = pinecone_api_key
        self.pinecone_envo = pinecone_envo
        self.pinecone_index = pinecone_index

    
    async def write_storm_article(self):
        
        try:
            builder_of_storm = StateGraph(ResearchState)
            
            
            nodes = [
                ("init_research", initialize_research),
                ("conduct_interviews", conduct_interviews),
                ("refine_outline", refine_outline),
                ("index_references", index_references),
                ("write_sections", write_sections),
                ("write_article", write_article),
            ]
            
            for i in range(len(nodes)):
                name, node = nodes[i]
                builder_of_storm.add_node(name, node)
                if i > 0:
                    builder_of_storm.add_edge(nodes[i - 1][0], name)
            
            builder_of_storm.set_entry_point(nodes[0][0])
            builder_of_storm.set_finish_point(nodes[-1][0])
            writer_graph = builder_of_storm.compile()
            
            config = {"recursion_limit": 100}
            
            async for step in writer_graph.astream(
                {
                    "topic": self.topic,
                    "open_ai_key": self.open_ai_key,
                    "pinecone_api_key": self.pinecone_api_key,
                    "pinecone_envo": self.pinecone_envo,
                    "pinecone_index": self.pinecone_index
                }, config=config
            ):
                name = next(iter(step))
                print(name)
                print("-- ", str(step[name])[:300])
                if END in step:
                    results = step
            
            article = results[END]["article"]
            
            return article
        
        except Exception as e:
            # Handle the exception here
            #print(f"An error occurred: {e}")
            return f"An error occurred: {e}" 