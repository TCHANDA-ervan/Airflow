from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.spark_submit import SparkSubmitOperator

from program import injection_meteo

# Définition de la configuration du DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Initialisation du DAG
dag = DAG(
    'meteo',
    default_args=default_args,
    description='les meteo previsionnel',
    schedule_interval=timedelta(days=1),  # Planification quotidienne
)

# Tâche 1 : Exécution de spark-submit pour le code Scala
# Définir la tâche Spark
spark_task = SparkSubmitOperator(
    task_id='spark_job_task',
    conn_id='spark_default',  # Connexion à la configuration Spark dans Airflow
    application='/home/ubuntu/Downloads/mnmcount/scala/target/scala-2.12/main-scala-mnmc_2.12-1.0.jar',  # Chemin vers le fichier JAR Spark
    name='Spark Job Task',  # Nom de la tâche
    verbose=True,
    conf={
        'spark.master': 'local[*]',  # Spécifier le mode de maître Spark
        'spark.executor.memory': '2g',  # Configuration de la mémoire de l'exécuteur
    },
    dag=dag,
)

# Tâche 2 : Exécutez une fonction Python
def python_function():
    print("Exécution de la fonction Python!")

python_task = PythonOperator(
    task_id='python_task',
    python_callable=injection_meteo,
    provide_context=True,
    dag=dag,
)

# Définir l'ordre d'exécution des tâches
python_task >> spark_task  # Correction de la syntaxe
