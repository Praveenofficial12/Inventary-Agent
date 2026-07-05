import os
import logging
from app.db.mongo import get_database

logger = logging.getLogger(__name__)

class AssistantAgent:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.llm = self._get_llm()
        self.rag = self._get_rag()
        self._load_prompt()

    def _get_llm(self):
        try:
            from app.ai.llm_provider import get_llm_provider
            return get_llm_provider()
        except Exception as e:
            logger.warning(f"LLM provider unavailable: {e}. Using rule-based chat.")
            return None

    def _get_rag(self):
        try:
            from app.ai.rag_pipeline import RAGPipeline
            return RAGPipeline()
        except Exception:
            return None

    def _load_prompt(self):
        try:
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            backend_dir = os.path.dirname(backend_dir)
            backend_dir = os.path.dirname(backend_dir)
            prompt_path = os.path.join(backend_dir, "docs", "prompts", "assistant_agent.txt")
            with open(prompt_path, "r") as f:
                self.system_prompt = f.read()
        except Exception:
            self.system_prompt = (
                "You are Nexus, an expert AI inventory management assistant. "
                "You have access to the company's full live stock database. "
                "Help users with questions about stock levels, low-stock alerts, reorder recommendations, "
                "product details, supplier info, and inventory valuation. "
                "When answering, always cite specific product names, SKUs, and quantities. "
                "Be concise, helpful, and professional."
            )

    async def _fetch_inventory(self):
        """Fetch all products and build a rich structured context."""
        db = get_database()

        # Fetch categories dict
        cat_map = {}
        async for c in db.categories.find():
            cat_map[str(c["_id"])] = c.get("name", "Unknown")

        # Fetch suppliers dict
        sup_map = {}
        async for s in db.suppliers.find():
            sup_map[str(s["_id"])] = s.get("name", "Unknown")

        # Fetch all products
        products = []
        async for p in db.products.find():
            p["_id"] = str(p["_id"])
            p["category_name"] = cat_map.get(p.get("category_id", ""), "Unknown")
            p["supplier_name"] = sup_map.get(p.get("supplier_id", ""), "Unknown")
            products.append(p)

        return products, cat_map, sup_map

    def _build_inventory_context(self, products):
        """Build a markdown-style summary of all products for LLM context."""
        lines = [
            f"LIVE INVENTORY DATABASE ({len(products)} products total):",
            "=" * 60,
        ]
        total_value = sum(p.get("quantity", 0) * p.get("unit_price", 0) for p in products)
        out_of_stock = [p for p in products if p.get("quantity", 0) == 0]
        low_stock = [p for p in products if 0 < p.get("quantity", 0) <= p.get("reorder_threshold", 10)]
        healthy = [p for p in products if p.get("quantity", 0) > p.get("reorder_threshold", 10)]

        lines.append(f"SUMMARY: Total Inventory Value: ${total_value:,.2f} | "
                     f"Out of Stock: {len(out_of_stock)} | Low Stock: {len(low_stock)} | Healthy: {len(healthy)}")
        lines.append("")

        if out_of_stock:
            lines.append("⛔ OUT OF STOCK (0 units):")
            for p in out_of_stock:
                lines.append(f"  - {p['name']} (SKU: {p['sku']}, Category: {p['category_name']}, Supplier: {p['supplier_name']}, Price: ${p.get('unit_price',0):.2f})")

        if low_stock:
            lines.append("\n⚠️ LOW STOCK (at or below reorder threshold):")
            for p in low_stock:
                lines.append(f"  - {p['name']} (SKU: {p['sku']}, Qty: {p['quantity']}, Threshold: {p['reorder_threshold']}, Category: {p['category_name']}, Supplier: {p['supplier_name']})")

        if healthy:
            lines.append("\n✅ HEALTHY STOCK (above threshold):")
            for p in healthy:
                lines.append(f"  - {p['name']} (SKU: {p['sku']}, Qty: {p['quantity']}, Price: ${p.get('unit_price',0):.2f}, Category: {p['category_name']})")

        return "\n".join(lines)

    async def get_response(self, user_input: str):
        db = get_database()

        products, cat_map, sup_map = await self._fetch_inventory()
        inventory_context = self._build_inventory_context(products)

        # Try RAG retrieval
        context_docs = ""
        if self.rag:
            try:
                relevant_docs = await self.rag.query(user_input, threshold=0.3)
                context_docs = "\n".join([doc.page_content for doc in relevant_docs])
            except Exception:
                pass

        # Try LLM first if available
        if self.llm:
            try:
                from langchain_core.prompts import ChatPromptTemplate

                full_system = self.system_prompt
                full_system += f"\n\n{inventory_context}"
                if context_docs:
                    full_system += f"\n\nPOLICY/COMPANY DOCUMENTS:\n{context_docs}"

                prompt = ChatPromptTemplate.from_messages([
                    ("system", full_system),
                    ("user", "{input}")
                ])
                chain = prompt | self.llm
                response = await chain.ainvoke({"input": user_input})
                return response.content
            except Exception as e:
                logger.warning(f"LLM chat failed: {e}")

        # ===== COMPREHENSIVE RULE-BASED FALLBACK =====
        user_lower = user_input.lower()

        # --- Out of stock ---
        if any(w in user_lower for w in ["out of stock", "zero stock", "no stock", "empty"]):
            out = [p for p in products if p.get("quantity", 0) == 0]
            if not out:
                return "✅ Great news! No products are currently out of stock."
            resp = f"⛔ **{len(out)} product(s) are completely out of stock:**\n\n"
            for p in out:
                resp += f"• **{p['name']}** (SKU: {p['sku']}) — Category: {p['category_name']}, Supplier: {p['supplier_name']}, Unit Price: ${p.get('unit_price',0):.2f}\n"
            resp += f"\n💡 Recommend placing urgent purchase orders for these {len(out)} items immediately."
            return resp

        # --- Low stock / reorder alerts ---
        elif any(w in user_lower for w in ["low stock", "low on stock", "reorder", "alert", "critical", "running low", "below threshold"]):
            low = [p for p in products if 0 < p.get("quantity", 0) <= p.get("reorder_threshold", 10)]
            out_stock = [p for p in products if p.get("quantity", 0) == 0]
            combined = out_stock + low
            if not combined:
                return "✅ All products are well-stocked above their reorder thresholds."
            resp = f"⚠️ **Stock Alert Summary — {len(combined)} item(s) need attention:**\n\n"
            if out_stock:
                resp += f"**⛔ OUT OF STOCK ({len(out_stock)} items):**\n"
                for p in out_stock:
                    resp += f"• {p['name']} (SKU: {p['sku']}) — Qty: 0 | Threshold: {p.get('reorder_threshold',10)} | Supplier: {p['supplier_name']}\n"
                resp += "\n"
            if low:
                resp += f"**⚠️ LOW STOCK ({len(low)} items):**\n"
                for p in low:
                    resp += f"• {p['name']} (SKU: {p['sku']}) — Qty: {p['quantity']} | Threshold: {p.get('reorder_threshold',10)} | Supplier: {p['supplier_name']}\n"
            return resp

        # --- Total value / valuation ---
        elif any(w in user_lower for w in ["total value", "worth", "valuation", "inventory value", "how much"]):
            total_val = sum(p.get("quantity", 0) * p.get("unit_price", 0) for p in products)
            by_cat = {}
            for p in products:
                cat = p.get("category_name", "Unknown")
                val = p.get("quantity", 0) * p.get("unit_price", 0)
                by_cat[cat] = by_cat.get(cat, 0) + val
            resp = f"💰 **Total Inventory Value: ${total_val:,.2f}**\n\n**Breakdown by Category:**\n"
            for cat, val in sorted(by_cat.items(), key=lambda x: -x[1]):
                resp += f"  • {cat}: ${val:,.2f}\n"
            return resp

        # --- Stock level for a specific product ---
        elif any(w in user_lower for w in ["stock", "quantity", "how many", "units", "available"]):
            # Check for specific product names
            matched = []
            words = user_lower.split()
            for p in products:
                pname = p["name"].lower()
                psku = p["sku"].lower()
                if any(w in pname or w in psku for w in words if len(w) > 2):
                    matched.append(p)

            if matched:
                resp = f"📦 **Stock levels for matching products:**\n\n"
                for p in matched[:10]:
                    status = "⛔ OUT OF STOCK" if p["quantity"] == 0 else ("⚠️ LOW" if p["quantity"] <= p.get("reorder_threshold", 10) else "✅ OK")
                    resp += f"• **{p['name']}** (SKU: {p['sku']}) — {p['quantity']} units {status}\n"
                return resp
            else:
                # Return summary
                out_c = sum(1 for p in products if p.get("quantity", 0) == 0)
                low_c = sum(1 for p in products if 0 < p.get("quantity", 0) <= p.get("reorder_threshold", 10))
                resp = f"📦 **Inventory Summary — {len(products)} total products:**\n\n"
                resp += f"• ⛔ Out of Stock: {out_c} products\n"
                resp += f"• ⚠️ Low Stock: {low_c} products\n"
                resp += f"• ✅ Healthy: {len(products) - out_c - low_c} products\n\n"
                resp += "Ask me about a specific product, category, or supplier for detailed info!"
                return resp

        # --- Top/expensive products ---
        elif any(w in user_lower for w in ["expensive", "costly", "highest price", "most valuable", "top product"]):
            top = sorted(products, key=lambda x: x.get("unit_price", 0), reverse=True)[:10]
            resp = "💎 **Top 10 Most Expensive Products:**\n\n"
            for i, p in enumerate(top, 1):
                resp += f"{i}. **{p['name']}** (SKU: {p['sku']}) — ${p.get('unit_price',0):.2f}/unit, Qty: {p['quantity']}\n"
            return resp

        # --- Category query ---
        elif any(w in user_lower for w in ["category", "categories", "department", "type"]):
            by_cat = {}
            for p in products:
                cat = p.get("category_name", "Unknown")
                if cat not in by_cat:
                    by_cat[cat] = {"count": 0, "value": 0}
                by_cat[cat]["count"] += 1
                by_cat[cat]["value"] += p.get("quantity", 0) * p.get("unit_price", 0)
            resp = f"📂 **Inventory by Category ({len(by_cat)} categories):**\n\n"
            for cat, info in sorted(by_cat.items()):
                resp += f"• **{cat}**: {info['count']} products, Value: ${info['value']:,.2f}\n"
            return resp

        # --- Supplier query ---
        elif any(w in user_lower for w in ["supplier", "vendor", "manufacturer", "source"]):
            by_sup = {}
            for p in products:
                sup = p.get("supplier_name", "Unknown")
                if sup not in by_sup:
                    by_sup[sup] = {"count": 0}
                by_sup[sup]["count"] += 1
            resp = f"🏭 **Supplier Overview ({len(by_sup)} suppliers):**\n\n"
            for sup, info in sorted(by_sup.items()):
                resp += f"• **{sup}**: {info['count']} products\n"
            return resp

        # --- Greetings ---
        elif any(w in user_lower for w in ["hello", "hi", "hey", "good morning", "good afternoon"]):
            out_c = sum(1 for p in products if p.get("quantity", 0) == 0)
            low_c = sum(1 for p in products if 0 < p.get("quantity", 0) <= p.get("reorder_threshold", 10))
            total_val = sum(p.get("quantity", 0) * p.get("unit_price", 0) for p in products)
            return (
                f"👋 Hello! I'm **Nexus**, your AI Inventory Intelligence assistant.\n\n"
                f"**Quick Snapshot:**\n"
                f"• 📦 Total Products: {len(products)}\n"
                f"• 💰 Total Value: ${total_val:,.2f}\n"
                f"• ⛔ Out of Stock: {out_c}\n"
                f"• ⚠️ Low Stock Alerts: {low_c}\n\n"
                f"I can help you with stock levels, alerts, valuations, supplier info, and more. What would you like to know?"
            )

        # --- Help ---
        elif any(w in user_lower for w in ["help", "what can you", "what do you", "capabilities"]):
            return (
                "🤖 **Nexus AI Inventory Assistant — Capabilities:**\n\n"
                "• 📦 **Stock Queries**: 'What is the stock level of MacBook Pro?'\n"
                "• ⚠️ **Low Stock Alerts**: 'What products are running low on stock?'\n"
                "• ⛔ **Out of Stock**: 'Show me all out of stock items'\n"
                "• 💰 **Valuation**: 'What is the total inventory value?'\n"
                "• 📂 **Categories**: 'Show me inventory by category'\n"
                "• 🏭 **Suppliers**: 'List all suppliers'\n"
                "• 💎 **Top Products**: 'What are the most expensive products?'\n"
                "• 📊 **Summary**: 'Give me an inventory summary'\n\n"
                "Just ask in plain English!"
            )

        # --- Default: full summary ---
        else:
            total_val = sum(p.get("quantity", 0) * p.get("unit_price", 0) for p in products)
            out_c = sum(1 for p in products if p.get("quantity", 0) == 0)
            low_c = sum(1 for p in products if 0 < p.get("quantity", 0) <= p.get("reorder_threshold", 10))
            resp = (
                f"🔍 I searched for that in the inventory database.\n\n"
                f"**Current Inventory Snapshot:**\n"
                f"• Total Products: {len(products)}\n"
                f"• Inventory Value: ${total_val:,.2f}\n"
                f"• ⛔ Out of Stock: {out_c} items\n"
                f"• ⚠️ Low Stock: {low_c} items\n\n"
                f"Could you be more specific? Try asking:\n"
                f"• 'Show me low stock items'\n"
                f"• 'What products are out of stock?'\n"
                f"• 'What is the stock level of [product name]?'"
            )
            return resp
