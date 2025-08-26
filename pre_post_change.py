import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- load ---
event_df = pd.read_parquet('./data/treatment_event_study.parquet')
control_df = pd.read_parquet('./data/control_event_study.parquet')

# --- clean ---
for df in (event_df, control_df):
    df['relative_week'] = pd.to_numeric(df['relative_week'], errors='coerce')
    if df['percent_change'].dtype == object:
        df['percent_change'] = (df['percent_change'].astype(str)
                                .str.replace('%','', regex=False).str.strip())
    df['percent_change'] = pd.to_numeric(df['percent_change'], errors='coerce')
    df.loc[~np.isfinite(df['percent_change']), 'percent_change'] = np.nan  # drop ±inf

def summarize(df):
    g = (df.groupby('relative_week', as_index=False)['percent_change']
           .agg(mean_percent='mean', std_percent='std', count='count'))
    g['se'] = g['std_percent'] / np.sqrt(g['count'])
    g['ci_lower'] = g['mean_percent'] - 1.96 * g['se']
    g['ci_upper'] = g['mean_percent'] + 1.96 * g['se']
    return g.sort_values('relative_week')

treat = summarize(event_df)
ctrl  = summarize(control_df)

# x-axis ticks (ensure -4,-3,-2 show if present)
all_weeks = np.unique(np.concatenate([treat['relative_week'].to_numpy(),
                                      ctrl['relative_week'].to_numpy()]))

# --- plot ---
fig, ax = plt.subplots(figsize=(10, 8))

ax.plot(treat['relative_week'], treat['mean_percent'],
        marker='o', linestyle='-', linewidth=2,
        label=f'Repurposed Accounts (Treatment) (n={event_df["channel_id"].nunique()})')
ax.fill_between(treat['relative_week'], treat['ci_lower'], treat['ci_upper'], alpha=0.2)

ax.plot(ctrl['relative_week'], ctrl['mean_percent'],
        marker='s', linestyle='-', linewidth=2,
        label=f'Non-Repurposed Accounts (Control) (n={control_df["channel_id"].nunique()})')
ax.fill_between(ctrl['relative_week'], ctrl['ci_lower'], ctrl['ci_upper'], alpha=0.2)

ax.axvline(x=0, color='red', linestyle='--', alpha=0.7, label='Repurposing Event (Only Affects Repurposed Accounts)')
ax.axhline(y=0, color='gray', linestyle='-', alpha=0.5)

ax.set_xlim(all_weeks.min(), all_weeks.max())
ax.set_xticks(all_weeks)
ax.set_xlabel('Weeks Relative to Repurposing Event', fontsize=16)
ax.set_ylabel('Subscriber Growth (%)', fontsize=16)
ax.tick_params(axis='both', which='major', labelsize=16)
ax.set_title('', pad=12)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.1f}%'))
ax.grid(True, linestyle='--', alpha=0.7)
ax.legend(frameon=True, framealpha=0.9, fontsize=16, markerscale=1.5)

plt.savefig('./output/pre_post_change.pdf', format='pdf', bbox_inches='tight')
plt.tight_layout()
plt.show()
