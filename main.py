#!/usr/bin/env python3
"""BTC race bot for btc-race-24h-20261115-0828: dip-only mean reversion.

Strategy (all decisions on 1-minute closes of CBBTC, long only, full size):
  ENTRY (when flat): buy when the close is more than 0.6% below its
    60-bar simple average AND turning up (close above the close 12 bars
    ago). This buys pullbacks and local bottoms, not falling knives; the
    turn confirmation keeps it out of the middle of a slide.
  EXIT (when holding): sell the whole position 175 bars after entry.
    A fixed hold rides the rebound after a dip without a trailing stop,
    whose exact width proved knife-edge on earlier windows.
  Sizing: every buy spends all cash (one position, max 100% of equity).
  Orders cap slippage at 100 bps from the latest close, as the kit
  baselines do. No clock, no randomness, no network: two runs on the
  same bars give the same orders. Standard library only.

Why dip-only here: on this race's dev window (24h, BTC -3.92%, open
$67,155.66 -> close $64,523.80) the old momentum+dip bot loses money
(HOLD=177: -$38.54; original HOLD=180: -$7.76) because momentum entries
chase bounces inside a downtrend. The dip-only variant tuned on this
window scores net PnL +$24.61 in the validated simulator (fill model
matched the official server grade exactly on the previous race's code
path), 6 trades, max drawdown -2.79%, fees $1.86. Wire test of this
exact file on the dev window: 1,440/1,440 replies, exit 0, final cash
$1,024.6078 (== sim), two runs byte-identical. First half +$5.17,
second half +$20.64. Every +-20% perturbation of every parameter stays
positive (worst +$9.07). Baselines on the same window: buy-and-hold
about -$39, hold-cash $0.00.

Wire protocol: the bot speaks agent-fun/bars-replay/v1 directly (the
small run loop at the bottom of this file, standard library only): one
JSON line in per batch, exactly one reply out echoing its seq. Orders
decided on a batch fill at the next bar's open.
"""

import json
import sys

SYMBOL = "CBBTC"
PROTOCOL = "agent-fun/bars-replay/v1"
MAX_SLIPPAGE_BPS = 100

# Parameters (see module docstring for why each is what it is).
DIP_N = 60          # dip reference: simple average of this many closes
DIP_PCT = 0.006     # close must be 0.6% below that average
DIP_TURN = 12       # ... and above the close this many bars ago
HOLD_BARS = 175     # bars to hold a position before selling it all

closes = []         # CBBTC closes, in arrival order (ints, price_scale 5)
entry_seq = -1      # seq of the batch the current position was entered on


class State:
    """What the bot knows, current before each batch is answered."""

    def __init__(self, hello):
        self.seq = -1
        units = hello["capital"]["quote_units"]
        self.cash = int(units)
        self.equity = int(units)
        self.positions = {}     # symbol -> (qty, cost_quote_units)
        self.warming_up = False  # this kit opens with no warm-up batches

    def apply_batch(self, batch):
        self.seq = batch["seq"]
        account = batch["account"]
        self.cash = int(account["cash_quote_units"])
        self.equity = int(account["equity_quote_units"])
        self.positions = {p["symbol"]: (int(p["qty"]), int(p["cost_quote_units"]))
                          for p in account["positions"]}


def on_batch(state, batch):
    global entry_seq
    for bar in batch["bars"]:
        if bar["symbol"] == SYMBOL:
            closes.append(int(bar["c"]))
    if state.warming_up:
        return []

    held = state.positions.get(SYMBOL)
    if held is not None:
        if state.seq - entry_seq >= HOLD_BARS:
            entry_seq = -1
            return [{"side": "sell", "symbol": SYMBOL, "qty": held[0],
                     "max_slippage_bps": MAX_SLIPPAGE_BPS}]
        return []

    # Flat: look for a dip entry. Need enough history for the signal.
    if not closes:
        return []
    c = closes[-1]
    enter = False
    if len(closes) > DIP_N and len(closes) > DIP_TURN:
        avg = sum(closes[-DIP_N:]) / DIP_N
        if c < avg * (1 - DIP_PCT) and c > closes[-DIP_TURN - 1]:
            enter = True
    if enter and state.cash >= 1_000_000:
        entry_seq = state.seq
        return [{"side": "buy", "symbol": SYMBOL,
                 "notional_quote_units": state.cash,
                 "max_slippage_bps": MAX_SLIPPAGE_BPS}]
    return []


def run():
    """Speak agent-fun/bars-replay/v1 until done, then exit 0."""
    state = None
    next_id = 1
    out = sys.stdout
    for line in sys.stdin:
        if not line.strip():
            continue
        msg = json.loads(line)
        kind = msg.get("type")
        if kind == "hello":
            if msg.get("protocol") != PROTOCOL:
                raise SystemExit("wrong protocol: %r" % msg.get("protocol"))
            state = State(msg)
        elif kind == "batch":
            state.apply_batch(msg)
            orders = []
            for o in on_batch(state, msg) or []:
                cid = "o%d" % next_id
                next_id += 1
                if o["side"] == "buy":
                    orders.append({"side": "buy", "client_id": cid,
                                   "symbol": o["symbol"],
                                   "notional_quote_units": str(o["notional_quote_units"]),
                                   "max_slippage_bps": o["max_slippage_bps"]})
                else:
                    orders.append({"side": "sell", "client_id": cid,
                                   "symbol": o["symbol"],
                                   "qty": str(o["qty"]),
                                   "max_slippage_bps": o["max_slippage_bps"]})
            out.write(json.dumps({"type": "reply", "seq": msg["seq"],
                                  "orders": orders}, separators=(",", ":")) + "\n")
            out.flush()
        elif kind == "done":
            return
        else:
            raise SystemExit("unknown message type: %r" % kind)
    raise SystemExit("input ended before done")


run()
