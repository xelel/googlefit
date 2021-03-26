
from datetime import datetime, timedelta
from json import dumps
from os import name
import time
import json
import requests
from random import randint
accessToken = ''



def create_dataPointns(horario):
    # recebe uma data,converte pra nanosegundos, e uma representação para datapoints
    return int(time.mktime(horario.timetuple())) * 1000000000


def deleteDataSource(SourceId):
    #deleta algum data source com base no seu ID
    url = f"https://www.googleapis.com/fitness/v1/users/me/dataSources/+{SourceId}"

    headers = {'content-type': 'application/json',
               'Authorization': f'Bearer {accessToken}'}

    r = requests.delete(url, headers=headers)
    return r.content


def getDataSource():
    #Captura algum dataSource que esteja escrito
    url = "https://www.googleapis.com/fitness/v1/users/me/dataSources"
    headers = {'content-type': 'application/json',
               'Authorization': f'Bearer {accessToken}'}

    r = requests.get(url, headers=headers)

    if r.status_code == 200:
        with open('datasource.txt', 'w') as file:
            file.write(r.text)
        return r.text
    else:
        print(r.status_code)
        print(r.content)
        return False


def createDataSource(arquivo):
    #Cria algum data Source 
    url = "https://www.googleapis.com/fitness/v1/users/me/dataSources"

    headers = {'content-type': 'application/json',
               'Authorization': f'Bearer {accessToken}'}

    with open(f'{arquivo}', 'r') as file:
        dado = file.read()
    dado = json.loads(dado)
    dado['device']['uid'] = str(randint(0, 1000))
    dado = dumps(dado)

    with open(f'{arquivo}', 'w') as file:
        file.write(dado)
    #Escreve o dado escrito em JSON usando requests e o método post
    r = requests.post(url, headers=headers, data=dado)

    if r.status_code == 200:
        response = json.loads(r.content)
        dataSourceId = response['dataStreamId']
        with open('SourceIds.txt', 'a') as file:
            file.writelines(f'{dataSourceId}\n')

        return dataSourceId

    if r.status_code == 409:
        print('datasource ja existente, verifique na lista de DataSourceIds adicionados')

    else:
        print(r.status_code)
        print(r.content)
        return False


def create_dataset(startime, endtime, dataSourceId, point):
    #Cria um registro de atividade(dataset) para alguma atividade selecionada
    url = "https://www.googleapis.com/fitness/v1/users/me/dataSources/" + \
        dataSourceId+"/datasets/"+f"{str(startime)}-{str(endtime)}"

    headers = {'content-type': 'application/json',
               'Authorization': f'Bearer {accessToken}'}
    data = {
        "dataSourceId": dataSourceId,
        "minStartTimeNs": startime,
        "maxEndTimeNs": endtime,
        "point": point
    }

    r = requests.patch(url, headers=headers, data=json.dumps(data))

    if r.status_code == 200:
        response = json.loads(r.content)
        print(response)

    else:
        print(r.status_code)
        print(r.content)
        return False


def adicionar_velocidade_esteira(velocidade):
    """This data type captures the user's speed in meters per second. 
    The value represents the scalar magnitude of the speed, so negative values should not occur. 
    Because each data point represents the speed at the time of the reading, only the end time should be set. 
    This will be used as the timestamp for the reading.
    """
    # com.google.speed
    pass


def adicionar_distanciaPercorrida(d, tempo_Atividade):
    """This data type captures distance travelled by the user since the last reading, in meters. 
    The total distance over an interval can be calculated by adding together all the values during the interval. 
    The start time of each data point should represent the start of the interval in which the distance was covered. 
    The start time must be equal to or greater than the end time of the previous data point."""
    #cria uma data source para o atributo distancia no google fit
    id = createDataSource('distance.json')
    inicio = create_dataPointns(
        datetime.now()+timedelta(seconds=-tempo_Atividade))
    fim = create_dataPointns(
        datetime.now())
    point = {
        "dataTypeName": "com.google.distance.delta",
        "startTimeNanos": f"{inicio}",
        "endTimeNanos": f"{fim}",
        "value": [
            {
                "fpVal": f"{d}"
            }
        ]
    }
    #envia o json para o dataSource escolhido.
    create_dataset(inicio, fim, point=point, dataSourceId=id)


def adicionar_peso(p):
    id = createDataSource('weight.json')
    """This data type captures that user's weight in kilograms. 
    Because each data point represents the weight of the user at the time of the reading, 
    only the end time should be set. 
    This will be used as the timestamp for the reading."""
    now = create_dataPointns(datetime.now())
    point = {
        "dataTypeName": "com.google.weight",
        "startTimeNanos": f"{now}",
        "endTimeNanos": f"{now}",
        "value": [
            {
                "fpVal": f"{p}"
            }
        ]
    }
    create_dataset(now, now, point=point, dataSourceId=id)


def adicionar_altura(altura):
    """This data type captures that user's height in meters. 
    Because each data point represents the height of the user at the time of the reading, 
    only the end time should be set. 
    This will be used as the timestamp for the reading."""
    """This data type captures that user's weight in kilograms. 
    Because each data point represents the weight of the user at the time of the reading, 
    only the end time should be set. 
    This will be used as the timestamp for the reading."""
    id = createDataSource('height.json')
    now = create_dataPointns(datetime.now())
    point = {
        "dataTypeName": "com.google.height",
        "startTimeNanos": f"{now}",
        "endTimeNanos": f"{now}",
        "value": [
            {
                "fpVal": f"{altura}"
            }
        ]
    }
    create_dataset(now, now, point=point, dataSourceId=id)


def adicionar_passos(passos, tempo_Atividade):
    """This data type captures the number of steps taken since the last reading. 
    Each step is only reported once so data points shouldn't have overlapping time. 
    The start time of each data point should represent the start of the interval in which steps were taken.
    The start time must be equal to or greater than the end time of the previous data point. 
    Adding all of the values together for a period of time calculates the total number of steps during that period."""
    id = createDataSource('step.json')
    inicio = create_dataPointns(
        datetime.now()+timedelta(minutes=-tempo_Atividade))
    fim = create_dataPointns(datetime.now())
    point = {
        "dataTypeName": "com.google.step_count.delta",
        "startTimeNanos": f"{inicio}",
        "endTimeNanos": f"{fim}",
        "value": [
            {
                "intVal": f"{passos}"
            }
        ]
    }
    create_dataset(inicio, fim, point=point, dataSourceId=id)


def adicionar_Bmr(bmr):
    """This data type captures the BMR of a user, in kilocalories. Each data point represents 
    The number of kilocalories a user would burn 
    if at rest all day, based on their height and weight. 
    Only the end time should be set. This will be used as the timestamp for the reading."""
    id = createDataSource('bmr.json')

    now = create_dataPointns(datetime.now())
    point = {
        "dataTypeName": "com.google.calories.bmr",
        "startTimeNanos": f"{now}",
        "endTimeNanos": f"{now}",
        "value": [
            {
                "fpVal": f"{bmr}"
            }
        ]
    }
    create_dataset(now, now, point=point, dataSourceId=id)


def adicionar_caloriasQueimadas(cal, tempo_Atividade):
    """This data type captures the total calories (in kilocalories) burned by the user, 
    including calories burned at rest (BMR). 
    Each data point represents the total kilocalories burned over a time interval, 
    so both the start and end times should be set."""
    id = createDataSource('caloriesburned.json')
    inicio = create_dataPointns(
        datetime.now()+timedelta(minutes=-tempo_Atividade))
    fim = create_dataPointns(datetime.now())
    point = {
        "dataTypeName": "com.google.calories.expended",
        "startTimeNanos": f"{inicio}",
        "endTimeNanos": f"{fim}",
        "value": [
            {
                "fpVal": f"{cal}"
            }
        ]
    }
    create_dataset(inicio, fim, point=point, dataSourceId=id)


def adicionar_HeartHate(bpm):
    id = createDataSource('hearthate.json')

    now = create_dataPointns(datetime.now())
    point = {
        "dataTypeName": "com.google.heart_rate.bpm",
        "startTimeNanos": f"{now}",
        "endTimeNanos": f"{now}",
        "value": [
            {
                "fpVal": f"{bpm}"
            }
        ]
    }
    create_dataset(now, now, point=point, dataSourceId=id)


def adicionar_HeartPoints(hp):
    """This data type captures the number of Heart Points a user has earned, from all their activity. 
    Each data point represents the number of Heart Points calculated for a time interval."""
    id = createDataSource('heartpoints.json')
    inicio = create_dataPointns(
        datetime.now())
    fim = inicio
    point = {
        "dataTypeName": "com.google.heart_minutes",
        "startTimeNanos": f"{inicio}",
        "endTimeNanos": f"{fim}",
        "value": [
            {
                "fpVal": f"{hp}"
            }
        ]
    }
    create_dataset(inicio, fim, point=point, dataSourceId=id)


def adicionar_atividade(atv, tempo_Atividade):
    """Each data point represents a single continuous set of a workout exercise performed by a user. 
    The data point contains fields for the exercise type (for example resistance exercises or weight training), 
    the number of repetitions of the exercise, the duration of the exercise, and the resistance."""

    id = createDataSource('activityType.json')
    inicio = create_dataPointns(
        datetime.now()+timedelta(minutes=-tempo_Atividade))
    fim = create_dataPointns(
        datetime.now())
    point = {
        "dataTypeName": "com.google.activity.segment",
        "startTimeNanos": f"{inicio}",
        "endTimeNanos": f"{fim}",
        "value": [
            {
                "intVal": f"{atv}"
            }
        ]
    }
    create_dataset(inicio, fim, point=point, dataSourceId=id)


def adicionar_Body_FatPercentage(cfp):
    """This data type captures the body fat percentage of a user. 
    Each data point represents a person's total body fat as a percentage of their total body mass."""
    # com.google.body.fat.percentage
    pass


if __name__ == "__main__":
    # adicionar_altura(1.78)
    # adicionar_peso(80)
    # adicionar_HeartHate(130.5)
    #adicionar_caloriasQueimadas(85, 10)
    # adicionar_Bmr(2100)
    # adicionar_distanciaPercorrida(200,30)
    # adicionar_passos(500,10)
    # 88 representa o valor da atividade esteira
    #adicionar_atividade(88, 30)
    # adicionar_HeartPoints(15)
    # adicionar_velocidade_esteira(10)
    adicionar_Body_FatPercentage(10.5)
