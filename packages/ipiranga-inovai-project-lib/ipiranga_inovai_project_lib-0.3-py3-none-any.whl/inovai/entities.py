from datetime import datetime
from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Integer, Text, Numeric, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class IntegrationDocument(Base):
    __tablename__ = 'documento_integracao'
    __table_args__ = {'schema': 'fiscal'}

    document_id = Column('no_seq_doc_integr', Integer, primary_key=True, nullable=False)
    access_key = Column('cd_chave_doc_integr', String(44))
    json_content = Column('aq_json', JSON, nullable=False)
    document_movement_type = Column('cd_tipo_mov_doc_integr', String(1))
    document_type = Column('cd_tipo_doc_integr', String(4))
    document_series = Column('cd_serie_doc_integr', String(3), nullable=False)
    document_number = Column('no_doc_integr', Numeric(precision=11, scale=0), nullable=False)
    document_model = Column('cd_modl_doc_integr', String(3), nullable=False)
    branch_code = Column('cd_filial', Numeric(precision=6, scale=0), nullable=False)
    recipient_cnpj = Column('cd_cnpj_dest', String(14), nullable=False)
    issuer_cnpj = Column('cd_cnpj_emit', String(14), nullable=False)
    issuance_date = Column('dt_emis_doc_integr', Date, nullable=False)
    fiscal_date = Column('dt_fisc', Date, nullable=False)
    created_at = Column('dt_hora_criacao', DateTime, nullable=False)
    updated_at = Column('dt_incl', DateTime, nullable=False, server_default='NOW()')
    request_id = Column('id_req_doc_fisc', String(40), nullable=True)
    origin = Column('nm_sist_orig', String(50), nullable=True)

    integration_batch = relationship('IntegrationDocumentBatch', back_populates='integration_document')
    kit_integration_document_status = relationship("KitIntegrationDocumentStatus", back_populates="integration_document")

    def to_dict(self):
        return {
            "no_seq_doc_integr": self.document_id,
            "cd_chave_doc_integr": self.access_key,
            "aq_json": self.json_content,
            "cd_tipo_mov_doc_integr": self.document_movement_type,
            "cd_tipo_doc_integr": self.document_type,
            "cd_serie_doc_integr": self.document_series,
            "no_doc_integr": self.document_number,
            "cd_modl_doc_integr": self.document_model,
            "cd_filial": self.branch_code,
            "cd_cnpj_dest": self.recipient_cnpj,
            "cd_cnpj_emit": self.issuer_cnpj,
            "dt_emis_doc_integr": self.issuance_date.strftime("%Y-%m-%d") if self.issuance_date is not None else None,
            "dt_fisc": self.fiscal_date.strftime("%Y-%m-%d") if self.fiscal_date is not None else None,
            "dt_hora_criacao": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at is not None else None,
            "dt_incl": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at is not None else None,
            "request_id": self.request_id
        }

    def __str__(self):
        return str(self.to_dict())


class ObiOrganizationUnit(Base):
    __tablename__ = 'unidade_organizacional_obi'
    __table_args__ = {'schema': 'fiscal'}

    employer_number = Column("cd_cnpj_empr", String(14), primary_key=True, nullable=False)
    organization_code = Column("cd_filial", Integer, nullable=False)
    corporate_name = Column("nm_razao_social", String(60), nullable=False)
    active = Column("id_status_integr", Boolean, nullable=False)
    create_at = Column("dt_incl", DateTime, nullable=False)

    def __init__(self, employer_number, organization_code, corporate_name, active, create_at):
        super().__init__()
        self.employer_number = employer_number
        self.organization_code = organization_code
        self.corporate_name = corporate_name
        self.active = active
        self.create_at = create_at

    def __str__(self):
        return (f"Employer Number: {self.employer_number}, Organization Code: {self.organization_code}, "
                f"Corporate Name: {self.corporate_name}, Active: {self.active}, Create At: {self.create_at}")


class IntegrationBatch(Base):
    __tablename__ = 'lote_integracao'
    __table_args__ = {'schema': 'fiscal'}

    integration_batch_id = Column('cd_integr', String(36), primary_key=True, nullable=False)
    employer_number = Column('cd_cnpj_empr', String(14), ForeignKey(ObiOrganizationUnit.employer_number),
                             nullable=False)
    first_date_document = Column('dt_ini_doc_integr', Date)
    last_date_document = Column('dt_fim_doc_integr', Date)
    error_reason = Column('ds_mot_erro', String)
    batch_code = Column('cd_lote_obi', String)
    start_integration_date = Column('dt_hora_ini_lote_integr', DateTime)
    end_integration_date = Column('dt_hora_fim_lote_integr', DateTime)
    created_at = Column('dt_incl', DateTime, nullable=False)

    batch_files = relationship('BatchFileIntegration', back_populates='integration_batch')
    integration_processing = relationship('IntegrationProcessing', back_populates='integration_batch')

    def __init__(self, integration_batch_id, employer_number, first_date_document, last_date_document):
        super().__init__()
        self.integration_batch_id = integration_batch_id
        self.employer_number = employer_number
        self.first_date_document = first_date_document
        self.last_date_document = last_date_document
        self.start_integration_date = datetime.now()
        self.created_at = self.start_integration_date


class IntegrationFile(Base):
    __tablename__ = 'arquivo_integracao'
    __table_args__ = {'schema': 'fiscal'}

    integration_file_id = Column('no_seq_aq_integr', Integer, primary_key=True, nullable=False)
    file_name = Column('nm_aq', String(50))
    crypt_file_integration = Column('aq_integr_criptog', Text)
    created_at = Column('dt_incl', DateTime, nullable=False)

    batch_files = relationship('BatchFileIntegration', back_populates='integration_file')

    def __init__(self, file_name, crypt_file_integration):
        super().__init__()
        self.file_name = file_name
        self.crypt_file_integration = crypt_file_integration
        self.created_at = datetime.now()


class BatchFileIntegration(Base):
    __tablename__ = 'lote_arquivo_integracao'
    __table_args__ = {'schema': 'fiscal'}

    integration_file_id = Column('cd_dos_aq_integr', Integer, ForeignKey('fiscal.arquivo_integracao.no_seq_aq_integr'),
                                 primary_key=True, nullable=False)
    integration_batch_id = Column('cd_integr', String(36), ForeignKey('fiscal.lote_integracao.cd_integr'),
                                  primary_key=True, nullable=False)
    created_at = Column('dt_incl', DateTime, nullable=False)

    integration_batch = relationship('IntegrationBatch', back_populates='batch_files')
    integration_file = relationship('IntegrationFile', back_populates='batch_files')

    def __init__(self, file_integration_id, integration_batch_id):
        super().__init__()
        self.integration_batch_id = integration_batch_id
        self.integration_file_id = file_integration_id
        self.created_at = datetime.now()


class ParamProcessingKit(Base):
    __tablename__ = 'param_processamento_kit'
    __table_args__ = {'schema': 'fiscal'}

    param_processing_kit_id = Column('no_seq_proc', Numeric(precision=8, scale=0), primary_key=True, nullable=False)
    kit_id = Column('cd_kit', Integer, ForeignKey('fiscal.kit_obi.no_seq_kit'), nullable=False)
    process_code = Column('cd_proc_obi', String(30))
    status = Column('id_status_param', Boolean, nullable=False)
    created_at = Column('dt_incl', DateTime, nullable=False, server_default='NOW()')

    def __init__(self, param_processing_kit_id, kit_id, process_code, status):
        super().__init__()
        self.param_processing_kit_id = param_processing_kit_id
        self.kit_id = kit_id
        self.process_code = process_code
        self.status = status
        self.created_at = datetime.now()


class IntegrationProcessing(Base):
    __tablename__ = 'integracao_processamento'
    __table_args__ = {'schema': 'fiscal'}

    integration_batch_id = Column('cd_integr', String(36), ForeignKey('fiscal.lote_integracao.cd_integr'),
                                  primary_key=True, nullable=False)
    param_processing_kit_id = Column('no_seq_proc', Numeric(precision=8, scale=0),
                                     ForeignKey('fiscal.param_processamento_kit.no_seq_proc'),
                                     primary_key=True, nullable=False)
    created_at = Column('dt_incl', DateTime, nullable=False)

    integration_batch = relationship('IntegrationBatch', back_populates='integration_processing')
    param_processing_kit = relationship(ParamProcessingKit,
                                        primaryjoin="IntegrationProcessing.param_processing_kit_id == "
                                                    "ParamProcessingKit.param_processing_kit_id")

    def __init__(self, integration_batch_id, param_processing_kit_id):
        super().__init__()
        self.param_processing_kit_id = param_processing_kit_id
        self.integration_batch_id = integration_batch_id
        self.created_at = datetime.now()


class IntegrationDocumentBatch(Base):
    __tablename__ = 'lote_documento_integracao'
    __table_args__ = {'schema': 'fiscal'}

    integration_batch_id = Column('cd_integr', String(36), ForeignKey('fiscal.lote_integracao.cd_integr'),
                                  primary_key=True, nullable=False)
    integration_document_id = Column('cd_seq_doc_integr', Integer, ForeignKey('fiscal.documento_integracao'
                                                                              '.no_seq_doc_integr'),
                                     primary_key=True, nullable=False)
    created_at = Column('dt_incl', DateTime, nullable=False)

    integration_document = relationship('IntegrationDocument', back_populates='integration_batch')

    def __init__(self, integration_batch_id, integration_document_id):
        super().__init__()
        self.integration_document_id = integration_document_id
        self.integration_batch_id = integration_batch_id
        self.created_at = datetime.now()


class KitObi(Base):
    __tablename__ = 'kit_obi'
    __table_args__ = {'schema': 'fiscal'}

    kit_id = Column('no_seq_kit', Integer, primary_key=True, nullable=False)
    kit_description = Column('ds_kit', String(150))
    created_at = Column('dt_incl', DateTime, nullable=False)


class ObiAuthentication(Base):
    __tablename__ = 'autenticacao_obi'
    __table_args__ = {'schema': 'fiscal'}

    id_obi_authentication = Column('no_seq_token', Integer, primary_key=True, nullable=False)
    access_token = Column('ds_access_token_obi', Text, nullable=False)
    expiration_date = Column('dt_hora_expir_token', DateTime, nullable=False)
    created_date = Column('dt_hora_criacao_token', DateTime)
    created_at = Column('dt_incl', DateTime, nullable=False)

    def __init__(self, access_token, expiration_date):
        super().__init__()
        self.access_token = access_token
        self.expiration_date = expiration_date
        self.created_date = datetime.now()
        self.created_at = datetime.now()


class KitIntegrationDocumentStatus(Base):
    __tablename__ = 'kit_documento_integracao_status'
    __table_args__ = {'schema': 'fiscal'}

    document_id = Column('no_seq_doc_integr', Integer, ForeignKey('fiscal.documento_integracao.no_seq_doc_integr'),
                         primary_key=True, nullable=False)
    kit_id = Column('no_seq_kit', Integer, ForeignKey('fiscal.kit_obi.no_seq_kit'),
                    primary_key=True, nullable=False)
    integration_status = Column('ds_status_proc', String(20), nullable=False)
    created_at = Column('dt_incl', DateTime, nullable=False)

    integration_document = relationship(IntegrationDocument, back_populates="kit_integration_document_status")

    def __init__(self, document_id, kit_id, integration_status):
        super().__init__()
        self.document_id = document_id
        self.kit_id = kit_id
        self.integration_status = integration_status
        self.created_at = datetime.now()
