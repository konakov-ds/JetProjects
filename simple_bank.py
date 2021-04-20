import random
import sqlite3

# create database for project
connect_base = sqlite3.connect('card.s3db')
queries = connect_base.cursor()
queries.execute('DROP TABLE IF EXISTS card;')
queries.execute("""
CREATE TABLE IF NOT EXISTS card (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number TEXT,
    pin TEXT,
    balance INTEGER DEFAULT 0
);""")
connect_base.commit()


class Client:
    # class for store client info
    def __init__(self, card_id, card_pin, balance=0, log_flag=False):
        self.card_id = card_id
        self.card_pin = card_pin
        self.balance = balance
        self.log_flag = log_flag


class Bank:
    # class for bank operations
    IIN = '400000'

    def __init__(self):
        self._database = dict()

    def insert_new_card(self, card_id, pin):
        conn = sqlite3.connect('card.s3db')
        cur = conn.cursor()
        cur.execute(
            f"INSERT INTO card(number, pin)\
             VALUES {(card_id, pin)}"
        )
        conn.commit()

    def find_card(self, card_id):
        conn = sqlite3.connect('card.s3db')
        cur = conn.cursor()
        cur.execute(
            f"SELECT number FROM card\
              WHERE number = {card_id}"
        )
        result = cur.fetchone()
        return result

    def update_balance(self, card_id, blnc):
        conn = sqlite3.connect('card.s3db')
        cur = conn.cursor()
        cur.execute(
            f"UPDATE card\
              SET balance = {blnc}\
              WHERE number = {card_id}"
        )
        conn.commit()

    def delete_card(self, card_id):
        conn = sqlite3.connect('card.s3db')
        cur = conn.cursor()
        cur.execute(
            f"DELETE FROM card\
              WHERE number = {card_id}"
        )
        conn.commit()

    def luhn_algo(self, card_id):
        mult_odd = [2 * int(j) if i % 2 == 0 else int(j) for i, j in enumerate(card_id)]
        sbstrct_9 = [i - 9 if i > 9 else i for i in mult_odd]
        card_sum = sum(sbstrct_9)
        for num in range(10):
            if (num + card_sum)%10 == 0:
                return str(num)

    def create_account(self):
        flag = True
        while flag:
            gen_id = ''.join([str(random.randint(0, 9)) for _ in range(9)])
            card_id = self.IIN + gen_id
            checksum = self.luhn_algo(card_id)
            card_id = card_id + checksum
            card_pin = ''.join([str(random.randint(0, 9)) for _ in range(4)])
            if card_id not in self._database:
                flag = False
                client = Client(card_id, card_pin)
                self._database[card_id] = client
                self.insert_new_card(card_id, card_pin)
                print(f'\nYour card has been created\nYour card number:\n{card_id}\nYour card PIN:\n{card_pin}\n')
                self.run_session()

    def login(self):
        card_id = input('Enter your card number:\n')
        card_pin = input('Enter your PIN:\n')
        if card_id not in self._database or self._database[card_id].card_pin != card_pin:
            print('Wrong card number or PIN!\n')
            self.run_session()
        else:
            self._database[card_id].log_flag = True
            print('You have successfully logged in!\n')
            self.run_session(client=self._database[card_id])

    def menu(self, client=False):
        if client:
            cl_input = input('1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit\n')
        else:
            cl_input = input('1. Create an account\n2. Log into account\n0. Exit\n')
        return cl_input

    def run_session(self, client=False):
        cl_input = self.menu(client)
        if cl_input == '1' and not client:
            self.create_account()
        elif cl_input == '2' and not client:
            self.login()
        elif cl_input == '1' and client:
            print(f'Balance: {client.balance}')
            self.run_session(client=client)
        elif cl_input == '2' and client:
            income_input = input('Enter income:\n')
            client.balance += int(income_input)
            self.update_balance(client.card_id, client.balance)
            print('Income was added!\n')
            self.run_session(client=client)
        elif cl_input == '3' and client:
            print('Transfer\n')
            transfer_card = input('Enter card number:\n')
            if self.luhn_algo(transfer_card[:-1]) != transfer_card[-1]:
                print('Probably you made a mistake in the card number. Please try again!\n')
                self.run_session(client=client)
            elif self.find_card(transfer_card) is None:
                print('Such a card does not exist\n')
                self.run_session(client=client)
            else:
                transfer_value = input('Enter how much money you want to transfer:\n')
                if int(transfer_value) >= client.balance:
                    print('Not enough money!')
                    self.run_session(client=client)
                else:
                    client.balance -= int(transfer_value)
                    self.update_balance(client.card_id, client.balance)
                    transfer_client = self._database[transfer_card]
                    transfer_client.balance += int(transfer_value)
                    self.update_balance(transfer_client.card_id,  transfer_client.balance)
                    print('Success!\n')
                    self.run_session(client=client)
        elif cl_input == '4' and client:
            self._database.pop(client.card_id)
            self.delete_card(client.card_id)
            print('The account has been closed!\n')
            self.run_session()
        elif cl_input == '5' and client:
            client.log_flag = False
            print('You have successfully logged out!\n')
            self.run_session()
        elif cl_input == '0' and client:
            print('Bye')


bank = Bank()
bank.run_session()