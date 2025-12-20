"""Draft management pure functions."""
from datetime import datetime

from core.domain.models import Draft
from core.domain.enums import Language
from core.domain.result import Ok, Err, Result
from core.domain.errors import NotFoundError, StorageError
from core.ports.repositories import IDraftRepository


def get_draft(
    user_id: str,
    problem_id: int,
    language: Language,
    draft_repo: IDraftRepository,
) -> Result[Draft, NotFoundError]:
    """Get existing draft."""
    return draft_repo.get(user_id, problem_id, language)


def save_draft(
    user_id: str,
    problem_id: int,
    language: Language,
    code: str,
    draft_repo: IDraftRepository,
) -> Result[Draft, StorageError]:
    """Save or update draft."""
    draft = Draft(
        user_id=user_id,
        problem_id=problem_id,
        language=language,
        code=code,
        updated_at=datetime.now(),
    )
    return draft_repo.save(draft)


def delete_draft(
    user_id: str,
    problem_id: int,
    language: Language,
    draft_repo: IDraftRepository,
) -> Result[None, NotFoundError]:
    """Delete draft after successful submission."""
    return draft_repo.delete(user_id, problem_id, language)


def get_or_create_code(
    user_id: str,
    problem_id: int,
    language: Language,
    signature: str,
    draft_repo: IDraftRepository,
) -> str:
    """Get draft code or return template with signature."""
    result = get_draft(user_id, problem_id, language, draft_repo)
    match result:
        case Ok(draft):
            return draft.code
        case Err(_):
            # Return template with just the signature
            return f"{signature}\n    pass"
