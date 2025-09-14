"""
Pydantic models for SelfLayer TUI application.

This module defines the core data models used throughout the SelfLayer TUI,
including models for API responses like Profile, Document, Note, SearchResult,
and AppState for managing application state.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class Profile(BaseModel):
    """
    Represents a user profile from the SelfLayer API.
    """

    id: str = Field(..., description="Profile ID")
    user_id: str = Field(..., description="User ID")
    full_name: str = Field(..., description="User's full name")
    occupation: Optional[str] = Field(default=None, description="User's occupation")
    primary_company: Optional[str] = Field(default=None, description="Primary company")
    key_skills: Optional[str] = Field(default=None, description="Key skills")
    main_goals: Optional[str] = Field(default=None, description="Main goals")
    timezone: Optional[str] = Field(default=None, description="User's timezone")
    safe_mode: bool = Field(default=False, description="Safe mode setting")

    # Legacy fields for backward compatibility
    email: Optional[str] = Field(default=None, description="User's email address")
    preferences: dict[str, Any] = Field(
        default_factory=dict, description="User preferences"
    )
    created_at: Optional[datetime] = Field(
        default=None, description="Account creation date"
    )
    subscription_tier: Optional[str] = Field(
        default=None, description="User's subscription tier"
    )
    usage_stats: Optional[dict[str, Any]] = Field(
        default_factory=dict, description="Usage statistics"
    )

    @property
    def name(self) -> str:
        """Get the user's display name for backward compatibility."""
        return self.full_name

    def get_greeting(self) -> str:
        """Get a personalized greeting message."""
        if self.full_name:
            # Use first name for greeting
            first_name = self.full_name.split()[0] if self.full_name else "User"
            return f"Welcome back, {first_name}!"
        return "Welcome to SelfLayer!"

    def to_display_dict(self) -> dict[str, Any]:
        """Convert to dictionary optimized for display purposes."""
        return {
            "name": self.full_name,
            "occupation": self.occupation or "Not specified",
            "company": self.primary_company or "Not specified",
            "skills": self.key_skills or "Not specified",
            "timezone": self.timezone or "Not specified",
            "safe_mode": "Enabled" if self.safe_mode else "Disabled",
            "email": self.email or "Not provided",
            "subscription": self.subscription_tier or "Free",
            "member_since": (
                self.created_at.strftime("%B %Y") if self.created_at else "Unknown"
            ),
            "documents": (
                self.usage_stats.get("documents", 0) if self.usage_stats else 0
            ),
            "notes": self.usage_stats.get("notes", 0) if self.usage_stats else 0,
        }


class Document(BaseModel):
    """
    Represents a document from the SelfLayer API.
    """

    id: str = Field(..., description="Document ID")
    file_name: str = Field(..., description="Original file name")
    status: str = Field(..., description="Processing status (FULLY_PROCESSED, etc.)")
    summary: Optional[str] = Field(default=None, description="Document summary")
    keywords: Optional[str] = Field(default=None, description="Document keywords")
    created_at: str = Field(..., description="Creation timestamp (ISO string)")
    updated_at: str = Field(..., description="Last update timestamp (ISO string)")

    # Legacy/computed fields for backward compatibility
    file_size: Optional[int] = Field(default=None, description="File size in bytes")
    visibility: str = Field(default="personal", description="Document visibility")
    content_type: Optional[str] = Field(default=None, description="MIME content type")

    @property
    def title(self) -> str:
        """Get document title from filename for backward compatibility."""
        # Remove file extension and clean up name
        name = self.file_name
        if "." in name:
            name = ".".join(name.split(".")[:-1])  # Remove extension
        return name.replace("_", " ").replace("-", " ").title()

    @property
    def processing_status(self) -> str:
        """Get processing status for backward compatibility."""
        return self.status.lower().replace("_", " ").title()

    def get_status_emoji(self) -> str:
        """Get emoji representation of processing status."""
        status_map = {
            "fully_processed": "✅",
            "fully processed": "✅",
            "processing": "⏳",
            "failed": "❌",
            "pending": "📄",
        }
        return status_map.get(self.status.lower(), "❓")

    def get_size_display(self) -> str:
        """Get human-readable file size."""
        if not self.file_size:
            return "Unknown size"

        # Convert bytes to human readable format
        for unit in ["B", "KB", "MB", "GB"]:
            if self.file_size < 1024.0:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024.0
        return f"{self.file_size:.1f} TB"

    def to_display_dict(self) -> dict[str, Any]:
        """Convert to dictionary optimized for display purposes."""
        from datetime import datetime

        # Parse ISO string to datetime for display
        try:
            created_dt = datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
            created_str = created_dt.strftime("%Y-%m-%d %H:%M")
        except (ValueError, AttributeError):
            created_str = self.created_at

        return {
            "id": self.id,
            "title": self.title,
            "file_name": self.file_name,
            "status": self.status,
            "status_emoji": self.get_status_emoji(),
            "size": self.get_size_display(),
            "created": created_str,
            "summary": self.summary or "No summary available",
        }


class Note(BaseModel):
    """
    Represents a note from the SelfLayer API.
    """

    id: str = Field(..., description="Note ID")
    user_id: str = Field(..., description="User ID")
    title: str = Field(..., description="Note title")
    content: str = Field(..., description="Note content")
    status: str = Field(..., description="Processing status")
    processing_error: Optional[str] = Field(
        default=None, description="Processing error if any"
    )
    created_at: str = Field(..., description="Creation timestamp (ISO string)")
    updated_at: str = Field(..., description="Last update timestamp (ISO string)")

    # Legacy fields for backward compatibility
    tags: list[str] = Field(default_factory=list, description="Note tags")
    visibility: str = Field(default="personal", description="Note visibility")

    def get_preview(self, max_length: int = 100) -> str:
        """Get a preview of the note content."""
        if len(self.content) <= max_length:
            return self.content
        return self.content[: max_length - 3] + "..."

    def get_tags_display(self) -> str:
        """Get formatted tags for display."""
        if not self.tags:
            return "No tags"
        return ", ".join(self.tags)

    def to_display_dict(self) -> dict[str, Any]:
        """Convert to dictionary optimized for display purposes."""
        from datetime import datetime

        # Parse ISO string to datetime for display
        try:
            created_dt = datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
            created_str = created_dt.strftime("%Y-%m-%d %H:%M")
        except (ValueError, AttributeError):
            created_str = self.created_at

        try:
            updated_dt = datetime.fromisoformat(self.updated_at.replace("Z", "+00:00"))
            updated_str = updated_dt.strftime("%Y-%m-%d %H:%M")
        except (ValueError, AttributeError):
            updated_str = self.updated_at

        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "preview": self.get_preview(),
            "tags": self.get_tags_display(),
            "created": created_str,
            "updated": updated_str,
        }


class Integration(BaseModel):
    """
    Represents an integration connection from the SelfLayer API.
    """

    id: str = Field(..., description="Integration ID")
    provider: str = Field(..., description="Provider name (GMAIL, GDRIVE, etc.)")
    display_name: str = Field(..., description="Display name for the connection")
    account_identifier: str = Field(..., description="Account identifier (email, etc.)")
    is_default: bool = Field(
        default=False, description="Whether this is the default connection"
    )
    scopes: list[str] = Field(default_factory=list, description="OAuth scopes")
    created_at: str = Field(..., description="Creation timestamp (ISO string)")
    is_sync_enabled: bool = Field(default=False, description="Whether sync is enabled")
    is_retrieval_enabled: bool = Field(
        default=False, description="Whether retrieval is enabled"
    )
    is_syncable: bool = Field(
        default=False, description="Whether this connection can be synced"
    )
    sync_status: str = Field(
        ..., description="Sync status (SUCCESS, NEVER_SYNCED, etc.)"
    )
    last_synced_at: Optional[str] = Field(
        default=None, description="Last sync timestamp"
    )
    last_sync_error: Optional[str] = Field(
        default=None, description="Last sync error if any"
    )
    summary: str = Field(..., description="Summary of the integration status")
    tags: list[str] = Field(
        default_factory=list, description="Tags for this integration"
    )

    def get_provider_emoji(self) -> str:
        """Get emoji representation of the provider."""
        provider_map = {
            "gmail": "📧",
            "gdrive": "📁",
            "notion": "📝",
            "slack": "💬",
            "trello": "📋",
            "linear": "🎯",
            "gcal": "📅",
        }
        return provider_map.get(self.provider.lower(), "🔗")

    def get_status_emoji(self) -> str:
        """Get emoji representation of sync status."""
        status_map = {
            "success": "✅",
            "never_synced": "⭕",
            "error": "❌",
            "syncing": "🔄",
        }
        return status_map.get(self.sync_status.lower(), "❓")

    def to_display_dict(self) -> dict[str, Any]:
        """Convert to dictionary optimized for display purposes."""
        from datetime import datetime

        # Parse ISO string to datetime for display
        try:
            created_dt = datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
            created_str = created_dt.strftime("%Y-%m-%d %H:%M")
        except (ValueError, AttributeError):
            created_str = self.created_at

        # Parse last synced timestamp
        last_sync_str = "Never"
        if self.last_synced_at:
            try:
                last_sync_dt = datetime.fromisoformat(
                    self.last_synced_at.replace("Z", "+00:00")
                )
                last_sync_str = last_sync_dt.strftime("%Y-%m-%d %H:%M")
            except (ValueError, AttributeError):
                last_sync_str = "Unknown"
            except (ValueError, AttributeError):
                last_sync_str = "Unknown"

        return {
            "id": self.id,
            "provider": self.provider,
            "provider_emoji": self.get_provider_emoji(),
            "display_name": self.display_name,
            "account": self.account_identifier,
            "sync_status": self.sync_status,
            "status_emoji": self.get_status_emoji(),
            "is_default": self.is_default,
            "created": created_str,
            "last_sync": last_sync_str,
            "summary": self.summary,
            "tags": ", ".join(self.tags) if self.tags else "No tags",
        }


class Automation(BaseModel):
    """
    Represents an automation from the SelfLayer API.
    """

    id: str = Field(..., description="Automation ID")
    user_id: str = Field(..., description="User ID")
    title: str = Field(..., description="Automation title")
    description: str = Field(..., description="Automation description")
    prompt: str = Field(..., description="Automation prompt/instruction")
    type: str = Field(..., description="Automation type (manual, cron, trigger)")
    trigger_slug: Optional[str] = Field(
        default=None, description="Trigger slug if type is trigger"
    )
    cron_schedule: Optional[str] = Field(
        default=None, description="Cron schedule if type is cron"
    )
    is_enabled: bool = Field(default=False, description="Whether automation is enabled")
    last_run_at: Optional[str] = Field(default=None, description="Last run timestamp")
    last_run_status: Optional[str] = Field(default=None, description="Last run status")
    last_run_message: Optional[str] = Field(
        default=None, description="Last run message"
    )
    created_at: str = Field(..., description="Creation timestamp (ISO string)")
    updated_at: str = Field(..., description="Last update timestamp (ISO string)")

    def get_type_emoji(self) -> str:
        """Get emoji representation of the automation type."""
        type_map = {
            "manual": "🎯",
            "cron": "⏰",
            "trigger": "⚡",
        }
        return type_map.get(self.type.lower(), "🔄")

    def get_status_emoji(self) -> str:
        """Get emoji representation of the last run status."""
        if not self.last_run_status:
            return "❓"

        status_map = {
            "success": "✅",
            "error": "❌",
            "failed": "❌",
            "running": "🔄",
            "pending": "⏳",
        }
        return status_map.get(self.last_run_status.lower(), "❓")

    def get_schedule_display(self) -> str:
        """Get human-readable schedule display."""
        if self.type == "manual":
            return "Manual"
        elif self.type == "trigger" and self.trigger_slug:
            return f"Trigger: {self.trigger_slug.replace('_', ' ').title()}"
        elif self.type == "cron" and self.cron_schedule:
            # Convert common cron patterns to readable format
            cron_map = {
                "0 9 * * *": "Daily at 9:00 AM",
                "0 */1 * * *": "Every hour",
                "*/5 * * * *": "Every 5 minutes",
                "0 0 * * 0": "Weekly on Sunday",
            }
            return cron_map.get(self.cron_schedule, f"Cron: {self.cron_schedule}")
        return "Unknown"

    def to_display_dict(self) -> dict[str, Any]:
        """Convert to dictionary optimized for display purposes."""
        from datetime import datetime

        # Parse ISO string to datetime for display
        try:
            created_dt = datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
            created_str = created_dt.strftime("%Y-%m-%d %H:%M")
        except (ValueError, AttributeError):
            created_str = self.created_at

        # Parse last run timestamp
        last_run_str = "Never"
        if self.last_run_at:
            try:
                last_run_dt = datetime.fromisoformat(
                    self.last_run_at.replace("Z", "+00:00")
                )
                last_run_str = last_run_dt.strftime("%Y-%m-%d %H:%M")
            except (ValueError, AttributeError):
                last_run_str = "Unknown"
            except (ValueError, AttributeError):
                last_run_str = "Unknown"

        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "type": self.type,
            "type_emoji": self.get_type_emoji(),
            "schedule": self.get_schedule_display(),
            "is_enabled": self.is_enabled,
            "enabled_status": "✅ Enabled" if self.is_enabled else "⏸️ Disabled",
            "last_run": last_run_str,
            "last_status": self.last_run_status or "Never run",
            "status_emoji": self.get_status_emoji(),
            "created": created_str,
            "prompt": self.prompt,
        }


class SearchResult(BaseModel):
    """
    Represents a search result from the SelfLayer API.
    """

    user_profile: Optional[dict[str, Any]] = Field(
        default=None, description="User profile info"
    )
    graph_results: list[dict[str, Any]] = Field(
        default_factory=list, description="Knowledge graph results"
    )
    graph_relationships: list[dict[str, Any]] = Field(
        default_factory=list, description="Graph relationships"
    )
    document_summaries: list[dict[str, Any]] = Field(
        default_factory=list, description="Document summaries"
    )
    source_chunks: list[dict[str, Any]] = Field(
        default_factory=list, description="Source chunks"
    )
    conversation_history: list[dict[str, Any]] = Field(
        default_factory=list, description="Conversation history"
    )
    honcho_insights: list[dict[str, Any]] = Field(
        default_factory=list, description="Honcho insights"
    )

    def get_total_results(self) -> int:
        """Get total number of results."""
        return (
            len(self.graph_results)
            + len(self.document_summaries)
            + len(self.source_chunks)
            + len(self.conversation_history)
            + len(self.honcho_insights)
        )

    def to_display_dict(self) -> dict[str, Any]:
        """Convert to dictionary optimized for display purposes."""
        return {
            "graph_count": len(self.graph_results),
            "document_count": len(self.document_summaries),
            "source_count": len(self.source_chunks),
            "conversation_count": len(self.conversation_history),
            "insights_count": len(self.honcho_insights),
            "total_count": self.get_total_results(),
        }


class Notification(BaseModel):
    """
    Represents a notification from the SelfLayer API.
    """

    id: str = Field(..., description="Notification ID")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    type: str = Field(..., description="Notification type")
    read: bool = Field(default=False, description="Whether notification is read")
    datetime: str = Field(..., description="Notification timestamp (ISO string)")

    @property
    def created_at(self) -> str:
        """Get created_at for backward compatibility."""
        return self.datetime

    def get_type_emoji(self) -> str:
        """Get emoji representation of notification type."""
        type_map = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "document": "📄",
            "note": "📝",
            "integration": "🔗",
        }
        return type_map.get(self.type, "📢")

    def to_display_dict(self) -> dict[str, Any]:
        """Convert to dictionary optimized for display purposes."""
        from datetime import datetime

        # Parse ISO string to datetime for display
        try:
            created_dt = datetime.fromisoformat(self.datetime.replace("Z", "+00:00"))
            created_str = created_dt.strftime("%Y-%m-%d %H:%M")
        except (ValueError, AttributeError):
            created_str = self.datetime

        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "type": self.type,
            "type_emoji": self.get_type_emoji(),
            "read": self.read,
            "read_status": "✅" if self.read else "⭕",
            "created": created_str,
        }


class PersonaProfile(BaseModel):
    """
    Persona profile information.
    """

    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    title: Optional[str] = Field(default=None, description="Job title")
    company: Optional[str] = Field(default=None, description="Company")


class ProposedAction(BaseModel):
    """
    A proposed action from the persona agent.
    """

    short_display: str = Field(..., description="Short display text")
    execution_payload: dict[str, Any] = Field(..., description="Execution payload")


class PersonaAgentResponse(BaseModel):
    """
    Response from the persona agent (RMS).
    """

    rms: str = Field(..., description="Relationship Micro-Summary")
    profile: PersonaProfile = Field(..., description="Profile information")
    proposed_actions: list[ProposedAction] = Field(
        default_factory=list, description="Proposed actions"
    )

    def to_display_dict(self) -> dict[str, Any]:
        """Convert to dictionary optimized for display purposes."""
        return {
            "rms": self.rms,
            "profile": self.profile.model_dump(),
            "actions_count": len(self.proposed_actions),
            "actions": [action.short_display for action in self.proposed_actions],
        }


# Keep the old model for backward compatibility with surface endpoint
class SurfaceResult(BaseModel):
    """
    Represents a memory surfacing result from the SelfLayer API.
    """

    intent: str = Field(..., description="Intent type (qa, etc.)")
    content: str = Field(..., description="Surfaced content or response")

    def to_display_dict(self) -> dict[str, Any]:
        """Convert to dictionary optimized for display purposes."""
        return {
            "intent": self.intent,
            "content": self.content,
        }


class AppState(BaseModel):
    """
    Represents the current state of the SelfTUI application.

    This model tracks the application's current state including API connectivity,
    user profile, and cached data for state management in the TUI.
    """

    api_key_set: bool = Field(
        default=False, description="Whether API key is configured"
    )
    user_profile: Optional[Profile] = Field(
        default=None, description="User profile data"
    )
    current_search_query: str = Field(default="", description="Last search query")
    search_results: Optional[SearchResult] = Field(
        default=None, description="Current search results"
    )
    documents: list[Document] = Field(
        default_factory=list, description="Cached documents"
    )
    notes: list[Note] = Field(default_factory=list, description="Cached notes")
    notifications: list[Notification] = Field(
        default_factory=list, description="Cached notifications"
    )
    integrations: list[Integration] = Field(
        default_factory=list, description="Cached integrations"
    )
    automations: list[Automation] = Field(
        default_factory=list, description="Cached automations"
    )
    last_error: str = Field(default="", description="Last error message")
    session_start: datetime = Field(
        default_factory=datetime.utcnow, description="When the session started"
    )

    # Index lookups for numbered commands
    document_index: dict[int, str] = Field(
        default_factory=dict, description="Document index to ID mapping"
    )
    note_index: dict[int, str] = Field(
        default_factory=dict, description="Note index to ID mapping"
    )
    notification_index: dict[int, str] = Field(
        default_factory=dict, description="Notification index to ID mapping"
    )
    integration_index: dict[int, str] = Field(
        default_factory=dict, description="Integration index to ID mapping"
    )
    automation_index: dict[int, str] = Field(
        default_factory=dict, description="Automation index to ID mapping"
    )

    def set_profile(self, profile_data: dict[str, Any]) -> None:
        """Set user profile from API data."""
        self.user_profile = Profile(**profile_data)
        self.api_key_set = True

    def update_documents(self, documents_data: list[dict[str, Any]]) -> None:
        """Update documents and rebuild index."""
        self.documents = [Document(**doc) for doc in documents_data]
        self.document_index = {i + 1: doc.id for i, doc in enumerate(self.documents)}

    def update_notes(self, notes_data: list[dict[str, Any]]) -> None:
        """Update notes and rebuild index."""
        self.notes = [Note(**note) for note in notes_data]
        self.note_index = {i + 1: note.id for i, note in enumerate(self.notes)}

    def update_notifications(self, notifications_data: list[dict[str, Any]]) -> None:
        """Update notifications and rebuild index."""
        self.notifications = [Notification(**notif) for notif in notifications_data]
        self.notification_index = {
            i + 1: notif.id for i, notif in enumerate(self.notifications)
        }

    def update_integrations(self, integrations_data: list[dict[str, Any]]) -> None:
        """Update integrations and rebuild index."""
        self.integrations = [Integration(**integ) for integ in integrations_data]
        self.integration_index = {
            i + 1: integ.id for i, integ in enumerate(self.integrations)
        }

    def update_automations(self, automations_data: list[dict[str, Any]]) -> None:
        """Update automations and rebuild index."""
        self.automations = [Automation(**auto) for auto in automations_data]
        self.automation_index = {
            i + 1: auto.id for i, auto in enumerate(self.automations)
        }

    def get_document_by_index(self, index: int) -> Optional[Document]:
        """Get document by display index."""
        doc_id = self.document_index.get(index)
        if doc_id:
            return next((doc for doc in self.documents if doc.id == doc_id), None)
        return None

    def get_note_by_index(self, index: int) -> Optional[Note]:
        """Get note by display index."""
        note_id = self.note_index.get(index)
        if note_id:
            return next((note for note in self.notes if note.id == note_id), None)
        return None

    def get_notification_by_index(self, index: int) -> Optional[Notification]:
        """Get notification by display index."""
        notif_id = self.notification_index.get(index)
        if notif_id:
            return next(
                (notif for notif in self.notifications if notif.id == notif_id), None
            )
        return None

    def get_integration_by_index(self, index: int) -> Optional[Integration]:
        """Get integration by display index."""
        integ_id = self.integration_index.get(index)
        if integ_id:
            return next(
                (integ for integ in self.integrations if integ.id == integ_id), None
            )
        return None

    def get_automation_by_index(self, index: int) -> Optional[Automation]:
        """Get automation by display index."""
        auto_id = self.automation_index.get(index)
        if auto_id:
            return next((auto for auto in self.automations if auto.id == auto_id), None)
        return None

    def clear_all_data(self) -> None:
        """Clear all cached data."""
        self.documents = []
        self.notes = []
        self.notifications = []
        self.integrations = []
        self.automations = []
        self.search_results = None
        self.current_search_query = ""
        self.document_index = {}
        self.note_index = {}
        self.notification_index = {}
        self.integration_index = {}
        self.automation_index = {}
        self.last_error = ""

    def set_error(self, error: str) -> None:
        """Set an error message in the state."""
        self.last_error = error

    def get_session_duration(self) -> str:
        """Get formatted session duration."""
        duration = datetime.utcnow() - self.session_start
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

    def get_unread_notifications_count(self) -> int:
        """Get count of unread notifications."""
        return sum(1 for notif in self.notifications if not notif.read)


# Export all models
__all__ = [
    "Profile",
    "Document",
    "Note",
    "SearchResult",
    "Notification",
    "Integration",
    "Automation",
    "AppState",
]
