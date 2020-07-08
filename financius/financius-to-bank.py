""" Script to convert Financius App (RIP) exported CSV data to file accepted in Wallet App.

"""

import logging
import click
import pandas as pd


@click.command()
@click.option('-f', '--file', help='Path to the CSV data file')
def main(file):
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    financius_export = pd.read_csv(file, sep=',', encoding='utf8',
                                   header=None,
                                   names=["date", "time", "type", "status", "comment", "from", "to", "category", "tags",
                                          "amount", "currency", "rate"],
                                   parse_dates=["date"],
                                   dayfirst=True)

    # filters:
    # status -> confirmed
    # currency -> EUR
    # rate -> 1.0
    df_confirmed = financius_export[(financius_export.status == "Confirmed") & (financius_export.currency == 'EUR') & (
            financius_export.rate == 1.0)]

    # type -> Expense/Income
    df_exp = df_confirmed[df_confirmed.type != "Transfer"]

    # from or to -> Société Générale
    df_sg = df_exp[~((df_exp["from"] != "Société Générale") & (df_exp["to"] != "Société Générale"))]

    # date before 27/09/18
    df_old = df_sg[df_sg.date < "2018-09-27"]

    # transformations:
    # type Expense -> negative amount
    df_old.loc[df_old.type == "Expense", "amount"] *= -1

    # concat "category | tags | comment" -> note
    df_old.loc[:, "note"] = df_old["category"].fillna("") + " | " + \
                            df_old["tags"].fillna("") + " | " + \
                            df_old["comment"].fillna("")

    # output cols: date, amount, currency, note, category
    df_old[["date", "amount", "currency", "note", "category"]].to_csv("exportFinanciusSociete260918.csv", index=False)


if __name__ == '__main__':
    main()
