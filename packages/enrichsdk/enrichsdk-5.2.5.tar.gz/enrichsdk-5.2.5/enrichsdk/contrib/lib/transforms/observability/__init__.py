import os
import json
import numpy as np
import pandas as pd
import time
import random
import sqlite3
import tempfile
import hashlib
import shutil
from enrichsdk import Compute, S3Mixin
from datetime import datetime, timedelta, date
import logging
import unidecode
from collections import defaultdict
from sqlalchemy import create_engine, text as satext

from enrichsdk.contrib.lib.transforms import note
from enrichsdk.contrib.lib.assets import profilespec
from enrichsdk.lib.integration import send_html_email

logger = logging.getLogger("app")


class DataObserverBase(Compute):
    """
    Monitor an input data source given a spec

    Features of transform baseclass include:
        * Flexible configuration
        * Highlevel specification of observability:
            * specified data source
            * custom defined testing conditions for observability
            * custom defined output of observability results
            * notification of observability results on success/failure
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "DataObserverBase"
        self.description = "Monitor an input data source given a spec"
        self.testdata = {
            "data_root": os.path.join(os.environ["ENRICH_TEST"], self.name),
            "statedir": os.path.join(os.environ["ENRICH_TEST"], self.name, "state"),
            "conf": {"args": {}},
            "data": {},
        }

    @classmethod
    def instantiable(cls):
        return False

    def get_handlers(self, spec):
        """
        Define various callbacks that take a dataframe, spec
        and compute.
        """
        return {}

    ###########################################
    # Check method for observability
    ###########################################
    def process_spec(self, spec, data):

        if data is None:
            msg = "No dataset loaded" + "\n"
            logger.exception(
                f"Spec: {spec['name']} -- skipping",
                extra={"transform": self.name}
            )
            return None

        name = spec['name']
        config = spec['config']
        checks = config['checks']

        results = []
        checks_done = []
        checked_at = datetime.now()

        run_id = f"{name}-{checked_at}"
        run_id = hashlib.md5(run_id.encode('utf-8')).hexdigest()

        # check if checks object is a list
        if not isinstance(checks, list):
            logger.exception(
                f"Invalid config param -- check", extra={"transform": self.name, "data": json.dumps(config, indent=4)}
            )
            return None

        # for each observability check
        for check in checks:
            do_check = True

            for f in ['name', 'method']:
                if f not in check:
                    logger.exception(
                        f"Invalid config param -- check", extra={"transform": self.name, "data": json.dumps(config, indent=4)}
                    )
                    do_check = False
                    break
            if do_check is False:
                continue

            if not hasattr(self, check['method']):
                logger.exception(
                    f"No method defined -- skipping check", extra={"transform": self.name, "data": json.dumps(check, indent=4)}
                )
                continue

            # we now have the callback
            callback = getattr(self, check['method'])
            result = callback(data)

            # add additional columns of interest
            result['run_id'] = run_id
            result['spec'] = name
            result['check'] = check['name']
            result['checked_at'] = checked_at
            result['status'] = 'fail' if result['status'] is False else 'pass'

            # add this check to the list of completed checks
            checks_done.append(check['name'])

            # add result to master list
            results.append(result)

        # convert the list into a DF
        results = pd.DataFrame(results)

        msg = f"Total {len(checks_done)} checks done: {checks_done}" + "\n"
        msg += note(results, "Check results")
        logger.debug(
            f"Processed checks: {spec['name']}",
            extra={"transform": self.name, "data": msg}
        )

        # if no checks were possible, return None so further pipelined steps are not done
        results = None if len(results) == 0 else results

        return results


    ###########################################
    # Helper Functions
    ###########################################

    def update_frame(self, source, description, df, lineage=None):
        if isinstance(source, str):
            name = source
        else:
            name = source["name"]

        params = self.get_column_params(name, df)
        if lineage is not None:
            if isinstance(lineage, dict):
                params.append(lineage)
            else:
                params.extend(lineage)

        detail = {
            "name": name,
            "df": df,
            "frametype": "pandas",
            "description": description,
            "params": params,
            "transform": self.name,
            "history": [],
        }

        self.state.update_frame(name, detail)

    ###########################################
    # I/O Functions
    ###########################################

    def read_s3_data(self, filename, params, **kwargs):
        # assume we have a resolved s3fs object
        s3 = self.args['s3']
        if s3.exists(filename):
            df = pd.read_csv(s3.open(filename), **params)
            return df
        return None

    def get_dataset_s3(self, spec):
        """
        Use the dataset object to read the dataset
        """
        run_date    = self.args['run_date']
        name        = spec["name"]
        config      = spec['config']
        source      = config['source']

        for f in ["dataset", "filename"]:
            if f not in source:
                msg = f"{f} param needed in config source" + "\n"
                logger.exception(
                    f"Dataset: {name} -- skipping", extra={"transform": self.name, "data": msg}
                )
                return None

        dataset_type    = source['type']
        dataset         = source['dataset']
        pieces          = dataset.split('-')
        dataset_main    = "-".join(pieces[:-1])
        dataset_subset  = pieces[-1]
        filename        = source["filename"]
        params          = source.get("params", {})

        cache = self.args.get("cache", False)
        cachename = f"{dataset}-{run_date}"
        cachefile = f"cache/{self.name}-anonymizer-cache-" + cachename + ".csv"

        if cache:
            try:
                os.makedirs(os.path.dirname(cachefile))
            except:
                pass
            if os.path.exists(cachefile):
                msg = f"Location: {cachefile}" + "\n"
                df = pd.read_csv(cachefile, **params)
                msg += note(df, f"Cached {dataset}") + "\n"
                logger.debug(f"Read cached {name}", extra={"transform": self.name, "data": msg})
                return df

        if dataset_type == "registry":
            if not hasattr(self, "get_dataset"):
                raise Exception(
                    "get_dataset_s3 expects get_dataset method"
                )
            datasetobj = self.get_dataset(dataset_main) # this method should be defined in the derived class

            if hasattr(self, 'update_doodle'):
                self.update_doodle(datasetobj, source['filename'])

            df, metadata = datasetobj.read_data(
                run_date,
                run_date,
                filename=filename,
                readfunc=self.read_s3_data,
                params=params,
            )
        elif dataset_type == "direct":
            df = self.read_s3_data(filename, params)
            metadata = { "files": [filename] }
        else:
            logger.exception(
                f"Unknown source param: {dataset_type}, skipping", extra={"transform": self.name, "data": json.dumps(spec, indent=4)}
            )
            return None

        msg = note(df, f"Fresh {dataset}") + "\n"
        logger.debug(f"Read fresh {name}", extra={"transform": self.name, "data": msg})

        # Cache it for future use...
        if cache:
            df.to_csv(cachefile, index=False)

        # Insert lineage if possible
        lineage = None
        if ("files" in metadata) and (len(metadata["files"]) > 0):
            lineage = {
                "type": "lineage",
                "transform": self.name,
                "dependencies": [
                    {
                        "type": "file",
                        "nature": "input",
                        "objects": [metadata["files"][-1]],
                    },
                ],
            }

        if not self.state.has_frame(spec['name']):
            self.update_frame(spec, f"Dataset: {dataset}", df, lineage)

        return df


    def get_dataset_db(self, spec):
        name = spec['name']
        config = spec['config']
        source = config['source']

        testmode = self.args.get('testmode', False)
        env      = 'test' if testmode else 'prod'

        # Get the db engine
        engine_name = source['params'][env]['engine']
        engine = self.engines[engine_name]

        # Get the query
        query = source['params'][env]['query']
        if query.endswith('.sql'):
            # we have a file containing the query
            sqlfile = os.path.join(self.scriptdir, query)
            query = open(sqlfile).read()

        df = self.read_db_source(engine, query)

        # Now the input load...
        lineage = {
            "type": "lineage",
            "transform": self.name,
            "dependencies": [
                {
                    "type": "database",
                    "nature": "input",
                    "objects": [source['dataset']],
                },
            ],
        }

        self.update_frame(spec, f"Dataset: {name}", df, lineage)

        return df

    def read_db_source(self, engine, query):

        # Run the query
        attempt = 0
        while attempt < 3:
            attempt += 1
            try:
                df = pd.read_sql_query(satext(query), con=engine)
                return df
            except:
                logger.exception(f"Failed query: try {attempt}")
                time.sleep(30) # sleep for 10 secs

        raise Exception("Failed to read DB")


    def load_dataset(self, spec, datasets):

        name        = spec['name']
        generate    = spec.get('generate')
        config      = spec['config']
        source      = config['source']
        dataset     = source['dataset']
        dataset_type = source.get('type')

        if dataset_type == None:
            msg = f"Spec name: name" + "\n"
            msg += f"Config: {json.dumps(config, indent=4)}" + "\n"
            logger.exception(f"Unknown dataset type, skipping", extra={"transform": self.name, "data": msg})
            return None

        # get the dataset nature
        nature = source.get('nature')
        if dataset_type == "direct":
            if nature == None:
                msg = f"Spec name: name" + "\n"
                msg += f"Config: {json.dumps(config, indent=4)}" + "\n"
                logger.exception(f"Unknown dataset nature, skipping", extra={"transform": self.name, "data": msg})
                return None
        elif dataset_type == "registry":
            paths = datasets[dataset].paths
            for path in paths:
                if path['name'] == 'default':
                    nature = path['nature']
                    break
        elif dataset_type == "db":
            nature = "db"
        else:
            msg = f"Spec name: name" + "\n"
            msg += f"Config: {json.dumps(config, indent=4)}" + "\n"
            logger.exception(f"Unknown dataset type, skipping", extra={"transform": self.name, "data": msg})
            return None


        try:
            if nature == "db":
                data = self.get_dataset_db(spec)
            elif nature == "s3":
                data = self.get_dataset_s3(spec)
            elif (
                (generate is not None)
                and (generate in handlers)
                and (callable(handlers[generate]))
            ):
                data = handlers[generate](spec)
            elif (generate is not None) and (hasattr(self, generate)):
                data = getattr(self, generate)(spec)
            else:
                raise Exception(f"Dataset: {name} -- Invalid specification")
        except:
            msg =  "Could not load data, either nature or handlers not valid" + "\n"
            logger.exception(
                f"Dataset: {name} -- Generation failed", extra={"transform": self.name, "data": msg}
            )
            raise Exception(msg)

        msg = note(data, f"Dataset: {name}")
        logger.debug(
            f"Loaded dataset: {name}", extra={"transform": self.name, "data": msg}
        )

        return data

    def s3_store_result(self, spec, data):
        name        = spec['name']
        run_date    = self.args['run_date']
        s3          = self.args['s3']
        epoch       = time.time()

        # add additional columns
        data["__run_date__"] = run_date

        # where are we storing it?
        file = os.path.join(self.args['s3root'], f"{run_date}/{epoch}__{name}.csv")

        # write to s3
        with s3.open(file, 'w') as fd:
            data.to_csv(fd, index=False)

        msg = f"s3 location: {file}" + "\n"

        logger.debug(f"Wrote check results to S3",
                        extra={"transform": self.name,
                                "data": msg})

    def db_store_result(self, spec, results, data):
        name    = spec['name']
        config  = spec['config']
        store   = config['store']

        testmode = self.args.get('testmode', False)
        env      = 'test' if testmode else 'prod'

        # Get the db engine
        engine_name = store['params'][env]['engine']
        engine = self.engines[engine_name]

        # write results to db
        table_name = store['params'][env]['table']
        ret = results.to_sql(table_name,
                            engine,
                            if_exists='append',
                            index=False)
        # write data to db
        data_table_name = name.replace('-','_')
        ret = data.to_sql(data_table_name,
                            engine,
                            if_exists='append',
                            index=False)

        msg = f"DB engine: {engine}" + "\n"

        logger.debug(f"Wrote monitor results to DB",
                        extra={"transform": self.name,
                                "data": msg})

    def store_result(self, spec, results, data):
        name    = spec['name']
        config  = spec['config']
        store   = config['store']

        for f in ["sink", "params"]:
            if f not in store:
                logger.exception(
                    f"Store has no {f} param, skipping.",
                    extra={"transform": self.name, "data": json.dumps(spec, indent=4)}
                )
                return

        run_id = results['run_id'].values[0]
        data['run_id'] = run_id

        sink = store['sink']
        if sink == "s3":
            # store in s3
            self.s3_store_result(spec, results, data)
        elif sink == "db":
            # store in db
            self.db_store_result(spec, results, data)
        else:
            logger.exception(f"Unknown store for dataset: {name}",
                         extra={
                             'transform': self.name
                         })

    ###########################################
    # Notification Functions
    ###########################################

    def check_notify_default(self, notify_set, notify_obj, spec, results):
        # default method to check if a notification needs to be sent
        name    = spec['name']
        config  = spec['config']
        store   = config['store']

        sink        = store['sink']
        channel     = notify_set['channel']
        notifier    = notify_set['name']
        send_on     = notify_set.get('send_on', 'fail')
        freq        = notify_set.get('freq', 'always')
        set_id      = notify_obj.get('set_id', '__ALL__')

        check_name      = results['check'].values[0]
        check_status    = results['status'].values[0]

        do_notify   = False

        # set time between notifications
        if freq == 'always':
            hours_between_notifications = 0
        else:
            try:
                hours_between_notifications = float(freq)
            except:
                # invalid notification frequency in spec
                msg = f"Spec: {name}" + "\n"
                msg += f"Target: {notify_set}" + "\n"
                msg += f"Defaulting to 1 hour" + "\n"
                logger.exception(f"Invalid notification frequency",
                             extra={
                                 'transform': self.name,
                                 'data': msg
                             })
                hours_between_notifications = 6

        # setup the send_on list
        send_on = ["pass", "fail"] if send_on=='both' else [send_on]

        msg = f"Channel: {channel}" + "\n"
        msg += f"Frequency: {freq}" + "\n"
        msg += f"Hours betwwen: {hours_between_notifications}" + "\n"
        msg += f"Send on: {send_on}" + "\n"
        logger.debug(f"Got notification params",
                     extra={
                         'transform': self.name,
                         'data': msg
                     })

        msg = ""
        if sink == "s3":
            # get result+notification data from s3
            pass
        elif sink == "db":
            # get result+notification data from db
            # get the environment we are in
            testmode = self.args.get('testmode', False)
            env      = 'test' if testmode else 'prod'
            # Get the db engine
            engine_name = store['params'][env]['engine']
            engine = self.engines[engine_name]
            table_name = store['params'][env]['table']
            # get the latest notification sent for this spec and notification channel
            query = f"""SELECT *
                        FROM {table_name}
                        WHERE `spec`='{name}'
                            AND `check`='{check_name}'
                            AND `set_id`='{set_id}'
                            AND `notifier`='{channel}'
                            AND `notified`=1
                        ORDER BY `notified_at` DESC
                        LIMIT 1
                        """
            msg += f"Engine: {engine}" + "\n"
            msg += f"Query: {query}" + "\n"
            try:
                df = self.read_db_source(engine, query)
            except:
                # empty dataframe
                msg += f"Failed reading DB, defaulting to empty DF" + "\n"
                df = pd.DataFrame()
        else:
            logger.exception(f"Unknown store for {name}",
                         extra={
                             'transform': self.name,
                             'data': json.dumps(store, indent=4)
                         })
            return False

        msg += note(df, "Last notification DF") + "\n"
        msg += f"check_status={check_status}, send_on={send_on}" + "\n"
        logger.debug(f"Last notification status",
                     extra={
                         'transform': self.name,
                         'data': msg
                     })

        if len(df) > 0:
            # find time between last notification and now
            last_notified_at = pd.Timestamp(df['notified_at'].values[0])
            time_elapsed = (datetime.now() - last_notified_at).total_seconds() / (60*60) # convert to hours
            # check if time elapsed since last notification is more than spec
            if time_elapsed > hours_between_notifications and check_status in send_on:
                do_notify = True
        else:
            if check_status in send_on:
                do_notify = True

        return do_notify

    def notify_via_slack(self, target, spec):
        # trivial notification method to simulate
        # notification by slack
        return True

    def notify_via_email(self, notify_obj, spec):
        # notification via email
        name        = spec['name']
        receivers   = notify_obj['receivers']
        bcc         = notify_obj.get('bcc', [])
        cc         = notify_obj.get('cc', [])
        reply_to    = notify_obj.get('reply_to', [])
        content     = notify_obj.get('content')
        subject     = notify_obj.get('subject')
        sender      = notify_obj.get('sender')
        smtpcred    = notify_obj.get('smtpcred', {})
        retries     = notify_obj.get('retries', 1)
        data        = notify_obj['data']
        send_attachment = notify_obj.get('send_attachment', False)
        notify_success  = False

        # create the content if not available
        if content == None:
            content = f"Ran ledger balance checks, data attached"
        # create the subject if not available
        if subject == None:
            content = f"[{self.args['run_date']}] Ledger Balance Alert"

        # write the result to tmp
        try:
            msg = ""
            tmpdir = tempfile.mkdtemp()
            fname = os.path.join(tmpdir, f'LEDGER-BALANCE-CHECK_{name}.csv')
            data.to_csv(fname, index=False)

            if send_attachment:
                attachments = [fname]
            else:
                attachments = []

            # send the email
            try:
                notify_success = True
                msg = f"Spec: {name}" + "\n"
                msg += f"Retries: {retries}\n"
                msg += f"Sender: {sender}" + "\n"
                msg += f"Receivers: {receivers}" + "\n"
                msg += f"Reply-To: {reply_to}" + "\n"
                msg += f"CC: {cc}" + "\n"
                msg += f"BCC: {bcc}" + "\n"
                msg += f"Subject: {subject}" + "\n"
                msg += f"Content: {content}" + "\n"

                send_html_email(content=content,
                                sender=sender,
                                receivers=receivers,
                                cc=cc,
                                bcc=bcc,
                                reply_to=reply_to,
                                subject=subject,
                                attachments=attachments,
                                cred=smtpcred,
                                retries=retries)
                logger.debug(
                    f"Sent notifications",
                    extra={"transform": self.name, "data": msg}
                )
            except:
                logger.exception(
                    f"Error sending email",
                    extra={"transform": self.name, "data": msg}
                )
        except:
            logger.exception(
                f"Error sending email",
                extra={"transform": self.name, "data": msg}
            )

        if os.path.exists(tmpdir):
            try:
                shutil.rmtree(tmpdir)
            except:
                logger.exception(
                    f"Unable to cleanup tmpdir",
                    extra={"transform": self.name, 'data': tmpdir}
                )

        return notify_success


    def notify_target_common(self, notify_obj, spec):
        # common notification handler
        notify_channel = notify_obj['channel']
        notify_success = False

        if notify_channel == 'email':
            notify_success = self.notify_via_email(notify_obj, spec)
        elif notify_channel == 'slack':
            # send the slack notification
            notify_success = self.notify_via_slack(notify_obj, spec)
        else:
            logger.exception(
                f"Unsupported notification type, skipping",
                extra={"transform": self.name, "data": json.dumps(notify_obj, indent=4)}
            )

        return notify_success


    def notify_target(self, spec, target, results, data):
        config      = spec['config']
        store       = config['store']
        params      = target.get('params', {})

        status = {
            "stats": {
                "tries": 0,
                "success": 0,
            }
        }

        # check to see if a custom notification builder is available
        if target.get('method', 'default') != 'default':
            # check to see if custom handler is available
            handler = target.get('handler')
            if handler is None or not hasattr(self, handler):
                logger.exception(
                    f"No notification handler, skipping.",
                    extra={"transform": self.name, "data": json.dumps(target, indent=4)}
                )
                status['stats']['tries'] += 1
                return status
            # we have the notification callback
            callback = getattr(self, handler)

            # call the handler to set up the notification
            notify_set = callback(spec, target, results, data, params)
        else:
            notify_set = {
                "sent": False,
                "name": target['name'],
                "channel": target['channel'],
                "freq": target['freq'],
                "send_on": target['send_on'],
                "sets": [target]
            }

        status['channel'] = notify_set['channel']
        status['do_notify'] = {}

        # for each notify object in the set
        for notify_obj in notify_set['sets']:
            # check to see if we need to send notifications
            set_id = notify_obj.get('set_id', '__ALL__')
            do_notify = self.check_notify_default(notify_set, notify_obj, spec, results)
            status['do_notify'][set_id] = do_notify

            if do_notify and not notify_set['sent']:
                notify_obj['channel'] = notify_set['channel']
                status['stats']['tries'] += 1
                # we need to now send a notification, it's not been handled in the custom handler
                success = self.notify_target_common(notify_obj, spec)
                if success:
                    status['stats']['success'] += 1
            else:
                logger.debug(
                    f"[{set_id}] Notification not needed",
                    extra={"transform": self.name}
                )

        return status


    def notify_result(self, spec, results, data):
        # send notification
        name = spec['name']
        config = spec['config']
        checks = config['checks']
        store  = config['store']
        notify = config.get('notify')

        # validate notification spec
        if notify is None or not isinstance(notify, list) or len(notify) == 0:
            logger.debug(
                f"Skipping notification -- no targets specified",
                extra={"transform": self.name}
            )
            return results

        # validate store spec, we need it also
        for f in ["sink", "params"]:
            if f not in store:
                logger.exception(
                    f"Store has no {f} param, skipping.",
                    extra={"transform": self.name, "data": json.dumps(spec, indent=4)}
                )
                return results

        # all good, we can proceed
        targets_notified = []
        results_expanded = []
        notified_at = datetime.now()

        # for each notification target
        for target in notify:

            skip_target = False

            for f in ["method"]:
                if f not in target:
                    logger.exception(
                        f"Target has no {f} param, skipping.",
                        extra={"transform": self.name, "data": json.dumps(target, indent=4)}
                    )
                    skip_target = True
            if skip_target:
                return results

            # process the notification for each check in the spec
            for check in checks:

                r = results[results['check']==check['name']].copy()
                notify_status = self.notify_target(spec, target, r, data)

                # note it
                targets_notified.append({
                    check['name']: notify_status
                })

                for set_id, is_notified in notify_status['do_notify'].items():
                    # we need to make one copy per set_id
                    _r = r.copy()

                    # add this check+set to a list
                    _r['set_id']   = set_id
                    _r['notified'] = is_notified
                    _r['notifier'] = target['name']
                    _r['notified_at'] = None

                    if is_notified:
                        _r['notified_at'] = notified_at

                    results_expanded.append(_r)

        if len(targets_notified)>0:
            msg = f"Total {len(targets_notified)} checks notified: {targets_notified}" + "\n"
            logger.debug(
                f"Notifications processed",
                extra={"transform": self.name, "data": msg}
            )

        # concat all the sets of notification events for the results
        # we should have one per notification target
        results = pd.concat(results_expanded)

        return results


    def process(self, state):
        """
        Run the computation and update the state
        """
        logger.debug(
            "Start execution", extra=self.config.get_extra({"transform": self.name})
        )

        # Will be used in other places..
        self.state = state

        # Get the profile spec
        is_valid, profile, msg = profilespec.get_profile(self, "observability")
        if is_valid:
            logger.debug(
                f"Loaded profilespec",
                extra={"transform": self.name, "data": msg}
            )
        else:
            logger.error(
                f"Could not load profilespec",
                extra={"transform": self.name, "data": msg}
            )
            raise Exception("could not load profilespec")

        specs = profile.get("specs", None)
        if specs is None:
            raise Exception("Could not find 'specs' in profile")

        # get the dataset lookup table
        customer_datasets = profilespec.construct_dataset_list(self, specs)

        # Now go through each spec and process it
        for spec in specs:

            ## first, some checks on the spec
            do_process_spec = True
            name = spec.get('name', 'NO_SPEC_NAME')

            enabled = spec.get("enable", True)
            if not enabled:
                logger.debug(
                    f"Spec not enabled, skipping.",
                    extra={"transform": self.name, "data": json.dumps(spec, indent=4)}
                )
                do_process_spec = False
                continue

            for f in ["name", "config"]:
                if f not in spec:
                    logger.exception(
                        f"Spec has no {f} param, skipping.",
                        extra={"transform": self.name, "data": json.dumps(spec, indent=4)}
                    )
                    do_process_spec = False
                    break
            if do_process_spec == False:
                continue

            config = spec['config']

            for f in ["source", "checks", "store"]:
                if f not in config:
                    logger.exception(
                        f"Spec config has no {f} param, skipping.",
                        extra={"transform": self.name, "data": json.dumps(spec, indent=4)}
                    )
                    do_process_spec = False
                    break
            if do_process_spec == False:
                continue


            ## we can now proceed with processing the spec
            # frist, load the source data
            data = self.load_dataset(spec, customer_datasets)

            # then, process it
            results = self.process_spec(spec, data)
            if results is None:
                continue

            ## notify the observability result
            results = self.notify_result(spec, results, data)

            ## store the observability result and notification status
            self.store_result(spec, results, data)

            # update frame for pipline
            description = spec.get("desc", f"{name} observability results")
            lineage = {
                "type": "lineage",
                "transform": self.name,
                "dependencies": [
                    {
                        "type": "file",
                        "nature": "input",
                        "objects": [spec.get("filename", "__NEW__")],
                    },
                ],
            }
            self.update_frame(
                spec,
                description,
                results,
                lineage,
            )

        # Done
        logger.debug(
            "Complete execution", extra=self.config.get_extra({"transform": self.name})
        )

        ###########################################
        # => Return
        ###########################################
        return state

    def validate_results(self, what, state):
        pass
