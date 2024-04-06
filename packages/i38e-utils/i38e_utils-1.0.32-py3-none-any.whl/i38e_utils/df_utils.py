#  Copyright (c) 2023. ISTMO Center S.A.  All Rights Reserved
#
from .log_utils import Logger

logger = Logger(log_dir='./logs/', logger_name=__name__, log_file=f'{__name__}.log')


def load_grouped_activity(df, **kwargs):
    debug = kwargs.pop('debug', False)
    group_by_expr = kwargs.pop('group_by_expr', None)
    if group_by_expr is None:
        raise ValueError('group_by_expr must be specified')
    group_expr = kwargs.pop('group_expr', 'count')
    if group_by_expr is not None:
        if debug:
            logger.info("Grouping by: {}".format(group_by_expr))
        df = df.groupby(by=group_by_expr).size().reset_index(name=group_expr)
    return df


def summarise_data(df, **opts):
    summary_columns = opts.get("summary_column", None)
    if summary_columns is None:
        raise ValueError('summary_column must be specified')
    value_columns = opts.get("values_column", None)
    if value_columns is None:
        raise ValueError('values_column must be specified')
    resample_rule = opts.get("rule", "D")
    agg_func = opts.get("agg_func", 'count')
    df = df.pivot_table(index=df.index, columns=summary_columns, values=value_columns,
                        aggfunc=agg_func).fillna(0)
    df = df.resample(resample_rule).sum()
    return df


def summarize_and_resample_data(df, summary_columns, value_columns, **opts):
    if summary_columns is None:
        raise ValueError('summary_column must be specified')
    if value_columns is None:
        raise ValueError('values_column must be specified')

    resample_rule = opts.get("rule", "D")
    agg_func = opts.get("agg_func", 'count')

    return (df.pivot_table(index=df.index, columns=summary_columns, values=value_columns, aggfunc=agg_func)
            .fillna(0)
            .resample(resample_rule)
            .sum())


def load_latest(df, **kwargs):
    kwargs.update({'duplicate_keep': 'last'})
    return eval_duplicate_removal(df, **kwargs)


def load_earliest(df, **kwargs):
    kwargs.update({'duplicate_keep': 'first'})
    return eval_duplicate_removal(df, **kwargs)


def add_df_totals(df):
    df.loc['Total'] = df.sum(numeric_only=True, axis=0)
    df.loc[:, 'Total'] = df.sum(numeric_only=True, axis=1)
    return df


def eval_duplicate_removal(df, **df_options):
    duplicate_expr = df_options.get('duplicate_expr', None)
    debug = df_options.get('debug', False)
    if duplicate_expr is None:
        return df
    if debug:
        df_duplicates = df[df.duplicated(duplicate_expr)]
        print("Duplicate Rows based on columns are:", df_duplicates, sep='\n')
    sort_field = df_options.get('sort_field', None)
    keep_which = df_options.get('duplicate_keep', 'last')
    if sort_field is None:
        df = df.drop_duplicates(duplicate_expr, keep=keep_which)
    else:
        df = df.sort_values(sort_field).drop_duplicates(duplicate_expr, keep=keep_which)
    return df
