import os
import logging
from app.db.mongo import get_database

logger = logging.getLogger(__name__)

class ReportAgent:
    def __init__(self):
        self.llm = self._get_llm()
        self._load_prompt()

    def _get_llm(self):
        try:
            from app.ai.llm_provider import get_llm_provider
            return get_llm_provider()
        except Exception as e:
            logger.warning(f"LLM provider unavailable: {e}. Using rule-based report.")
            return None

    def _load_prompt(self):
        try:
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            backend_dir = os.path.dirname(backend_dir)
            backend_dir = os.path.dirname(backend_dir)
            prompt_path = os.path.join(backend_dir, "docs", "prompts", "report_agent.txt")
            with open(prompt_path, "r") as f:
                self.system_prompt = f.read()
        except Exception:
            self.system_prompt = ""

    async def generate(self):
        db = get_database()

        products = []
        async for p in db.products.find():
            p["_id"] = str(p["_id"])
            products.append(p)

        # Try LLM
        if self.llm and self.system_prompt:
            try:
                from langchain_core.prompts import ChatPromptTemplate
                from langchain_core.output_parsers import JsonOutputParser
                parser = JsonOutputParser()
                prompt = ChatPromptTemplate.from_messages([
                    ("system", self.system_prompt),
                    ("user", "Data: {products}")
                ])
                chain = prompt | self.llm | parser
                return await chain.ainvoke({"products": products})
            except Exception as e:
                logger.warning(f"LLM report failed, using rule-based: {e}")

        # Rule-based report
        total_value = sum(p.get("quantity", 0) * p.get("unit_price", 0) for p in products)
        low_stock = [p for p in products if p.get("quantity", 0) <= p.get("reorder_threshold", 10)]
        out_of_stock = [p for p in products if p.get("quantity", 0) == 0]
        
        sections = [
            {
                "heading": "Inventory Overview",
                "content": f"Total products tracked: {len(products)}. Total inventory value: ${total_value:,.2f}."
            },
            {
                "heading": "Stock Alerts",
                "content": f"{len(out_of_stock)} items out of stock, {len(low_stock)} items below reorder threshold."
            },
            {
                "heading": "Low Stock Items",
                "content": ", ".join([p.get("name", "") for p in low_stock]) if low_stock else "All items adequately stocked."
            },
            {
                "heading": "Recommendations",
                "content": "Prioritize restocking out-of-stock items immediately. Review reorder thresholds for frequently low items."
            }
        ]

        return {
            "title": "Nexus AI Inventory Report",
            "summary": f"Comprehensive inventory analysis: {len(products)} products, ${total_value:,.2f} total value, {len(out_of_stock)} critical stock issues.",
            "key_metrics": {
                "total_products": len(products),
                "total_value": total_value,
                "low_stock_count": len(low_stock),
                "out_of_stock_count": len(out_of_stock)
            },
            "sections": sections
        }
