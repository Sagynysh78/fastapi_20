from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List
from notes.models import Note
from notes.schemas import NoteCreate, NoteUpdate, NoteOut
from models import User
from database import get_session
from auth.dependencies import get_current_user
from redis_cache import get_cache_manager, CacheManager

router = APIRouter(prefix="/notes", tags=["notes"])

@router.post("/", response_model=NoteOut)
async def create_note(
    note_in: NoteCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    cache_manager: CacheManager = Depends(get_cache_manager)
):
    note = Note(text=note_in.text, owner_id=current_user.id)
    session.add(note)
    await session.commit()
    await session.refresh(note)
    
    # Invalidate cache for this user
    await cache_manager.delete_pattern(f"notes:{current_user.id}:*")
    print(f"Cache invalidated for user {current_user.id} after creating note")
    
    return note

@router.get("/", response_model=List[NoteOut])
async def read_notes(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    cache_manager: CacheManager = Depends(get_cache_manager),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    search: str = Query(None)
):
    # Generate cache key based on user and query parameters
    cache_key = f"notes:{current_user.id}:{skip}:{limit}:{search or 'none'}"
    
    # Try to get data from cache first
    cached_data = await cache_manager.get(cache_key)
    if cached_data:
        print(f"Cache HIT for key: {cache_key}")
        return cached_data
    
    print(f"Cache MISS for key: {cache_key}")
    
    # If not in cache, get from database
    query = select(Note).where(Note.owner_id == current_user.id)
    if search:
        query = query.where(Note.text.contains(search))
    query = query.offset(skip).limit(limit)
    result = await session.execute(query)
    notes = result.scalars().all()
    
    # Convert to dict for caching (Pydantic models need to be serialized)
    notes_data = [note.dict() for note in notes]
    
    # Store in cache
    await cache_manager.set(cache_key, notes_data)
    
    return notes

@router.get("/{note_id}", response_model=NoteOut)
async def read_note(
    note_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    note = await session.get(Note, note_id)
    if not note or note.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.put("/{note_id}", response_model=NoteOut)
async def update_note(
    note_id: int,
    note_in: NoteUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    cache_manager: CacheManager = Depends(get_cache_manager)
):
    note = await session.get(Note, note_id)
    if not note or note.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Note not found")
    if note_in.text is not None:
        note.text = note_in.text
    await session.commit()
    await session.refresh(note)
    
    # Invalidate cache for this user
    await cache_manager.delete_pattern(f"notes:{current_user.id}:*")
    print(f"Cache invalidated for user {current_user.id} after updating note {note_id}")
    
    return note

@router.delete("/{note_id}")
async def delete_note(
    note_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    cache_manager: CacheManager = Depends(get_cache_manager)
):
    note = await session.get(Note, note_id)
    if not note or note.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Note not found")
    await session.delete(note)
    await session.commit()
    
    # Invalidate cache for this user
    await cache_manager.delete_pattern(f"notes:{current_user.id}:*")
    print(f"Cache invalidated for user {current_user.id} after deleting note {note_id}")
    
    return {"ok": True} 