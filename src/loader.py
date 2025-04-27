from .database import *

class DataLoader:
    def __init__(self, db_constants):
        self.contact_types = db_constants['contact_types']
        self.status_ids = db_constants['status_ids']
        self.stats = {
            "clients_total": 0, "clients_inserted": 0, "clients_existed": 0,
            "contacts_inserted": 0, "contracts_inserted": 0, "plans_inserted": 0
        }

    def load_data(self, clients, contracts, dropped_records):
        self.stats["clients_total"] = len(clients)
        client_ids = self._process_clients(clients)
        self._process_contracts(contracts, client_ids)
        self.stats["dropped_records"] = dropped_records
        return self.stats

    def _process_clients(self, clients):
        client_ids = {}
        for client in clients:
            existing = Cliente.select().where(Cliente.cpf_cnpj == client["cpf_cnpj"]).first()
            if existing:
                client_ids[client["cpf_cnpj"]] = existing.id
                self.stats["clients_existed"] += 1
            else:
                new_client = Cliente.create(**self._get_client_data(client))
                client_ids[client["cpf_cnpj"]] = new_client.id
                self.stats["clients_inserted"] += 1
            self._process_contacts(client, client_ids[client["cpf_cnpj"]])
        return client_ids

    def _get_client_data(self, client):
        return {
            'nome_razao_social': client["nome_razao_social"],
            'nome_fantasia': client.get("nome_fantasia", ""),
            'cpf_cnpj': client["cpf_cnpj"],
            'data_nascimento': client.get("data_nascimento"),
            'data_cadastro': client["data_cadastro"]
        }

    def _process_contacts(self, client, client_id):
        for contact in client["contatos"]:
            if contact["tipo"] in self.contact_types:
                if not ClienteContato.select().where(
                    (ClienteContato.cliente == client_id) &
                    (ClienteContato.tipo_contato == self.contact_types[contact["tipo"]]) &
                    (ClienteContato.contato == contact["contato"])
                ).exists():
                    ClienteContato.create(
                        cliente=client_id,
                        tipo_contato=self.contact_types[contact["tipo"]],
                        contato=contact["contato"]
                    )
                    self.stats["contacts_inserted"] += 1

    def _process_contracts(self, contracts, client_ids):
        for contract in contracts:
            if contract["cliente_cpf_cnpj"] in client_ids:
                plan, created = Plano.get_or_create(
                    descricao=contract["plano"]["descricao"],
                    valor=contract["plano"]["valor"]
                )
                if created:
                    self.stats["plans_inserted"] += 1

                ClienteContrato.create(
                    cliente=client_ids[contract["cliente_cpf_cnpj"]],
                    plano=plan.id,
                    **self._get_contract_data(contract)
                )
                self.stats["contracts_inserted"] += 1

    def _get_contract_data(self, contract):
        return {
            'dia_vencimento': contract["dia_vencimento"],
            'isento': contract["isento"],
            'endereco_logradouro': contract["endereco_logradouro"],
            'endereco_numero': contract.get("endereco_numero", ""),
            'endereco_bairro': contract["endereco_bairro"],
            'endereco_cidade': contract["endereco_cidade"],
            'endereco_complemento': contract.get("endereco_complemento", ""),
            'endereco_cep': contract["endereco_cep"],
            'endereco_uf': contract["endereco_uf"],
            'status': self.status_ids.get(contract["status"])
        }

def print_import_summary(stats):
    print("\n===== IMPORT SUMMARY =====")
    print(f"Total clients processed: {stats['clients_total']}")
    print(f"New clients inserted: {stats['clients_inserted']}")
    print(f"Existing clients updated: {stats['clients_existed']}")
    print(f"Contacts inserted: {stats['contacts_inserted']}")
    print(f"Contracts inserted: {stats['contracts_inserted']}")
    print(f"Plans created: {stats['plans_inserted']}")
    
    total_dropped = sum(len(r) for r in stats['dropped_records'].values())
    if total_dropped > 0:
        print(f"\n{total_dropped} records could not be processed:")
        for category, records in stats['dropped_records'].items():
            if records:
                print(f"\n- {category.replace('_', ' ').title()} ({len(records)} records):")
                
                # Print first 5 records
                for i, record in enumerate(records[:5], 1):
                    identifier = record['data'].get('CPF/CNPJ', 'Unknown') or \
                               record['data'].get('Nome/Razão Social', 'Unknown')
                    print(f"  {i}. {identifier}: {record['reason']}")
                
                # Show remaining count if there are more than 5
                if len(records) > 5:
                    remaining = len(records) - 5
                    print(f"  ... and {remaining} more")