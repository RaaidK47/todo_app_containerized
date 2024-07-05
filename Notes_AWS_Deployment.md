* Connect to EC2 using SSH.
* Pull Project from Github.
    * For these 2 steps, get detailed info from `recipe-api` project of Django REST API.

* If there is an error in fetching Docker Images (e.g. http+docker) error.
    * Uninstall `requests` package using `pip unistall requests`
    * Install `requests==2.31.0` using `pip install requests==2.31.0`

* Make sure that docker daemon is running.
* Change Directory to `todo_app_containerized`
* Start Project using `docker-compose -f compose.yaml up -d`

* Make Sure to 
    * Allow Ports 8000 & 8501 & 5432 to accept all TCP traffic.
    * I.e. allow ports that are forwarded in Docker.
    * Create a `.env` file in *api* folder. Use nano to add `DATABASE_URL=postgresql+psycopg2://raaidk:pass123@PostgresContainer/todo_database`

**Note:** App version with Kafka will not be run in EC2 instance due to hardware limitations. Use old version.

* Git Clone using ssh from github
* Checkout to old version using command
  * `git checkout 4c29e1d3ed4e10633b882650aefa66c6f68205de