import datetime
import json
import threading
import time
import numpy as np

import serial


class RfidSensor():
    results = {}

    def __init__(self, arduino_port='/dev/cu.usbmodem143301', baud_rate=115200, duration=1 ):
        # Arduino가 연결된 시리얼 포트와 바우드 레이트 설정

        # 시리얼 연결 초기화
        self.ser = serial.Serial(arduino_port, baud_rate, timeout=1)
        self.ser.flush()



        # 장치가 데이터 전송 준비를 할 수 있도록 잠시 대기
        time.sleep(2)

        thread1 = threading.Thread(target=self._threading, args=(duration, ))
        thread1.start()


    def sensorClose(self):
        self.ser.close()

    def _threading(self, duration):
        while True:
            self._sensor_data(duration)


    def _sensor_data(self, duration=1):
        try:

            start_time = time.time()
            data_by_id = {}

            while time.time() - start_time < duration:
                try:
                    rowData = self.ser.readline()
                    # print(rowData)
                    # print(len(rowData))

                    if len(rowData) > 0:
                        strData = rowData.decode('utf-8', errors='ignore').rstrip()
                        isFlag = False

                        if strData != "" and len(strData) > 0:
                            data = strData
                            try:

                                data = json.loads(data)

                                # ID별로 데이터 저장
                                epc = data.get("epc")

                                if epc is not None:
                                    rssiDec = data.get("rssi_dec")
                                    typeData = data.get("type")

                                    if typeData != "dummy":
                                        isFlag = True
                                        if epc in data_by_id:
                                            data_by_id[epc].append(float(rssiDec))
                                        else:
                                            data_by_id[epc] = [float(rssiDec)]
                            except json.JSONDecodeError as e:
                                print(e)

                            if type(data) == dict and isFlag is True:
                                dDateTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                # print(dDateTime , " :: ", data)


                except Exception as e:
                    print(e)

            # 각 ID에 대한 표준편차 계산 및 출력
            if len(data_by_id.items()) > 0:
                # 거리 추정 결과
                self.results = self.estimate_distance(data_by_id)

                # 결과 출력
                # for sensor_id, (occurrence, std_dev, distance) in results.items():
                #     print(f"Sensor ID: {sensor_id}, Occurrence: {occurrence}, RSSI Std Dev: {std_dev:.2f}, Estimated Distance: {distance:.2f} meters")
        except Exception as e:
            print(e)
            self.sensorClose()


    def estimate_distance(self, data, rssi_at_1m=180, path_loss_exponent=3):
        """
        각 센서 ID 별로 발생 횟수와 값의 표준 편차를 계산하고, 거리를 추정하는 함수.

        :param data: 센서 ID를 키로 하고, 해당 센서의 RSSI 값들의 리스트를 값으로 하는 딕셔너리.
        :param rssi_at_1m: 1미터 거리에서의 RSSI 값.
        :param path_loss_exponent: 환경에 따라 달라지는 신호 감쇠 지수.
        :return: 센서 ID를 키로 하고, 해당 센서의 발생 횟수, RSSI 값의 표준 편차와 추정된 거리를 튜플로 가지는 딕셔너리.
        """

        # 센서 ID 오름차순으로 정렬
        sorted_data = {sensor_id: data[sensor_id] for sensor_id in sorted(data)}

        results = {}
        for sensor_id, rssi_values in sorted_data.items():
            occurrence = len(rssi_values)  # 발생 횟수
            std_dev_rssi = np.std(rssi_values)  # RSSI 값의 표준 편차
            avg_rssi = np.mean(rssi_values)  # RSSI 평균 값
            # 거리 추정
            distance = 10 ** ((rssi_at_1m - avg_rssi) / (10 * path_loss_exponent))
            results[sensor_id] = {
                "occurrence" : occurrence
                , "std_dev_rssi" : std_dev_rssi
                , "distance" : distance
            }
        return results


    def getData(self):
        return self.results


