import json
import pandas as pd
import sys
import traceback

try:
    sys.path.insert(1, 'F:/Python/__My Python Programs/APItools')
    from APItools import APItools
except:
    sys.path.insert(1, 'C:/Users/magnu/s/Python310/My Python3_10 Programs/APItools')
    from APItools import APItools
sys.path.insert(1, 'F:/Python/__My Python Programs/GetCurrentTime')
from GetCurrentTime import GetCurrentTime
sys.path.insert(1, 'F:/Python/__My Python Programs/ErrorLogger')
from ErrorLogger import ErrorLogger

class OmniScan:
    def __init__(self):
        self.evan = True
        self.APIT = APItools()
        self.GCT = GetCurrentTime()
        self.EL = ErrorLogger()
        self.wallets = json.load(open('wallets.json', 'r'))
        self.contracts = json.load(open('contracts.json', 'r'))
        self.spreadsheets = json.load(open('spreadsheets.json', 'r'))
        self.tokens = json.load(open('tokens.json', 'r'))
        

    def newScan(self, scan_plan):
        #self.scan_history =
        shit = 'balls'

    def readTransactions(self, wallet_name, file_name=None):
        if not(file_name):
            file_name = wallet_name
        URL = self.APIT.URL_dict['Solscan']['account']['exportTransactions'].split('<ADDRESS>')[0] + \
              self.wallets[wallet_name] + self.APIT.URL_dict['Solscan']['account']['exportTransactions'].split('<ADDRESS>')[1]
        transactions = self.APIT.request(URL, self.APIT.headers_dict['Solscan'], output_type='csv', file_name=file_name)
        return(transactions)

    def createTransactionLog(self, wallet_name):
        transaction_history = self.readTransactions(wallet_name, 'transaction_logs/' + wallet_name + '_transaction_log')

    def updateTransactionLog(self, wallet_name):
        try:
            new_transaction_history = self.readTransactions(wallet_name)
            transaction_log = pd.read_csv(open('transaction_logs/' + wallet_name + '_transaction_log.csv'))
            del transaction_log['Unnamed: 0']
            list_of_dicts = []
            for num in range(len(new_transaction_history)):
                if new_transaction_history['BlockTime'][num] > max(transaction_log['BlockTime']):
                    new_transaction_dict = {}
                    column_names = []
                    for column_name in new_transaction_history:
                        new_transaction_dict[column_name] = new_transaction_history[column_name][num]
                        column_names.append(column_name)
                    list_of_dicts.append(new_transaction_dict)
            print(len(list_of_dicts))
            new_transactions_dataframe = pd.DataFrame(list_of_dicts, columns=column_names)
            #new_transactions_dataframe.to_csv('transaction_logs/' + wallet_name + '_new_transactions.csv')
            for num in range(len(new_transactions_dataframe)):
                if new_transaction_history['TokenAddress'][num] in self.contracts:
                    print(self.contracts[new_transaction_history['TokenAddress'][num]])
            latest_transaction_time = max(new_transactions_dataframe['BlockTime Unix'])
            last_latest_transaction_time = max(transaction_log['BlockTime Unix'])
            time_passed_seconds = (int(latest_transaction_time) - int(last_latest_transaction_time)) / 10
            time_passed_hours = time_passed_seconds / 360
            time_passed_days = time_passed_hours / 24
            print(time_passed_days)
            print(max(new_transactions_dataframe['BlockTime']))
            print(max(transaction_log['BlockTime']))
            return(new_transactions_dataframe)
##            for thing in new_transaction_history:
##                print(new_transaction_history[thing][0])
##            for thing in transaction_log:
##                print(transaction_log[thing][0])
        except FileNotFoundError as exception:
            print('Transaction Log not found. Creating it now...')
            self.createTransactionLog(wallet_name)

    def createUpdateCSV(self, spreadsheet_name='default'):
# Notes
#   Tokens come after $USD
        if spreadsheet_name == 'default':
            spreadsheet_name = self.spreadsheets['default']
        self.spreadsheet = self.spreadsheets[spreadsheet_name]
        new_transaction_dataframe = self.updateTransactionLog(self.spreadsheet["default_wallet"])
        default_column_names = self.spreadsheet['default_column_names']
        token_names_dict = {}
        token_names_list = []
        for contract_name in self.contracts:
            if '/' in contract_name:
                token_A = contract_name.split('/')[0]
                token_B = contract_name.split('/')[1]
                if not(token_A in token_names_list) and not('USD' in token_A):
                    token_names_list.append(token_A)
                    token_names_dict[len(token_names_list)] = token_A
                if not(token_B in token_names_list) and not('USD' in token_B):
                    token_names_list.append(token_B)
                    token_names_dict[len(token_names_list)] = token_B
        ####Evan Fix
        if self.evan:
            token_names_dict[2] = 'ORCA'
            token_names_dict[len(token_names_dict) + 1] = 'SOL'
        print(token_names_dict)
        new_column_names = []
        index = 1
        for column_name in default_column_names:
            new_column_names.append(default_column_names[column_name])
            index += 1
            if default_column_names[column_name] == '$USD':
                for token_name in token_names_dict:
                    ####Evan Fix
                    if self.evan and token_names_dict[token_name] == 'SOL':
                        shit = 'balls'
                    else:
                        new_column_names.append(token_names_dict[token_name])
                        index += 1
                        ####Evan Fix
                        if self.evan:
                            if token_names_dict[token_name] == 'PUFF':
                                new_column_names.append('SOL')
                                index += 1
                            elif token_names_dict[token_name] == 'NOVA':
                                new_column_names.append('HBB')
                                index += 1
        print(new_column_names)
        list_of_rows = []
        for source in self.spreadsheet['sources']:
            list_of_rows = self.createRows(source, new_column_names, list_of_rows, token_names_dict)
        self.APIT.CC.convertListOfDictsToCSV(list_of_rows, new_column_names, file_name='shit')

    def createRows(self, row_source, column_names, list_of_rows, token_names_dict):
        row_index = len(list_of_rows) + 1
        if row_source == 'contracts':
            for symbol_pair in self.spreadsheet['sources']['contracts']:
                token_symbol = token_names_dict[row_index]
                list_of_rows.append(self.createDefiRow(column_names, symbol_pair, token_symbol, row_index))
                row_index += 1
        return(list_of_rows)

    def createDefiRow(self, column_names, symbol_pair, token_symbol, row_index):
        new_row = {}
        column_index = 1
        print(token_symbol)
        for column_name in column_names:
            new_entry = ''
            current_column_letter = self.APIT.CC.column_index_converter[column_index + 1]
            left_column_letter = self.APIT.CC.column_index_converter[column_index]
            right_column_letter = self.APIT.CC.column_index_converter[column_index + 2]
            current_cell_pos = current_column_letter + str(self.spreadsheet['rows'] + row_index)
            left_cell_pos = left_column_letter + str(self.spreadsheet['rows'] + row_index)
            right_cell_pos = right_column_letter + str(self.spreadsheet['rows'] + row_index)
            prior_cell_pos = current_column_letter + str(self.spreadsheet['rows'] + row_index - self.spreadsheet['last_section_height'])
            if column_name == 'Time':
                if row_index == 1:
                    date = self.GCT.getDateString()
                    new_entry = date
                elif row_index == 2:
                    time = self.GCT.getTimeString()
                    new_entry = time
                elif row_index == 3:
                    timestamp = self.GCT.getTimeStamp()
                    new_entry = timestamp
            elif column_name == 'Days':
                if row_index == 1:
                    last_timestamp_pos = self.APIT.CC.column_index_converter[column_index - 1] + str(self.spreadsheet['rows'] - self.spreadsheet['last_section_height'] + 3)
                    latest_timestamp_pos = self.APIT.CC.column_index_converter[column_index - 1] + str(self.spreadsheet['rows'] + 3)
                    new_entry = "'=ROUND((" + latest_timestamp_pos + "-" + last_timestamp_pos + ") / 60 / 60 / 24,3)"
                elif row_index == 2:
                    last_total_days_pos = current_column_letter + str(self.spreadsheet['rows'] - self.spreadsheet['last_section_height'] + 2)
                    latest_days_pos = current_column_letter + str(self.spreadsheet['rows'] + row_index - 1)
                    new_entry = "'=" + last_total_days_pos + "+" + latest_days_pos
            elif column_name == 'Source':
                new_entry = symbol_pair
            elif column_name == 'Platform':
                new_entry = self.spreadsheet['sources']['contracts'][symbol_pair]
            elif column_name == 'APR':
                new_entry = '<APR of ' + symbol_pair + ' farm>'
            elif column_name == "APR '%'":
                new_entry = "'=" + left_cell_pos + "/" + right_cell_pos
            elif column_name == '<1st recorded APR>':
                new_entry = "'=" + prior_cell_pos
            elif column_name == 'Symbol':
                new_entry = token_symbol
            elif column_name == 'Price':
                token_price = round(self.getPrice(token_symbol), 6)
                new_entry = token_price
            new_row[column_name] = new_entry
            column_index += 1
        #print(new_row)
        return(new_row)

    def getPrice(self, token_symbol, source='default'):
        ####Evan Fix
        if self.evan:
            if token_symbol == 'SOL':
                token_symbol = 'stSOL'
        token_address = self.tokens[token_symbol]
        URL = self.APIT.URL_dict['Solscan']['market']['token'] + token_address
        try:
            response = self.APIT.request(URL, self.APIT.headers_dict['Solscan'])
            token_price = response['priceUsdt']
            if token_price == None:
                token_price = 0
        except Exception as error:
            self.EL.inCaseOfError(**{'error': error, \
                                    'description': 'API failed to return price', \
                                    'pause_time': 5, \
                                    'program': 'OmniScan', \
                                    'line_number': traceback.format_exc().split('line ')[1].split(',')[0]})

        return(token_price)

    def readTransactions_RAW(self, wallet_name, limit=1):
        transactions = self.APIT.request(self.APIT.URL_dict['Solscan']['account']['transactions'] + self.wallets[wallet_name] + '&limit=' + str(limit), \
                                         self.APIT.headers_dict['Solscan'])
        return(transactions)

 

OS = OmniScan()
OS.createUpdateCSV('PWA Staking')
                           
