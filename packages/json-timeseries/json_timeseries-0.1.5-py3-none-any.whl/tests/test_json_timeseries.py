import json
import unittest
from datetime import datetime, timedelta
from string import Template

from json_timeseries import TsRecord, TimeSeries, JtsDocument


class TestTimeSeries(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.NOW = datetime.now()  # new Date(Math.round(new Date().getTime() / 1000) * 1000)
        self.ONE_MINUTE_AGO = self.NOW - timedelta(minutes=1)  # new Date(NOW.getTime() - (60 * 1000))

        self.NUMBER_RECORDS = [
            TsRecord(**{"timestamp": self.ONE_MINUTE_AGO, "value": 1, "quality": 192, "annotation": 'comment'}),
            TsRecord(**{"timestamp": self.NOW, "value": 2})]

        self.TEST_UUID = '2bf5ddbb-c370-428f-9329-7379fc72488d'

    # def tearDown(self):
    #     pass

    def test_insert_single_record(self):
        ts = TimeSeries(name='TEST1', identifier=self.TEST_UUID, units='C', records=self.NUMBER_RECORDS)
        ts.insert(TsRecord(datetime.now(), 55))
        self.assertEqual(len(ts), 3)
        # print(ts)
        #

    def test_insert_list_record(self):
        ts = TimeSeries(name='TEST1', identifier=self.TEST_UUID, units='C', records=self.NUMBER_RECORDS)
        ts.insert([TsRecord(datetime.now(), 55), TsRecord(datetime.now(), 77)])
        self.assertEqual(len(ts), 4)


    # def test_to_JSON(self):
    #     ts = TimeSeries(name='TEST1', ts_id=self.TEST_UUID, units='C', records=self.NUMBER_RECORDS)
    #     ts_json = """{"id": "2bf5ddbb-c370-428f-9329-7379fc72488d", "name": "TEST1", "units": "C", "type": "NUMBER", "records": [{"timestamp": "%s", "value": 1, "quality": 192, "annotation": "comment"}, {"timestamp": "%s", "value": 2}]}""" % (
    #         self.ONE_MINUTE_AGO.isoformat(), self.NOW.isoformat())
    #     self.assertEqual(ts.toJSON(), ts_json)

class TestJtsDocument(unittest.TestCase):

    maxDiff = None

    def setUp(self):
        self.NOW = datetime.now()  # new Date(Math.round(new Date().getTime() / 1000) * 1000)
        self.ONE_MINUTE_AGO = self.NOW - timedelta(minutes=1)  # new Date(NOW.getTime() - (60 * 1000))
        self.ONE_MILISECOND_AGO = self.NOW - timedelta(milliseconds=1)
        self.TWO_MILISECONDS_AGO = self.NOW - timedelta(milliseconds=2)
        self.THREE_MILISECONDS_AGO = self.NOW - timedelta(milliseconds=3)

        self.NUMBER_RECORDS = [
            TsRecord(**{"timestamp": self.ONE_MINUTE_AGO, "value": 1, "quality": 192, "annotation": 'comment'}),
            TsRecord(**{"timestamp": self.NOW, "value": 2})]

        self.TEST_UUID = '2bf5ddbb-c370-428f-9329-7379fc72488d'
        
        self.NUMBER_SUBSECOND_RECORDS = [
            TsRecord(**{"timestamp": self.ONE_MINUTE_AGO, "value": 1, "quality": 192, "annotation": 'comment'}),
            TsRecord(**{"timestamp": self.THREE_MILISECONDS_AGO, "value": 2}),
            TsRecord(**{"timestamp": self.TWO_MILISECONDS_AGO, "value": 2}),
            TsRecord(**{"timestamp": self.ONE_MILISECOND_AGO, "value": 2}),
            TsRecord(**{"timestamp": self.NOW, "value": 2})]
        
        self.NUMBER_SUBSECOND_RECORDS_OUT_OF_ORDER = [
            TsRecord(**{"timestamp": self.ONE_MILISECOND_AGO, "value": 2}),
            TsRecord(**{"timestamp": self.NOW, "value": 2}),
            TsRecord(**{"timestamp": self.TWO_MILISECONDS_AGO, "value": 2}),
            TsRecord(**{"timestamp": self.ONE_MINUTE_AGO, "value": 1, "quality": 192, "annotation": 'comment'}),
            TsRecord(**{"timestamp": self.THREE_MILISECONDS_AGO, "value": 2})]

        '''
        Other sample dataTypes for tests:
        
        const TEXT_RECORDS = [
          { timestamp: ONE_MINUTE_AGO, value: 'Test value', quality: 192, annotation: 'comment' },
          { timestamp: NOW, value: null }
        ]

        const TIME_RECORDS = [
          { timestamp: ONE_MINUTE_AGO, value: ONE_MINUTE_AGO, quality: 192, annotation: 'comment' },
          { timestamp: NOW, value: null }
        ]

        const COORDINATES_RECORDS = [
          { timestamp: ONE_MINUTE_AGO, value: [100, 200], quality: 192, annotation: 'comment' },
          { timestamp: NOW, value: null }
        ]
        '''

    # def tearDown(self):
    #     pass

    def test_create_doc(self):
        jts_doc = JtsDocument(TimeSeries(name="series_1", records=self.NUMBER_RECORDS))
        self.assertEqual(len(jts_doc), 1)

    def test_add_single_series(self):
        jts_doc = JtsDocument()
        jts_doc.addSeries(TimeSeries(name="series_1", records=self.NUMBER_RECORDS))
        self.assertEqual(len(jts_doc), 1)

    def test_add_multiple_series(self):
        jts_doc = JtsDocument()
        jts_doc.addSeries([
            TimeSeries(name="series_3", records=self.NUMBER_RECORDS),
            TimeSeries(name="series_4", records=self.NUMBER_RECORDS)
        ])
        self.assertEqual(len(jts_doc), 2)

    def test_toJSON_NUMBER(self):
        timeseries1 = TimeSeries(identifier='series_1', name='Series 1', data_type='NUMBER', records=[
            TsRecord(**{"timestamp": self.ONE_MINUTE_AGO, "value": '1.23', "quality": 192, "annotation": 'comment'}),
            TsRecord(**{"timestamp": self.NOW, "value": '2.34', "quality": 245, "annotation": 'comment number 2'})]
                                 )
        timeseries2 = TimeSeries(identifier='series_2', name='Series 2', data_type='NUMBER', units="C", records=[
            TsRecord(**{"timestamp": self.NOW, "value": '1.11', "quality": 111, "annotation": 'comment ts2 111'}),
            TsRecord(**{"timestamp": self.ONE_MINUTE_AGO, "value": '2.22', "quality": 222, "annotation": 'comment ts2'})
        ])

        jts_document = JtsDocument(series=[timeseries1, timeseries2])

        t = Template("""
        {
            "docType": "jts",
            "version": "1.0",
            "header": {
                "startTime": "$ONE_MINUTE_AGO",
                "endTime": "$NOW",
                "recordCount": 2,
                "columns": {
                    "0": {
                        "id": "series_1",
                        "name": "Series 1",
                        "dataType": "NUMBER"
                    },
                    "1": {
                        "id": "series_2",
                        "name": "Series 2",
                        "dataType": "NUMBER",
                        "units": "C"
                    }
                }
            },
            "data": [
                {
                    "ts": "$ONE_MINUTE_AGO",
                    "f": {
                        "0": {
                            "v": 1.23,
                            "q": 192,
                            "a": "comment"
                        },
                        "1": {
                            "v": 2.22,
                            "q": 222,
                            "a": "comment ts2"
                        }
                        
                    }
                },
                {
                    "ts": "$NOW",
                    "f": {
                        "0": {
                            "v": 2.34,
                            "q": 245,
                            "a": "comment number 2"
                        },
                        "1": {
                            "v": 1.11,
                            "q": 111,
                            "a": "comment ts2 111"
                        }
                    }
                }
            ]
        }
        """)

        jts_str = t.substitute(ONE_MINUTE_AGO=self.ONE_MINUTE_AGO.isoformat(),
                               NOW=self.NOW.isoformat())
        jts_payload = jts_document.toJSONString()
        self.assertEqual(jts_payload, json.dumps(json.loads(jts_str)))

    def test_fromJSON(self):
        timeseries1 = TimeSeries(identifier='series_1', name='Series 1', data_type='NUMBER', records=[
            TsRecord(**{"timestamp": self.ONE_MINUTE_AGO, "value": '1.23', "quality": 192, "annotation": 'comment'}),
            TsRecord(**{"timestamp": self.NOW, "value": '2.34', "quality": 245, "annotation": 'comment number 2'})]
                                 )
        timeseries2 = TimeSeries(identifier='series_2', name='Series 2', data_type='NUMBER', units="C", records=[
            TsRecord(**{"timestamp": self.NOW, "value": '1.11', "quality": 111, "annotation": 'comment ts2 111'}),
            TsRecord(
                **{"timestamp": self.ONE_MINUTE_AGO, "value": '2.22', "quality": 222, "annotation": 'comment ts2 222'})]
                                 )

        jts_document = JtsDocument(series=[timeseries1, timeseries2])

        t = Template("""
        {
            "docType": "jts",
            "version": "1.0",
            "header": {
                "startTime": "$ONE_MINUTE_AGO",
                "endTime": "$NOW",
                "recordCount": 2,
                "columns": {
                    "0": {
                        "id": "series_1",
                        "name": "Series 1",
                        "dataType": "NUMBER"
                    },
                    "1": {
                        "id": "series_2",
                        "name": "Series 2",
                        "dataType": "NUMBER",
                        "units": "C"
                    }
                }
            },
            "data": [
                {
                    "ts": "$ONE_MINUTE_AGO",
                    "f": {
                        "0": {
                            "v": 1.23,
                            "q": 192,
                            "a": "comment"
                        },
                        "1": {
                            "v": 2.22,
                            "q": 222,
                            "a": "comment ts2 222"
                        }

                    }
                },
                {
                    "ts": "$NOW",
                    "f": {
                        "0": {
                            "v": 2.34,
                            "q": 245,
                            "a": "comment number 2"
                        },
                        "1": {
                            "v": 1.11,
                            "q": 111,
                            "a": "comment ts2 111"
                        }
                    }
                }
            ]
        }
        """)

        jts_str = t.substitute(ONE_MINUTE_AGO=self.ONE_MINUTE_AGO.isoformat(),
                               NOW=self.NOW.isoformat())
        jts_loaded = JtsDocument.fromJSON(jts_str)

        self.assertEqual(jts_loaded.toJSON(), jts_document.toJSON())

    def test_getSeriesByID(self):
        timeseries1 = TimeSeries(identifier='series_1', name='Series 1', data_type='NUMBER', records=[
            TsRecord(**{"timestamp": self.ONE_MINUTE_AGO, "value": '1.23', "quality": 192, "annotation": 'comment'}),
            TsRecord(**{"timestamp": self.NOW, "value": '2.34', "quality": 245, "annotation": 'comment number 2'})]
                                 )
        timeseries2 = TimeSeries(identifier='series_2', name='Series 2', data_type='NUMBER', units="C",
                                 records=TsRecord(timestamp=self.NOW, value=1.11, quality=111, annotation='comment ts2 111')
                                 )
        jts_doc = JtsDocument([timeseries1, timeseries2])

        test_series = jts_doc.getSeries(identifier='series_2')
        self.assertEqual(test_series.identifier, "series_2")
        self.assertEqual(len(test_series), 1)

        # test('get series by id', () = > {
        #     const
        # jtsDocument = new
        # JtsDocument()
        # jtsDocument.addSeries([new TimeSeries({id: 'series_1', records: NUMBER_RECORDS}), new
        #                        TimeSeries({id: 'series_2', records: NUMBER_RECORDS})])
        # expect(jtsDocument.getSeries('series_1')?.length).toEqual(NUMBER_RECORDS.length)
        # })

        # TODO extend test to other dataTypes as below
        # describe('static methods', () => {
        #   test('construct from JSON', () => {
        #     expect(() => JtsDocument.from('')).toThrow()
        #     const jtsDocument = new JtsDocument()
        #     jtsDocument.addSeries(new TimeSeries({ type: 'NUMBER', records: NUMBER_RECORDS }))
        #     jtsDocument.addSeries(new TimeSeries({ type: 'TEXT', records: TEXT_RECORDS }))
        #     jtsDocument.addSeries(new TimeSeries({ type: 'TIME', records: TIME_RECORDS }))
        #     jtsDocument.addSeries(new TimeSeries({ type: 'COORDINATES', records: COORDINATES_RECORDS }))
        #     const jtsDocument2 = JtsDocument.from(jtsDocument.toJSON()) || new JtsDocument()
        #     expect(jtsDocument).toEqual(jtsDocument2)
        #     expect(jtsDocument.toString()).toEqual(jtsDocument2.toString())

    def test_subSecondRecords(self):
        jts_doc = JtsDocument()
        jts_doc.addSeries(TimeSeries(name="ts", identifier="series_1", records=self.NUMBER_SUBSECOND_RECORDS))
        self.assertEqual(len(jts_doc), 1)
        ts = jts_doc.getSeries(identifier="series_1")
        self.assertEqual(len(ts.records), 5)
        self.assertEqual(len(jts_doc.toJSON()['data']), 5)
    
    def test_sortingSubSecondRecords(self):
        expected = JtsDocument()
        expected.addSeries(TimeSeries(name="ts", identifier="series_1", records=self.NUMBER_SUBSECOND_RECORDS))
        
        jts_doc = JtsDocument()
        jts_doc.addSeries(TimeSeries(name="ts", identifier="series_1", records=self.NUMBER_SUBSECOND_RECORDS_OUT_OF_ORDER))
        
        self.assertEqual(len(jts_doc), 1)
        self.assertEqual(jts_doc.toJSON()['header']['startTime'], expected.toJSON()['header']['startTime'])
        self.assertEqual(jts_doc.toJSON()['header']['endTime'], expected.toJSON()['header']['endTime'])
        for i in range(5): 
            self.assertEqual(jts_doc.toJSON()['data'][i]['ts'], expected.toJSON()['data'][i]['ts'])

        self.assertEqual(jts_doc.toJSON(), expected.toJSON())
        self.assertEqual(jts_doc.toJSONString(), expected.toJSONString())

        if __name__ == '__main__':
            unittest.main()
