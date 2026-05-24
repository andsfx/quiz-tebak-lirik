# Sequence Edu-Based Config Plan: Meridian + Charon

Date: 2026-05-24
Owner: Andy
Status: Draft only, not applied

## Goal

Create config update plan for Meridian and Charon based on Sequence Edu trading principles:

- Structure first, not candle-chasing.
- Volume/fee confirmation before entry.
- Sideways or zombie pools = no trade.
- Risk first, profit second.
- Fee/TVL below 2% = hard no-entry floor.
- Pool fee kecil = volume kecil = capital cuma parkir.

This file is planning only. No config changes applied yet.

## Core rule from Andy

```text
fee/TVL < 2% => do not enter
```

Interpretation:

- `0.02` is hard minimum floor, not recommended operating target.
- Production can and should use stricter floor above 2% when data supports it.
- Current Meridian `minFeeActiveTvlRatio: 0.06` remains valid because it is stricter than Andy's hard no-entry floor.
- Do not loosen fee/TVL just because 2% was mentioned.

## Sequence Edu principles mapped to bots

### Trading principle

Sequence Edu repeats same trading pattern:

1. Wait for clear structure.
2. Confirm with volume.
3. Execute with risk management.
4. No trade is valid when market is unclear.

### Bot equivalent

1. Candidate structure clear:
   - Mcap/liquidity not dead.
   - Holder count sufficient.
   - Not fresh-wallet/bundler farm.
   - Not bottom-catch setup.

2. Fee/volume confirmation:
   - Fee/TVL above production floor.
   - Total fees paid enough to prove demand.
   - Fee/volume ratio not wash-trading.

3. Execution with risk:
   - Small size.
   - Stop loss deterministic.
   - Profit lock / trailing exits.
   - Cooldown repeated tokens.

4. No trade:
   - If candidates fail fee/TVL or total fee proof, no deploy/buy is correct.

---

# Meridian Plan

## Current inspected config snapshot

From `/home/ubuntu/meridian/user-config.json`:

```json
{
  "deployAmountSol": 0.2,
  "maxPositions": 2,
  "minFeeActiveTvlRatio": 0.06,
  "minTokenFeesSol": 15,
  "minTvl": 8000,
  "minVolume": 3000,
  "minOrganic": 40,
  "maxBotHoldersPct": 40,
  "minMcap": 250000,
  "takeProfitPct": 15,
  "stopLossPct": -4,
  "trailingTriggerPct": 8,
  "highVolatilityThreshold": 3,
  "highVolatilityTrailingDropPct": 3.5,
  "outOfRangeWaitMinutes": 30,
  "dynamicTpEnabled": true,
  "dynamicTpTriggerPct": 3,
  "dynamicTpBoostPct": 5,
  "screeningSource": "gmgn",
  "useDiscordSignals": true,
  "discordSignalMode": "merge"
}
```

From `/home/ubuntu/meridian/gmgn-config.json`:

```json
{
  "minTotalFeeSol": 4,
  "minMcap": 10000,
  "maxMcap": 2000000,
  "minHolders": 100,
  "athFilterPct": null,
  "maxBotDegenRate": 0.55,
  "minSmartDegenCount": 0
}
```

## Diagnosis

Good:

- Fee/TVL gate already stricter than 2% hard floor.
- Size is conservative: 0.2 SOL, max 2 positions.
- Dynamic TP and tight volatile trailing already align with risk-first logic.
- Discord merge expands discovery without disabling quality gates.

Weak:

- `gmgn-config.minTotalFeeSol: 4` is too low for Sequence-style volume confirmation.
- `gmgn-config.minMcap: 10000` allows very small micro pools.
- `user-config.minMcap: 250000` may be too high after GMGN prefilter, causing mismatch: tiny pools enter discovery but later stricter gates may kill too many.

## Recommended Meridian patch

### `/home/ubuntu/meridian/user-config.json`

Patch only these keys:

```json
{
  "minFeeActiveTvlRatio": 0.06,
  "minTokenFeesSol": 15,
  "minTvl": 8000,
  "minVolume": 3000,
  "minOrganic": 40,
  "maxBotHoldersPct": 40,
  "minMcap": 150000,
  "deployAmountSol": 0.2,
  "maxPositions": 2,
  "takeProfitPct": 15,
  "stopLossPct": -4,
  "trailingTriggerPct": 8,
  "trailingDropPct": 6,
  "highVolatilityThreshold": 3,
  "highVolatilityTrailingDropPct": 3.5,
  "outOfRangeWaitMinutes": 30,
  "dynamicTpEnabled": true,
  "dynamicTpTriggerPct": 3,
  "dynamicTpBoostPct": 5,
  "screeningSource": "gmgn",
  "useDiscordSignals": true,
  "discordSignalMode": "merge"
}
```

Rationale:

- Keep fee/TVL at 6%, above hard 2% floor.
- Lower final mcap floor from 250k to 150k to avoid over-filtering early valid fee pools.
- Keep all exit/risk controls unchanged.

### `/home/ubuntu/meridian/gmgn-config.json`

Patch only these keys:

```json
{
  "minTotalFeeSol": 8,
  "minMcap": 50000,
  "maxMcap": 2000000,
  "minHolders": 150,
  "athFilterPct": null,
  "requireBullishSupertrend": true,
  "rejectAlreadyAtBottom": true,
  "maxBotDegenRate": 0.55,
  "minSmartDegenCount": 0
}
```

Rationale:

- `minTotalFeeSol: 4 -> 8`: adds real fee proof without going full extreme-fear 15+ SOL.
- `minMcap: 10000 -> 50000`: removes ultra-micro trash.
- `minHolders: 100 -> 150`: adds participation proof.
- Keep ATH allowed because Panda-style momentum can work, but require other quality gates.

## Meridian validation plan

Before applying:

```bash
cd /home/ubuntu/meridian
node - <<'NODE'
const user=require('./user-config.json');
const gmgn=require('./gmgn-config.json');
console.log(JSON.stringify({
  user: {
    minFeeActiveTvlRatio:user.minFeeActiveTvlRatio,
    minMcap:user.minMcap,
    minTokenFeesSol:user.minTokenFeesSol,
    deployAmountSol:user.deployAmountSol,
    maxPositions:user.maxPositions,
    screeningSource:user.screeningSource,
    useDiscordSignals:user.useDiscordSignals,
    discordSignalMode:user.discordSignalMode
  },
  gmgn: {
    minTotalFeeSol:gmgn.minTotalFeeSol,
    minMcap:gmgn.minMcap,
    minHolders:gmgn.minHolders,
    maxMcap:gmgn.maxMcap
  }
}, null, 2));
NODE
```

After applying:

```bash
cd /home/ubuntu/meridian
node -e "JSON.parse(require('fs').readFileSync('user-config.json','utf8')); JSON.parse(require('fs').readFileSync('gmgn-config.json','utf8')); console.log('JSON OK')"
/home/ubuntu/.nvm/versions/node/v22.22.1/bin/pm2 restart meridian --update-env
/home/ubuntu/.nvm/versions/node/v22.22.1/bin/pm2 logs meridian --lines 120 --nostream
```

Observe next 24h:

- Candidate funnel counts.
- Post-filter reject distribution.
- Deploy count.
- Fee/TVL of deployed pools.
- Realized PnL from `lessons.json.performance`.
- Whether `minTotalFeeSol: 8` causes total starvation.

If idle 24h+ and no candidates survive, do not lower fee/TVL first. Inspect reject distribution first.

---

# Charon Plan

## Current inspected strategy snapshot

Source: `/home/ubuntu/charon/charon.sqlite`, table `strategies`.

Relevant strategies currently disabled:

- `candidate_c`: enabled 0
- `candidate_d`: enabled 0
- `profit_lock`: enabled 0
- `sniper`: enabled 0
- `dip_buy`: enabled 0
- `smart_money`: enabled 0

Current `candidate_c` and `candidate_d` shape:

```json
{
  "min_mcap_usd": 12000,
  "max_mcap_usd": 15000,
  "min_gmgn_total_fee_sol": 3,
  "min_holders": 150,
  "position_size_sol": 0.05,
  "max_open_positions": 10,
  "sl_percent": -5.5,
  "profit_lock_enabled": true,
  "min_liquidity_usd": 8000,
  "min_fee_volume_ratio": 0.0015,
  "max_young_wallet_ratio": 0.4,
  "max_bundler_combo_rate": 0.15,
  "max_bot_pct": 0.4
}
```

## Diagnosis

Charon does not visibly expose `fee/TVL` in inspected strategy config. So Andy's rule needs translation through available Charon gates:

- `min_gmgn_total_fee_sol`
- `min_liquidity_usd`
- `min_fee_volume_ratio`
- `min_mcap_usd`
- `min_holders`
- bot/bundler/young-wallet gates

If Charon code supports or gets patched to support `min_fee_tvl_ratio`, use:

```json
{
  "hard_min_fee_tvl_ratio": 0.02,
  "min_fee_tvl_ratio": 0.04
}
```

Interpretation:

- `< 0.02`: hard reject.
- `0.02-0.04`: reject unless special strategy explicitly allows.
- `> 0.04`: acceptable.
- `> 0.06`: preferred.

## Recommended Charon strategy draft

Do not enable live mode until Andy approves. This is config draft only.

### Candidate C: quality early-pool mode

Target: keep degen size small, but require more proof than current 12k-15k / 3 SOL fee window.

```json
{
  "entry_mode": "immediate",
  "min_source_count": 1,
  "require_fee_claim": false,
  "token_age_max_ms": 3600000,

  "min_mcap_usd": 15000,
  "max_mcap_usd": 35000,
  "min_gmgn_total_fee_sol": 5,
  "min_holders": 180,
  "min_liquidity_usd": 10000,

  "min_fee_volume_ratio": 0.0015,
  "max_bot_pct": 0.4,
  "trending_max_bundler_rate": 0.15,
  "max_young_wallet_ratio": 0.4,
  "max_young_wallet_combo_ratio": 0.7,
  "max_bundler_combo_rate": 0.15,
  "max_ponyin_red_flags": 1,

  "position_size_sol": 0.05,
  "max_open_positions": 6,
  "tp_percent": 999999,
  "sl_percent": -5.5,

  "profit_lock_enabled": true,
  "profit_lock_tiers": [
    { "trigger": 3, "lock": 0 },
    { "trigger": 6, "lock": 2 },
    { "trigger": 10, "lock": 4 },
    { "trigger": 18, "lock": 9 },
    { "trigger": 35, "lock": 20 },
    { "trigger": 60, "lock": 38 },
    { "trigger": 90, "lock": 60 }
  ],
  "profit_lock_exit_buffer_percent": 8,

  "early_no_follow_enabled": true,
  "early_no_follow_ms": 90000,
  "early_no_follow_peak_pnl_percent": 3,
  "early_no_follow_exit_pnl_percent": -4.5,

  "peak_drop_enabled": true,
  "peak_drop_min_peak_pnl_percent": 12,
  "peak_drop_retrace_percent": 6,

  "recovery_exit_enabled": true,
  "recovery_exit_drawdown_pnl_percent": -8,
  "recovery_exit_recover_to_pnl_percent": -3,
  "recovery_exit_min_recovery_ms": 30000,

  "token_cooldown_ms": 21600000,
  "candidate_label": "candidate_c_sequence_quality_draft"
}
```

Rationale:

- Raises total fee proof from 3 SOL to 5 SOL.
- Raises mcap range to 15k-35k instead of ultra-tight 12k-15k.
- Raises liquidity to 10k.
- Reduces max open positions from 10 to 6 to avoid scatter-gun exposure.
- Keeps 0.05 SOL size.

### Candidate D: safer liquidity mode

Target: slightly later entries, more liquidity, more total-fee proof.

```json
{
  "entry_mode": "immediate",
  "min_source_count": 1,
  "require_fee_claim": false,
  "token_age_max_ms": 3600000,

  "min_mcap_usd": 25000,
  "max_mcap_usd": 60000,
  "min_gmgn_total_fee_sol": 7,
  "min_holders": 250,
  "min_liquidity_usd": 15000,

  "min_fee_volume_ratio": 0.0015,
  "max_bot_pct": 0.4,
  "trending_max_bundler_rate": 0.15,
  "max_young_wallet_ratio": 0.4,
  "max_young_wallet_combo_ratio": 0.7,
  "max_bundler_combo_rate": 0.15,
  "max_ponyin_red_flags": 1,

  "position_size_sol": 0.05,
  "max_open_positions": 5,
  "tp_percent": 999999,
  "sl_percent": -5.5,

  "profit_lock_enabled": true,
  "profit_lock_tiers": [
    { "trigger": 3, "lock": 0 },
    { "trigger": 6, "lock": 2 },
    { "trigger": 10, "lock": 4 },
    { "trigger": 18, "lock": 9 },
    { "trigger": 35, "lock": 20 },
    { "trigger": 60, "lock": 38 },
    { "trigger": 90, "lock": 60 }
  ],
  "profit_lock_exit_buffer_percent": 8,

  "early_no_follow_enabled": true,
  "early_no_follow_ms": 90000,
  "early_no_follow_peak_pnl_percent": 3,
  "early_no_follow_exit_pnl_percent": -4.5,

  "peak_drop_enabled": true,
  "peak_drop_min_peak_pnl_percent": 12,
  "peak_drop_retrace_percent": 6,

  "recovery_exit_enabled": true,
  "recovery_exit_drawdown_pnl_percent": -8,
  "recovery_exit_recover_to_pnl_percent": -3,
  "recovery_exit_min_recovery_ms": 30000,

  "token_cooldown_ms": 21600000,
  "candidate_label": "candidate_d_sequence_liquidity_draft"
}
```

Rationale:

- Later and cleaner than Candidate C.
- More aligned with Sequence's volume confirmation principle.
- Better if Andy wants fewer but higher-quality buys.

## Charon validation plan

Before applying:

```bash
cd /home/ubuntu/charon
sqlite3 charon.sqlite "select id, enabled, config_json from strategies where id in ('candidate_c','candidate_d');"
```

If applying draft to SQLite, create backup first:

```bash
cd /home/ubuntu/charon
cp charon.sqlite charon.sqlite.backup-$(date +%Y%m%d-%H%M%S)
```

After applying:

```bash
cd /home/ubuntu/charon
sqlite3 charon.sqlite "select id, enabled, json_extract(config_json,'$.min_gmgn_total_fee_sol'), json_extract(config_json,'$.min_mcap_usd'), json_extract(config_json,'$.max_mcap_usd'), json_extract(config_json,'$.min_liquidity_usd'), json_extract(config_json,'$.position_size_sol'), json_extract(config_json,'$.candidate_label') from strategies where id in ('candidate_c','candidate_d');"
pm2 restart charon --update-env
pm2 logs charon --lines 120 --nostream
```

Observe sample:

- Do not tune before enough sample closes.
- Minimum useful sample: 30 closed positions per cohort.
- Track win rate, median PnL, tail loss, fee proof at entry, mcap bucket, liquidity bucket, holder bucket.

---

# Risks and tradeoffs

## Meridian risks

- Raising `minTotalFeeSol` to 8 may reduce deploy frequency.
- Lowering user-level `minMcap` from 250k to 150k may allow more volatile pools, but GMGN min mcap and total-fee proof offset this.
- Keeping fee/TVL at 6% may still reject many pools. That is acceptable if rejected pools are below quality threshold.

## Charon risks

- No explicit fee/TVL field visible in strategy config. Approximation via total fee + liquidity + fee/volume may not perfectly enforce Andy's 2% fee/TVL rule.
- Candidate C/D currently disabled. Enabling is separate decision and needs Andy approval.
- Too many open positions on Charon is risky. Draft reduces max open positions but still needs wallet/exposure check.

## Open questions

1. Should Charon get code support for explicit `min_fee_tvl_ratio`?
2. Should Candidate C and Candidate D both run, or only one cohort to keep experiment clean?
3. Should Meridian `minTotalFeeSol: 8` be tested for 24h first before considering 10-15 SOL?
4. Should Charon remain dry-run until 30 closes, or small live 0.05 SOL is acceptable?

---

# Proposed execution order after approval

1. Apply Meridian config patch first.
2. Observe 24h funnel and deploy quality.
3. Prepare Charon SQLite update script separately.
4. If Andy approves Charon experiment, enable one cohort only:
   - Candidate C for more flow.
   - Candidate D for safer quality.
5. Wait for 30 closes before tuning Charon thresholds.

Recommended first move:

```text
Apply Meridian patch first. Do not enable Charon live yet.
```

Reason:

- Meridian is already active and has fee/TVL architecture.
- Charon needs clearer cohort/sample discipline.
- Applying both live at once muddies attribution.
