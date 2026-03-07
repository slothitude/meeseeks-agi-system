# SteamArb Implementation Plan - Betfair Integration

## Current Status (1:05 PM, March 7, 2026)

### What's Working ✅
- Edge detection: Finding 10%+ price movements
- R management: Tracking bankroll correctly
- Strategy logic: BACK STEAM, LAY DRIFT
- Betfair login: Session token acquired
- Paper trading: 7 trades placed, 3R remaining

### What's Missing ❌
- Betfair market ID matching
- Selection ID mapping
- Actual bet placement

---

## The Problem

**Ladbrokes API provides:**
- Runner names: "Final Voyage", "Shelly's Ace"
- Prices: $12.00, $35.00
- Race times: 2026-03-07T13:10:00Z

**Betfair API requires:**
- Market ID: "1.123456789"
- Selection ID: "12345678"
- These IDs are NOT in Ladbrokes data

---

## Solution: Build Market Matcher

### Step 1: Get Betfair Markets (15 mins)
```python
def get_betfair_markets():
    """Get all AU horse racing markets from Betfair"""
    params = {
        "filter": {
            "eventTypeIds": ["7"],  # Horse racing
            "marketCountries": ["AU"],
            "marketTypeCodes": ["WIN"],
            "marketStartTime": {
                "from": datetime.now().isoformat(),
                "to": (datetime.now() + timedelta(hours=6)).isoformat()
            }
        },
        "maxResults": 100
    }
    # Call: SportsAPING/v1.0/listMarketCatalogue
```

### Step 2: Match Tracks (10 mins)
```python
def match_track(ladbrokes_track: str, betfair_venue: str) -> bool:
    """Match Ladbrokes track name to Betfair venue"""
    # Normalize names
    # "Murray Bridge" → "Murray Bridge"
    # "Randwick" → "Randwick"
    # "Flemington" → "Flemington"
    return normalize(ladbrokes_track) == normalize(betfair_venue)
```

### Step 3: Match Race Times (5 mins)
```python
def match_race_time(ladbrokes_time: datetime, betfair_time: datetime) -> bool:
    """Match race start times (within 1 minute tolerance)"""
    diff = abs((ladbrokes_time - betfair_time).total_seconds())
    return diff < 60  # 1 minute tolerance
```

### Step 4: Match Runners (10 mins)
```python
def match_runner(ladbrokes_name: str, betfair_name: str) -> bool:
    """Match runner names"""
    # Normalize: remove punctuation, lowercase
    # "Final Voyage" → "final voyage"
    # "Shelly's Ace" → "shellys ace"
    return normalize(ladbrokes_name) == normalize(betfair_name)
```

### Step 5: Cache Mappings (5 mins)
```python
# Store in JSON for quick lookup
market_cache = {
    "Murray Bridge_R4_2026-03-07T13:10:00Z": {
        "market_id": "1.123456789",
        "runners": {
            "Final Voyage": {"selection_id": "12345678"},
            "Shelly's Ace": {"selection_id": "87654321"}
        }
    }
}
```

---

## Implementation Timeline (Tonight)

### Hour 1: Core Matcher
- Get Betfair markets
- Match tracks
- Match race times
- Match runners

### Hour 2: Integration
- Combine with existing edge detection
- Place actual bets
- Track fills

### Hour 3: Testing
- Paper trade with real market IDs
- Validate matching accuracy
- Test bet placement

### Hour 4: Documentation
- Update live_trading_real.py
- Create user guide
- Plan for tomorrow

---

## Expected Results (Tomorrow)

**With market matcher:**
- ✅ Place real bets on Betfair
- ✅ Track actual positions
- ✅ Calculate real R-multiples
- ✅ Full automation

**Projected performance:**
- 40 trades/day
- +$0.05 per trade
- +$2.00/day
- +$40/month (at $1 R-unit)

---

## Risk Mitigation

1. **Start small:** $1.00 bets only
2. **Validate first:** Paper trade with real market IDs
3. **Stop loss:** -0.05R per trade
4. **Max exposure:** 2 trades per race
5. **Exit buffer:** 3 minutes before race

---

## Key Learnings from Today

1. **Edge detection works** - Found 45+ edges in 9 races
2. **R potential positive** - +1.856R from 4 races
3. **System stable** - Running for 4+ hours
4. **Strategy sound** - DRIFT (57%), STEAM (29%), VOLATILITY (14%)
5. **Paper trading valuable** - Validated before risking real money

---

## Next Steps

1. ✅ Continue paper trading today
2. ⏳ Build market matcher tonight
3. ⏳ Test with real Betfair data
4. ⏳ Start live trading tomorrow morning

---

*Status: Paper trading until 5pm, implementation tonight, live tomorrow*
