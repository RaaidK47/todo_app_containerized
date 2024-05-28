* Connect to EC2 using SSH.
* Pull Project from Github.
    * For these 2 steps, get detailed info from `recipe-api` project of Django REST API.

* If there is an error in fetching Docker Images (e.g. http+docker) error.
    * Uninstall `requests` package using `pip unistall requests`
    * Install `requests==2.31.0` using `pip install requests==2.31.0`

* Make sure that docker daemon is running.

* Start Project using `docker-compose -f compose.yaml up -d`