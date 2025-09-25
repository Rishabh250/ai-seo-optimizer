"""
Data models for reviews information.
"""
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ReviewComment:
    """Individual review comment structure."""
    rating: Optional[int] = None
    comment: Optional[str] = None


@dataclass
class ReviewsData:
    """Complete reviews data structure."""
    comments: List[ReviewComment] = field(default_factory=list)
    overall_rating: Optional[float] = None
    college_id: Optional[int] = None
    college_name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    cleaned_raw: Optional[Dict[str, Any]] = None

    @classmethod
    def from_raw_output(cls, college_id: int, raw_output: str, college_name: str, city: str, state: str, cleaned_raw: Dict[str, Any]) -> "ReviewsData":
        """Create ReviewsData from raw JSON output."""
        try:
            if isinstance(raw_output, str):
                data = json.loads(raw_output)
            else:
                data = raw_output
        except json.JSONDecodeError:
            return cls(college_id=college_id)

        comments = []
        for comment_data in data.get("comments", []):
            if isinstance(comment_data, dict):
                rating = comment_data.get("rating")
                comment_text = comment_data.get("comment")
                
                if rating and rating >= 4:
                    comments.append(ReviewComment(
                        rating=rating,
                        comment=comment_text
                    ))

        return cls(
            comments=comments,
            overall_rating=data.get("overall_rating"),
            college_id=college_id,
            college_name=college_name,
            city=city,
            state=state,
            cleaned_raw=cleaned_raw
        )

    def extract_key_review_info(self) -> Dict[str, Any]:
        """Extract key review information for content generation."""
        info = {}
        
        info["college_id"] = self.college_id
        info["overall_rating"] = self.overall_rating or 4.0
        
        high_rating_comments = [c for c in self.comments if c.rating and c.rating >= 4]
        
        if high_rating_comments:
            info["total_reviews"] = len(high_rating_comments)
            info["average_rating"] = sum(c.rating for c in high_rating_comments) / len(high_rating_comments)
            
            sample_comments = high_rating_comments[:5]
            info["sample_comments"] = [c.comment for c in sample_comments if c.comment]
            
            rating_counts = {5: 0, 4: 0}
            for comment in high_rating_comments:
                if comment.rating in rating_counts:
                    rating_counts[comment.rating] += 1
            
            info["five_star_count"] = rating_counts[5]
            info["four_star_count"] = rating_counts[4]
            
        else:
            info["total_reviews"] = 0
            info["average_rating"] = 4.0
            info["sample_comments"] = []
            info["five_star_count"] = 0
            info["four_star_count"] = 0
        
        return info
