import os
import logging
from app.db.mongo import get_database

logger = logging.getLogger(__name__)

class AnalysisAgent:
    def __init__(self):
        self.llm = self._get_llm()
        self._load_prompt()

    def _get_llm(self):
        try:
            from app.ai.llm_provider import get_llm_provider
            return get_llm_provider()
        except Exception as e:
            logger.warning(f"LLM provider unavailable: {e}. Using rule-based analysis.")
            return None

    def _load_prompt(self):
        try:
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            backend_dir = os.path.dirname(backend_dir)
            backend_dir = os.path.dirname(backend_dir)
            prompt_path = os.path.join(backend_dir, "docs", "prompts", "analysis_agent.txt")
            with open(prompt_path, "r") as f:
                self.system_prompt = f.read()
        except Exception:
            self.system_prompt = ""

    async def analyze(self):
        db = get_database()

        products = []
        async for p in db.products.find():
            p["_id"] = str(p["_id"])
            products.append(p)

        logs = []
        async for l in db.inventory_logs.find().limit(100):
            l["_id"] = str(l["_id"])
            logs.append(l)

        # Rule-based analysis (always works, no LLM needed)
        alerts = []
        for p in products:
            qty = p.get("quantity", 0)
            threshold = p.get("reorder_threshold", 10)
            name = p.get("name", "Unknown")
            sku = p.get("sku", "")
            if qty == 0:
                alerts.append({
                    "product_name": name,
                    "sku": sku,
                    "message": f"{name} is completely out of stock. Immediate reorder required.",
                    "severity": "high",
                    "quantity": qty,
                    "threshold": threshold
                })
            elif qty <= threshold:
                alerts.append({
                    "product_name": name,
                    "sku": sku,
                    "message": f"{name} is running low ({qty} units remaining, threshold: {threshold}).",
                    "severity": "medium",
                    "quantity": qty,
                    "threshold": threshold
                })

        summary = f"Analyzed {len(products)} products. Found {len(alerts)} alerts."

        # Try LLM enhancement if available
        if self.llm and self.system_prompt:
            try:
                from langchain_core.prompts import ChatPromptTemplate
                from langchain_core.output_parsers import JsonOutputParser
                parser = JsonOutputParser()
                prompt = ChatPromptTemplate.from_messages([
                    ("system", self.system_prompt),
                    ("user", "Analyze this data: Products: {products}, Logs: {logs}")
                ])
                chain = prompt | self.llm | parser
                result = await chain.ainvoke({"products": products, "logs": logs})
                return result
            except Exception as e:
                logger.warning(f"LLM analysis failed, using rule-based: {e}")

        return {"alerts": alerts, "summary": summary}
