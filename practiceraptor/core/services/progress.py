"""Progress tracking pure functions."""
from datetime import datetime

from core.domain.models import Progress
from core.domain.enums import Difficulty, Language, ProgressStatus
from core.domain.result import Ok, Err
from core.ports.repositories import IProgressRepository


def get_user_progress(
    user_id: str,
    problem_id: int,
    progress_repo: IProgressRepository,
) -> Progress:
    """Get user progress for a problem, creating initial if not exists."""
    result = progress_repo.get(user_id, problem_id)
    match result:
        case Ok(progress):
            return progress
        case Err(_):
            return Progress(
                user_id=user_id,
                problem_id=problem_id,
                status=ProgressStatus.NOT_STARTED,
                attempts=0,
                solved_languages=(),
            )


def update_progress_on_attempt(
    progress: Progress,
    solved: bool,
    language: Language,
) -> Progress:
    """Create updated progress after an attempt (immutable)."""
    new_attempts = progress.attempts + 1

    if solved:
        new_languages = progress.solved_languages
        if language not in new_languages:
            new_languages = (*new_languages, language)

        return Progress(
            user_id=progress.user_id,
            problem_id=progress.problem_id,
            status=ProgressStatus.SOLVED,
            attempts=new_attempts,
            solved_languages=new_languages,
            first_solved_at=progress.first_solved_at or datetime.now(),
        )
    else:
        new_status = (
            ProgressStatus.SOLVED
            if progress.status == ProgressStatus.SOLVED
            else ProgressStatus.IN_PROGRESS
        )
        return Progress(
            user_id=progress.user_id,
            problem_id=progress.problem_id,
            status=new_status,
            attempts=new_attempts,
            solved_languages=progress.solved_languages,
            first_solved_at=progress.first_solved_at,
        )


def calculate_user_stats(
    user_id: str,
    progress_repo: IProgressRepository,
) -> dict:
    """Calculate overall user statistics."""
    all_progress = progress_repo.get_all_for_user(user_id)

    solved = [p for p in all_progress if p.status == ProgressStatus.SOLVED]
    in_progress = [p for p in all_progress if p.status == ProgressStatus.IN_PROGRESS]

    return {
        "total_solved": len(solved),
        "in_progress": len(in_progress),
        "total_attempts": sum(p.attempts for p in all_progress),
    }


def calculate_stats_by_difficulty(
    user_id: str,
    progress_repo: IProgressRepository,
    problem_difficulties: dict[int, Difficulty],
) -> dict[Difficulty, dict]:
    """Calculate stats grouped by difficulty."""
    all_progress = progress_repo.get_all_for_user(user_id)

    stats: dict[Difficulty, dict] = {d: {"solved": 0, "total": 0} for d in Difficulty}

    for progress in all_progress:
        difficulty = problem_difficulties.get(progress.problem_id)
        if difficulty:
            stats[difficulty]["total"] += 1
            if progress.status == ProgressStatus.SOLVED:
                stats[difficulty]["solved"] += 1

    return stats
