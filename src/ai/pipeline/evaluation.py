from langchain_openai import ChatOpenAI
from langgraph.types import Command
from typing import Literal, List, Dict, Any
from src.ai.pipeline.agent_state import AgentState
from src.logging import AgentLogger
from colorama import Fore, Style
from src.ai.embedding import EmbeddingGenerator

class Evaluation:
    """
    This class is used to evaluate the conversation between the student and the teacher.
    Only called when the user ends the conversation.
    """

    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(model=model_name)
        self.logger = AgentLogger.get_logger("Evaluation")
        self.embedding_generator = EmbeddingGenerator()

    def retrieve_classroom_management_context(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve relevant classroom management knowledge from the vector store.
        
        Args:
            query: The search query to find relevant classroom management information
            top_k: Number of most relevant documents to retrieve
            
        Returns:
            List of relevant documents with their content and metadata
        """
        self.logger.info(f"Retrieving classroom management context for: {query}")
        
        try:
            # Generate embedding for the query
            chroma_client = self.embedding_generator.return_chroma()
            
            # Search for similar documents in the vector store
            search_results = chroma_client.similarity_search_with_score(
                query=query, 
                k=top_k
            )
            
            results = []
            for doc, score in search_results:
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": score
                })
                
            self.logger.info(f"Found {len(results)} relevant classroom management documents")
            return results
        
        except Exception as e:
            self.logger.error(f"Error retrieving classroom management context: {str(e)}")
            return []

    def evaluate(self, state: AgentState) -> Command[Literal['supervisor']]:
        """
        Evaluate the conversation between teacher and student.

        Args:
            state: Current agent state

        Returns:
            Command with evaluation results
        """
        self.logger.info("Running conversation evaluation")

        messages = state.get("messages", [])
        student_profile = state.get("studentProfile", "No profile available")
        scenario = state.get("scenario", "No scenario available")

        # Skip if there aren't enough messages
        if len(messages) < 3:
            self.logger.warning("Not enough messages to evaluate")
            evaluation_results = {
                "summary": "Conversation was too short to evaluate.",
                "effectiveness": "N/A",
                "authenticity": "N/A",
                "suggestions": ["Have a longer conversation to receive meaningful feedback."]
            }
        else:
            # Extract conversation topics for knowledge base retrieval
            conversation_text = "\n".join([
                f"{msg.name if hasattr(msg, 'name') else 'Unknown'}: {msg.content if hasattr(msg, 'content') else str(msg)}"
                for msg in messages
            ])
            
            # Extract key classroom management topics from the conversation
            extraction_prompt = f"""
            Given this teacher-student conversation, identify 1-3 key classroom management 
            topics or challenges that are addressed or should have been addressed.
            Return these as a comma-separated list of concise search terms.
            
            CONVERSATION:
            {conversation_text}
            """
            
            self.logger.debug("Extracting classroom management topics from conversation")
            topic_extraction = self.llm.invoke(extraction_prompt)
            search_topics = topic_extraction.content if hasattr(topic_extraction, 'content') else str(topic_extraction)
            
            self.logger.info(f"Extracted classroom management topics: {search_topics}")
            
            # Retrieve relevant classroom management knowledge
            kb_results = self.retrieve_classroom_management_context(search_topics)
            
            # Format KB content for the evaluation prompt
            kb_context = ""
            if kb_results:
                kb_context = "\nRELEVANT CLASSROOM MANAGEMENT KNOWLEDGE:\n"
                for i, result in enumerate(kb_results):
                    kb_context += f"{i+1}. {result['content']}\n\n"
            
            # Create evaluation prompt with KB content
            evaluation_prompt = f"""
            You are an educational expert evaluating a teacher-student interaction.
            
            STUDENT PROFILE:
            {student_profile}
            
            SCENARIO:
            {scenario}
            
            {kb_context}
            
            Analyze the following conversation between a teacher and student.
            Evaluate how well the teacher addressed the student's needs based on their profile.
            Compare the teacher's approach to best practices in classroom management from the knowledge provided.
            
            CONVERSATION:
            {[f"{msg.name if hasattr(msg, 'name') else 'Unknown'}: {msg.content if hasattr(msg, 'content') else str(msg)}"
             for msg in messages]}
            
            Provide the following in your evaluation:
            1. Summary of the interaction
            2. Effectiveness score (1-10) with explanation
            3. Authenticity score (1-10) for how well the student was portrayed
            4. Specific suggestions for improvement based on classroom management best practices
            
            Format your response as JSON with the following keys:
            summary, effectiveness, authenticity, suggestions
            """

            # Get evaluation from LLM
            try:
                self.logger.debug("Sending evaluation prompt to LLM")
                result = self.llm.invoke(evaluation_prompt)

                response_content = result.content if hasattr(
                    result, 'content') else str(result)

                # Try to parse as JSON, fallback to text if not valid JSON
                try:
                    import json
                    import re

                    # Extract JSON if it's wrapped in backticks
                    json_match = re.search(
                        r'```json\s*(.*?)\s*```', response_content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1)
                    else:
                        json_str = response_content

                    evaluation_results = json.loads(json_str)
                    self.logger.debug(
                        "Successfully parsed evaluation results as JSON")
                except:
                    self.logger.warning(
                        "Could not parse evaluation as JSON, using raw text")
                    evaluation_results = {
                        "summary": response_content[:500],
                        "effectiveness": "See summary",
                        "authenticity": "See summary",
                        "suggestions": ["See summary for details"]
                    }
            except Exception as e:
                self.logger.error(f"Error during evaluation: {str(e)}")
                evaluation_results = {
                    "summary": f"Error during evaluation: {str(e)}",
                    "effectiveness": "Error",
                    "authenticity": "Error",
                    "suggestions": ["Try again later."]
                }

        # Print evaluation results
        print("\n" + "="*50)
        print(f"{Fore.GREEN}CONVERSATION EVALUATION:{Style.RESET_ALL}")
        print(
            f"Summary: {evaluation_results.get('summary', 'No summary available')}")
        print(
            f"Effectiveness: {evaluation_results.get('effectiveness', 'N/A')}")
        print(f"Authenticity: {evaluation_results.get('authenticity', 'N/A')}")
        print("Suggestions:")
        for suggestion in evaluation_results.get('suggestions', ['No suggestions available']):
            print(f"- {suggestion}")
        print("="*50)

        # Update UI metadata
        ui_metadata = state.get("ui_metadata", {})
        ui_metadata.update({
            "is_evaluating": False,
            "is_complete": True,
            "evaluation_complete": True
        })

        return Command(
            update={
                'current_node': 'evaluation',
                'evaluation_results': evaluation_results,
                'conversation_done': True,
                'ui_metadata': ui_metadata
            },
            goto='supervisor'
        )
