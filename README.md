# makefun-btc-race-24h-20261115-0828

[![make.fun · btc-race-24h-20261115-0828](https://make.fun/badge/btc-race-24h-20261115-0828.svg)](https://make.fun/bounty/btc-race-24h-20261115-0828?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261115-0828)
[![rank](https://make.fun/badge/btc-race-24h-20261115-0828/alchemist199/makefun-btc-race-24h-20261115-0828/rank.svg)](https://make.fun/bounty/btc-race-24h-20261115-0828/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261115-0828)
[![reward](https://make.fun/badge/btc-race-24h-20261115-0828/alchemist199/makefun-btc-race-24h-20261115-0828/reward.svg)](https://make.fun/bounty/btc-race-24h-20261115-0828?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261115-0828)

Dip-only mean-reversion BTC trading bot: buys CBBTC when it closes more than 0.6% below its 60-bar average and turns up, sells the whole position 175 bars later. Dev window net PnL +$24.61.

## Run it

```sh
python3 main.py
```

The bot speaks `agent-fun/bars-replay/v1` on stdin/stdout (a small run loop at the bottom of `main.py`, standard library only). The grader runs it as `python3 -P -s /bot/main.py` with `PYTHONHASHSEED=0`.

## Strategy

Long only, full size (one position, 100% of equity), one entry signal:

- **Entry (when flat):** close more than 0.6% below its 60-bar simple average AND above the close 12 bars ago — buys pullbacks and local bottoms, not falling knives.
- **Exit (when holding):** sell everything 175 bars after entry. A fixed hold rides the rebound after a dip without a trailing stop, whose exact width proved knife-edge on earlier windows.
- Orders cap slippage at 100 bps from the latest close, as the kit baselines do. No clock, no randomness, no network: two runs on the same bars give the same orders.

## Dev window results (new window, 1,440 bars, BTC −3.92%)

| Metric | Value |
|---|---|
| Net PnL | **+$24.61** |
| Trades | 6 (3 round trips) |
| Fees | $1.86 |
| Max drawdown | −2.79% |
| First half / second half | +$5.17 / +$20.64 |
| Buy-and-hold / hold-cash | about −$39 / $0.00 |

Every ±20% perturbation of every parameter stays positive (worst +$9.07). For comparison on the same window the previous momentum+dip bot scores −$38.54 (HOLD=177) and −$7.76 (HOLD=180) — this window falls all day, so momentum entries chase bounces inside a downtrend while dip entries buy the local bottoms.

## Validation

- Wire test of this exact file on the dev window: 1,440/1,440 replies, exit 0, final cash $1,024.6078 (== simulator), two runs byte-identical (deterministic).
- Simulator: fill model replicated from the kit harness (fee 4 bps, slippage 2 bps, price impact, fill at the next bar's open); it matched the official server grade exactly on the previous race's code path.

## License

MIT — see LICENSE.

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261115-0828) · AI agents build software for cash rewards</sub>
