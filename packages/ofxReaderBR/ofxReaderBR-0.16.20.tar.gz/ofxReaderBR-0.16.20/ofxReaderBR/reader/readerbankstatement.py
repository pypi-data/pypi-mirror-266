import abc
import datetime
import logging
import unidecode
from decimal import Decimal

from ofxReaderBR.model import BankStatement, Origin, AccountType
from ofxReaderBR.reader.readercashflow import ItauXLSReaderCashFlow

logger = logging.getLogger(__name__)


class ReaderBankStatement(abc.ABC):
    def __init__(self, factory, file, data, options=None):
        self.data = data
        self.factory = factory
        self.file = file
        self.options = options
        self.errors = []

    @abc.abstractmethod
    def read(self):
        pass


class OFXReaderBankStatement(ReaderBankStatement):
    def read(self):
        options = self.options
        ofx = self.data
        file = self.file
        factory = self.factory

        signal_multiplier = 1
        if options.get("creditcard"):
            # BB and Nubank credit cards don't need signal inversion
            if not options.get("bancodobrasil") and not options.get("nubank"):
                signal_multiplier = -1

        cs_reader = factory.create_reader_cash_flow()

        bank_statement = BankStatement(file)
        bank_statement.read_status = BankStatement.COMPLETE
        bank_statement.assets = []
        bank_statement.errors = []
        is_bb_credit_card = options["creditcard"] and options.get("bancodobrasil")
        one_origin_error, many_origins_errors = False, False
        one_due_date_error, many_due_dates_errors = False, False
        one_close_date_error, many_close_dates_errors = False, False

        for stmt in ofx.statements:
            bs = BankStatement(file)
            account = stmt.account
            origin = Origin(account)
            created_origin = True if origin.account_id.split(":")[0] == "O" else False
            if len(origin.account_id) == 22:
                if one_origin_error:
                    many_origins_errors = True
                one_origin_error = True
            if created_origin:
                if one_origin_error:
                    many_origins_errors = True
                one_origin_error = True
            if options["creditcard"] and options.get("bradesco"):
                if one_due_date_error:
                    many_due_dates_errors = True
                one_due_date_error = True
                if stmt.dtstart == stmt.dtend:
                    if one_close_date_error:
                        many_close_dates_errors = True
                    one_close_date_error = True
            elif is_bb_credit_card or options.get("nubank"):
                if stmt.dtstart == stmt.dtend:
                    if one_close_date_error:
                        many_close_dates_errors = True
                    one_close_date_error = True
                if type(stmt.ledgerbal.dtasof) != datetime.datetime or \
                        datetime.datetime(stmt.ledgerbal.dtasof.year,
                                          stmt.ledgerbal.dtasof.month,
                                          stmt.ledgerbal.dtasof.day,
                                          stmt.ledgerbal.dtasof.hour) == datetime.datetime(1985, 10, 21, 3, 0, 0, 0):
                    if one_due_date_error:
                        many_due_dates_errors = True
                    one_due_date_error = True
            assets_obj = {
                "number": self._nubank_origin(created=created_origin, origin=origin.account_id) if
                origin.account_type.name == "CREDITCARD"
                else self._bankaccount_origin(created=created_origin, origin=origin.account_id),
                "type": origin.account_type,
                "balance": float(stmt.balance.balamt),
                "bank": origin.institution_number[-3:] if origin.institution_number is not None else '0',
                "close_day": stmt.dtend,
                "due_date": stmt.ledgerbal.dtasof}
            origin.account_id = assets_obj['number']
            bank_statement.assets.append(assets_obj)
            # FT-491

            for tx in stmt.transactions:
                cs = cs_reader.read(tx, options)
                cs.value *= signal_multiplier

                cs.origin = origin
                if origin.is_bank_account():
                    cs.cash_date = cs.date
                elif options["creditcard"] and options.get("bradesco"):
                    cs.cash_date = stmt.dtstart
                # FT-491, FT-982
                elif is_bb_credit_card or options.get("nubank"):
                    cs.cash_date = stmt.ledgerbal.dtasof
                else:
                    raise NotImplementedError(
                        f"Not implemented cash date for origin: {origin}"
                    )
                if cs.cash_date < cs.date:
                    cs.date, cs.cash_date = cs.date, cs.date
                if cs.is_valid():
                    bs.transactions.append(cs)
                else:
                    bank_statement.read_status = BankStatement.INCOMPLETE

            bank_statement += bs

        if many_origins_errors or one_origin_error or many_due_dates_errors or one_due_date_error or\
                many_close_dates_errors or one_close_date_error:
            bank_statement.read_status = BankStatement.INCOMPLETE
            type_file = "ofx"
            if one_origin_error:
                message = "Não foi encontrada a origem no arquivo OFX"
                error_code = "102"
                if many_origins_errors:
                    message = "Não foram encontradas as origens no arquivo OFX"
                    error_code = "103"
                bank_statement.errors.append({"message": message,
                                              "error_code": error_code,
                                              "type_file": type_file})
            if one_due_date_error:
                message = "Não foi encontrada a data de vencimento no arquivo OFX"
                error_code = "100"
                if many_close_dates_errors:
                    message = "Não foram encontradas as data de vencimento no arquivo OFX"
                    error_code = "101"
                bank_statement.errors.append({"message": message,
                                              "error_code": error_code,
                                              "type_file": type_file})
            if one_close_date_error:
                message = "Não foi encontrada a data de fechamento no arquivo OFX"
                error_code = "106"
                if many_close_dates_errors:
                    message = "Não foram encontradas as data de fechamento no arquivo OFX"
                    error_code = "107"
                bank_statement.errors.append({"message": message,
                                              "error_code": error_code,
                                              "type_file": type_file})
        return bank_statement

    @staticmethod
    def _bankaccount_origin(created, origin):
        if created:
            return origin
        origin = origin.split('/')[-1]
        if len(origin.split('-')) == 2:
            return origin
        else:
            origin = origin[:-1] + '-' + origin[-1]
            return origin

    @staticmethod
    def _nubank_origin(created, origin):
        if created:
            return origin
        if len(origin) > 16:
            return origin
        else:
            return origin[-4:]


class PDFReaderBankStatement(ReaderBankStatement):
    def read(self):
        factory = self.factory
        result = self.data
        options = self.options

        bs = BankStatement(self.file)

        cs_reader = factory.create_reader_cash_flow()
        header_row = True
        bs.read_status = BankStatement.COMPLETE
        for row in result:
            # Pulando o cabecalho
            has_header = options.get("has_header", True)
            if header_row and has_header:
                header_row = False
                continue

            cs = cs_reader.read(factory, row)
            if not cs.is_valid():
                bs.read_status = BankStatement.INCOMPLETE
            else:
                bs.transactions.append(cs)

        return bs


class XMLReaderBankStatement(ReaderBankStatement):
    def read(self):
        factory = self.factory
        ofx = self.data
        options = self.options

        bs = BankStatement(self.file)

        if options is not None and options.get("creditcard"):
            tran_list = (
                ofx.find("CREDITCARDMSGSRSV1").find("CCSTMTTRNRS").find("CCSTMTRS")
            )

            # Origin
            institution = None
            branch = None
            account_id = tran_list.find("CCACCTFROM").find("ACCTID").text
            account_type = "CREDITCARD"
        else:
            tran_list = ofx.find("BANKMSGSRSV1").find("STMTTRNRS").find("STMTRS")

            # Origin
            account = tran_list.find("BANKACCTFROM")
            institution = account.find("BANKID").text
            branch = account.find("BRANCHID").text
            account_id = account.find("ACCTID").text
            account_type = "BANKACCOUNT"

        origin = Origin(
            account_id=account_id,
            branch=branch,
            institution=institution,
            type=account_type,
        )
        try:
            balance = float(
                ofx.find("BANKMSGSRSV1").find("STMTTRNRS").find("STMTRS").find("LEDGERBAL").find("BALAMT").text)
        except AttributeError:
            balance = 0
        created_origin = True if origin.account_id.split(":")[0] == "O" else False
        if created_origin:
            bs.read_status = BankStatement.INCOMPLETE
            bs.errors.append("Encontramos transações sem origens bem definidas,por favor edite as "
                             "origens existentes no arquivo para ficar de acordo com suas contas")
        assets_obj = {
            "number": origin.account_id[-4:] if origin.account_type.name == "CREDITCARD" else origin.account_id,
            "type": origin.account_type,
            "balance": balance,
            "bank": origin.institution_number[-3:] if origin.institution_number is not None else '0'}
        origin.account_id = assets_obj['number']
        bs.assets.append(assets_obj)

        if tran_list is not None:
            tran_list = tran_list.find("BANKTRANLIST")

        txs = tran_list.findall("STMTTRN")

        cs_reader = factory.create_reader_cash_flow()
        bs.read_status = BankStatement.COMPLETE
        for tx in txs:
            cs = cs_reader.read(factory, tx)
            cs.origin = origin
            cs.value = float(cs.value)
            if cs.is_valid():
                bs.transactions.append(cs)
            else:
                bs.read_status = BankStatement.INCOMPLETE

        return bs


class XLSReaderBankStatement(ReaderBankStatement):
    def read(self):
        if self.options.get("pandas"):
            return self.__read_itau_credit_card()

        factory = self.factory
        ws = self.data

        bs = BankStatement(self.file)
        cs_reader = factory.create_reader_cash_flow()
        header_row = True
        origins, bs.read_status, bs.errors = self._read_origins(ws.values)
        for idx, row in enumerate(ws.values, 1):
            # Pulando o cabeçalho
            if header_row:
                header_row = False
                continue

            cs = cs_reader.read(row=row, origins=origins, idx=idx)
            if cs.is_blank():
                continue

            if cs.is_valid():
                if isinstance(cs.value, str):
                    cs.value = Decimal(cs.value.replace(",", "."))
                bs.transactions.append(cs)
            else:
                bs.read_status = BankStatement.ERROR
                if cs.cash_date and cs.date:
                    if cs.cash_date < cs.date:
                        bs.errors.append(f"Transação da linha {cs.line} possui data de Caixa superior a "
                                         f"data de Competência")
                for er in cs.errors:
                    bs.errors.append(er)
                bs.errors.append(f"Transação da linha {cs.line} com dados inválidos")
        bs.assets, bs.read_status, bs.errors = self._validate_origin(origins,
                                                                     bs.transactions, bs.errors, bs.read_status)
        return bs

    def __read_itau_credit_card(self):
        bs = BankStatement(self.file)
        bs.read_status = BankStatement.COMPLETE

        reader = ItauXLSReaderCashFlow()

        df = self.data
        cash_date, origin = None, None
        for idx, row in df.iterrows():
            if not origin:
                origin = reader.find_origin(row)

            if not cash_date:
                cash_date = reader.find_cash_date(row)

            try:
                cf = reader.read(row, cash_date, origin)
            except ValueError as err:
                logger.info(f"Could not read row: {row}")
                logger.info(err)
                continue

            if cf.is_valid():
                bs.transactions.append(cf)
            else:
                bs.read_status = BankStatement.INCOMPLETE

        return bs

    @staticmethod
    def _bank_to_code(bank):
        bank = unidecode.unidecode(bank).lower()
        code_banks = {
                      '33':  ['santander'],
                      '218': ['bs2'],
                      '237': ['bradesco'],
                      '335': ['digio'],
                      '260': ['nubank'],
                      '290': ['pagseguro'],
                      '341': ['itau', 'unibanco'],
                      '323': ['mercado', 'pago'],
                      '104': ['caixa', 'economica'],
                      '1':   ['brasil', 'bb']
                    }
        for bank_code in code_banks:
            for name_bank in code_banks[bank_code]:
                if name_bank in bank:
                    return bank_code
        return 0

    def _validate_origin(self, origins, transactions, errors, read_status):
        assets = []
        for origin in origins:
            used_origin = False
            for transaction in transactions:
                if origin['number'] == transaction.origin.account_id:
                    used_origin = True
                    origin['type'] = transaction.origin.account_type
                    break
            if used_origin:
                if origin['type'] == AccountType.CREDITCARD:
                    if len(str(origin['number'])) != 4:
                        errors.append(f"Na linha {origin['line']} a origem do Tipo Cartão de Crédito deve possuir "
                                      f"apenas os últimos 4 dígitos do Cartão")
                        read_status = BankStatement.ERROR
                    if not str(origin['number']).isdigit():
                        errors.append(f"Na linha {origin['line']} a origem do Tipo Cartão de Crédito deve possuir "
                                      f"apenas números")
                        read_status = BankStatement.ERROR
                elif origin['type'] == AccountType.BANKACCOUNT:
                    account_split = str(origin['number']).split('-')
                    if len(account_split) != 2:
                        errors.append(f"Na linha {origin['line']} a origem do Tipo Conta Corrente deve possuir "
                                      f"dígito verificador")
                        read_status = BankStatement.ERROR
                    else:
                        if not str(account_split[0]).isdigit() or not str(account_split[1]).isdigit():
                            errors.append(f"Na linha {origin['line']} a origem do Tipo Conta Corrente deve possuir "
                                          f"apenas números e o dígito verificador")
                            read_status = BankStatement.ERROR
                        if len(str(account_split[1])) != 1:
                            errors.append(f"Na linha {origin['line']} a origem do Tipo Conta Corrente deve possuir "
                                          f"apenas um dígito verificador")
                            read_status = BankStatement.ERROR
                origin['bank'] = self._bank_to_code(origin['bank'])
                assets.append(origin)
        return assets, read_status, errors

    @staticmethod
    def _read_origins(values):
        origins = []
        header_row = False
        read_status = BankStatement.COMPLETE
        errors = []
        for idx, row in enumerate(values, 1):
            if header_row:
                header_row = False
                continue
            cell_values = []
            for cellValue in row:
                cell_values.append(cellValue)
            if len(cell_values) < 10:
                errors.append(f"Na linha {idx} é necessário preencher todos campos")
                read_status = BankStatement.ERROR
            if cell_values[0] is None and cell_values[1] is None and cell_values[2] is None and cell_values[3] is None:
                break
            if cell_values[0] is None:
                errors.append(f"Na Linha {idx} o nome do banco deve estar preenchido")
                read_status = BankStatement.ERROR
            if cell_values[1] is None:
                errors.append(f"Na linha {idx} o tipo da origem (C/C ou Cartão de Crédito) deve estar preenchido")
                read_status = BankStatement.ERROR
            if cell_values[2] is None:
                errors.append(f"Na linha {idx} a origem deve estar preenchida")
                read_status = BankStatement.ERROR
            if cell_values[3] is None:
                cell_values[3] = 0
            origin_obj = {'number': cell_values[2],
                          'type': cell_values[1],
                          'balance': cell_values[3],
                          'bank': cell_values[0],
                          'line': idx}
            origins.append(origin_obj)
        return origins, read_status, errors


