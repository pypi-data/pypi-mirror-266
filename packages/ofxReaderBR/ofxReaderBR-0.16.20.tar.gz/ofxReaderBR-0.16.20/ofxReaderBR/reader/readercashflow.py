import logging
import math
import re
from collections import namedtuple
from datetime import datetime
import unidecode

from ofxReaderBR.model import AccountType, CashFlow, CashFlowType, Origin

logger = logging.getLogger(__name__)


class ItauXLSReaderCashFlow:

    @staticmethod
    def read(row, cash_date, origin):
        name = row[1]
        if name == 'PAGAMENTO EFETUADO':
            raise ValueError(f'This row would generate an invalid cash flow: {row}')

        value = row[3]
        if isinstance(value, float) and math.isnan(value):
            raise ValueError(f'Invalid value on row: {row}')

        return CashFlow(
            origin=origin,
            accrual_date=str(row[0]),
            cash_date=cash_date,
            name=row[1],
            value=value * -1
        )

    @staticmethod
    def find_cash_date(row):
        return row[2] if str(row[0]) in ['aberta', 'fechada'] else None

    @staticmethod
    def find_origin(row):
        row_0_str = str(row[0])
        if '(titular)' in row_0_str:
            digits_list = re.findall(r'\d{4}', row_0_str)
            if digits_list:
                account_id = digits_list[0]
                return Origin(type='CREDITCARD', account_id=account_id)
        return None


class OFXReaderCashFlow:
    @staticmethod
    def read(transaction, options):
        name = transaction.name if transaction.name is not None else transaction.memo
        cf = CashFlow(
            name=name,
            value=transaction.trnamt,
            accrual_date=transaction.dtposted,
        )
        if transaction.trntype == 'CREDIT':
            cf.flowType = CashFlowType.CREDIT
            # FT-1140
            if options.get('creditcard') and options.get('bancodobrasil'):
                cf.value = abs(cf.value)
        return cf


class PDFReaderCashFlow:
    @staticmethod
    def read(factory, ofx):
        cs = CashFlow()

        result = ofx

        cs.date = result[0]
        cs.name = result[1]
        cs.value = result[2]

        if len(result) > 3:
            last_digits = result[3]
            cs.origin = Origin(type='CREDITCARD', account_id=last_digits)

        if len(result) > 4:
            cash_date = result[4]
            if cash_date:
                cs.cash_date = cash_date

        if not cs.cash_date:
            cs.cash_date = cs.date

        return cs


class XMLReaderCashFlow:
    @staticmethod
    def read(factory, ofx):
        cs = CashFlow()

        cs.name = ofx.find('MEMO').text
        cs.value = float(ofx.find('TRNAMT').text)
        dtposted = ofx.find('DTPOSTED').text

        try:
            # YYYYMMDDHHMMSS
            cs.date = datetime.strptime(dtposted[:dtposted.find('[')],
                                        '%Y%m%d%H%M%S')
        except:
            cs.date = datetime.strptime(dtposted, '%Y%m%d')

        # FT-272
        cs.cash_date = cs.date

        if ofx.find('TRNTYPE') == 'CREDIT':
            cs.flowType = CashFlowType.CREDIT

        return cs


class XLSXReaderCashFlow:
    @staticmethod
    def read(row, origins=None, idx=0):
        cs = CashFlow()

        cell_values = []
        cs.errors = []
        cs.line = idx
        for cell_value in row:
            if cell_value is not None:
                if type(cell_value) == str:
                    cell_value = cell_value.strip()
            cell_values.append(cell_value)
        if len(cell_values) < 10:
            cs.errors.append(f"Na linha {idx} todos os campos da transação devem estar preenchidos")
            cs.name = "Transacao invalida"
            return cs
        if all([(value is None or value == "") for value in cell_values]):
            logger.info('Row with blank columns. Made cash flow invalid.')
            return cs
        found_origin = False
        origin_type = ""
        for origin_number in origins:
            if cell_values[5] == origin_number['number']:
                found_origin = True
                origin_type = origin_number['type']
                break
        if not found_origin:
            cs.errors.append(f"A transação da linha {idx} não pode conter uma origem não definida")
            cs.name = "Transacao invalida"
            return cs
        else:
            Account = namedtuple('Account', 'acctid')
            if isinstance(cell_values[5], str):
                acctid = cell_values[5].lstrip('0')
            else:
                acctid = cell_values[5]
            account = Account(acctid=acctid)
            origin = Origin(account)
            if origin_type.upper() == 'C/C':
                origin.account_type = AccountType.BANKACCOUNT
            elif "cartao" in unidecode.unidecode(origin_type).lower() or \
                    "card" in unidecode.unidecode(origin_type).lower() or \
                    "credit" in unidecode.unidecode(origin_type).lower():
                origin.account_type = AccountType.CREDITCARD
            else:
                cs.errors.append(f"O valor para tipo de origem não é valido na linha {idx}. (C/C ou Cartão de Crédito)")
                cs.name = "Transacao invalida"
                return cs
        cs.origin = origin
        cs.date = cell_values[6]
        cs.cash_date = cell_values[7]
        cs.name = cell_values[8]
        cs.value = cell_values[9]

        return cs
