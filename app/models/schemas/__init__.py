# Import all schema classes to make them discoverable
from .notes import NotesExtraction
from .bookmarks import BookmarkExtraction
from .books import BookExtraction
from .job_postings import JobPostingExtraction
from .recipes import RecipeExtraction
from .quotes import QuotesExtraction
from .insights import InsightsExtraction

__all__ = [
    "NotesExtraction",
    "BookmarkExtraction",
    "BookExtraction",
    "JobPostingExtraction",
    "RecipeExtraction",
    "QuotesExtraction",
    "InsightsExtraction",
]
