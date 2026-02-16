class CopilotService:
    def __init__(self, retriever):
        self.retriever = retriever

    def generate_response(self, intent, query):
        context = self.retriever.retrieve(query)

        return {
            "intent": intent,
            "context": context,
            "final_response": f"Intent detected: {intent}. Based on context: {context}"
        }
