import os
import logging
from app.db.mongo import get_database

logger = logging.getLogger(__name__)

class RecommendationAgent:
    def __init__(self):
        self.llm = self._get_llm()
        self._load_prompt()

    def _get_llm(self):
        try:
            from app.ai.llm_provider import get_llm_provider
            return get_llm_provider()
        except Exception as e:
            logger.warning(f"LLM provider unavailable: {e}. Using rule-based recommendations.")
            return None

    def _load_prompt(self):
        try:
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            backend_dir = os.path.dirname(backend_dir)
            backend_dir = os.path.dirname(backend_dir)
            prompt_path = os.path.join(backend_dir, "docs", "prompts", "recommendation_agent.txt")
            with open(prompt_path, "r") as f:
                self.system_prompt = f.read()
        except Exception:
            self.system_prompt = ""

    async def get_recommendations(self):
        db = get_database()

        products = []
        async for p in db.products.find():
            p["_id"] = str(p["_id"])
            products.append(p)

        suppliers = []
        async for s in db.suppliers.find():
            s["_id"] = str(s["_id"])
            suppliers.append(s)

        # Rule-based recommendations (always works)
        recommendations = []
        insights = []

        low_stock = [p for p in products if p.get("quantity", 0) <= p.get("reorder_threshold", 10)]
        out_of_stock = [p for p in products if p.get("quantity", 0) == 0]
        
        for p in out_of_stock:
            recommendations.append({
                "product_name": p.get("name"),
                "sku": p.get("sku"),
                "action": "Urgent Reorder",
                "reason": "Product is completely out of stock",
                "suggested_quantity": p.get("reorder_threshold", 10) * 3,
                "priority": "critical"
            })

        for p in low_stock:
            if p not in out_of_stock:
                recommendations.append({
                    "product_name": p.get("name"),
                    "sku": p.get("sku"),
                    "action": "Reorder Soon",
                    "reason": f"Stock ({p.get('quantity')}) is at or below reorder threshold ({p.get('reorder_threshold')})",
                    "suggested_quantity": p.get("reorder_threshold", 10) * 2,
                    "priority": "high"
                })

        healthy = [p for p in products if p.get("quantity", 0) > p.get("reorder_threshold", 10)]
        insights.append(f"{len(healthy)} products have healthy stock levels.")
        if out_of_stock:
            insights.append(f"{len(out_of_stock)} products are out of stock and need immediate attention.")
        if len(suppliers) > 0:
            insights.append(f"{len(suppliers)} suppliers are available for procurement.")

        # Try LLM enhancement if available
        if self.llm and self.system_prompt:
            try:
                from langchain_core.prompts import ChatPromptTemplate
                from langchain_core.output_parsers import JsonOutputParser
                parser = JsonOutputParser()
                prompt = ChatPromptTemplate.from_messages([
                    ("system", self.system_prompt),
                    ("user", "Inventory Data: {products}, Suppliers: {suppliers}")
                ])
                chain = prompt | self.llm | parser
                return await chain.ainvoke({"products": products, "suppliers": suppliers})
            except Exception as e:
                logger.warning(f"LLM recommendation failed, using rule-based: {e}")

        return {"recommendations": recommendations, "insights": insights}
