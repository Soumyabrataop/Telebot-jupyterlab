# Crypto libraries Documentation

**Overview**\
The new **libs.web3lib** library is designed to simplify and secure transactions on Ethereum-compatible (EVM) blockchains. This library is packed with robust features like:

* **Multi-network support:** Interact with over 30 EVM chains effortlessly.
* **Automatic gas estimation:** Avoid under- or overestimating gas.
* **Retry logic:** Optionally retry transactions on transient errors.
* **Proxy:** The library uses a large set of proxies, which minimizes rate limit errors.
* **Centralized key management:** Easily store and retrieve private keys using Telebot Creator's MongoDB integration.

**Deprecated Libraries**\
Please note that the following libraries are now deprecated and no longer supported:

* **libs.Polygon**
* **libs.ARB**
* **libs.TTcoin**
* **libs.Tomochain**

We strongly recommend using **libs.web3lib** for all new projects.\\

#### Below is a comprehensive explanation of each function, its parameters, and how to use them.

***

### **`sendNativeCoin(...)`**

This function allows you to send native coins like **ETH**, **BNB**, **MATIC**, etc., on supported EVM chains. It’s ideal for simple value transfers without smart contracts.

#### **Function Signature**

```tpy
def sendNativeCoin(
    value: float,
    to: str,
    rpc_url: Optional[str] = None,
    gas: Optional[int] = None,
    gasPrice: Optional[int] = None,
    private_key: Optional[str] = None,
    increase_gas: Optional[int] = None,
    wait_for_confirmation: bool = True,
    confirmation_timeout: int = 15,
    network: Optional[str] = None,
    estimate_gas: bool = True,
    retry: bool = False,
)
```

#### **Parameter Details**

| Parameter                   | Type            | Description                                                                                                                                |
| --------------------------- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **`value`**                 | `float`         | Amount of native coin (e.g., ETH, BNB) to send.                                                                                            |
| **`to`**                    | `str`           | The recipient's wallet address.                                                                                                            |
| **`rpc_url`**               | `Optional[str]` | Custom RPC URL for the target network. If not provided, you must define the `network` parameter.                                           |
| **`gas`**                   | `Optional[int]` | Manually set gas limit. If not provided, gas will be estimated automatically.                                                              |
| **`gasPrice`**              | `Optional[int]` | Specify the gas price. Defaults to network’s current gas price if omitted.                                                                 |
| **`private_key`**           | `Optional[str]` | Your wallet’s private key for signing the transaction. Required for successful execution.                                                  |
| **`increase_gas`**          | `Optional[int]` | Increase the estimated gas price by a percentage. Useful for faster confirmations.                                                         |
| **`wait_for_confirmation`** | `bool`          | If `True`, the function waits until the transaction is confirmed. Default is `True`.                                                       |
| **`confirmation_timeout`**  | `int`           | Maximum seconds to wait for confirmation. Default is `15`.                                                                                 |
| **`network`**               | `Optional[str]` | Instead of defining an `rpc_url`, specify the network name (e.g., `"ethereum"`, `"bsc"`, `"polygon"`).                                     |
| **`estimate_gas`**          | `bool`          | If `True`, gas will be estimated automatically. Recommended for convenience. Default is `True`.                                            |
| **`retry`**                 | `bool`          | If `True`, the function retries the transaction once if it fails. Useful to bypass common errors like "nonce too low". Default is `False`. |

***

### **`sendETHER(...)`**

This function is used to send **ERC-20 tokens** by specifying a token contract address. It's designed for token transfers that require interacting with smart contracts.

#### **Function Signature**

```tpy
def sendETHER(
    value: float, 
    to: str, 
    rpc_url: Optional[str] = None, 
    gas: Optional[int] = None,
    gasPrice: Optional[int] = None, 
    private_key: Optional[str] = None,
    increase_gas: Optional[int] = None,
    wait_for_confirmation: bool = True,
    confirmation_timeout: int = 15,
    network: Optional[str] = None,
    contract_address: Optional[str] = None,
    retry: bool = False,
    estimate_gas: bool = True,
)
```

#### **Parameter Details**

| Parameter                   | Type            | Description                                                                                                                                |
| --------------------------- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **`value`**                 | `float`         | Amount of tokens to send.                                                                                                                  |
| **`to`**                    | `str`           | The recipient's wallet address.                                                                                                            |
| **`rpc_url`**               | `Optional[str]` | Custom RPC URL for the target network. If not provided, you must define the `network` parameter.                                           |
| **`gas`**                   | `Optional[int]` | Manually set gas limit. If not provided, gas will be estimated automatically.                                                              |
| **`gasPrice`**              | `Optional[int]` | Specify the gas price. Defaults to network’s current gas price if omitted.                                                                 |
| **`private_key`**           | `Optional[str]` | Your wallet’s private key for signing the transaction. Required for successful execution.                                                  |
| **`increase_gas`**          | `Optional[int]` | Increase the estimated gas price by a percentage. Useful for faster confirmations.                                                         |
| **`wait_for_confirmation`** | `bool`          | If `True`, the function waits until the transaction is confirmed. Default is `True`.                                                       |
| **`confirmation_timeout`**  | `int`           | Maximum seconds to wait for confirmation. Default is `15`.                                                                                 |
| **`network`**               | `Optional[str]` | Instead of defining an `rpc_url`, specify the network name (e.g., `"ethereum"`, `"bsc"`, `"polygon"`).                                     |
| **`contract_address`**      | `Optional[str]` | The ERC-20 contract address. **Required for token transfers.**                                                                             |
| **`estimate_gas`**          | `bool`          | If `True`, gas will be estimated automatically. Recommended for convenience. Default is `True`.                                            |
| **`retry`**                 | `bool`          | If `True`, the function retries the transaction once if it fails. Useful to bypass common errors like "nonce too low". Default is `False`. |

***

### Supported Networks

Below is a table listing all the EVM chains supported by libs.web3lib:

| Network   | Chain ID   | Default RPC URL                           |
| --------- | ---------- | ----------------------------------------- |
| Ethereum  | 1          | <https://rpc.ankr.com/eth>                |
| BSC       | 56         | <https://bsc-dataseed.binance.org/>       |
| Polygon   | 137        | <https://polygon-rpc.com/>                |
| Avalanche | 43114      | <https://api.avax.network/ext/bc/C/rpc>   |
| Fantom    | 250        | <https://rpc.ftm.tools/>                  |
| Arbitrum  | 42161      | <https://arb1.arbitrum.io/rpc>            |
| Optimism  | 10         | <https://mainnet.optimism.io/>            |
| Harmony   | 1666600000 | <https://api.harmony.one/>                |
| Cronos    | 25         | <https://evm.cronos.org/>                 |
| Moonriver | 1285       | <https://rpc.moonriver.moonbeam.network/> |
| Moonbeam  | 1284       | <https://rpc.api.moonbeam.network/>       |
| Celo      | 42220      | <https://forno.celo.org/>                 |
| Heco      | 128        | <https://rpc.ankr.com/huobichain>         |
| Okexchain | 66         | <https://exchainrpc.okex.org/>            |
| Xdai      | 100        | <https://rpc.gnosischain.com/>            |
| KCC       | 321        | <https://rpc-mainnet.kcc.network/>        |
| Metis     | 1088       | <https://andromeda.metis.io/?owner=1088>  |
| Aurora    | 1313161554 | <https://mainnet.aurora.dev>              |
| Base      | 8453       | <https://mainnet.base.org>                |
| ZKSync    | 324        | <https://mainnet.era.zksync.io>           |
| Scroll    | 534352     | <https://rpc.scroll.io>                   |
| Linea     | 59144      | <https://rpc.linea.build>                 |
| Boba      | 288        | <https://mainnet.boba.network>            |
| Kava      | 2222       | <https://evm.kava.io>                     |
| Fuse      | 122        | <https://rpc.fuse.io>                     |
| Evmos     | 9001       | <https://evmos-evm.publicnode.com>        |
| Canto     | 7700       | <https://canto.slingshot.finance>         |
| Astar     | 592        | <https://evm.astar.network>               |
| Telos     | 40         | <https://mainnet.telos.net/evm>           |
| Rootstock | 30         | <https://public-node.rsk.co>              |
| TTcoin    | 22023      | <https://mainnet-rpc.tscscan.com>         |

***

### Usage Examples

#### Example 1: Sending a Native Coin Transfer (ETH)

```tpy
dummy_private_key = "0xYOUR_PRIVATE_KEY_HERE"
test_rpc = "https://rpc.ankr.com/eth"
test_recipient = "0xRecipientAddressHere"

tx_hash = libs.web3lib.sendNativeCoin(
    value = 0.5,
    to = test_recipient,
    rpc_url = test_rpc,
    private_key = dummy_private_key,
    network = "ethereum",
    retry = True,
    estimate_gas = True
)

bot.sendMessage(f"Native Transfer TX Hash: {tx_hash}")
```

#### Example 2: Sending an ERC‑20 Token Transfer

```tpy
dummy_private_key = "0xYOUR_PRIVATE_KEY_HERE"
dummy_contract = "0xTokenContractAddressHere"
test_recipient = "0xRecipientAddressHere"
test_rpc = "https://rpc.ankr.com/eth"

tx_hash = libs.web3lib.sendETHER(
    value = 1,                     # Token amount (assuming 18 decimals)
    to = test_recipient,
    rpc_url = test_rpc,
    private_key = dummy_private_key,
    contract_address = dummy_contract,
    network = "ethereum",
    retry = True,
    estimate_gas = True
)

bot.sendMessage(f"Token Transfer TX Hash: {tx_hash}")
```

#### Example 3: Using Network Parameter Only

```tpy
dummy_private_key = "0xYOUR_PRIVATE_KEY_HERE"
dummy_contract = "0xTokenContractAddressHere"
test_recipient = "0xRecipientAddressHere"

tx_hash = libs.web3lib.sendETHER(
    value = 0.25,
    to = test_recipient,
    network = "polygon",
    private_key = dummy_private_key,
    contract_address = dummy_contract,
    retry = False,
    estimate_gas = True
)

bot.sendMessage(f"Token Transfer on Polygon TX Hash: {tx_hash}")
```

***

### Final Notes

* **Deprecated Libraries:**\
  The old libraries (libs.Polygon, libs.ARB, libs.TTcoin, libs.Tomochain) are now deprecated and should no longer be used.\
  Please update your projects to use **libs.web3lib**, which offers a unified and more powerful interface for all EVM chains.
