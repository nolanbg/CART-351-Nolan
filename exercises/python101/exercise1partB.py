import requests
from rich.console import Console
from rich.table import Table


def fetch_and_display_planets():
    console = Console()

    # 1. Fetch planet data from the Star Wars API
    url = "https://swapi.dev/api/planets/"
    console.print(
        "[yellow]Fetching planet data from SWAPI... Please wait.[/yellow]"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        planets = data.get("results", [])
    except Exception as e:
        console.print(f"[red]Error fetching data from API: {e}[/red]")
        return

    # 2. Initialize Table
    table = Table(
        title="🌌 Star Wars Planets", title_style="bold magenta", border_style="cyan"
    )

    # Add column headers
    table.add_column("Planet Name", style="bold green", justify="left")
    table.add_column("Diameter (km)", style="blue", justify="right")
    table.add_column("Population", style="magenta", justify="right")

    # 3. Populate the table rows
    for planet in planets:
        name = planet.get("name", "Unknown")
        diameter = planet.get("diameter", "Unknown")
        population = planet.get("population", "Unknown")

        # Format large numbers for population and diameter if they are numeric
        if diameter.isdigit():
            diameter = f"{int(diameter):,}"
        if population.isdigit():
            population = f"{int(population):,}"

        table.add_row(name, diameter, population)

    # 4. Print the completed table to the console
    console.print(table)


if __name__ == "__main__":
    fetch_and_display_planets()