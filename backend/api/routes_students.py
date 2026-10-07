from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from backend.services.db_service import DatabaseService

router = APIRouter(prefix="/api", tags=["Students"])

@router.get("/students")
async def list_students(
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query("", description="Search by Student ID or Name")
):
    try:
        students = DatabaseService.get_all_students(limit=limit, search=search)
        return {
            "total": len(students),
            "students": students
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/student/{student_id}")
async def get_student(student_id: str):
    data = DatabaseService.get_student_by_id(student_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"Student with ID '{student_id}' not found.")
    return data
