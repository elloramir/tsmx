import pandas as pd
from .helpers import check_cpf, state_to_uf, normalize_text

class DataProcessor:
    def __init__(self):
        self.dropped_records = {
            "missing_data": [],
            "invalid_cpf": [],
            "other_errors": []
        }

    def preprocess_data(self, file_path):
        try:
            df = pd.read_excel(file_path)
            df = self._validate_required_columns(df)
            if df is not None:
                df = self._clean_data(df)
            return df
        except Exception as e:
            self.dropped_records["other_errors"].append({"reason": str(e)})
            return None

    def _validate_required_columns(self, df):
        required_cols = [
            "Nome/Razão Social", "CPF/CNPJ", "Data Cadastro cliente",
            "Vencimento", "Endereço", "Bairro", "Cidade", "CEP", "UF",
            "Status", "Plano Valor", "Plano"
        ]
        
        # Create mask of valid rows
        valid_mask = pd.Series(True, index=df.index)
        for col in required_cols:
            col_mask = df[col].notna()
            invalid_rows = df[~col_mask]
            
            if not invalid_rows.empty:
                self._add_dropped_records(invalid_rows, f"Missing required value: {col}")
                valid_mask &= col_mask

        return df[valid_mask].copy()  # Ensure we return a copy

    def _clean_data(self, df):
        df = df.copy()  # Work on a clean copy to avoid SettingWithCopyWarning
        df = self._filter_invalid_cpfs(df)
        
        # Convert NaT to None for date fields
        df.loc[:, "Data Nasc."] = df["Data Nasc."].where(pd.notna(df["Data Nasc."]), None)
        df.loc[:, "Isento"] = df["Isento"].str.lower() == "sim"
        df.loc[:, "Plano Valor"] = df["Plano Valor"].astype(float)
        df.loc[:, "UF"] = df["UF"].apply(state_to_uf)
        
        return df

    def _filter_invalid_cpfs(self, df):
        invalid_mask = ~df["CPF/CNPJ"].astype(str).apply(check_cpf)
        invalid_rows = df[invalid_mask]
        
        if not invalid_rows.empty:
            self._add_dropped_records(invalid_rows, "Invalid CPF/CNPJ format")
        
        return df[~invalid_mask].copy()

    def _add_dropped_records(self, df_rows, reason):
        for _, row in df_rows.iterrows():
            self.dropped_records["missing_data"].append({
                "reason": reason,
                "data": row.to_dict()
            })

    def extract_clients(self, df):
        """Extract client data from dataframe"""
        clients = {}
        
        for _, row in df.iterrows():
            cpf_cnpj = str(row["CPF/CNPJ"])
            
            if cpf_cnpj not in clients:
                clients[cpf_cnpj] = {
                    "nome_razao_social": row["Nome/Razão Social"],
                    "nome_fantasia": row.get("Nome Fantasia", ""),
                    "cpf_cnpj": cpf_cnpj,
                    "data_nascimento": row.get("Data Nasc.", None),
                    "data_cadastro": row["Data Cadastro cliente"],
                    "contatos": self._extract_contacts(row)
                }
        
        return list(clients.values())

    def _extract_contacts(self, row):
        """Extract contact information from a row"""
        contacts = []
        contact_types = {
            "Celular": "Celulares",
            "Telefone": "Telefones", 
            "E-Mail": "Emails"
        }
        
        for tipo, col in contact_types.items():
            if pd.notna(row.get(col, pd.NA)):
                contact_value = str(row[col])
                # Remove decimal part if it's a phone number
                if tipo in ["Celular", "Telefone"]:
                    contact_value = contact_value.split('.')[0]
                contacts.append({
                    "tipo": tipo,
                    "contato": contact_value
                })
        
        return contacts

    def extract_contracts(self, df, clients):
        """Extract contract data from dataframe"""
        contracts = []
        client_cpf_cnpjs = {c["cpf_cnpj"] for c in clients}
        
        for _, row in df.iterrows():
            cpf_cnpj = str(row["CPF/CNPJ"])
            if cpf_cnpj in client_cpf_cnpjs:
                contracts.append({
                    "cliente_cpf_cnpj": cpf_cnpj,
                    "dia_vencimento": int(row["Vencimento"]),
                    "isento": bool(row.get("Isento", False)),
                    "endereco_logradouro": row["Endereço"],
                    "endereco_numero": row.get("Número", ""),
                    "endereco_bairro": row["Bairro"],
                    "endereco_cidade": row["Cidade"],
                    "endereco_complemento": row.get("Complemento", ""),
                    "endereco_cep": row["CEP"],
                    "endereco_uf": row["UF"],
                    "status": row["Status"],
                    "plano": {
                        "descricao": row["Plano"],
                        "valor": float(row["Plano Valor"])
                    }
                })
        
        return contracts