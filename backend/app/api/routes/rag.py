from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.core.database import get_db
from app.rag.pipeline import rag_answer

router = APIRouter(prefix="/api/admin", tags=["rag"], dependencies=[Depends(require_admin)])


class RagQuery(BaseModel):
    query: str


@router.post("/rag/query")
async def query_rag(body: RagQuery, db: AsyncSession = Depends(get_db)) -> dict:
    return await rag_answer(db, body.query)