# BTC race bot — btc-race-24h-20261115-0828

Dip-only mean-reversion bot for the make.fun BTC race
(`btc-race-24h-20261115-0828`): buys when CBBTC closes more than 0.6%
below its 60-bar average and turns up, sells the whole position 175
bars later. Full size, long only, no leverage.

## Dev window result (simulator, validated fill model)

- Net PnL **+$24.61** on the race's 24h dev window (BTC -3.92%)
- 6 trades (3 round trips), max drawdown -2.79%, fees $1.86
- First half +$5.17, second half +$20.64
- Every ±20% perturbation of every parameter stays positive (worst +$9.07)
- Wire test of this exact file: 1,440/1,440 replies, exit 0, final cash
  $1,024.6078, two runs byte-identical

For comparison on the same window the previous momentum+dip bot scores
-$38.54 (HOLD=177) and -$7.76 (HOLD=180), and buy-and-hold about -$39 —
this window falls all day, so momentum entries chase bounces inside a
downtrend while dip entries buy the local bottoms.

## Run

Python 3.13, standard library only. The bot speaks
`agent-fun/bars-replay/v1` on stdin/stdout through a small run loop at
the bottom of `main.py` (no vendored SDK needed).

## License

MIT — see LICENSE.
