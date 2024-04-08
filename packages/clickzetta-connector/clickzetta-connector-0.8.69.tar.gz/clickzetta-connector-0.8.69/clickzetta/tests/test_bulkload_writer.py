import random
import re
import unittest
from decimal import Decimal

import pandas
import sqlalchemy
import sqlparse
from clickzetta import connect, Client
from clickzetta.dbapi import Connection
from clickzetta.session import Session
from clickzetta.proto.generated import ingestion_pb2
from clickzetta.bulkload.bulkload_enums import *
import pytest
from pyarrow import fs
from google.protobuf.json_format import MessageToJson, MessageToDict, Parse, ParseDict
from sqlalchemy import text


class TestBulkLoad(unittest.TestCase):

    def test_bulkload_config(self):
        writer_config = ingestion_pb2.BulkloadStreamWriterConfig()
        writer_config.max_num_rows_per_file = 100
        writer_config.max_size_in_bytes_per_file = 200
        mgs_dict = MessageToDict(writer_config)
        protobuf_msg = ParseDict(mgs_dict, ingestion_pb2.BulkloadStreamWriterConfig())
        print(protobuf_msg.max_num_rows_per_file)

    def test_bulkload_simplified_interface(self):
        conn = connect(username='cz_lh_smoke_test', password='Abc123456',
                       service='dev-api.zettadecision.com', instance='clickzetta',
                       workspace='system_smoke', vcluster='cz_gp_daily')
        bulkload_stream = conn.create_bulkload_stream(schema='lakehouse_daily', table='append_cluster_python')
        writer = bulkload_stream.open_writer(0)
        row = writer.create_row()
        row.set_value('id', 1)
        row.set_value('month', 'January')
        row.set_value('amount', 45)
        row.set_value('cost', 113.56)
        writer.write(row)
        writer.close()
        bulkload_stream.commit()
        bulkload_stream.close()

    def test_get_bulkload_stream(self):
        conn = connect(username='cz_lh_smoke_test', password='Abc123456',
                       service='dev-api.zettadecision.com', instance='clickzetta',
                       workspace='system_smoke', vcluster='cz_gp_daily')
        stream1 = conn.create_bulkload_stream(schema='lakehouse_daily', table='append_cluster_python',
                                              operation=BulkLoadOperation.OVERWRITE)
        stream2 = conn.get_bulkload_stream(schema='lakehouse_daily', table='append_cluster_python',
                                           stream_id=stream1.get_stream_id())
        self.assertEqual(stream1.get_stream_id(), stream2.get_stream_id())

        writer1 = stream1.open_writer(1)
        row = writer1.create_row()
        row.set_value('id', 1)
        row.set_value('month', 'January')
        row.set_value('amount', 45)
        row.set_value('cost', 113.56)
        writer1.write(row)
        writer1.close()

        writer2 = stream2.open_writer(2)
        row = writer2.create_row()
        row.set_value('id', 2)
        row.set_value('month', 'Feb')
        row.set_value('amount', 67)
        row.set_value('cost', 561.13)
        writer2.write(row)
        writer2.close()

        stream1.commit()
        cur = conn.cursor()
        cur.execute('select id,month,amount,cost from lakehouse_daily.append_cluster_python order by id asc;')
        rs = cur.fetchall()
        cur.close()
        self.assertEqual(len(rs), 2)
        self.assertEqual(rs[0], (1, 'January', 45, Decimal('113.56')))
        self.assertEqual(rs[1], (2, 'Feb', 67, Decimal('561.13')))

    def test_bulkload_minor_writer(self):
        config = {
            'url': 'clickzetta://cz_lh_smoke_test:Abc123456@clickzetta.dev-api.zettadecision.com/system_smoke?virtualcluster=cz_gp_daily'}
        session = Session.builder.configs(config).create()
        bulkload_config = BulkLoadOptions(BulkLoadOperation.APPEND, None, None)
        bulkload_stream = session.create_bulkload_stream('lakehouse_daily', 'append_cluster_python', bulkload_config)
        writer = bulkload_stream.open_writer(0)

        row = writer.create_row()
        row.set_value('id', 1)
        row.set_value('month', 'January')
        row.set_value('amount', 45)
        row.set_value('cost', 113.56)
        writer.write(row)

        writer.close()
        commit_options = BulkLoadCommitOptions('system_smoke', 'cz_gp_daily')
        bulkload_stream.commit(commit_options)
        bulkload_stream.close()
        session.close()

    def test_bulkload_major_writer(self):
        config = {
            'url': 'clickzetta://cz_lh_smoke_test:Abc123456@clickzetta.dev-api.zettadecision.com/system_smoke?virtualcluster=cz_gp_daily'}
        session = Session.builder.configs(config).create()
        bulkload_config = BulkLoadOptions(BulkLoadOperation.APPEND, None, None)
        bulkload_stream = session.create_bulkload_stream('lakehouse_daily', 'append_cluster_python', bulkload_config)
        writer = bulkload_stream.open_writer(0)

        for index in range(1, 6000000):
            row = writer.create_row()
            row.set_value('id', index)
            row.set_value('month', 'January')
            row.set_value('amount', 45)
            row.set_value('cost', 113.56)
            writer.write(row)

        writer.close()
        commit_options = BulkLoadCommitOptions('system_smoke', 'cz_gp_daily')
        bulkload_stream.commit(commit_options)
        bulkload_stream.close()
        session.close()

    def test_bulkload_distributed_writer(self):
        config = {
            'url': 'clickzetta://cz_lh_smoke_test:Abc123456@clickzetta.dev-api.zettadecision.com/system_smoke?virtualcluster=cz_gp_daily'}
        session = Session.builder.configs(config).create()
        bulkload_config = BulkLoadOptions(BulkLoadOperation.APPEND, None, None)
        driver_bulkload_stream = session.create_bulkload_stream('lakehouse_daily', 'append_cluster_python',
                                                                bulkload_config)
        stream_id = driver_bulkload_stream.get_stream_id()
        executor_stream = session.get_bulkload_stream('lakehouse_daily', 'append_cluster_python', stream_id)
        writer_list = []
        for index in range(3):
            writer_list.append(executor_stream.open_writer(index))

        for writer in writer_list:
            row = writer.create_row()
            row.set_value('id', random.randint(1, 1000))
            row.set_value('month', 'January')
            row.set_value('amount', 45)
            row.set_value('cost', 113.56)
            writer.write(row)

        for writer in writer_list:
            writer.close()
        executor_stream.close()
        commit_options = BulkLoadCommitOptions('system_smoke', 'cz_gp_daily')
        driver_bulkload_stream.commit(commit_options)
        driver_bulkload_stream.close()
        session.close()

    def test_bulkload_major_overwriter(self):
        config = {
            'url': 'clickzetta://cz_lh_smoke_test:Abc123456@clickzetta.dev-api.zettadecision.com/system_smoke?virtualcluster=cz_gp_daily'}
        session = Session.builder.configs(config).create()
        bulkload_config = BulkLoadOptions(BulkLoadOperation.OVERWRITE, None, None)
        bulkload_stream = session.create_bulkload_stream('lakehouse_daily', 'append_cluster_python', bulkload_config)
        writer = bulkload_stream.open_writer(0)

        for index in range(1, 1000000):
            row = writer.create_row()
            row.set_value('id', index + 1)
            row.set_value('month', 'January')
            row.set_value('amount', 45)
            row.set_value('cost', 113.56)
            writer.write(row)

        writer.close()
        commit_options = BulkLoadCommitOptions('system_smoke', 'cz_gp_daily')
        bulkload_stream.commit(commit_options)
        bulkload_stream.close()
        session.close()

    def test_bulkload_major_upsert_writer(self):
        config = {
            'url': 'clickzetta://cz_lh_smoke_test:Abc123456@clickzetta.dev-api.zettadecision.com/system_smoke?virtualcluster=cz_gp_daily'}
        session = Session.builder.configs(config).create()
        bulkload_config = BulkLoadOptions(BulkLoadOperation.UPSERT, None, ['id'])
        bulkload_stream = session.create_bulkload_stream('lakehouse_daily', 'append_cluster_python', bulkload_config)
        writer = bulkload_stream.open_writer(0)

        for index in range(1, 1000000):
            row = writer.create_row()
            row.set_value('id', index + 1)
            row.set_value('month', 'January')
            row.set_value('amount', 45)
            row.set_value('cost', 113.56)
            writer.write(row)

        writer.close()
        commit_options = BulkLoadCommitOptions('system_smoke', 'cz_gp_daily')
        bulkload_stream.commit(commit_options)
        bulkload_stream.close()
        session.close()

    def test_bulkload_major_append_pt_writer(self):
        config = {
            'url': 'clickzetta://cz_lh_smoke_test:Abc123456@clickzetta.dev-api.zettadecision.com/system_smoke?virtualcluster=cz_gp_daily'}
        session = Session.builder.configs(config).create()
        bulkload_config = BulkLoadOptions(BulkLoadOperation.APPEND, "pt=python_bulkload", None)
        bulkload_stream = session.create_bulkload_stream('lakehouse_daily', 'upsert_cluster_pt_python', bulkload_config)
        writer = bulkload_stream.open_writer(0)

        for index in range(1, 1000000):
            row = writer.create_row()
            row.set_value('id', index + 1)
            row.set_value('month', 'January')
            row.set_value('amount', 45)
            row.set_value('cost', 113.56)
            writer.write(row)

        writer.close()
        commit_options = BulkLoadCommitOptions('system_smoke', 'cz_gp_daily')
        bulkload_stream.commit(commit_options)
        bulkload_stream.close()
        session.close()

    def test_bulkload_major_pt_overwriter(self):
        config = {
            'url': 'clickzetta://cz_lh_smoke_test:Abc123456@clickzetta.dev-api.zettadecision.com/system_smoke?virtualcluster=cz_gp_daily'}
        session = Session.builder.configs(config).create()
        bulkload_config = BulkLoadOptions(BulkLoadOperation.OVERWRITE, "pt=python_bulkload", None)
        bulkload_stream = session.create_bulkload_stream('lakehouse_daily', 'upsert_cluster_pt_python', bulkload_config)
        writer = bulkload_stream.open_writer(0)

        for index in range(1, 3000000):
            row = writer.create_row()
            row.set_value('id', index + 1)
            row.set_value('month', 'January')
            row.set_value('amount', 45)
            row.set_value('cost', 113.56)
            writer.write(row)

        writer.close()
        commit_options = BulkLoadCommitOptions('system_smoke', 'cz_gp_daily')
        bulkload_stream.commit(commit_options)
        bulkload_stream.close()
        session.close()

    def test_bulkload_major_upsert_pt_writer(self):
        config = {
            'url': 'clickzetta://cz_lh_smoke_test:Abc123456@clickzetta.dev-api.zettadecision.com/system_smoke?virtualcluster=cz_gp_daily'}
        session = Session.builder.configs(config).create()
        bulkload_config = BulkLoadOptions(BulkLoadOperation.UPSERT, "pt=python_bulkload", ['id'])
        bulkload_stream = session.create_bulkload_stream('lakehouse_daily', 'upsert_cluster_pt_python', bulkload_config)
        writer = bulkload_stream.open_writer(0)

        for index in range(1, 1000000):
            row = writer.create_row()
            row.set_value('id', index + 1)
            row.set_value('month', 'January')
            row.set_value('amount', 45)
            row.set_value('cost', 113.56)
            writer.write(row)

        writer.close()
        commit_options = BulkLoadCommitOptions('system_smoke', 'cz_gp_daily')
        bulkload_stream.commit(commit_options)
        bulkload_stream.close()
        session.close()

    def test_ut_2(self):
        config = {
            'url': 'clickzetta://on_lh_test:Abc123456@6f5afa19.dev-api.clickzetta.com/qa_smoke_test?virtualcluster=default'}
        session = Session.builder.configs(config).create()
        bulkload_config = BulkLoadOptions(BulkLoadOperation.APPEND, None, None)
        bulkload_stream = session.create_bulkload_stream('PUBLIC', 'lh_smoke_test_python_sdk_bulkload', bulkload_config)
        writer = bulkload_stream.open_writer(0)

        for index in range(1, 6000000):
            row = writer.create_row()
            row.set_value('col1', index)
            row.set_value('col2', str(index))
            writer.write(row)

        writer.close()
        commit_options = BulkLoadCommitOptions('qa_smoke_test', 'DEFAULT')
        bulkload_stream.commit(commit_options)
        bulkload_stream.close()
        session.close()

    def test_ut_3(self):
        from clickzetta.client import Client
        from clickzetta.dbapi.connection import Connection
        client = Client(
            cz_url="clickzetta://SD_demo:Asddemo123@6861c888.api.clickzetta.com/quickStart_WS?virtualCluster=default")
        conn = Connection(client)

        cursor = conn.cursor()
        sql = "select * from clickzetta_sample_data.ecommerce_events_history.ecommerce_events_multicategorystore_live limit 20000;"
        cursor.execute(sql)
        results = cursor.fetchone()
        count = 0
        print(results)
        for r in results:
            count += 1
            print(count)
            print(r)

    def test_huge_result_case(self):
        from sqlalchemy import create_engine
        from sqlalchemy import text

        engine = create_engine(
            "clickzetta://SD_demo:Asddemo123!@6861c888.api.clickzetta.com/quickStart_WS?virtualCluster=default")

        sql = text(
            "select * from clickzetta_sample_data.ecommerce_events_history.ecommerce_events_multicategorystore_live limit 100000;")

        count = 0
        with engine.connect() as conn:
            cursor = conn.execute(sql)
            results = cursor.fetchall()
            for r in results:
                count += 1
                print(count)
                print(r)

    def test_query_with_magic_token(self):
        from sqlalchemy import create_engine
        from sqlalchemy import text
        engine = create_engine(
            "clickzetta://:@6861c888.api.clickzetta.com/quickStart_WS?virtualCluster=default&magic_token=eyJhbGciOiJIUzI1Ni.eyJhY2NvdW50SWQiOjExMTAxMSwidGVuYW50SWQiOjExMTAxMSwidXNlck5hbWUiOiJTRF9kZW1vIiwidXNlcklkIjoxMDA4MTQ5LCJpYXQiOjE2OTI4NjAyMDMsImV4cCI6MTY5MzExOTQwM30.HP7JN8QLyPOLF3gs_tmEmGQtmd0yTo77h2TIPEc0ZwA&schema=ecommerce_events_history")

        sql = text(
            "select * from clickzetta_sample_data.ecommerce_events_history.ecommerce_events_multicategorystore_live limit 1000;")

        count = 0
        with engine.connect() as conn:
            results = conn.execute(sql).fetchall()
            for r in results:
                count += 1
                print(count)
                print(r)

    def test_get_job_profile(self):
        from clickzetta.client import Client
        from clickzetta.dbapi.connection import Connection
        client = Client(
            cz_url="clickzetta://SD_demo:Asddemo123!@6861c888.api.clickzetta.com/quickStart_WS?virtualCluster=default")
        conn = Connection(client)

        cursor = conn.cursor()
        sql = "select * from clickzetta_sample_data.ecommerce_events_history.ecommerce_events_multicategorystore_live limit 10000;"
        cursor.execute(sql)
        results = cursor.fetchall()
        count = 0
        print(results)
        for r in results:
            count += 1
            print(count)
            print(r)
        print(conn.get_job_profile(cursor.job_id))

    def test_url_protocol(self):
        from sqlalchemy import create_engine
        from sqlalchemy import text

        engine = create_engine(
            "clickzetta://SD_demo:Asddemo123!@6861c888.api.clickzetta.com/quickStart_WS?virtualCluster=default&protocol=http")

        sql = text(
            "select * from clickzetta_sample_data.ecommerce_events_history.ecommerce_events_multicategorystore_live limit 1000;")

        count = 0
        with engine.connect() as conn:
            cursor = conn.execute(sql)
            results = cursor.fetchall()
            for r in results:
                count += 1
                print(count)
                print(r)

    def test_sdk_timeout(self):
        conn = connect(username='xxx', password='xxx',instance='xxx', service='api.clickzetta.com', workspace='syntax_space', schema='public', vcluster='SYNTAX_AP')
        hints = {
            "cz.sql.group.by.having.use.alias.first": "true",
            "cz.top.down.pass.through": "false",
            "cz.bottom.up.pass.through": "false",
            "cz.optimizer.post.process.join.column.prune": "true",
            "cz.sql.playback.scratch": "true",
            "cz.optimizer.enable.agg.push.down": "false",
            "sdk.job.timeout": "10"
        }
        parmas = {'hints': hints}
        cursor = conn.cursor()
        cursor.execute("select count(*) from validation_query_result_db.validation_query_result_table_20230920150841409405", parameters=parmas)
        results = cursor.fetchall()
        for result in results:
            print(result)

    def test_repeat_column_names(self):
        from sqlalchemy import create_engine
        from sqlalchemy import text

        engine = create_engine(
            "clickzetta://SD_demo:Asddemo123!@6861c888.api.clickzetta.com/quickStart_WS?virtualCluster=default&protocol=http")

        sql = text(
            "SELECT DATE_FORMAT(NOW(),'HH:mm:ss'), DATE_FORMAT(NOW(),'HH:mm:ss'), DATE_FORMAT(NOW(),'HH:mm:ss');")

        with engine.connect() as conn:
            cursor = conn.execute(sql)
            results = cursor.fetchall()
            for r in results:
                print(r)

    def test_get_volume(self):
        from clickzetta.client import Client
        from clickzetta.dbapi.connection import Connection
        client = Client(
            cz_url="clickzetta://system_admin:Abc123456@clickzetta.dev-api.zettadecision.com/default?virtualcluster=cz_gp_daily&schema=copy_test")
        conn = Connection(client)

        cursor = conn.cursor()
        sql = "show volume directory vol_test_092616;"
        cursor.execute(sql)
        results = cursor.fetchall()
        for r in results:
            print(r)
        get_volume_sql = 'get volume vol_test_092616/1/2.txt to /tmp/5.txt;'
        cursor.execute(get_volume_sql)
        result = cursor.fetchall()
        print(result)

    def test_put_volume(self):
        from clickzetta.client import Client
        from clickzetta.dbapi.connection import Connection
        client = Client(
            cz_url="clickzetta://system_admin:Abc123456@clickzetta.dev-api.zettadecision.com/default?virtualcluster=cz_gp_daily&schema=copy_test")
        conn = Connection(client)

        cursor = conn.cursor()

        get_volume_sql = 'put /tmp/3.txt to volume vol_test_092616/1/25.txt;'
        cursor.execute(get_volume_sql)
        result = cursor.fetchall()
        print(result)
        sql = "show volume directory vol_test_092616;"
        cursor.execute(sql)
        results = cursor.fetchall()
        for r in results:
            print(r)

    def test_repeat_column_names_1(self):
        from sqlalchemy import create_engine
        from sqlalchemy import text

        engine = create_engine(
            "clickzetta://atlas:Aatlas12345@809b4f0a.ap-southeast-1-alicloud.api.clickzetta.com/quickstart_ws?virtualCluster=ANALYSIS")

        sql = text(
            "select * from atlas_dwd.dwd_search_t_search_log_h_inc limit 10")

        with engine.connect() as conn:
            cursor = conn.execute(sql)
            results = cursor.fetchall()
            for r in results:
                print(r)
    def test_multi_result_files(self):
        from clickzetta.client import Client
        from clickzetta.dbapi.connection import connect
        conn = connect(cz_url="")
        cursor = conn.cursor()
        cursor.get_job_id()
        client = Client(
            cz_url="clickzetta://yunqi:Amedia_track12@ac5079d2.ap-shanghai-tencentcloud.api.clickzetta.com/media_track?virtualcluster=MEDIATRACK_AP&schema=realtime")
        conn = Connection(client)

        cursor = conn.cursor()
        sql = "select distinct `database_name`, `schema_name`, `table_name` from realtime.cdc_events where `emitted_at`>=1702635844470 and `emitted_at`<=1702635875947;"
        cursor.execute(sql)
        results = cursor.fetchall()
        print(len(results))
        for r in results:
            print(r)