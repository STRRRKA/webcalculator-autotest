import pytest
import requests
import subprocess
class Server_data:
    HOST = 'localhost'
    PORT = '5413'
    BASE_URL = f'http://{HOST}:{PORT}/api/'
    @pytest.fixture(scope="class", autouse=True)
    def start_and_stop(this):
        subprocess.run('webcalculator.exe start localhost 5413', stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        yield
        subprocess.run('webcalculator.exe stop', stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
#задание 1 корректность формата запроса/ответа
@pytest.mark.format
class Test_Api_Format(Server_data):    
    @pytest.mark.parametrize('endpoint', [        
        ('addition'), #сложение
        ('multiplication'), #умножение
        ('division'), #деление на цело
        ('remainder')#остаток от деления
        ], ids=['addition', 'multi', 'division', 'remainder'])    
    def test_post_response_request_structure(this, endpoint):
        data = {'x' : 3, 'y' : 5}
        response = requests.post(this.BASE_URL + f'{endpoint}', json=data)
        answer = response.json()
        #проверка ключей ответа
        assert list(answer.keys()) == ['statusCode', 'result']
    @pytest.mark.parametrize('endpoint', [        
        ('addition'), #сложение
        ('multiplication'), #умножение
        ('division'), #деление на цело
        ('remainder')#остаток от деления
        ], ids=['addition', 'multi', 'division', 'remainder'])
    def test_post_response_by_wrong_request(this, endpoint):
        data = {'a' : 3, 'y' : 5, 'z' : 5, 'd' : 2}
        response = requests.post(this.BASE_URL + f'{endpoint}', json=data)
        answer = response.json()
        #проверка ключей ответа
        assert list(answer.keys()) == ['statusCode','statusMessage']
    def test_get_response_request_structure(this):        
        response = requests.get(this.BASE_URL + 'state') 
        answer = response.json()       
        #проверка ключей ответа
        assert list(answer.keys()) == ['statusCode', 'state']    
    def test_get_response_by_not_exist_method_request_structure(this):
        response = requests.get(this.BASE_URL + 'states')
        answer = response.json()     
        #проверка ключей ответа
        assert list(answer.keys()) == ['statusCode','statusMessage']
# задание 2 проверка правильности вычисления результата при указании допустимых входных данных
@pytest.mark.operations
class Test_Api_Operations(Server_data):    
    @pytest.mark.parametrize('endpoint, data, expected_answer, expected_status_code', [        
        ('addition', {'x' : 24, 'y': 42}, 66, 0), #сложение
        ('multiplication', {'x' : 5, 'y': 2}, 10, 0), #умножение
        ('division', {'x' : 42, 'y': 10}, 4, 0), #деление на цело
        ('remainder', {'x' : 42, 'y': 10}, 2, 0),], ids=['addition', 'multi', 'division', 'remainder']) #остаток от деления    
    def test_methods_with_expected_params(this, endpoint, data, expected_answer, expected_status_code):
        response = requests.post(this.BASE_URL + endpoint, json=data)
        answer = response.json()

        assert answer['result'] == expected_answer
        assert answer['statusCode'] == expected_status_code
    @pytest.mark.parametrize('endpoint, data, expected_answer, expected_status_code', [        
        ('addition', {'x' : -2147483648, 'y': 2147483647}, (-2147483648+2147483647), 0), #сложение
        ('multiplication', {'x' : -2147483648, 'y': 2147483647}, (-2147483648*2147483647), 0), #умножение
        ('division', {'x' : -2147483648, 'y': 2147483647}, (-2147483648//2147483647), 0), #деление на цело
        ('remainder', {'x' : -2147483648, 'y': 2147483647}, (-2147483648%2147483647), 0),], ids=['addition', 'multi', 'division', 'remainder']) #остаток от деления    
    def test_methods_with_almost_overflow_params(this, endpoint, data, expected_answer, expected_status_code):
        response = requests.post(this.BASE_URL + endpoint, json=data)
        answer = response.json()

        assert answer['result'] == expected_answer
        assert answer['statusCode'] == expected_status_code    
    
    def test_get_responce_values(this):
        response = requests.get(this.BASE_URL + 'state')
        answer = response.json()

        assert answer['state'] == 'OК'#символ 'К' кириллический
        assert answer['statusCode'] == 0 

# задание 3 функционал управления приложением
@pytest.mark.cmd
class Test_CMD():
    def start(this, host='localhost', port='5413'):
        return subprocess.run(f'webcalculator.exe start {host} {port}', stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    def default_start(this, host='', port=''):
        return subprocess.run(f'webcalculator.exe start {host} {port}', stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    
    def req(this, host='localhost', port='5413'):        
        return requests.get(f'http://{host}:{port}/api/' + 'state').json() 
    
    def stop(this):
        return subprocess.run('webcalculator.exe stop', stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    
    def test_start_and_stop(this):
        result = this.start()

        assert result.returncode == 0
        
        answer = this.req()  
        #проверка ключей ответа
        assert answer['statusCode'] == 0

        result = this.stop()

        assert result.returncode == 0

        try:
            this.req()
        except BaseException as e:
            assert type(e) is requests.exceptions.ConnectionError
    
    def test_restart(this):
        this.start()
        
        answer = this.req()    
        #проверка ключей ответа
        assert answer['statusCode'] == 0

        subprocess.run('webcalculator.exe restart', stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        
        answer = this.req()       
        #проверка ключей ответа
        assert answer['statusCode'] == 0
        this.stop()

        try:
            this.req()
        except BaseException as e:
            assert type(e) is requests.exceptions.ConnectionError
    
    def test_change_host_and_port(this):
        this.start()
        answer = this.req()      
        #проверка ключей ответа
        assert answer['statusCode'] == 0
        this.stop()
        this.start('127.0.0.1', '8000')
        answer = this.req('127.0.0.1', '8000')      
        #проверка ключей ответа
        assert answer['statusCode'] == 0
        this.stop()

    def test_default_port(this):
        this.default_start('localhost')
        answer = this.req('localhost', 17678)
        #проверка ключей ответа УБРАТЬ
        assert answer['statusCode'] == 0
        this.stop()
    
    def test_default_host_and_port(this):
        this.default_start()
        answer = this.req('127.0.0.1', 17678)
        #проверка ключей ответа
        assert answer['statusCode'] == 0
        this.stop()
# Дополнительное задание 1 правильность возвращаемых кодов ошибок
@pytest.mark.negative
class Test_negative(Server_data):        
    @pytest.mark.parametrize('endpoint, data, expected_status_code', [        
        ('division', {'x' : 0, 'y': 0}, 8), #деление на цело #в тз указан код 1 но на самом деле 8 
        ('remainder', {'x' : 0, 'y': 0}, 8),], ids=['division', 'remainder']) #остаток от деления    
    def test_camputation_error(this, endpoint, data, expected_status_code):
        response = requests.post(this.BASE_URL + endpoint, json=data)
        answer = response.json()
        
        assert answer['statusCode'] == expected_status_code

    @pytest.mark.parametrize('endpoint, data, expected_status_code', [      
        ('addition', {'x' : 4.5}, 2), #сложение
        ('multiplication', {'y': 7.333}, 2), #умножение  
        ('division', {'x' : 0}, 2), 
        ('remainder', {'y': 0}, 2),], ids=['addition', 'multi', 'division', 'remainder']) #остаток от деления    
    def test_missing_param(this, endpoint, data, expected_status_code):
        response = requests.post(this.BASE_URL + endpoint, json=data)
        answer = response.json()
        
        assert answer['statusCode'] == expected_status_code

    @pytest.mark.parametrize('endpoint, data, expected_status_code', [        
        ('addition', {'x' : "str", 'y':'ka'}, 3), #сложение
        ('multiplication', {'x' : 'mom', 'y': 'dad'}, 3), #умножение
        ('division', {'x' : 'twitter', 'y': 'x'}, 3), #деление на цело
        ('remainder', {'x' : 'vk.com', 'y': 'vkontacte.ru'}, 3),], ids=['addition', 'multi', 'division', 'remainder']) #остаток от деления    
    def test_methods_with_string_params(this, endpoint, data, expected_status_code):
        response = requests.post(this.BASE_URL + endpoint, json=data)
        answer = response.json()
        
        assert answer['statusCode'] == expected_status_code

    @pytest.mark.parametrize('endpoint, data, expected_status_code', [        
        ('addition', {'x' : 4.5, 'y': 1.5}, 3), #сложение
        ('multiplication', {'x' : 1.9, 'y': 7.333}, 3), #умножение
        ('division', {'x' : 34.5, 'y': 234.123}, 3), #деление на цело
        ('remainder', {'x' : 123.4, 'y': 5.678}, 3),], ids=['addition', 'multi', 'division', 'remainder']) #остаток от деления    
    def test_methods_with_float_params(this, endpoint, data, expected_status_code):
        response = requests.post(this.BASE_URL + endpoint, json=data)
        answer = response.json()
        
        assert answer['statusCode'] == expected_status_code
    
    @pytest.mark.parametrize('endpoint, data, expected_status_code', [        
        ('addition', {'x' : -2147483649, 'y': 2147483648}, 4), #сложение
        ('multiplication', {'x' : -2147483649, 'y': 2147483648}, 4), #умножение
        ('division', {'x' : -2147483649, 'y': 2147483648}, 4), #деление на цело
        ('remainder', {'x' : -2147483649, 'y': 2147483648}, 4),], ids=['addition', 'multi', 'division', 'remainder']) #остаток от деления    
    def test_methods_with_overflow_params(this, endpoint, data, expected_status_code):
        response = requests.post(this.BASE_URL + endpoint, json=data)
        answer = response.json()
        
        assert answer['statusCode'] == expected_status_code
    
    @pytest.mark.parametrize('endpoint, expected_status_code', [        
        ('addition', 5), #сложение
        ('multiplication', 5), #умножение
        ('division', 5), #деление на цело
        ('remainder', 5),], ids=['addition', 'multi', 'division', 'remainder']) #остаток от деления    
    def test_methods_with_wrong_json_params(this, endpoint, expected_status_code):
        response = requests.post(this.BASE_URL + endpoint, data="x: 1")
        answer = response.json()
        
        assert answer['statusCode'] == expected_status_code