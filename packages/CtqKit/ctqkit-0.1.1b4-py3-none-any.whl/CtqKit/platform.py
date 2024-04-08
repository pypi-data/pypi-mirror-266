import datetime
import json
import logging
import re
from time import time, sleep
from typing import Optional, Union, List, Dict

import requests
import numpy as np

from .account import Account

logger = logging.getLogger(__name__)


class RequestError(Exception):
    pass


class Platform:
    """管理任务"""

    SUCCESS_CODE = 200

    def __init__(
            self,
            login_token: str = None,
            account: Account = None,
            machine: str = None
    ):
        """
        Task Management of Tianyan（天衍） Quantum Computing Cloud platform

        Users need to provide account or token. Choose one of the two.

        :param login_token: login token, can be found here https://qc.zdxlz.com/userCenter
        :param account: Account object
        :param machine: Quantum or simulator machine name
        """
        assert login_token or account, "The user must provide a token or manually create an Account object"
        if login_token:
            account = Account(login_key=login_token)
        self.account = account
        self._machine_name = machine

        self._cache_machine_list = None
        self._cache_language_list = None

    @property
    def machine_list(self, cache=True) -> list:
        """
        Quantum or simulator machine list

        :return:
        """
        if self._cache_machine_list and isinstance(self._cache_machine_list, list):
            return self._cache_machine_list
        resp = requests.get(
            f'{self.account.base_url}/qccp-quantum/experiment/quantum/computer/by/user',
            headers={
                'Authorization': f'Bearer {self.account.access_token}',
                'ApiCode': 'byUser',
                'RequestTime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        )
        data = resp.json()
        if data.get('code') != self.SUCCESS_CODE:
            raise RequestError(f"get machine list failed: {data.get('msg')}")
        d = data.get('data')
        if cache:
            self._cache_machine_list = d
        return d

    @property
    def language_list(self, cache=True) -> list:
        """
        quantum language list

        :return:
        """
        if self._cache_language_list and isinstance(self._cache_language_list, list):
            return self._cache_language_list
        resp = requests.get(
            f'{self.account.base_url}/qccp-quantum/experiment/quantum/language/findAll',
            headers={
                'Authorization': f'Bearer {self.account.access_token}',
                'ApiCode': 'findAll',
                'RequestTime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        )
        data = resp.json()
        if data.get('code') != self.SUCCESS_CODE:
            raise RequestError(f"get language list failed: {data.get('msg')}")
        d = data.get('data')
        if cache:
            self._cache_language_list = d
        return d

    def isq_to_qcis(self, circuit: str) -> list:
        """
        编译
        :param circuit:
        :return:
        """

    def create_experiment_collection(
            self,
            name: str,
            remark: Optional[str] = ""
    ):
        """create a new collection of experiments.

        :param name: new experiment collection Name.
        :param remark: experimental remarks.

        :return: new experimental collection id
        """
        url = f'{self.account.base_url}/qccp-quantum/experiment/create'
        data = {"name": name, "remark": remark}
        headers = {
            "Authorization": f'Bearer {self.account.access_token}',
            'ApiCode': 'experimentCreate',
            'RequestTime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        res = requests.post(url, json=data, headers=headers)
        if res.status_code != 200:
            raise RequestError(f'create experiment failed, status code:{res.status_code}')
        result = res.json()
        code = result.get('code', -1)
        msg = result.get('msg', 'create experiment failed')
        if code != self.SUCCESS_CODE:
            raise RequestError(f'create experiment failed: {msg}')
        collect_id = result.get('data').get('id')
        return collect_id

    def get_experiment_collection_list(
            self,
            start: int = 0,
            count: int = 100
    ):
        """get experiments collection list.

        :param start: start order.
        :param count: query count.

        :returns data:
            records: collection list.
            total: total count of experiments collection list.

        """
        url = f'{self.account.base_url}/qccp-quantum/experiment/byUser?current={start}&size={count}'
        headers = {
            "Authorization": f'Bearer {self.account.access_token}',
            'ApiCode': 'getExperimentByUser',
            'RequestTime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        res = requests.get(url, headers=headers)
        if res.status_code != self.SUCCESS_CODE:
            raise RequestError(f'create experiment failed, status code:{res.status_code}')
        result = res.json()
        code = result.get('code', -1)
        msg = result.get('msg', 'query failed')
        if code != self.SUCCESS_CODE:
            raise RequestError(f'create experiment failed: {msg}')
        return result.get('data')

    def create_experiment(
            self,
            collection_id: str,
            exp_data: str,
            machine_code: Optional[str] = None,
            name: Optional[str] = "",
            language: Optional[str] = "qcis",
    ):
        """create the experiment and return the experiment ID.

        :param collection_id: the result returned by the create_experiment_collection interface, experimental set id
        :param exp_data: experimental content, qics or isq circuit.
        :param name: experimental Details Name. Defaults to "".
        :param machine_code: backend machine code.
        :param language: Quantum computer language, including ['isq', 'qcis']. Defaults to "qcis".

        :returns id: the experiment ID
        """
        language_list = {language['code'].lower() for language in self.language_list}
        language = language.lower()
        if language not in language_list:
            raise ValueError(
                f'Failed to save the experiment, quantum language can only be selected from {language_list}.')
        if machine_code is None:
            if self.machine is None:
                raise ValueError("No machine")
            machine_code = self.machine
        # format circuit
        lines = []
        for line in exp_data.split('\n'):
            lines.append(' '.join([word for word in line.strip().split() if word]))
        exp_data = '\n'.join(lines)

        if language == 'qcis':
            exp_data = exp_data.upper()

        url = f'{self.account.base_url}/qccp-quantum/experiment/experiment/detail'
        data = {
            "inputCode": exp_data,
            "experimentId": collection_id,
            "languageCode": language,
            "name": name,
            "source": "SDK",
            "computerCode": machine_code
        }
        headers = {
            "Authorization": f'Bearer {self.account.access_token}',
            'ApiCode': 'detail',
            'RequestTime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        res = requests.post(url, json=data, headers=headers)
        status_code = res.status_code
        if status_code != 200:
            raise RequestError(f'创建实验接口请求失败, status_code:{status_code}')
        result = res.json()
        code = result.get('code', -1)
        msg = result.get('msg', '创建实验失败')
        if code != self.SUCCESS_CODE:
            raise RequestError(f'创建实验失败：{msg}')
        exp_id = result.get('data').get('id')
        return exp_id

    def get_experiment_list(
            self,
            collection_id: int,
            start: int = 1,
            count: int = 100
    ):
        """
        get experiment list for collection_id
        :param collection_id: collection id
        :param start: start index
        :param count: count

        """
        url = f'{self.account.base_url}/qccp-quantum/experiment/detailList'
        headers = {
            "Authorization": f'Bearer {self.account.access_token}',
            'ApiCode': 'experimentDetailList',
            'RequestTime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        params = {
            'current': start,
            'size': count,
            'experimentId': str(collection_id)
        }
        res = requests.get(url, headers=headers, params=params)
        if res.status_code != self.SUCCESS_CODE:
            raise RequestError(f'create experiment failed, status code:{res.status_code}')
        result = res.json()
        code = result.get('code', -1)
        msg = result.get('msg', 'query failed')
        if code != self.SUCCESS_CODE:
            raise RequestError(f'create experiment failed: {msg}')
        return result.get('data')

    def run_experiment(
            self,
            exp_id: str,
            num_shots: Optional[int] = 10000,
            is_verify: Optional[bool] = True
    ):
        """running the experiment returns the query result id.

        Args:
            exp_id:
                the result returned by the save_experiment interface, experimental id
            num_shots:
                number of repetitions per experiment. Defaults to 10000. max 10000
            is_verify:
                Is the circuit verified.True verify, False do not verify. Defaults to True.

        Returns:
            Union[int, str]: 0 failed, not 0 successful, success returns the query id
        """
        data = {
            "experimentDetailId": exp_id,
            "shots": num_shots,
            "is_verify": is_verify,
            "source": "sdk",
        }
        return self._run_experiment(data)

    def _run_experiment(self, data):
        """
        提交任务，并运行

        :param data:
        :return:
        """
        url = f'{self.account.base_url}/qccp-quantum/experiment/sdkCommit'
        headers = {
            "Authorization": f'Bearer {self.account.access_token}',
            'ApiCode': 'commit',
            'RequestTime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        res = requests.post(url, json=data, headers=headers)
        status_code = res.status_code
        if status_code != 200:
            raise RequestError(f'运行实验接口请求失败, status_code:{status_code}')
        result = res.json()
        code = result.get('code', -1)
        msg = result.get('msg', '运行实验失败')
        if code != self.SUCCESS_CODE:
            raise RequestError(f'运行实验失败：{msg}')
        task_id = result.get('data').get('experimentTaskId')
        return task_id

    def submit_job(
            self,
            circuit: Optional[Union[List, str]] = None,
            exp_name: Optional[str] = "exp0",
            parameters: Optional[List[List]] = None,
            values: Optional[List[List]] = None,
            num_shots: Optional[int] = 5000,
            collection_id: Optional[str] = None,
            exp_id: Optional[str] = None,
            language: Optional[str] = 'qcis',
            version: Optional[str] = "version01",
            is_verify: Optional[bool] = True
    ):
        """submit experimental tasks

        Args:
            circuit:
                experimental content, qics. Defaults to None.
            exp_name:
                new experiment collection Name. Defaults to 'exp0'.
            parameters:
                parameters that need to be assigned in the experimental content. Defaults to None.
            values:
                The values corresponding to the parameters that need to be assigned in the experimental content. Defaults to None.
            num_shots:
                number of repetitions per experiment. Defaults to 5000, max 10000.
            collection_id:
                the result returned by the create_experiment_collection interface, experimental set id. Defaults to None.
            exp_id:
                the result returned by the save_experiment interface, experimental id. Defaults to None.
            version:
                version description. Defaults to 'version01'.
            is_verify:
                Is the circuit verified.True verify, False do not verify. Defaults to True.
        description:
            There are some parameter range limitations when using batch submission circiuts.
            1. circuits length less than 50
                numshots maximum 100000
                the number of measurement qubits is less than 15
            2. circuits length greater than 50 but less than 100
                numshots maximum 50000
                the number of measurement qubits is less than 30
            3. circuits length greater than 100 but less than 600
                numshots maximum 10000
                the number of measurement bits is less than the number of all available qubits
            4. When the circuit is none, the exp_id cannot be none and the lab_id needs to be none,
            5. When the circuit is not none, when the circuit is multiple lines, the version and exp_id need to be none,
                and the line will be saved under the default collection if the lab_id or exp_name is not transmitted.
            6. When the circuit is not none, when the circuit is a single line, exp_id need none,
                version does not transmit to generate the default, lab_id or exp_name does not transmit the line is saved under the default collection.

        description:
            1. When the circuit is none, the exp_id cannot be none and the lab_id needs to be none,
            2. When the circuit is not none, when the circuit is multiple lines, the version and exp_id need to be none,
               and the line will be saved under the default collection if the lab_id or exp_name is not transmitted.
            3. When the circuit is not none, when the circuit is a single line, exp_id need none,
               version does not transmit to generate the default, lab_id or exp_name does not transmit the line is saved under the default collection.
        Returns:
            Union[int, str]: 0 failed, not 0 successful, success returns the query id.
        """
        assert num_shots <= 10000, 'num_shots should be less than 10000'
        if isinstance(circuit, str):
            circuit = [circuit]
        if len(circuit) > 1:
            version = None
        if circuit and parameters and values and len(parameters) == len(circuit) == len(values):
            new_circuit = self.assign_parameters(circuit, parameters, values)
            if not new_circuit:
                raise ValueError('无法为线路赋值，请检查线路，参数和参数值之后重试')
        else:
            new_circuit = circuit
        data = [{
            "exp_id": exp_id,
            "experimentId": collection_id,
            "inputCode": c,
            "languageCode": language,
            "name": f'{exp_name}.{i}',
            "shots": num_shots,
            "source": "sdk",
            "computerCode": self.machine,
            "experimentDetailName": version,
            "is_verify": is_verify
        } for i, c in enumerate(new_circuit)]
        return self._batch_run_experiment(data)

    def _batch_run_experiment(self, data):
        """
        批量提交任务，返回任务 id 列表，并后台排队运行
        todo: 接口未完成

        :param data:
        :return:
        """
        url = f'{self.account.base_url}/qccp-quantum/experiment/runContentList'
        headers = {
            "Authorization": f'Bearer {self.account.access_token}',
            'ApiCode': 'QuantumRunContentList',
            'RequestTime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        res = requests.post(url, json=data, headers=headers)
        status_code = res.status_code
        if status_code != 200:
            raise RequestError(f'运行实验接口请求失败, status_code:{status_code}')
        result = res.json()
        code = result.get('code', -1)
        msg = result.get('msg', '运行实验失败')
        if code != self.SUCCESS_CODE:
            raise RequestError(f'运行实验失败：{msg}')
        task_ids = result.get('data')
        return task_ids

    @staticmethod
    def assign_parameters(
            circuits: List[str],
            parameters: List[List],
            values: List[List]
    ):
        """Check if the number of parameters, values match the circuit definition

        :param circuits: string list, QCIS circuit definition with or without parameter place holder
        :param parameters: list or ndarray of strings, parameters to be filled
        :param values: list or ndarray of floats, values to be assigned

        :return circuit: circuit with parameters replaced by values or empty string,
            empty string occurs when errors prevents parameters to be assigned

        :example:
        # Define a QCIS circuit with placeholders
        circuits = ['H(q[0]); CX(q[0], q[1]); RZ(q[1], {theta});']

        # Parameters and their corresponding values
        parameters = [['theta']]
        values = [[3.1415]]

        # Assign the values to the circuit
        circuit = self.assign_parameters(circuits, parameters, values)
        print(circuit)

        # Expected Output:
        # ['H(q[0]); CX(q[0], q[1]); RZ(q[1], 3.1415);']

        :note: For ISQ programs, it's important to use double braces {{}} in the original code block to
           escape the format placeholders. This is necessary because the single brace {} is used as
           a special character in the `str.format` method.

        ```isq
        import std;
        qbit q[2];
        unit main() {{
            H(q[0]);
            H(q[1]);
            M(q[0]);
            M(q[1]);
        }}
        ````

        """
        p = re.compile(r'\{(\w+)}')
        new_circuits = []
        for circuit, parameter, value in zip(circuits, parameters, values):
            circuit_parameters = p.findall(circuit)
            if circuit_parameters:
                if not value:
                    raise ValueError(f'线路含有参数{circuit_parameters}, 请提供相应的参数值')
                else:
                    # 去重
                    circuit_parameters = set(circuit_parameters)
                    if len(circuit_parameters) != len(value):
                        raise ValueError(f'线路含有{len(circuit_parameters)}个参数, 您提供了{len(value)}个参数值')
                    elif parameter and len(circuit_parameters) != len(parameter):
                        raise ValueError(
                            f'线路含有{len(circuit_parameters)}个参数, 您提供了{len(parameter)}个参数')
                    elif set(parameter) != set(circuit_parameters):
                        raise ValueError('线路中的参数与您输入的参数名称不符')
                    else:
                        param_dic = {p: v for p, v in zip(parameter, value)}
                        new_circuits.append(circuit.format(**param_dic))
            elif parameter or value:
                raise ValueError('线路定义中不含有参数，无法接受您输入的参数或参数值')
            else:
                new_circuits.append(circuit.format({}))
        return new_circuits

    def compile_to_qcis(self, circuit, language='isq'):
        """
        isq circuit compile to qcis

        :param circuit: circuit
        :param language: circuit language
        :return:
        """
        languages = ['isq']
        assert language in languages, f'language must be {languages}'
        url = f'{self.account.base_url}/qccp-quantum/experiment/experiment/compile'
        headers = {
            "Authorization": f'Bearer {self.account.access_token}',
            'ApiCode': 'quantumComputerZDX',
            'RequestTime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        data = {
            "source": "sdk",
            "languageCode": language,
            "inputCode": circuit,
            "computerCode": self.machine,
            'name': 'exp' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        res = requests.post(url, json=data, headers=headers)
        status_code = res.status_code
        if status_code != 200:
            raise RequestError(f'运行编译接口请求失败, status_code:{status_code}')
        result = res.json()
        code = result.get('code', -1)
        msg = result.get('msg', '运行编译失败')
        if code != self.SUCCESS_CODE:
            raise RequestError(f'运行实验失败：{msg}')
        return result.get('data').get('qcis')

    def query_experiment(
            self,
            query_id: Union[str, List[str]],
            max_wait_time: Optional[int] = 60
    ):
        """query experimental results

        :param query_id: the result returned by the run_experiment interface, experimental set id
        :param max_wait_time: maximum waiting time for querying experiments. Defaults to 60.

        description:
            The maximum number of experimental result queries supported by the server is 50.
            If there are more than 50, an error message will be displayed.

        :return:
            Union[int, str]: 0 failed, not 0 successful, success returns the experimental result
        """
        if isinstance(query_id, str):
            query_id = [query_id]
        t0 = time()
        while time() - t0 < max_wait_time:
            try:
                url = f'{self.account.base_url}/qccp-quantum/experiment/getResultByIds'
                headers = {
                    "Authorization": f'Bearer {self.account.access_token}',
                    'ApiCode': 'getResultByIds',
                    'RequestTime': self.current_datetime()
                }
                # data = {"query_ids": query_id}
                data = query_id
                res = requests.post(url, json=data, headers=headers)
                status_code = res.status_code
                if status_code != 200:
                    raise RequestError(f'查询接口请求失败, status_code:{status_code}')
                result = res.json()
                code = result.get('code', -1)
                msg = result.get('msg', '查询实验失败')
                if code != self.SUCCESS_CODE:
                    raise RequestError(f'查询实验失败：{msg}')
                query_exp = result.get('data')
                if query_exp:
                    resp = []
                    for exp in query_exp:
                        if isinstance(exp, str):
                            exp = json.loads(exp)
                        resp.append(exp)

                    return resp
            except:
                continue
            print(f'查询实验结果请等待: {{:.2f}}秒'.format(5))
            sleep(5)
        raise Exception('查询实验结果失败, 实验结果为空')

    def download_config(
            self,
            # read_time=None,
            machine: str = '',
            save_file: bool = True
    ):
        """download experimental parameters.

        # :param read_time: select configuration data according to the reading time, and the parameter format is yyyy-MM-dd HH:mm:ss, Defaults to None.
        :param machine:  machine name
        :param save_file: the parameter is True to write to the file, and False to directly return the experimental parameters. Defaults to True.

        :return: Union[int, str]: 0 failed, not 0 successful, success returns the experimental parameters.
        """

        url = f'{self.account.base_url}/qccp-quantum/experiment/downloadConfig'
        headers = {
            "Authorization": f'Bearer {self.account.access_token}',
            'ApiCode': 'downloadConfig',
            'RequestTime': self.current_datetime()
        }
        if not machine:
            machine = self.machine

        res = requests.get(url, headers=headers, params={'computerCode': machine})
        status_code = res.status_code
        if status_code != 200:
            raise Exception(f'下载实验参数失败接口请求失败, status_code:{status_code}')
        result = res.json()
        code = result.get('code')
        if code != self.SUCCESS_CODE:
            msg = result.get('msg', '下载实验参数失败')
            raise RequestError(f'下载实验参数失败:{msg}')
        data = result.get('data')
        try:
            data = json.loads(data)
        except Exception as e:
            raise Exception("config file parse error")
        if save_file:
            with open(f'./{self.machine}_config_param_{self.current_datetime()}.json', 'w') as f:
                f.write(json.dumps(data))
        return data

    @staticmethod
    def current_datetime(fmt='%Y-%m-%d %H:%M:%S'):
        return datetime.datetime.now().strftime(fmt)

    @property
    def machine(self):
        return self._machine_name

    @machine.setter
    def machine(self, machine_name: str):
        """set the machine name.

        :param machine_name: name of quantum computer or simulator .
        """
        self._machine_name = machine_name

    def qcis_check_regular(self, qcis_raw: str, machine: str = ''):
        """qcis regular check,normal returns 1, abnormal returns 0

        :param qcis_raw: qcis
        :param machine: target machine name

        :return:
            Union[int, str]: 0 failed, not 0 successful, successfully returned the input qics.
        """
        url = f'{self.account.base_url}/qccp-quantum/experiment/qcisRule'
        data = {
            "computerCode": machine or self.machine,
            "inputCode": qcis_raw
        }
        headers = {
            "Authorization": f'Bearer {self.account.access_token}',
            'ApiCode': 'qcisRule',
            'RequestTime': self.current_datetime()
        }
        res = requests.post(url, json=data, headers=headers)
        status_code = res.status_code
        if status_code != 200:
            raise RequestError(f'qcis检验失败接口请求失败, status_code:{status_code}')
        result = json.loads(res.text)
        code = result.get('code', -1)
        msg = result.get('msg', 'qcis检验失败')
        if code != self.SUCCESS_CODE:
            raise RequestError(f'qcis检验失败: {msg}')
        return qcis_raw

    # 量子态概率矫正
    def probability_calibration(self, result: Dict, config_json: Optional[Dict] = None):
        """correction of the measured probability of 01 quantum state.

        :param result: the results returned after query_experiment.
        :param config_json: experimental parameters of quantum computer. \
                config_json value is None, read the latest experimental parameters for calculation. \
                Defaults to None.

        Raises:
            Exception: cannot calibrate probability with fidelity.

        Returns:
            Dict: corrected probability.
        """
        CM_CACHE = {}
        if config_json is None:
            config_json = self.download_config(save_file=False)
        qubit_num = [f'Q{i}' for i in result.get('resultStatus')[0]]
        n = len(qubit_num)  # 测量比特个数
        qubits = config_json['readout']['readoutArray']['|0> readout fidelity']['qubit_used']
        readout_fidelity0 = config_json['readout']['readoutArray']['|0> readout fidelity']['param_list']
        readout_fidelity1 = config_json['readout']['readoutArray']['|1> readout fidelity']['param_list']
        iq2prob_fidelity = [[readout_fidelity0[qubits.index(q)], readout_fidelity1[qubits.index(q)]] for q in qubit_num]
        P = self.readout_data_to_state_probabilities_whole(result)
        Pm = list(P.values())
        if not isinstance(iq2prob_fidelity[0], list):
            iq2prob_fidelity = [iq2prob_fidelity]
        f = tuple([float(fi) for fi in sum(iq2prob_fidelity, [])])
        if f not in CM_CACHE:
            inv_CM = 1
            for k in iq2prob_fidelity[::-1]:
                F00 = k[0]
                F11 = k[1]
                if F00 + F11 == 1:
                    raise Exception(f'Cannot calibrate probability with fidelity: [{F00}, {F11}]')
                inv_cm = np.array([[F11, F11 - 1], [F00 - 1, F00]]) / (F00 + F11 - 1)
                inv_CM = np.kron(inv_CM, inv_cm)
            CM_CACHE[f] = inv_CM
        else:
            inv_CM = CM_CACHE[f]
        Pi = np.dot(inv_CM, (np.array(Pm, ndmin=2).T))
        Pi = {bin(idx)[2:].zfill(n): k[0] for idx, k in enumerate(Pi)}
        return Pi

    @staticmethod
    def probability_correction(probabilities):
        """correction of the measured probability of 01 quantum state.
           If there is a probability greater than 1, change this item to 1.
           If there is anything less than 0, change the item to 0.

        :param probabilities: corrected probability.

        :return: corrected probability.
        """
        abnormal_fidelity_list = list(filter(lambda x: x < 0 or x > 1, probabilities.values()))
        if not abnormal_fidelity_list:
            return probabilities
        for k, v in probabilities.items():
            if v > 1:
                probabilities[k] = 1
            elif v < 0:
                probabilities[k] = 0
        fidelity_sum = sum(probabilities.values())
        for k, v in probabilities.items():
            probabilities[k] = v / fidelity_sum
        return probabilities

    @staticmethod
    def get_coupling_map(config_json: Dict):
        """
        get coupling map
        :param config_json: config json
        :return:
        """
        qubits = config_json['overview']['qubits']
        qubits_used = config_json['qubit']['singleQubit']['gate error']['qubit_used']
        disable_qubits = [q for q in qubits if q not in qubits_used]
        coupler_map = config_json['overview']['coupler_map']
        adjacency_list = []
        for Q1, Q2 in coupler_map.values():
            q1 = int(Q1[1:])
            q2 = int(Q2[1:])
            if Q1 in disable_qubits or Q2 in disable_qubits: continue
            adjacency_list.append([q1, q2])
        return adjacency_list
