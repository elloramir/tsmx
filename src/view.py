from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.box import SIMPLE_HEAVY, ROUNDED, SIMPLE
from .database import *

def view_import_summary(stats):
    console = Console()
    
    # Main statistics table
    summary_table = Table(title="[bold]IMPORT SUMMARY[/]", box=SIMPLE_HEAVY)
    summary_table.add_column("Metric", style="cyan", no_wrap=True)
    summary_table.add_column("Count", style="magenta", justify="right")
    
    summary_table.add_row("Total clients processed", str(stats['clients_total']))
    summary_table.add_row("New clients inserted", str(stats['clients_inserted']))
    summary_table.add_row("Existing clients updated", str(stats['clients_existed']))
    summary_table.add_row("Contacts inserted", str(stats['contacts_inserted']))
    summary_table.add_row("Contracts inserted", str(stats['contracts_inserted']))
    summary_table.add_row("Plans created", str(stats['plans_inserted']))
    
    console.print(summary_table)
    
    # Section for unprocessed records
    total_dropped = sum(len(r) for r in stats['dropped_records'].values())
    if total_dropped > 0:
        dropped_panel = Panel.fit(
            f"[bold red]{total_dropped} records could not be processed[/]",
            title="[bold]DROPPED RECORDS[/]",
            border_style="red"
        )
        console.print(dropped_panel)
        
        for category, records in stats['dropped_records'].items():
            if records:
                # Table per error category
                error_table = Table(
                    title=f"[italic]{category.replace('_', ' ').title()} ({len(records)} records)",
                    box=SIMPLE_HEAVY,
                    show_header=True,
                    header_style="bold yellow"
                )
                error_table.add_column("#", style="dim", width=4)
                error_table.add_column("Identifier")
                error_table.add_column("Reason")
                
                for i, record in enumerate(records[:5], 1):
                    identifier = record['data'].get('CPF/CNPJ', 'Unknown') or \
                                 record['data'].get('Nome/Razão Social', 'Unknown')
                    error_table.add_row(
                        str(i),
                        identifier,
                        record['reason']
                    )
                
                if len(records) > 5:
                    error_table.add_row(
                        "...",
                        f"[dim]and {len(records)-5} more[/]",
                        ""
                    )
                
                console.print(error_table)


def view_contracts(limit=20):
    console = Console()
    
    # Corrected query with joins in the proper order
    contracts = (ClienteContrato
                .select(
                    ClienteContrato,
                    Cliente,
                    Plano,
                    StatusContrato
                )
                .join(Cliente, on=(ClienteContrato.cliente == Cliente.id))
                .join(Plano, on=(ClienteContrato.plano == Plano.id))
                .join(StatusContrato, on=(ClienteContrato.status == StatusContrato.id))
                .limit(limit))
    
    # Create table
    table = Table(
        title=f"[bold]LAST {limit} CONTRACTS[/]",
        box=ROUNDED,
        header_style="bold magenta",
        show_lines=True
    )
    
    # Columns
    table.add_column("ID", style="dim", width=8)
    table.add_column("Client", width=25)
    table.add_column("CPF/CNPJ", width=18)
    table.add_column("Plan", width=20)
    table.add_column("Value", justify="right", width=10)
    table.add_column("Due Date", justify="center", width=10)
    table.add_column("Status", width=15)
    
    # Add rows
    for contract in contracts:
        table.add_row(
            str(contract.id),
            contract.cliente.nome_razao_social[:24] + ("..." if len(contract.cliente.nome_razao_social) > 24 else ""),
            contract.cliente.cpf_cnpj,
            contract.plano.descricao[:19] + ("..." if len(contract.plano.descricao) > 19 else ""),
            f"R$ {contract.plano.valor:.2f}",
            str(contract.dia_vencimento),
            contract.status.status
        )
    
    console.print(table)
    
    # Statistical summary
    stats_table = Table(box=SIMPLE, width=80)
    stats_table.add_column("Statistic", style="cyan")
    stats_table.add_column("Value", style="green", justify="right")
    
    total_contracts = ClienteContrato.select().count()
    stats_table.add_row("Total contracts in database", str(total_contracts))
    stats_table.add_row("Exempt contracts", str(ClienteContrato.select().where(ClienteContrato.isento == True).count()))
    
    console.print(stats_table)