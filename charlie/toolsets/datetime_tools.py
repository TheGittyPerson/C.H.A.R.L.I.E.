from datetime import datetime, timedelta
from typing import Annotated
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from ..agent import Agent


def register_datetime_tools(charlie: Agent) -> None:
    _register_current_datetime_tools(charlie)
    _register_datetime_conversion_tools(charlie)


def _register_current_datetime_tools(charlie: Agent) -> None:
    @charlie.tool
    def get_current_datetime(
        timezone: Annotated[
            str,
            "IANA timezone name, such as UTC or Asia/Tokyo"
        ] = "UTC",
    ) -> dict[str, str | int]:
        """Get the current date and time in a timezone."""
        tz = _get_timezone(timezone)
        now = datetime.now(tz)
        return {
            "result": now.isoformat(),
            "timezone": timezone,
            "unix_timestamp": int(now.timestamp()),
        }

    @charlie.tool
    def get_weekday(
        date_text: Annotated[str, "ISO 8601 date in YYYY-MM-DD format"],
    ) -> dict[str, str]:
        """Get the weekday for a calendar date."""
        date_value = datetime.fromisoformat(date_text).date()
        return {"result": date_value.strftime("%A")}


def _register_datetime_conversion_tools(charlie: Agent) -> None:
    @charlie.tool
    def convert_datetime_timezone(
        datetime_text: Annotated[str, "ISO 8601 datetime string"],
        target_timezone: Annotated[str, "IANA timezone to convert into"],
        source_timezone: Annotated[
            str,
            "IANA timezone used when the input datetime has no timezone offset",
        ] = "UTC",
    ) -> dict[str, str]:
        """Convert an ISO 8601 datetime from one timezone to another."""
        source_tz = _get_timezone(source_timezone)
        target_tz = _get_timezone(target_timezone)
        source_dt = _parse_datetime(datetime_text, source_tz)
        converted = source_dt.astimezone(target_tz)
        return {
            "result": converted.isoformat(),
            "source_timezone": str(source_dt.tzinfo),
            "target_timezone": target_timezone,
        }

    @charlie.tool
    def add_duration_to_datetime(
        datetime_text: Annotated[str, "ISO 8601 datetime string"],
        days: Annotated[int, "Whole days to add"] = 0,
        hours: Annotated[int, "Whole hours to add"] = 0,
        minutes: Annotated[int, "Whole minutes to add"] = 0,
        source_timezone: Annotated[
            str,
            "IANA timezone used when the input datetime has no timezone offset",
        ] = "UTC",
    ) -> dict[str, str]:
        """Add a duration to an ISO 8601 datetime."""
        source_tz = _get_timezone(source_timezone)
        source_dt = _parse_datetime(datetime_text, source_tz)
        adjusted = source_dt + timedelta(
            days=days,
            hours=hours,
            minutes=minutes,
        )
        return {"result": adjusted.isoformat()}

    @charlie.tool
    def calculate_datetime_difference(
        start_datetime: Annotated[str, "Start ISO 8601 datetime"],
        end_datetime: Annotated[str, "End ISO 8601 datetime"],
        source_timezone: Annotated[
            str,
            "IANA timezone when either input datetime has no timezone offset",
        ] = "UTC",
    ) -> dict[str, str | int]:
        """Calculate the elapsed time between two datetimes."""
        source_tz = _get_timezone(source_timezone)
        start_dt = _parse_datetime(start_datetime, source_tz)
        end_dt = _parse_datetime(end_datetime, source_tz)
        total_seconds = int((end_dt - start_dt).total_seconds())
        return {
            "result": total_seconds,
            "human_readable": _format_duration(total_seconds),
        }


def _get_timezone(timezone_name: str) -> ZoneInfo:
    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"Unknown timezone: {timezone_name}") from exc


def _parse_datetime(datetime_text: str, default_timezone: ZoneInfo) -> datetime:
    normalized = datetime_text.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(
            "Datetime must be in ISO 8601 format."
        ) from exc

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=default_timezone)
    return parsed


def _format_duration(total_seconds: int) -> str:
    sign = "-" if total_seconds < 0 else ""
    remaining = abs(total_seconds)

    days, remaining = divmod(remaining, 86_400)
    hours, remaining = divmod(remaining, 3_600)
    minutes, seconds = divmod(remaining, 60)

    parts: list[str] = []
    if days:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds or not parts:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")

    return sign + ", ".join(parts)
