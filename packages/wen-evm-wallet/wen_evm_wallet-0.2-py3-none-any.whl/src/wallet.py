from eth_account import Account


def save_line(path, line):
    with open(path, 'a') as file:
        file.write(line)


def create_ethereum_wallet(num=50, path="./wallets.txt"):
    """
    自动生成num个以太坊钱包，助记词保存在path路径
    :param num:
    :return:
    """
    for i in range(num):
        # 生成以太坊钱包
        Account.enable_unaudited_hdwallet_features()
        acct, mnemonic = Account.create_with_mnemonic()
        save_line(path, str(mnemonic) + "\n")


def create_account_by_mnemonic(mnemonic, index):
    Account.enable_unaudited_hdwallet_features()
    mnemonic_phrase = mnemonic
    path = f"m/44'/60'/{index}'/0/0"
    wallet = Account.from_mnemonic(mnemonic_phrase, account_path=path)
    return (wallet.address, wallet.key.hex())