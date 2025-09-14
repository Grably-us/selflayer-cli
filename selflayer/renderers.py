"""
Rich rendering functions for SelfLayer TUI cards.

This module provides beautiful Rich-formatted rendering for all SelfLayer data types
including profiles, documents, notes, search results, notifications, and integrations.
"""

from __future__ import annotations

from typing import Any, Dict

from rich.columns import Columns
from rich.panel import Panel
from rich.table import Table

from .models import (
    Document,
    Integration,
    Note,
    Notification,
    PersonaAgentResponse,
    Profile,
    SearchResult,
    SurfaceResult,
)


def render_profile_card(profile: Profile) -> Panel:
    """
    Render a user profile as a beautiful card.

    Args:
        profile: Profile object to render

    Returns:
        Rich Panel with formatted profile information
    """
    display_data = profile.to_display_dict()

    # Create the profile content
    profile_lines = [
        f"👋 {profile.get_greeting()}",
        "",
        f"[bold]Name:[/bold] {display_data['name']}",
        f"[bold]Email:[/bold] {display_data['email']}",
        f"[bold]Subscription:[/bold] {display_data['subscription']}",
        f"[bold]Member Since:[/bold] {display_data['member_since']}",
        "",
        "📊 [bold]Usage Statistics:[/bold]",
        f"  📄 Documents: {display_data['documents']}",
        f"  📝 Notes: {display_data['notes']}",
    ]

    return Panel(
        "\n".join(profile_lines),
        title="[bold green]🧑‍💻 Your Profile[/bold green]",
        border_style="green",
        padding=(1, 2),
    )


def render_documents_list(documents: list[Document]) -> Panel:
    """
    Render a list of documents as beautiful cards.

    Args:
        documents: List of Document objects to render

    Returns:
        Rich Panel with formatted documents
    """
    if not documents:
        return Panel(
            "[yellow]📄 No documents found.[/yellow]\n\n"
            "Upload your first document with: [cyan]/d new /path/to/file[/cyan]",
            title="[bold yellow]Documents[/bold yellow]",
            border_style="yellow",
            padding=(1, 2),
        )

    document_cards = []

    for i, doc in enumerate(documents, 1):
        display_data = doc.to_display_dict()

        # Create card header with index and title
        header = f"[bold cyan][{i}][/bold cyan] [bold white]{display_data['title']}[/bold white]"

        # Status line with emoji and metadata
        status_line = f"{display_data['status_emoji']} [bold green]{display_data['status']}[/bold green] • [dim]📅 {display_data['created']} • 💾 {display_data['size']}[/dim]"

        # Summary - give it full space (no trimming)
        summary = display_data["summary"]

        # Build card content (simpler, cleaner)
        card_content = [
            header,
            status_line,
            "",
            f"📝 [bold]Summary:[/bold] {summary}",
        ]

        # Create individual card
        card = Panel(
            "\n".join(card_content),
            border_style="cyan",
            padding=(1, 1),
            width=60,  # Fixed width for consistency
        )
        document_cards.append(card)

    # Use Columns to arrange cards nicely
    if len(document_cards) == 1:
        content = document_cards[0]
    else:
        # Stack vertically for better readability with long summaries
        content = Columns(document_cards, equal=False, expand=True, column_first=True)

    return Panel(
        content,
        title=f"[bold blue]📄 Your Documents ({len(documents)} total)[/bold blue]",
        border_style="blue",
        padding=(1, 1),
    )


def render_document_card(document: Document, index: int | None = None) -> Panel:
    """
    Render a single document as a detailed card.

    Args:
        document: Document object to render
        index: Optional index number for display

    Returns:
        Rich Panel with formatted document information
    """
    display_data = document.to_display_dict()

    # Create title with index if provided
    title_text = f"[bold]{display_data['title']}[/bold]"
    if index:
        title_text = f"[bold cyan][{index}][/bold cyan] {title_text}"

    content_lines = [
        title_text,
        "",
        f"📁 [bold]File:[/bold] {display_data['file_name']}",
        f"{display_data['status_emoji']} [bold]Status:[/bold] {display_data['status']}",
        f"📦 [bold]Size:[/bold] {display_data['size']}",
        f"📅 [bold]Created:[/bold] {display_data['created']}",
        "",
        "📝 [bold]Summary:[/bold]",
        display_data["summary"],
    ]

    return Panel(
        "\n".join(content_lines),
        title="[bold magenta]📄 Document Details[/bold magenta]",
        border_style="magenta",
        padding=(1, 2),
    )


def render_notes_list(notes: list[Note]) -> Panel:
    """
    Render a list of notes with prominent content display.

    Args:
        notes: List of Note objects to render

    Returns:
        Rich Panel with formatted notes
    """
    if not notes:
        return Panel(
            "[yellow]📝 No notes found.[/yellow]\n\n"
            'Create your first note with: [cyan]/n new "Title" "Content here"[/cyan]',
            title="[bold yellow]Notes[/bold yellow]",
            border_style="yellow",
            padding=(1, 2),
        )

    content_lines = [
        f"📝 [bold]Your Notes ({len(notes)} total)[/bold]\n",
    ]

    for i, note in enumerate(notes, 1):
        display_data = note.to_display_dict()

        # Title with index
        title_line = f"[bold cyan][{i}][/bold cyan] [bold white]{display_data['title']}[/bold white]"

        # Metadata line
        metadata_line = f"    [dim]{display_data['created']}[/dim] • [dim]{display_data['updated']}[/dim]"

        # Content gets full space (no trimming)
        content = display_data["content"]
        content_line = f"    [bold]Content:[/bold] {content}"

        # Tags
        tags_line = f"    🏷️ {display_data['tags']}"

        content_lines.extend(
            [
                title_line,
                metadata_line,
                content_line,
                tags_line,
                "",  # Spacing between notes
            ]
        )

    return Panel(
        "\n".join(content_lines),
        title="[bold green]📝 Notes[/bold green]",
        border_style="green",
        padding=(1, 2),
    )


def render_note_card(note: Note, index: int | None = None) -> Panel:
    """
    Render a single note as a detailed card.

    Args:
        note: Note object to render
        index: Optional index number for display

    Returns:
        Rich Panel with formatted note information
    """
    display_data = note.to_display_dict()

    # Create title with index if provided
    title_text = f"[bold]{display_data['title']}[/bold]"
    if index:
        title_text = f"[bold cyan][{index}][/bold cyan] {title_text}"

    content_lines = [
        title_text,
        "",
        f"📅 [bold]Created:[/bold] {display_data['created']}",
        f"🔄 [bold]Updated:[/bold] {display_data['updated']}",
        f"🏷️ [bold]Tags:[/bold] {display_data['tags']}",
        "",
        "[bold]Content:[/bold]",
        display_data["content"],
    ]

    return Panel(
        "\n".join(content_lines),
        title="[bold green]📝 Note Details[/bold green]",
        border_style="green",
        padding=(1, 2),
    )


def render_search_results(search_result: SearchResult, query: str) -> Panel:
    """
    Render search results with all categories.

    Args:
        search_result: SearchResult object to render
        query: The search query that generated these results

    Returns:
        Rich Panel with formatted search results
    """
    display_data = search_result.to_display_dict()

    content_lines = [
        f"🔍 [bold]Search Query:[/bold] [cyan]{query}[/cyan]",
        f"📊 [bold]Total Results:[/bold] {display_data['total_count']}",
        "",
    ]

    # Graph results section with better visualization
    if search_result.graph_results:
        content_lines.extend(
            [
                f"🕸️  [bold green]Knowledge Graph ({display_data['graph_count']} results)[/bold green]",
            ]
        )

        # Build a simple graph representation
        graph_viz = render_graph_ascii(
            search_result.graph_results, search_result.graph_relationships
        )
        content_lines.extend(graph_viz)

        content_lines.append("")

        # Also show entities list
        content_lines.append("[bold]Entities:[/bold]")
        for i, entity in enumerate(
            search_result.graph_results[:8], 1
        ):  # Show more entities
            name = entity.get("name", entity.get("title", "Unknown"))
            entity_type = entity.get("type", "Entity")
            description = entity.get("description", "")
            source_kind = entity.get("source_kind", "")

            # Create a rich entity display
            if entity_type != "Entity":
                type_display = f"[cyan]{entity_type}[/cyan]"
            else:
                type_display = f"[dim]{source_kind or 'Entity'}[/dim]"

            display_text = f"  {i}. {type_display}: [bold]{name}[/bold]"
            if description:
                display_text += f" - [dim]{description[:80]}{'...' if len(description) > 80 else ''}[/dim]"

            content_lines.append(display_text)

        if len(search_result.graph_results) > 8:
            content_lines.append(
                f"  ... and {len(search_result.graph_results) - 8} more entities"
            )
        content_lines.append("")

    # Document summaries section
    if search_result.document_summaries:
        content_lines.extend(
            [
                f"📄 [bold blue]Documents ({display_data['document_count']} results)[/bold blue]",
            ]
        )
        for i, doc in enumerate(
            search_result.document_summaries[:5], 1
        ):  # Show first 5
            title = doc.get("title", "Untitled")
            snippet = doc.get("snippet", "No preview available")
            if len(snippet) > 100:
                snippet = snippet[:97] + "..."
            content_lines.extend(
                [
                    f"  {i}. [bold]{title}[/bold]",
                    f"     {snippet}",
                ]
            )

        if len(search_result.document_summaries) > 5:
            content_lines.append(
                f"  ... and {len(search_result.document_summaries) - 5} more"
            )
        content_lines.append("")

    # Source chunks section
    if search_result.source_chunks:
        content_lines.extend(
            [
                f"📋 [bold yellow]Source Chunks ({display_data['source_count']} results)[/bold yellow]",
            ]
        )
        for i, chunk in enumerate(search_result.source_chunks[:3], 1):  # Show first 3
            text = chunk.get("text", "No content available")
            if len(text) > 150:
                text = text[:147] + "..."
            content_lines.extend(
                [
                    f"  {i}. {text}",
                ]
            )

        if len(search_result.source_chunks) > 3:
            content_lines.append(
                f"  ... and {len(search_result.source_chunks) - 3} more chunks"
            )

    if display_data["total_count"] == 0:
        content_lines.extend(
            [
                "[yellow]No results found for this query.[/yellow]",
                "",
                "Try:",
                "• Different keywords",
                "• Broader search terms",
                "• Check your spelling",
            ]
        )

    return Panel(
        "\n".join(content_lines),
        title="[bold cyan]🔍 Search Results[/bold cyan]",
        border_style="cyan",
        padding=(1, 2),
    )


def render_notifications_list(notifications: list[Notification]) -> Panel:
    """
    Render a list of notifications.

    Args:
        notifications: List of Notification objects to render

    Returns:
        Rich Panel with formatted notifications
    """
    if not notifications:
        return Panel(
            "[green]🎉 All caught up! No notifications.[/green]",
            title="[bold green]Notifications[/bold green]",
            border_style="green",
            padding=(1, 2),
        )

    unread_count = sum(1 for n in notifications if not n.read)

    content_lines = [
        f"📢 [bold]Total:[/bold] {len(notifications)} | [bold]Unread:[/bold] {unread_count}",
        "",
    ]

    for i, notif in enumerate(notifications, 1):
        display_data = notif.to_display_dict()

        # Style based on read status
        if notif.read:
            style = "[dim]"
            end_style = "[/dim]"
        else:
            style = "[bold]"
            end_style = "[/bold]"

        content_lines.extend(
            [
                f"{style}[cyan][{i}][/cyan] {display_data['type_emoji']} {display_data['title']} {display_data['read_status']}{end_style}",
                f"{style}    {display_data['message']}{end_style}",
                f"{style}    [dim]{display_data['created']}[/dim]{end_style}",
                "",
            ]
        )

    return Panel(
        "\n".join(content_lines),
        title="[bold yellow]📢 Notifications[/bold yellow]",
        border_style="yellow",
        padding=(1, 2),
    )


def render_integrations_list(integrations: list[Integration]) -> Panel:
    """
    Render a list of integrations.

    Args:
        integrations: List of Integration objects to render

    Returns:
        Rich Panel with formatted integrations
    """
    if not integrations:
        return Panel(
            "[yellow]🔗 No integrations connected.[/yellow]\n\n"
            "Connect your first integration with: [cyan]/i connect gmail[/cyan]",
            title="[bold yellow]Integrations[/bold yellow]",
            border_style="yellow",
            padding=(1, 2),
        )

    table = Table(
        title=f"🔗 Your Integrations ({len(integrations)} total)",
        show_header=True,
        header_style="bold magenta",
        border_style="blue",
        expand=True,
    )

    table.add_column("#", style="cyan", width=3)
    table.add_column("Provider", style="bold white", width=15)
    table.add_column("Account", style="blue", ratio=2)
    table.add_column("Status", style="green", width=12)
    table.add_column("Last Sync", style="dim", width=16)

    for i, integration in enumerate(integrations, 1):
        display_data = integration.to_display_dict()

        table.add_row(
            f"[bold cyan]{i}[/bold cyan]",
            f"{display_data['provider_emoji']} {display_data['provider']}",
            display_data["account"],
            f"{display_data['status_emoji']} {display_data['sync_status']}",
            display_data["last_sync"],
        )

    return Panel(
        table,
        title="[bold blue]🔗 Integrations[/bold blue]",
        border_style="blue",
        padding=(0, 1),
    )


def render_ask_response(response: Dict[str, Any]) -> Panel:
    """
    Render an AI assistant response.

    Args:
        response: Response data from the ask API

    Returns:
        Rich Panel with formatted AI response
    """
    data = response.get("data", {})
    ai_response = data.get("response", "No response received")
    suggested_followups = data.get("suggested_followups", [])
    proposed_actions = data.get("proposed_actions", [])

    content_lines = [
        "🤖 [bold]SelfLayer AI Assistant[/bold]",
        "",
        ai_response,
    ]

    if suggested_followups:
        content_lines.extend(
            [
                "",
                "💡 [bold]Suggested follow-ups:[/bold]",
            ]
        )
        for followup in suggested_followups:
            content_lines.append(f"  • {followup}")

    if proposed_actions:
        content_lines.extend(
            [
                "",
                "⚡ [bold]Proposed actions:[/bold]",
            ]
        )
        for action in proposed_actions:
            content_lines.append(f"  • {action}")

    return Panel(
        "\n".join(content_lines),
        title="[bold green]🤖 AI Assistant[/bold green]",
        border_style="green",
        padding=(1, 2),
    )


def render_streaming_response(content: str, is_complete: bool = False) -> Panel:
    """
    Render a streaming AI response.

    Args:
        content: Current accumulated content
        is_complete: Whether the stream is complete

    Returns:
        Rich Panel with streaming response
    """
    title = "🤖 AI Assistant" + ("" if is_complete else " [dim](streaming...)[/dim]")
    border_style = "green" if is_complete else "yellow"

    content_lines = [
        f"[bold]{content}[/bold]" if is_complete else content,
    ]

    if not is_complete:
        content_lines.append("")
        content_lines.append("[dim]● Streaming response...[/dim]")

    return Panel(
        "\n".join(content_lines),
        title=f"[bold {border_style}]{title}[/bold {border_style}]",
        border_style=border_style,
        padding=(1, 2),
    )


def render_error_panel(error_message: str, title: str = "Error") -> Panel:
    """
    Render an error message as a panel.

    Args:
        error_message: Error message to display
        title: Title for the error panel

    Returns:
        Rich Panel with formatted error
    """
    return Panel(
        f"[red]{error_message}[/red]",
        title=f"[bold red]❌ {title}[/bold red]",
        border_style="red",
        padding=(1, 2),
    )


def render_success_panel(message: str, title: str = "Success") -> Panel:
    """
    Render a success message as a panel.

    Args:
        message: Success message to display
        title: Title for the success panel

    Returns:
        Rich Panel with formatted success message
    """
    return Panel(
        f"[green]{message}[/green]",
        title=f"[bold green]✅ {title}[/bold green]",
        border_style="green",
        padding=(1, 2),
    )


def render_persona_briefing(
    persona_response: PersonaAgentResponse, query: str = ""
) -> Panel:
    """
    Render a persona agent response (RMS).

    Args:
        persona_response: PersonaAgentResponse object to render
        query: The query that generated this result

    Returns:
        Rich Panel with formatted persona briefing
    """
    display_data = persona_response.to_display_dict()
    profile = display_data["profile"]

    content_lines = []

    if query:
        content_lines.append(f"🔍 [bold]Query:[/bold] [cyan]{query}[/cyan]")
        content_lines.append("")

    # Profile card section
    content_lines.extend(
        [
            "👤 [bold]Profile:[/bold]",
            f"  [bold white]{profile['name']}[/bold white]",
            f"  [dim]{profile['email']}[/dim]",
        ]
    )

    if profile.get("title") and profile.get("company"):
        content_lines.append(f"  [dim]{profile['title']} at {profile['company']}[/dim]")
    elif profile.get("title"):
        content_lines.append(f"  [dim]{profile['title']}[/dim]")
    elif profile.get("company"):
        content_lines.append(f"  [dim]{profile['company']}[/dim]")

    content_lines.extend(
        [
            "",
            "🤝 [bold]Relationship Micro-Summary:[/bold]",
            f"[italic]{persona_response.rms}[/italic]",
        ]
    )

    # Proposed actions
    if persona_response.proposed_actions:
        content_lines.extend(
            [
                "",
                f"⚙️ [bold]Suggested Actions ({len(persona_response.proposed_actions)}):[/bold]",
            ]
        )
        for i, action in enumerate(persona_response.proposed_actions, 1):
            content_lines.append(f"  {i}. [cyan]{action.short_display}[/cyan]")

    return Panel(
        "\n".join(content_lines),
        title="[bold magenta]🤝 Relationship Micro-Summary (RMS)[/bold magenta]",
        border_style="magenta",
        padding=(1, 2),
    )


def generate_graph_image(
    entities: list, relationships: list, output_path: str = None
) -> str | None:
    """
    Generate a visual graph image using networkx and matplotlib.

    Args:
        entities: List of graph entities
        relationships: List of graph relationships
        output_path: Optional path to save the image

    Returns:
        Path to the generated image or None if failed
    """
    try:
        import matplotlib
        import matplotlib.pyplot as plt
        import networkx as nx

        matplotlib.use("Agg")  # Use non-interactive backend

        if not entities or not relationships:
            return None

        # Build entity lookup
        entity_lookup = {}
        for entity in entities:
            uuid = entity.get("uuid")
            name = entity.get("name", entity.get("title", "Unknown"))
            entity_type = entity.get("type", "Entity")
            if uuid:
                entity_lookup[uuid] = {"name": name, "type": entity_type}

        # Create NetworkX graph
        G = nx.DiGraph()

        # Add nodes
        for uuid, info in entity_lookup.items():
            G.add_node(uuid, name=info["name"], type=info["type"])

        # Add edges
        for rel in relationships[:20]:  # Limit to 20 relationships for clarity
            source = rel.get("source")
            target = rel.get("target")
            rel_type = rel.get("type", "CONNECTED")

            if source in entity_lookup and target in entity_lookup:
                G.add_edge(source, target, type=rel_type)

        if not G.nodes():
            return None

        # Create visualization
        plt.figure(figsize=(12, 8))
        plt.title("Knowledge Graph Network", fontsize=16, fontweight="bold")

        # Use spring layout for better node distribution
        pos = nx.spring_layout(G, k=2, iterations=50)

        # Color nodes by type
        node_colors = []
        type_colors = {
            "Person": "#FF6B6B",
            "Application": "#4ECDC4",
            "Company": "#45B7D1",
            "Entity": "#96CEB4",
        }

        for node in G.nodes():
            node_type = entity_lookup[node]["type"]
            node_colors.append(type_colors.get(node_type, "#DDDDDD"))

        # Draw nodes
        nx.draw_networkx_nodes(
            G, pos, node_color=node_colors, node_size=1000, alpha=0.8
        )

        # Draw edges with different styles for different relationship types
        edge_colors = []
        edge_styles = []
        for edge in G.edges(data=True):
            rel_type = edge[2].get("type", "CONNECTED")
            if "EMAIL" in rel_type:
                edge_colors.append("#E74C3C")
                edge_styles.append("-")
            elif "WORK" in rel_type:
                edge_colors.append("#3498DB")
                edge_styles.append("--")
            else:
                edge_colors.append("#7F8C8D")
                edge_styles.append("-")

        nx.draw_networkx_edges(
            G, pos, edge_color=edge_colors, alpha=0.6, arrows=True, arrowsize=20
        )

        # Add labels (truncate long names)
        labels = {}
        for node in G.nodes():
            name = entity_lookup[node]["name"]
            labels[node] = name[:15] + "..." if len(name) > 15 else name

        nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight="bold")

        # Add legend
        legend_elements = [
            plt.Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor=color,
                markersize=10,
                label=type_name,
            )
            for type_name, color in type_colors.items()
            if type_name != "Entity"
        ]

        plt.legend(handles=legend_elements, loc="upper right")
        plt.axis("off")
        plt.tight_layout()

        # Save image
        if not output_path:
            import os
            import tempfile

            temp_dir = tempfile.gettempdir()
            output_path = os.path.join(temp_dir, "selflayer_graph.png")

        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close()

        return output_path

    except ImportError:
        return None
    except Exception:
        return None


def render_graph_ascii(entities: list, relationships: list) -> list[str]:
    """
    Create an ASCII representation of the knowledge graph with optional image generation.

    Args:
        entities: List of graph entities
        relationships: List of graph relationships

    Returns:
        List of strings representing the graph visualization
    """
    if not entities:
        return ["  [dim]No graph data available[/dim]"]

    # Build entity lookup by UUID
    entity_lookup = {}
    for entity in entities:
        uuid = entity.get("uuid")
        name = entity.get("name", entity.get("title", "Unknown"))
        entity_type = entity.get("type", "Entity")
        if uuid:
            entity_lookup[uuid] = {"name": name, "type": entity_type}

    graph_lines = []

    # Try to generate a visual graph
    if len(relationships) >= 3:  # Only generate image if we have enough data
        image_path = generate_graph_image(entities, relationships)
        if image_path:
            graph_lines.append(
                f"[bold]🖼️  Visual graph saved to:[/bold] [cyan]{image_path}[/cyan]"
            )
            graph_lines.append(f"  [dim]Open with: open {image_path}[/dim]")
            graph_lines.append("")

    # Create a simple network visualization
    if relationships:
        graph_lines.append("[bold]📊 Network Structure:[/bold]")

        # Group relationships by type
        rel_by_type = {}
        for rel in relationships[:10]:  # Limit to 10 relationships
            rel_type = rel.get("type", "CONNECTED")
            if rel_type not in rel_by_type:
                rel_by_type[rel_type] = []
            rel_by_type[rel_type].append(rel)

        for rel_type, rels in rel_by_type.items():
            graph_lines.append(f"  [cyan]{rel_type}:[/cyan]")
            for rel in rels[:5]:  # Show max 5 per type
                source_id = rel.get("source")
                target_id = rel.get("target")

                source_info = entity_lookup.get(
                    source_id, {"name": "Unknown", "type": "Entity"}
                )
                target_info = entity_lookup.get(
                    target_id, {"name": "Unknown", "type": "Entity"}
                )

                graph_lines.append(
                    f"    [dim]{source_info['name']}[/dim] → [dim]{target_info['name']}[/dim]"
                )
    else:
        # If no relationships, show top entities in a simple tree
        graph_lines.append("[bold]📊 Top Entities:[/bold]")
        for entity in entities[:6]:
            name = entity.get("name", entity.get("title", "Unknown"))
            entity_type = entity.get("type", entity.get("source_kind", "Entity"))
            graph_lines.append(f"  [cyan]{entity_type}[/cyan]: [dim]{name}[/dim]")

    return graph_lines


def render_surface_result(surface_result: SurfaceResult, query: str = "") -> Panel:
    """
    Render a memory surfacing result.

    Args:
        surface_result: SurfaceResult object to render
        query: The query that generated this result

    Returns:
        Rich Panel with formatted surface result
    """
    display_data = surface_result.to_display_dict()

    content_lines = []

    if query:
        content_lines.append(f"🌊 [bold]Query:[/bold] [cyan]{query}[/cyan]")
        content_lines.append("")

    content_lines.extend(
        [
            f"🧾 [bold]Intent:[/bold] {display_data['intent']}",
            "",
            "💭 [bold]Response:[/bold]",
            display_data["content"],
        ]
    )

    return Panel(
        "\n".join(content_lines),
        title="[bold magenta]🌊 Random Memory Surfacing[/bold magenta]",
        border_style="magenta",
        padding=(1, 2),
    )


# Export all rendering functions
__all__ = [
    "render_profile_card",
    "render_documents_list",
    "render_document_card",
    "render_notes_list",
    "render_note_card",
    "render_search_results",
    "render_notifications_list",
    "render_integrations_list",
    "render_ask_response",
    "render_streaming_response",
    "render_persona_briefing",
    "render_surface_result",
    "render_error_panel",
    "render_success_panel",
]
