import pandas as pd

from utils.constants import TX_HISTORY_PATH


class TransactionsTracker:
    def __init__(self):
        self.tx_history = self.read_tx()

    def read_tx(self):
        return pd.read_csv(TX_HISTORY_PATH, index_col=0, header=0)

    def add_tx(
        self,
        op_id,
        from_addr,
        to_add,
        send_at,
        completed_at,
        amount,
        tx_hash,
        tx_status,
        details,
    ):
        self.tx_history = self.tx_history.iloc[len(self.tx_history)] = [
            op_id,
            from_addr,
            to_add,
            send_at,
            completed_at,
            amount,
            tx_hash,
            tx_status,
            details,
        ]
        self.save()

    def save(self):
        self.tx_history.to_csv(TX_HISTORY_PATH)
