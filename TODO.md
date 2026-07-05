# TODO - Finish Full Project (Backend + Localhost Run)

## Plan summary
- Inspect remaining backend files (models/auth/ai/utils) to find missing or buggy logic.
- Implement/fix backend so all routes work end-to-end (auth, products/categories/suppliers/inventory, upload/RAG, chat, agents, reports + PDF).
- Ensure frontend has working API contract (optionally adjust frontend types if needed).
- Make local run instructions work (localhost) using docker-compose.
- Smoke test with `test_login.py` and basic endpoint calls.

## Steps
- [ ] Inspect backend/app/models/*.py and backend/app/auth/*.py
- [ ] Inspect backend/app/ai/*.py and backend/app/ai/agents/*.py
- [ ] Inspect backend/app/utils/pdf_gen.py
- [ ] Inspect any Pydantic models used by routes for missing/incorrect fields
- [ ] Inspect docs/prompts and any rag/embedding config usage
- [ ] Implement fixes for runtime errors discovered
- [ ] Run backend locally (docker-compose) and confirm `/health`
- [ ] Run `test_login.py`
- [ ] Smoke test major endpoints: auth, products CRUD, upload, chat, reports
- [ ] Update README with exact localhost URLs and env var notes
- [ ] Final verification: document working commands
