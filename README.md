# Developing dockerPMS

### Stack Requirements

You need a copy of Docker and Python3.12 on your system to build and develop this project.

I suggest using Pycharm Professional as it should be an out-of-the-box solution.

### Structure

- `DjangoPMS/DjangoPMS` - Top Level of the program. Things like settings and Exposing URLs will be registered here.
- `DjangoPMS/backend` - Backend for the program. Things like models, API will be registered here.
- `DjangoPMS/frontend` - frontend for the program. Things HTML, CSS, Views and URLs will be registered here.


### Running the project
If you aren't using Pycharm where there is a Run Config set up to build the project.
```bash
docker-compose up                             #Start Containers
docker-compose down                           #Stop Containers
```
If you want to build without cache (Useful if changes in the files are made)
```bash
docker-compose up --build --force-recreate
```


### macOS & Linux Specifics **IMPORTANT**
You need to make DjangoPMS/entrypoint.sh executable so run this command

```bash
chmod +x DjangoPMS/entrypoint.sh
```

This project has been completed. Friday 17th May 2024
