#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This file contains pluggable module for Hawat web interface containing features
related to `IDEA <https://idea.cesnet.cz/en/index>`__ event timeline based
visualisations.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import copy
import datetime
import pytz

import flask
from flask_babel import lazy_gettext

import mentat.stats.idea
import mentat.services.eventstorage
from mentat.const import tr_
from mentat.services.eventstorage import QTYPE_TIMELINE

import hawat.events
import hawat.const
import hawat.acl
import hawat.menu
import hawat.forms
from hawat.base import HawatBlueprint
from hawat.view import BaseSearchView, CustomSearchView
from hawat.view.mixin import HTMLMixin, AJAXMixin
from hawat.utils import URLParamsBuilder
from hawat.base import PsycopgMixin
from hawat.blueprints.timeline.forms import SimpleTimelineSearchForm
from hawat.events import get_after_cleanup

BLUEPRINT_NAME = 'timeline'
"""Name of the blueprint as module global constant."""

AGGREGATIONS = (
    (mentat.stats.idea.ST_SKEY_CNT_EVENTS, {}, {"aggr_set": None}),
    (mentat.stats.idea.ST_SKEY_CATEGORIES, {}, {"aggr_set": "category"}),
    (mentat.stats.idea.ST_SKEY_SOURCES, {}, {"aggr_set": "source_ip"}),
    (mentat.stats.idea.ST_SKEY_TARGETS, {}, {"aggr_set": "target_ip"}),
    (mentat.stats.idea.ST_SKEY_SRCPORTS, {}, {"aggr_set": "source_port"}),
    (mentat.stats.idea.ST_SKEY_TGTPORTS, {}, {"aggr_set": "target_port"}),
    (mentat.stats.idea.ST_SKEY_SRCTYPES, {}, {"aggr_set": "source_type"}),
    (mentat.stats.idea.ST_SKEY_TGTTYPES, {}, {"aggr_set": "target_type"}),
    (mentat.stats.idea.ST_SKEY_PROTOCOLS, {}, {"aggr_set": "protocol"}),
    (mentat.stats.idea.ST_SKEY_DETECTORS, {}, {"aggr_set": "node_name"}),
    (mentat.stats.idea.ST_SKEY_DETECTORTPS, {}, {"aggr_set": "node_type"}),
    (mentat.stats.idea.ST_SKEY_ABUSES, {}, {"aggr_set": "resolvedabuses"}),
    (mentat.stats.idea.ST_SKEY_CLASSES, {}, {"aggr_set": "eventclass"}),
    (mentat.stats.idea.ST_SKEY_SEVERITIES, {}, {"aggr_set": "eventseverity"}),
)


def _get_search_form(request_args=None):
    choices = hawat.events.get_event_form_choices()
    aggrchc = list(
        zip(
            map(lambda x: x[0], AGGREGATIONS),
            map(lambda x: x[0], AGGREGATIONS)
        )
    )
    sectionchc = [(mentat.stats.idea.ST_SKEY_CNT_EVENTS, mentat.stats.idea.ST_SKEY_CNT_EVENTS)] + aggrchc

    form = SimpleTimelineSearchForm(
        request_args,
        meta={'csrf': False},
        choices_source_types=choices['source_types'],
        choices_target_types=choices['target_types'],
        choices_host_types=choices['host_types'],
        choices_detectors=choices['detectors'],
        choices_detector_types=choices['detector_types'],
        choices_categories=choices['categories'],
        choices_severities=choices['severities'],
        choices_classes=choices['classes'],
        choices_protocols=choices['protocols'],
        choices_inspection_errs=choices['inspection_errs'],
        choices_sections=sectionchc,
        choices_aggregations=aggrchc
    )

    # In case no time bounds were set adjust them manually.
    if request_args and not (
            'dt_from' in request_args or 'dt_to' in request_args or 'st_from' in request_args or 'st_to' in request_args):
        form.dt_from.process_data(hawat.forms.default_dt_with_delta())
        form.dt_to.process_data(hawat.forms.default_dt())

    return form


class AbstractSearchView(PsycopgMixin, CustomSearchView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for view responsible for searching `IDEA <https://idea.cesnet.cz/en/index>`__
    event database and presenting the results in timeline-based manner.
    """
    authentication = True

    url_params_unsupported = ('page', 'sortby')

    @classmethod
    def get_view_icon(cls):
        return 'module-{}'.format(cls.module_name)

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext('Search event timeline')

    @classmethod
    def get_menu_title(cls, **kwargs):
        return lazy_gettext('Timeline')

    @staticmethod
    def get_search_form(request_args):
        return _get_search_form(request_args)

    def do_before_search(self, form_data):  # pylint: disable=locally-disabled,unused-argument
        self.response_context.update(
            sqlqueries=[]
        )

        form_data['groups'] = [item.name for item in form_data['groups']]

        # Timestamp timezone mangling magic. Convert everything to UTC naive.
        dt_from = form_data.get('dt_from', None)
        if dt_from:
            dt_from = dt_from.astimezone(pytz.utc)
            dt_from = dt_from.replace(tzinfo=None)
        else:
            dt_from = hawat.forms.default_dt_with_delta()
        dt_to = form_data.get('dt_to', None)
        if dt_to:
            dt_to = dt_to.astimezone(pytz.utc)
            dt_to = dt_to.replace(tzinfo=None)
        else:
            dt_to = datetime.datetime.utcnow()
        form_data['dt_from'] = dt_from
        form_data['dt_to'] = dt_to

        # Determine configurations for timelines.
        timeline_cfg = mentat.stats.idea.calculate_timeline_config(
            form_data['dt_from'],
            form_data['dt_to'],
            flask.current_app.config['HAWAT_CHART_TIMELINE_MAXSTEPS'],
            timezone=pytz.timezone(flask.session.get('timezone', 'UTC'))
        )

        self.response_context.update(
            timeline_cfg=timeline_cfg,
            after_cleanup=get_after_cleanup(form_data['dt_from'])
        )

        # Put calculated parameters together with other search form parameters.
        form_data['dt_from'] = timeline_cfg['dt_from']
        form_data['first_step'] = timeline_cfg['first_step']
        form_data['dt_to'] = timeline_cfg['dt_to']
        form_data['step'] = timeline_cfg['step']

        form_data['timezone'] = flask.session.get('timezone', 'UTC')

    def _search_events_aggr(self, form_args, qtype, aggr_name, enable_toplist=True):
        if self.SEARCH_QUERY_QUOTA_CHECK:
            self._check_search_query_quota()
        self.mark_time(
            '{}_{}'.format(qtype, aggr_name),
            'begin',
            tag='search',
            label='Begin aggregation calculations "{}:{}"'.format(
                qtype,
                aggr_name
            ),
            log=True
        )
        search_result = self.get_db().search_events_aggr(
            form_args,
            qtype=qtype,
            dbtoplist=enable_toplist,
            qname=self.get_qname()
        )
        self.mark_time(
            '{}_{}'.format(qtype, aggr_name),
            'end',
            tag='search',
            label='Finished aggregation calculations "{}:{}" [yield {} row(s)]'.format(
                qtype,
                aggr_name,
                len(search_result)
            ),
            log=True
        )

        self.response_context['sqlqueries'].append(
            self.get_db().cursor.lastquery.decode('utf-8')
        )
        self.response_context['search_result']["{}:{}".format(qtype, aggr_name)] = search_result

    def get_aggregations(self, form_args):
        """
        Returns a list of aggregations which should be calculated
        """
        raise NotImplementedError()

    def custom_search(self, form_args):
        aggregations_to_calculate = self.get_aggregations(form_args)
        self.response_context.update(
            search_result={},  # Raw database query results (rows).
            aggregations=aggregations_to_calculate,  # Note all performed aggregations for further processing.
        )

        # set aggregations to be shown as tabs
        if 'aggregations' in form_args and form_args['aggregations']:
            self.response_context['all_aggregations'] = form_args['aggregations']
        else:
            self.response_context['all_aggregations'] = [a[0] for a in AGGREGATIONS]

        qtype = QTYPE_TIMELINE

        # Perform timeline aggregations and aggregation aggregations for the selected aggregations
        for aggr_name, _, faupdates in AGGREGATIONS:
            if aggr_name in aggregations_to_calculate:
                fargs = copy.deepcopy(form_args)
                fargs.update(faupdates)
                self._search_events_aggr(
                    fargs,
                    qtype,
                    aggr_name,
                    enable_toplist=aggr_name != mentat.stats.idea.ST_SKEY_CNT_EVENTS
                )

    def do_after_search(self, **kwargs):
        self.response_context.update(
            statistics={
                'timeline_cfg': self.response_context['timeline_cfg']
            }
        )

        # Convert raw database rows into dataset structures.
        self.mark_time(
            'result_convert',
            'begin',
            tag='calculate',
            label='Converting result from database rows to statistical dataset',
            log=True
        )

        for aggr_name, *_ in AGGREGATIONS:
            key = "{}:{}".format(QTYPE_TIMELINE, aggr_name)
            if key in self.response_context['search_result']:
                mentat.stats.idea.aggregate_stats_timeline(
                    aggr_name,
                    self.response_context['search_result'][key],
                    self.response_context['statistics']
                )
        self.mark_time(
            'result_convert',
            'end',
            tag='calculate',
            label='Done converting result from database rows to statistical dataset',
            log=True
        )

        self.response_context.update(
            items_count=self.response_context['statistics'].get('cnt_events', 0)
        )
        self.response_context.pop('search_result', None)

    def _get_timeline_search_url(self, section):
        """Returns the search query URL with the provided section set"""
        params = self.response_context['query_params'].copy()
        params['section'] = section
        return flask.url_for(
            '{}.{}'.format(
                BLUEPRINT_NAME,
                APISearchView.get_view_name()
            ),
            **params
        )

    def do_before_response(self, **kwargs):
        self.response_context.update(
            quicksearch_list=self.get_quicksearch_by_time(),
            get_search_url=self._get_timeline_search_url,
        )


class SearchView(HTMLMixin, AbstractSearchView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View responsible for querying `IDEA <https://idea.cesnet.cz/en/index>`__
    event database and presenting the results in the form of HTML page.
    """
    methods = ['GET']

    def get_aggregations(self, form_args):
        if 'aggregations' in form_args and form_args['aggregations']:
            return form_args['aggregations']
        if 'section' in form_args and form_args['section']:
            return [form_args['section']]
        return [mentat.stats.idea.ST_SKEY_CNT_EVENTS]

    @classmethod
    def get_breadcrumbs_menu(cls):
        breadcrumbs_menu = hawat.menu.Menu()
        breadcrumbs_menu.add_entry(
            'endpoint',
            'home',
            endpoint=flask.current_app.config['ENDPOINT_HOME']
        )
        breadcrumbs_menu.add_entry(
            'endpoint',
            'search',
            endpoint='{}.search'.format(cls.module_name)
        )
        return breadcrumbs_menu


class APISearchView(AJAXMixin, AbstractSearchView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View responsible for querying `IDEA <https://idea.cesnet.cz/en/index>`__
    event database and presenting the results in the form of JSON document.
    """
    methods = ['GET', 'POST']

    def get_aggregations(self, form_args):
        if 'aggregations' in form_args and form_args['aggregations']:
            return form_args['aggregations']
        if 'section' in form_args and form_args['section']:
            return [form_args['section']]
        return [a[0] for a in AGGREGATIONS]

    def get_blocked_response_context_keys(self):
        return super().get_blocked_response_context_keys() + [
            'get_search_url',
            'all_aggregations'
        ]

    @classmethod
    def get_view_name(cls):
        return 'apisearch'


# -------------------------------------------------------------------------------


class AbstractLegacySearchView(PsycopgMixin, BaseSearchView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for view responsible for searching `IDEA <https://idea.cesnet.cz/en/index>`__
    event database and presenting the results in timeline-based manner.
    """
    authentication = True

    url_params_unsupported = ('page', 'limit', 'sortby')

    @classmethod
    def get_view_icon(cls):
        return 'module-{}'.format(cls.module_name)

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext('Search event timeline')

    @classmethod
    def get_menu_title(cls, **kwargs):
        return lazy_gettext('Timeline')

    @staticmethod
    def get_search_form(request_args):
        return _get_search_form(request_args)

    def do_before_search(self, form_data):  # pylint: disable=locally-disabled,unused-argument
        form_data['groups'] = [item.name for item in form_data['groups']]

    def do_after_search(self, items):
        self.logger.debug(
            "Calculating IDEA event timeline from %d records.",
            len(items)
        )
        if items:
            dt_from = self.response_context['form_data'].get('dt_from', None)
            if dt_from:
                dt_from = dt_from.astimezone(pytz.utc)
                dt_from = dt_from.replace(tzinfo=None)
            dt_to = self.response_context['form_data'].get('dt_to', None)
            if dt_to:
                dt_to = dt_to.astimezone(pytz.utc)
                dt_to = dt_to.replace(tzinfo=None)
            if not dt_from and items:
                dt_from = self.get_db().search_column_with('detecttime')
            if not dt_to and items:
                dt_to = datetime.datetime.utcnow()
            self.response_context.update(
                statistics=mentat.stats.idea.evaluate_timeline_events(
                    items,
                    dt_from=dt_from,
                    dt_to=dt_to,
                    max_count=flask.current_app.config['HAWAT_CHART_TIMELINE_MAXSTEPS'],
                    timezone=pytz.timezone(flask.session.get('timezone', 'UTC'))
                )
            )
            self.response_context.pop('items', None)

    def do_before_response(self, **kwargs):
        self.response_context.update(
            quicksearch_list=self.get_quicksearch_by_time()
        )

    @staticmethod
    def get_qtype():
        """
        Get type of the event select query.
        """
        return mentat.services.eventstorage.QTYPE_SELECT_GHOST


class APILegacySearchView(AJAXMixin, AbstractSearchView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View responsible for querying `IDEA <https://idea.cesnet.cz/en/index>`__
    event database and presenting the results in the form of JSON document.

    *Deprecated legacy implementation, kept only for the purposes of comparison.*
    """
    methods = ['GET', 'POST']

    @classmethod
    def get_view_name(cls):
        return 'apilegacysearch'


# -------------------------------------------------------------------------------


class TimelineBlueprint(HawatBlueprint):
    """Pluggable module - IDEA event timelines (*timeline*)."""

    @classmethod
    def get_module_title(cls):
        return lazy_gettext('<a href="https://idea.cesnet.cz/en/index">IDEA</a> event timelines')

    def register_app(self, app):
        app.menu_main.add_entry(
            'view',
            BLUEPRINT_NAME,
            position=150,
            view=SearchView,
            resptitle=True
        )

        # Register context actions provided by this module.
        app.set_csag(
            hawat.const.CSAG_ADDRESS,
            tr_('Search for source <strong>%(name)s</strong> on IDEA event timeline'),
            SearchView,
            URLParamsBuilder({'submit': tr_('Search')}).add_rule('source_addrs', True).add_kwrule('dt_from', False,
                                                                                                  True).add_kwrule(
                'dt_to', False, True)
        )


# -------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface for :py:mod:`hawat.Hawat` and factory function. This function
    must return a valid instance of :py:class:`hawat.app.HawatBlueprint` or
    :py:class:`flask.Blueprint`.
    """

    hbp = TimelineBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder='templates'
    )

    hbp.register_view_class(SearchView, '/{}/search'.format(BLUEPRINT_NAME))
    hbp.register_view_class(APISearchView, '/api/{}/search'.format(BLUEPRINT_NAME))
    hbp.register_view_class(APILegacySearchView, '/api/{}/legacysearch'.format(BLUEPRINT_NAME))

    return hbp
