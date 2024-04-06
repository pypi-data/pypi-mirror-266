import re
from datetime import date
import os.path
import uuid
import glob
import time
import shutil
from threading import Thread


class KawaDataLoader:

    def __init__(self, kawa_client, df, datasource_name=None, datasource_is_shared=False, datasource_id=None):
        if datasource_id is None and datasource_name is None:
            raise Exception('To build a KawaDataLoader you need either a datasource_name or a datasource_id')
        self._k = kawa_client
        self._df = df
        self._shared = datasource_is_shared
        self._name = '' if datasource_name is None else datasource_name.strip()
        self._datasource_id = datasource_id

    def create_datasource(self, primary_keys=None):
        """
        If the datasource with name == datasource_name does not exist in the current
        workspace, create it.
        This command is idempotent.
        Once the datasource exists, it will have no effect at all.

        The indicators of the datasource will be deduced from the columns of the dataframe.

        :param: primary_keys:
        Defines the list of columns that will be considered as primary key.
        If left empty, KAWA will generate a record_id which will act as an auto increment primary key.

        IMPORTANT: Those primary keys will be imported in the same order as they appear in the dataframe.

        :return: The created or existing datasource
        """
        if self._datasource_id:
            raise Exception('Cannot create data source when data source id has been provided')
        existing_datasource = self._k.entities.datasources().get_entity(entity_id_or_name=self._name)
        if existing_datasource:
            # Idempotent
            return existing_datasource
        else:
            ds = self._define_data_source_from_df(primary_keys=primary_keys)
            return self._k.commands.create_datasource(datasource=ds)

    def add_new_indicators_to_datasource(self):
        """
        Adds to the existing datasource (identified by its name) all the columns of the dataframe that
        were not already there.
        This command will only add new indicators to the datasource and will have no other effect.

        :raises: Exception is raised if the datasource does not exist in the current workspace
        :return: The updated datasource
        """
        existing_datasource = self._get_data_source_or_raise()
        existing_indicator_id = [i.get('indicatorId') for i in existing_datasource.get('indicators', [])]

        # No primary key here because we only look for new indicators
        # And BE does not support adding PK via the add_indicators_to_datasource command.
        new_datasource_from_df = self._define_data_source_from_df(primary_keys=[])

        new_indicators = []
        for new_indicator in new_datasource_from_df.get('indicators', []):
            new_indicator_id = new_indicator.get('indicatorId')
            if new_indicator_id not in existing_indicator_id:
                new_indicators.append(new_indicator)

        if new_indicators:
            print('Adding the following indicators: {}'.format([i.get('indicatorId') for i in new_indicators]))
            return self._k.commands.add_indicators_to_datasource(
                datasource=existing_datasource,
                new_indicators=new_indicators)
        else:
            print('No new indicator to add')
            return existing_datasource

    def load_data(self,
                  reset_before_insert=False,
                  create_sheet=False,
                  optimize_after_insert=False,
                  nb_threads=1,
                  parquet_file_list=None,
                  job_id=None):
        """
        Performs the following operations:
        1) Create the datasource if it does not exist, add any missing indicator to the existing one
        2) Send the dataframe to kawa

        :param: reset_before_insert:
        Set to True if the data has to be reset before the load.
        Set to False if the data has to be appended to existing data.

        :param: create_sheet:
        Set to True if a sheet should be created after the load.
        The URL to the sheet will be printed out.

        :param: nb_threads:
        Will split the data in nb_threads partition and load each one from
        a different thread.

        :return:
        The datasource object in which the data was loaded
        """
        created_data_source = self._load_data(optimize_after_insert=optimize_after_insert,
                                              reset_data=reset_before_insert,
                                              nb_threads=nb_threads,
                                              parquet_file_list=parquet_file_list,
                                              session_id_input=job_id)
        if create_sheet:
            self._k.commands.create_sheet(datasource=created_data_source,
                                          sheet_name=self._name)

        return created_data_source

    def _introspect_df(self):
        column_kawa_types = {}

        for column_name in self._df.columns:
            kawa_type = self._extract_kawa_type(column_name)
            column_kawa_types[column_name] = kawa_type

        return column_kawa_types

    def _define_data_source_from_df(self, primary_keys=None):

        defined_pks = primary_keys if primary_keys else []
        indicators = [self._define_indicator(c, c in defined_pks) for c in self._df.columns]

        # Add the auto increment key if there is no specified key
        key_indicators = [i for i in indicators if 'key' in i]
        if not key_indicators:
            indicators.insert(0, {
                'displayInformation': {
                    'displayName': 'record_id'
                },
                'includedInDefaultLayout': False,
                'indicatorId': 'record_id',
                'storageConfig': {
                    'indexed': True,
                    'automaticUniqueValue': True
                },
                'type': 'integer',
                'key': {
                    'keyType': 'PRIMARY_SHARDING_KEY'
                }
            })

        return {
            'shared': self._shared,
            'displayInformation': {
                'displayName': self._name
            },
            'storageConfiguration': {
                'loadingAdapterName': 'CLICKHOUSE'
            },
            'indicators': indicators,
        }

    def _define_indicator(self, column_name, is_primary_key=False):
        indicator = {
            'displayInformation': {
                'displayName': column_name
            },
            'includedInDefaultLayout': True,
            'indicatorId': column_name,
            'storageConfig': {
                'indexed': is_primary_key
            },
            'type': self._extract_kawa_type(column_name)
        }
        if is_primary_key:
            indicator['key'] = {'keyType': 'PRIMARY_SHARDING_KEY'}

        return indicator

    def _extract_kawa_type(self, column_name):
        column = self._df[column_name]
        column_type_name = str(column.dtype)

        if re.match(r'^datetime64', column_type_name):
            return 'date_time'

        if column_type_name == 'object':
            return self._introspect_values(column_name)

        if column_type_name == 'string':
            return 'text'

        if column_type_name == 'bool':
            return 'boolean'

        if re.match(r'^u?int[0-9]*$', column_type_name):
            return 'integer'

        if re.match(r'^float[0-9]*$', column_type_name):
            return 'decimal'

        raise Exception('Column {} with type {} is not supported'.format(column_name, column_type_name))

    def _introspect_values(self, column_name):
        for val in self._df[column_name]:
            if type(val) is str:
                return 'text'
            if type(val) is date:
                return 'date'
            if type(val) is list and val:
                for list_item in val:
                    if type(list_item) is str:
                        return 'list(integer,text)'
                    if type(list_item) is int:
                        return 'list(integer,integer)'
                    if type(list_item) is float:
                        return 'list(integer,decimal)'

        return 'any'

    def _get_data_source_or_raise(self):
        if self._datasource_id:
            datasource = self._k.entities.datasources().get_entity_by_id(self._datasource_id)
            if not datasource:
                raise Exception(
                    'No datasource with id: {} was found in the current workspace'.format(self._datasource_id))
        else:
            datasource = self._k.entities.datasources().get_entity(entity_id_or_name=self._name)
            if not datasource:
                raise Exception('No datasource with name: {} was found in the current workspace'.format(self._name))
        return datasource

    def _load_data(self,
                   show_progress=True,
                   reset_data=True,
                   optimize_after_insert=False,
                   nb_threads=1,
                   parquet_file_list=None,
                   session_id_input=None):

        df = self._df

        datasource = self._get_data_source_or_raise()
        datasource_id = datasource.get('id')

        indicators = datasource.get('indicators')
        session_id = session_id_input if session_id_input is not None else str(uuid.uuid4())
        print('Starting an ingestion session with id={}'.format(session_id))

        # URLs for ingestion session
        query_params = 'datasource={}&format=parquet&reset={}&session={}&optimize={}'.format(datasource_id, reset_data,
                                                                                             session_id,
                                                                                             optimize_after_insert)
        prepare_url = '{}/ingestion/prepare?{}'.format(self._k.kawa_api_url, query_params)
        ingest_url = '{}/ingestion/upload?{}'.format(self._k.kawa_api_url, query_params)
        finalize_url = '{}/ingestion/finalize?{}'.format(self._k.kawa_api_url, query_params)
        finalize_for_failure_url = '{}/ingestion/stop-with-failure?{}'.format(self._k.kawa_api_url, query_params)

        # Check that all date and date time indicators are numbers in the data frame
        temporal_indicators = [i for i in indicators if i.get('type') == 'date_time']
        for temporal_indicator in temporal_indicators:
            column_name = temporal_indicator.get('indicatorId')
            if column_name in df.columns:
                column_type_name = str(df[column_name].dtype)
                if re.match(r'^datetime64', column_type_name):
                    df[column_name] = df[column_name].map(lambda x: int(x.timestamp() * 1000) if x else None)

        # Call prepare data that will check if we can start loading and give us the offset for automatic index
        prepare_data = self._k.post(url=prepare_url, data={})

        if not prepare_data.get('canRunLoading'):
            raise Exception(
                'We cannot start ingestion due to: ' + prepare_data.get('raisonItCannotStart', 'No reason given'))

        parquet_directory = '{}/{}'.format(self._k.tmp_files_directory, str(uuid.uuid4()))
        os.makedirs(parquet_directory, exist_ok=True)

        try:
            auto_increment_indicator = [i for i in indicators if
                                        i.get('storageConfig', {}).get('automaticUniqueValue', False)]

            if len(auto_increment_indicator) == 1:
                if 'offsetToApplyToAutoIncrementIndex' not in prepare_data:
                    self._k.post(url=finalize_for_failure_url, data={})
                    raise Exception('The offset for to the auto_increment_index was not present in the answer from '
                                    'backend. Cannot continue')

                auto_increment_indicator_id = auto_increment_indicator[0].get('indicatorId')
                df[auto_increment_indicator_id] = df.index + prepare_data.get('offsetToApplyToAutoIncrementIndex') + 1

            # Check that all the indicators are present in the data frame, otherwise create empty columns
            for indicator in indicators:
                indicator_id = indicator.get('indicatorId')
                if indicator_id not in df.columns:
                    default_value = self._empty_value_for_indicator(indicator)
                    df[indicator_id] = default_value

            # Add a partition column to split up the frames into multiple parquet files
            if not parquet_file_list:
                partition_cols = []
                nb_partitions = max(1, nb_threads)
                if nb_partitions > 1:
                    df['__partition__'] = (df.index + 1) % nb_partitions
                    partition_cols.append('__partition__')

                if show_progress:
                    print('> Exporting the dataframe into {} parquet file{}'.format(nb_partitions,
                                                                                    's' if nb_partitions > 1 else ''))

                df.to_parquet(partition_cols=partition_cols, path=parquet_directory + '/', compression='gzip')

            start = time.time()
            loading_threads = []

            if parquet_file_list:
                parquet_files = parquet_file_list
            else:
                parquet_files = glob.glob('{}/**/*.parquet'.format(parquet_directory), recursive=True)

            for parquet_file in parquet_files:
                loading_thread = Thread(target=self._loading_thread, args=(ingest_url, parquet_file))
                loading_threads.append(loading_thread)

            if show_progress:
                print('> Starting {} loading threads'.format(len(loading_threads)))
            [t.start() for t in loading_threads]
            [t.join() for t in loading_threads]

            end = time.time()
            if show_progress:
                print('> {} rows were imported in {}ms'.format(df.shape[0], end - start))

        except Exception as e:
            self._k.post(url=finalize_for_failure_url, data={})
            raise e

        finally:
            if os.path.isdir(parquet_directory):
                shutil.rmtree(parquet_directory)

            self._k.post(url=finalize_url, data={})
            if show_progress:
                print('> Import was successfully finalized')

        return datasource

    def _loading_thread(self, ingestion_url, parquet_file):
        self._k.post_binary_file(filename=parquet_file, url=ingestion_url)

    @staticmethod
    def _empty_value_for_indicator(indicator):
        indicator_type = indicator.get('type')
        if indicator_type == 'text':
            return ''
        if indicator_type == 'date':
            return date(1970, 1, 1)
        if indicator_type == 'date_time':
            return 0
        if indicator_type.startswith('list('):
            raise 'Does not support omitting lists'
        return None
