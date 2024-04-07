#  Copyright (c) 2023. ISTMO Center S.A.  All Rights Reserved
#
#

import django

from django.core.paginator import Paginator
import pandas as pd

from .utils import update_with_verbose, get_related_model, object_to_dict, is_values_queryset

FieldDoesNotExist = (
    django.db.models.fields.FieldDoesNotExist
    if django.VERSION < (1, 8)
    else django.core.exceptions.FieldDoesNotExist
)


def to_fields(qs, fieldnames):
    """
    Get fields from a queryset based on the given fieldnames.

    :param qs: The queryset from which to extract fields.
    :param fieldnames: A list of fieldnames to extract.
    :return: An iterator that yields the corresponding fields from the queryset.
    """
    for fieldname in fieldnames:
        model = qs.model
        for fieldname_part in fieldname.split('__'):
            try:
                field = model._meta.get_field(fieldname_part)
            except FieldDoesNotExist:
                try:
                    rels = model._meta.get_all_related_objects_with_model()
                except AttributeError:
                    field = fieldname
                else:
                    for relobj, _ in rels:
                        if relobj.get_accessor_name() == fieldname_part:
                            field = relobj.field
                            model = field.model
                            break
            else:
                model = get_related_model(field)
        yield field


def read_frame(qs, fieldnames=(), index_col=None, coerce_float=False,
               verbose=True, datetime_index=False, column_names=None):
    """
        Read a DataFrame from a queryset or list of objects.

        :param qs: The queryset or list of objects.
        :param fieldnames: The field names to include in the DataFrame. If not provided, all fields will be included.
        :param index_col: The name of the column to use as the index in the DataFrame.
        :param coerce_float: Whether to coerce all values to floats.
        :param verbose: Whether to print verbose output during the process.
        :param datetime_index: Whether to convert the index column to datetime if it contains datetime values.
        :param column_names: The names of the columns in the DataFrame. If not provided, the field names will be used.
        :return: The DataFrame.

        .. note::
            - If `fieldnames` is provided, only the specified fields will be included in the DataFrame.
            - If `index_col` is provided, the specified column will be used as the index in the DataFrame.
            - If `coerce_float` is True, all values will be coerced to floats.
            - If `verbose` is True, verbose output will be printed during the process.
            - If `datetime_index` is True, the index column will be converted to datetime if it contains datetime values.
            - If `column_names` is provided, the specified names will be used as column names in the DataFrame.
    """

    if fieldnames:
        fieldnames = pd.unique(fieldnames)
        if index_col is not None and index_col not in fieldnames:
            # Add it to the field names if not already there
            fieldnames = tuple(fieldnames) + (index_col,)
            if column_names:
                column_names = tuple(column_names) + (index_col,)
        fields = to_fields(qs, fieldnames)
    elif is_values_queryset(qs):
        # if django.VERSION < (1, 9):  # pragma: no cover
        #     annotation_field_names = list(qs.query.annotation_select)
        #
        #     if annotation_field_names is None:
        #         annotation_field_names = []
        #
        #     extra_field_names = qs.extra_names
        #     if extra_field_names is None:
        #         extra_field_names = []
        #
        #     select_field_names = qs.field_names
        #
        # else:  # pragma: no cover
        annotation_field_names = list(qs.query.annotation_select)
        extra_field_names = list(qs.query.extra_select)
        select_field_names = list(qs.query.values_select)

        fieldnames = select_field_names + annotation_field_names + \
                     extra_field_names
        fields = [None if '__' in f else qs.model._meta.get_field(f)
                  for f in select_field_names] + \
                 [None] * (len(annotation_field_names) + len(extra_field_names))

        uniq_fields = set()
        fieldnames, fields = zip(
            *(f for f in zip(fieldnames, fields)
              if f[0] not in uniq_fields and not uniq_fields.add(f[0])))
    else:
        try:
            fields = qs.model._meta.fields
            fieldnames = [f.name for f in fields]
            fieldnames += list(qs.query.annotation_select.keys())
        except:
            pass

    if is_values_queryset(qs):
        recs = list(qs)
    else:
        try:
            recs = list(qs.values_list(*fieldnames))
            # recs = list(qs.values_list(*fieldnames).iterator())
        except:
            if fieldnames:
                recs = [object_to_dict(q, fieldnames) for q in qs]
                # recs = [object_to_dict(q, fieldnames) for q in qs.iterator()]
            else:
                recs = [object_to_dict(q) for q in qs]
                # recs = [object_to_dict(q) for q in qs.iterator()]

    df = pd.DataFrame.from_records(
        recs,
        columns=column_names if column_names else fieldnames,
        coerce_float=coerce_float
    )

    if verbose:
        update_with_verbose(df, fieldnames, fields)

    if index_col is not None:
        df.set_index(index_col, inplace=True)

    if datetime_index:
        df.index = pd.to_datetime(df.index, errors="ignore")
    return df
