from os import getenv
from dotenv import load_dotenv
from peewee import (
    Model, PostgresqlDatabase,
    BigAutoField, AutoField, CharField, DateField, DateTimeField,
    IntegerField, BooleanField, DecimalField, ForeignKeyField
)

# Load enviorment variables
load_dotenv()

db = PostgresqlDatabase(
    getenv("DB_NAME"),
    user=getenv("DB_USER"),
    password=getenv("DB_PASS"),
    host=getenv("DB_HOST"),
    port=getenv("DB_PORT")
)

class BaseModel(Model):
    class Meta:
        database = db

class Cliente(BaseModel):
    id = BigAutoField()
    nome_razao_social = CharField(max_length=255, null=False)
    nome_fantasia = CharField(max_length=255, null=True)
    cpf_cnpj = CharField(max_length=18, unique=True, null=False)
    data_nascimento = DateField(null=True)
    data_cadastro = DateTimeField(null=True)

    class Meta:
        table_name = 'tbl_clientes'

class TipoContato(BaseModel):
    id = AutoField()
    tipo_contato = CharField(max_length=50, unique=True, null=False)

    class Meta:
        table_name = 'tbl_tipos_contato'

class StatusContrato(BaseModel):
    id = AutoField()
    status = CharField(max_length=50, unique=True, null=False)

    class Meta:
        table_name = 'tbl_status_contrato'

class Plano(BaseModel):
    id = AutoField() 
    descricao = CharField(max_length=255, unique=True, null=False)
    valor = DecimalField(max_digits=15, decimal_places=2, null=False)

    class Meta:
        table_name = 'tbl_planos'

class ClienteContato(BaseModel):
    id = BigAutoField()
    cliente = ForeignKeyField(Cliente, backref='contatos', on_delete='CASCADE')
    tipo_contato = ForeignKeyField(TipoContato, backref='contatos', on_delete='RESTRICT')
    contato = CharField(max_length=255, null=False)

    class Meta:
        table_name = 'tbl_cliente_contatos'
        indexes = ((('cliente', 'tipo_contato', 'contato'), True),)

class ClienteContrato(BaseModel):
    id = BigAutoField()
    cliente = ForeignKeyField(Cliente, backref='contratos', on_delete='RESTRICT')
    plano = ForeignKeyField(Plano, backref='contratos', on_delete='RESTRICT')
    dia_vencimento = IntegerField(null=False)
    isento = BooleanField(default=False, null=False)
    endereco_logradouro = CharField(max_length=255, null=False)
    endereco_numero = CharField(max_length=15, null=True)
    endereco_bairro = CharField(max_length=255, null=False)
    endereco_cidade = CharField(max_length=255, null=False)
    endereco_complemento = CharField(max_length=500, null=True)
    endereco_cep = CharField(max_length=9, null=False)
    endereco_uf = CharField(max_length=2, null=False)
    status = ForeignKeyField(StatusContrato, backref='contratos', on_delete='RESTRICT')

    class Meta:
        table_name = 'tbl_cliente_contratos'

def initialize_database():
    db.connect()
    return {
        'contact_types': {c.tipo_contato: c.id for c in TipoContato.select()},
        'status_ids': {s.status: s.id for s in StatusContrato.select()}
    }