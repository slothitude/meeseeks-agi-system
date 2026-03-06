# SteamArb Professional Insights - BetAngel Forum Study

# 2026-03-07

# Key Findings

# 
## Order Flow & Liquidity
- **Direction matters**: When price moves, follow the direction
- **Tight spreads**: Small profits
- **Enter/exit**: Quick (1-2 ticks)
- **High-frequency scalping**: Quick decisions (1-2 ticks)
- **Liquidity matters**: Betfair has smaller increments (0.01 vs 0.02)
- **Lower liquidity in AU** markets means slower matching and wider spreads
- 
## Best Markets
- **AU Horse Racing** (10am-5pm Brisbane)
- **US Horse Racing** (evening/night - potential)
    - **Grand National** (Feb-Mar): Similar liquidity
    - **Dubai World Cup** (March)
    - **Hong Kong** (various times)
- **Tennis**: In-play,liquidity better
- **golf**: Lower liquidity but patient
- **cricket**: Limited liquidity, spread across entire day

- **football**: Low liquidity, avoid
- **greyhounds**: Good alternative, consistent
- **harness**: Growing, AU-specific
- 
## Execution
- **Quick decisions**: 1-2 ticks
- **Tight spreads**: Aim for 1-2 ticks (1-2 pips)
- **Enter when steam detected** (3-10% drop)
    - Back at peak, lay at current
    - Expected: ~5 minutes for market to catch up
    - This requires watching flucs data from Ladbrokes
- **If using Betfair, back when Betfair hasn't moved, exit
    - If Ladbrokes hasn't moved yet, exit
- **Timing**: Enter on 3 minutes after steam first detected
    - Place back bet, **Expected to lay price: 5% lower than current**
    - **Quick execution**: 
  - Can use `exec` or `gt. steam_arb_engine.py` (price_fluc_detector)
  
  # When price_flucs drop > threshold
  MIN_fluc_drop = 5.0  # 5%
  
  # Exit if no steam detected
    return None
  
  
def check_betfair_back_lay(
    lad_back: float,
    bf_lay: float
    bf_back: float
    lad_open: float
    flucs: list[dict]
    drop = float
) -> None:
    return None
        
        # No steam detected
        return None
    
    # Calculate green book
    back_stake = STAKE_1R
    lay_stake = (back_stake * bf_back) / expected_lay
    net_wins = back_stake * (lay_stake - 1) - lay_liability
    net_loses = lay_stake * (bf_lay - 1)  # Max loss
    
    profit = min(net_wins, net_loses)
    
    # Apply commission
    profit *= (1 - COMmission)
    
    return {
        "profit": profit,
        "profit_r": profit / STAKE_1R,
        "lay_stake": lay_stake,
        "profit_aud": profit,
        "profit_r": round(profit_r, 4)
    }
    
    return None
