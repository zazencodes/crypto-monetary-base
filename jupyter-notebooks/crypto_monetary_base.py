import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import datetime

def datetime_supply_curve(
    start_date,
    block_time,
    block_supply,
    ):
    df = pd.DataFrame(
        block_supply, columns=['block', 'total_supply']
    )
    df['total_supply_pct'] = (
        df['total_supply'] / df['total_supply'].values[-1]
        * 100
    )
    df['date'] = pd.date_range(
        start=start_date,
        freq=block_time,
        periods=len(df)
    )
    return df

def datetime_constant_supply_curve(
    start_date,
    num_weeks,
    supply_amount,
    pct_distributed
    ):
    supply = [supply_amount] * num_weeks
    
    df = pd.DataFrame(
        supply, columns=['total_supply']
    )
    df['distributed_supply'] = df.total_supply * pct_distributed
    
    df['total_supply_pct'] = (
        df['total_supply'] / df['total_supply'].values[-1]
        * 100
    )
    df['distributed_supply_pct'] = [pct_distributed*100] * num_weeks
    df['date'] = pd.date_range(
        start=start_date,
        freq='W',
        periods=len(df)
    )
    return df

def plot_supply_curve(
    supply,
    coin_name,
    plot_pct=True,
    max_size=10000,
    fmt='-',
    out_name='',
    ylim=None,
    ):
    max_size = min((max_size, len(supply)))
    step_size = int(len(supply) / max_size)
    dates = mpl.dates.date2num(supply.date.values[::step_size])
    if plot_pct:
        values = supply.total_supply_pct.values[::step_size]
    else:
        values = supply.total_supply.values[::step_size]
    plt.plot_date(
        dates,
        values,
        fmt=fmt,
        lw=4,
        label='distributed supply',
    )
    
    # Plot current date
    mask = supply.date > datetime.datetime.now()
    current_supply = supply[mask].iloc[0]
    dates = mpl.dates.date2num([current_supply.date])
    if plot_pct:
        values = [current_supply.total_supply_pct]
    else:
        values = [current_supply.total_supply]
    plt.plot(
        dates,
        values,
        'o',
        color='black',
        ms=6,
        label=current_supply.date.strftime('%Y'),
    )
    if ylim is not None:
        plt.ylim(*ylim)
    
    plt.title(
        r'$\textbf{{{}}}$ Monetary Base'.format(coin_name),
        y=1.05
    )
    plt.legend(loc='lower right')
    ax = plt.gca()
    if plot_pct:
        ax.yaxis.set_major_formatter(mpl.ticker.PercentFormatter())
    
    if not out_name:
        out_name = coin_name
    plt.savefig(
        '../charts/{}.png'.format(out_name),
        bbox_inches='tight',
        dpi=300
    )
    return plt


def plot_constant_supply_curve(
    supply,
    coin_name,
    plot_pct=True,
    max_size=10000,
    out_name='',
    ylim=None,
    ):
    max_size = min((max_size, len(supply)))
    step_size = int(len(supply) / max_size)
    dates = mpl.dates.date2num(supply.date.values[::step_size])
    
    # Plot total supply
    if plot_pct:
        values = supply.total_supply_pct.values[::step_size]
    else:
        values = supply.total_supply.values[::step_size]
    plt.plot_date(
        dates,
        values,
        fmt='-',
        lw=4,
        label='total supply',
    )
    
    # Plot distributed supply
    if plot_pct:
        values = supply.distributed_supply_pct.values[::step_size]
    else:
        values = supply.distributed_supply.values[::step_size]
    plt.plot_date(
        dates,
        values,
        fmt='--',
        lw=4,
        label='distributed supply ({})'.format(
            datetime.datetime.now().strftime('%b %Y')
        ),
    )
    
    # Plot current date
    mask = supply.date > datetime.datetime.now()
    current_supply = supply[mask].iloc[0]
    dates = mpl.dates.date2num([current_supply.date])
    if plot_pct:
        values = [current_supply.distributed_supply_pct]
    else:
        values = [current_supply.distributed_supply]
    plt.plot(
        dates,
        values,
        'o',
        color='black',
        ms=6,
        label=current_supply.date.strftime('%Y'),
    )
    if ylim is not None:
        plt.ylim(*ylim)
    
    plt.title(
        r'$\textbf{{{}}}$ Monetary Base'.format(coin_name),
        y=1.05
    )
    plt.legend(loc='lower right')
    ax = plt.gca()
    if plot_pct:
        ax.yaxis.set_major_formatter(mpl.ticker.PercentFormatter())
    
    if not out_name:
        out_name = coin_name
    plt.savefig(
        '../charts/{}.png'.format(out_name),
        bbox_inches='tight',
        dpi=300
    )
    return plt

def transform_supply(supply, coin, freq):
    df = supply.copy()
    df.set_index('date')
    # Group by datetime
    if freq == 'weekly':
        _freq = 'W'
    elif freq == 'monthly':
        _freq = 'M'
    elif freq == 'yearly':
        _freq = 'Y'
    else:
        raise ValueError('Cannot handle freq={}'.format(freq))
    df_transformed = (df.groupby(pd.Grouper(key='date', freq=_freq))
                        .head(1)
                        .reset_index(drop=True))
    df_transformed = pd.concat(
        (pd.Series([coin]*len(df_transformed), name='coin'), df_transformed),
        axis=1
    )
    df_transformed['date'] = (df_transformed
        .date.apply(lambda x: x.replace(day=1))
        .dt.date
    )
    f_name = '../output-data/{}_{}.csv'.format(coin, freq)
    df_transformed.to_csv(f_name, index=False)
    print('Wrote {} lines to file {}'.format(len(df_transformed), f_name))
    return df_transformed


