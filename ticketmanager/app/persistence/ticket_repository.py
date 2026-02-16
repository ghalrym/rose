"""SQLite-backed repository for tickets."""

import sqlite3
from datetime import datetime
from uuid import UUID

from ticketmanager.app.models.ticket import (
    Ticket,
    TicketStatus,
    TicketUpdate,
)


class TicketRepository:
    """Persists and retrieves tickets in SQLite."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        """Initialize with an open database connection.

        Args:
            connection: An open sqlite3.Connection (e.g. from get_connection).
        """
        self._connection = connection

    def create(self, ticket: Ticket) -> Ticket:
        """Insert a ticket into the database.

        Args:
            ticket: The ticket to insert (must have id and all fields set).

        Returns:
            The same Ticket instance.

        Raises:
            sqlite3.IntegrityError: If id already exists.
        """
        self._connection.execute(
            """
            INSERT INTO tickets (
                id, start_datetime, assignee, title, instructions, status, blocked_by_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(ticket.id),
                ticket.start_datetime.isoformat(),
                ticket.assignee,
                ticket.title,
                ticket.instructions,
                ticket.status.value,
                str(ticket.blocked_by_id) if ticket.blocked_by_id else None,
            ),
        )
        self._connection.commit()
        return ticket

    def get_by_id(self, ticket_id: UUID) -> Ticket | None:
        """Fetch a ticket by id.

        Args:
            ticket_id: The ticket UUID.

        Returns:
            The Ticket if found, otherwise None.
        """
        cursor = self._connection.execute(
            """
            SELECT id, start_datetime, assignee, title, instructions, status, blocked_by_id
            FROM tickets WHERE id = ?
            """,
            (str(ticket_id),),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return Ticket.from_row(row)

    def list(
        self,
        status: TicketStatus | None = None,
        assignee: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        search: str | None = None,
    ) -> list[Ticket]:
        """List tickets with optional filters.

        Args:
            status: If set, only tickets with this status.
            assignee: If set, only tickets with this assignee (exact match).
            from_date: If set, only tickets with start_datetime >= from_date.
            to_date: If set, only tickets with start_datetime <= to_date.
            search: If set, filter by title or instructions containing this string.

        Returns:
            List of matching tickets, ordered by start_datetime ascending.
        """
        query = """
            SELECT id, start_datetime, assignee, title, instructions, status, blocked_by_id
            FROM tickets
            WHERE 1=1
        """
        params: list[object] = []
        if status is not None:
            query += " AND status = ?"
            params.append(status.value)
        if assignee is not None and assignee != "":
            query += " AND assignee = ?"
            params.append(assignee)
        if from_date is not None:
            query += " AND start_datetime >= ?"
            params.append(from_date.isoformat())
        if to_date is not None:
            query += " AND start_datetime <= ?"
            params.append(to_date.isoformat())
        if search is not None and search.strip() != "":
            query += " AND (title LIKE ? OR instructions LIKE ?)"
            pattern = f"%{search.strip()}%"
            params.extend([pattern, pattern])
        query += " ORDER BY start_datetime ASC"
        cursor = self._connection.execute(query, params)
        return [Ticket.from_row(row) for row in cursor.fetchall()]

    def update(self, ticket_id: UUID, payload: TicketUpdate) -> Ticket | None:
        """Update an existing ticket with the given fields.

        Args:
            ticket_id: The ticket to update.
            payload: Fields to update; only non-None fields are applied.

        Returns:
            The updated Ticket if found, otherwise None.
        """
        existing = self.get_by_id(ticket_id)
        if existing is None:
            return None
        updates: list[str] = []
        params: list[object] = []
        if payload.title is not None:
            updates.append("title = ?")
            params.append(payload.title)
        if payload.instructions is not None:
            updates.append("instructions = ?")
            params.append(payload.instructions)
        if payload.assignee is not None:
            updates.append("assignee = ?")
            params.append(payload.assignee)
        if payload.start_datetime is not None:
            updates.append("start_datetime = ?")
            params.append(payload.start_datetime.isoformat())
        if payload.blocked_by_id is not None:
            updates.append("blocked_by_id = ?")
            params.append(str(payload.blocked_by_id) if payload.blocked_by_id else None)
        if not updates:
            return existing
        params.append(str(ticket_id))
        self._connection.execute(
            f"UPDATE tickets SET {', '.join(updates)} WHERE id = ?",
            params,
        )
        self._connection.commit()
        return self.get_by_id(ticket_id)

    def update_status(
        self,
        ticket_id: UUID,
        status: TicketStatus,
        blocked_by_id: UUID | None = None,
    ) -> Ticket | None:
        """Set the status of a ticket and optionally the blocking ticket (when status is blocked).

        Args:
            ticket_id: The ticket to update.
            status: The new status.
            blocked_by_id: When status is BLOCKED, the id of the ticket that blocks this one.
                When status is not BLOCKED, this is ignored and blocked_by_id is cleared.

        Returns:
            The updated Ticket if found, otherwise None.
        """
        if status == TicketStatus.BLOCKED and blocked_by_id is not None:
            self._connection.execute(
                "UPDATE tickets SET status = ?, blocked_by_id = ? WHERE id = ?",
                (status.value, str(blocked_by_id), str(ticket_id)),
            )
        else:
            self._connection.execute(
                "UPDATE tickets SET status = ?, blocked_by_id = ? WHERE id = ?",
                (status.value, None, str(ticket_id)),
            )
        self._connection.commit()
        return self.get_by_id(ticket_id)

    def delete(self, ticket_id: UUID) -> bool:
        """Delete a ticket by id.

        Args:
            ticket_id: The ticket to delete.

        Returns:
            True if a row was deleted, False if no such ticket.
        """
        cursor = self._connection.execute("DELETE FROM tickets WHERE id = ?", (str(ticket_id),))
        self._connection.commit()
        return cursor.rowcount > 0
