# 영화 추천 시스템 파이프라인 구축 과제
- 이미 정해진 영화에 대한 사용자의 과거 평점 데이터를 가져와 평점 기반으로 가장 인기있는 영화 추천
- 영화 평점 데이터는 API 를 통해 제공되며, 특정 기간의 영화 평점을 제공
- 해당 랭킹은 다운스트림에서 인기 영화를 추천할 때 사용할 수 있음

## 영화 평점 API
- 25M MovieLens 데이터 세트(https://grouplens.org/datasets/movielens/) 사용
- 데이터 세트는 62,000개의 영화에 대해 162,000 명의 유저가 평가한 2천5백만 개의 평점 데이터
- 데이터 세트는 flat file(ex) csv file) 로 제공되며, 이 파일을 Flask + REST API 로 구현하여 부분별로 제공받아야 함
- API 서빙을 위해 다중 컨테이너를 생성해야함
  - REST API 를 위한 컨테이너
  - Airflow 실행을 위한 컨테이너
- 컨테이너 구동 후 localhost 의 5000 port 로 영화 평점 API 에 접근 가능
- `http://localhost:5000` 접근시, API 에서 출력하는 `Hello from the Movie Rating API!` 메세지를 볼 수 있음 
- `http://localhost:5000/ratings` 를 통해 엔드포인트에 액세스하며, 사용자/비밀번호 인증이 필요  
  편의를 위해 사용자 이름 / 비밀번호는 airflow/airflow 로 설정
- 자격 인증 정보(credentials)를 입력하면 영화 평점의 초기 리스트를 받아옴  
  평점 데이터는 JSON 포맷으로 되어 있음
- 실제 평점 데이터는 `result` 필드 안에 포함되어 있으며, 필드 외에 2개의 필드가 더 있는데 `limit`, `offset` 임
- `limit` 은 결과 중 한번에 가져올 수 있는 레코드 개수를 의미하며, `offset`은 결과 중 몇 번째 결과부터 가져오는지를 의미
- 쿼리한 결과를 페이지별로 처리할 때 API 파라미터 중 offset 을 사용할 수 있음  
  예를 들어 다음 100개의 레코드를 가져올 때 offset 파라미터 값을 100으로 추가하여 사용  
  `http://localhost:5000/ratings?offset=100`
- 쿼리에서 한 번에 가져오는 레코드 수를 늘리려면 파라미터 중 `limit`을 사용  
  `http://localhost:5000/ratings?limit=1000`
- 특정 기간 동안의 평점 데이터를 가져오려면 `start_date` 와 `end_date` 파라미터를 사용하여 주어진 시작/종료 날짜 사이의 평점 데이터를 가져올 수 있음    
  `http://localhost:5000/ratings?start_date=2019-01-01&end_date=2019-01-02`
  
## 영화 추천 시스템 파이프라인 디렉토리 구조
- docker-compose file
- flask 실행을 위한 Python script
- DAG 실행을 위한 Python script 
```
├── dags
    ├── custom                        # dags 구현을 위한 help function
        ├── __init__.py               
        ├── hooks.py
        ├── opertors.py
        ├── ranking.py
        ├── sensors.py
    ├── 01_python.py                  # pythonOperator DAG
    ├── 02_hook.py                    # custom hook DAG
    ├── 03_operator.py                # jinja template + 
    ├── 04_sensor.py                  # custom sensor DAG
├── docker
    ├── movielens-api                 # api 를 위한 script
        ├── Dockerfile
        ├── app.py                    # flask endpoint 
        ├── fetch_ratings.py
        ├── requirements.txt
├── docker-compose.yml
├── packages
    ├── airflow-movielens            # airflow-movielens package
        ├── setup.py
        ├── src
            ├── airflow-movielens
                ├── __init__.py
                ├── hooks.py
                ├── operators.py
                ├── sensors.py    
├── readme.md
```

## docker-compose 실행
```shell
$ docker-compose up  # docker-compose 실행하여 이미지 생성
```