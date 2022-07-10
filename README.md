# thermal-storage
A program which simulates the behavior of a thermal storage.

## Running simulations
### 1. Clone the repository to a local directory
To run simulations, you can either run src/main.py script but this is prone to issues if there are dependencies missing.
Recommended is to run them in a Docker container.
### 2. Install [Docker](https://www.docker.com/get-started/)
### 3. Build a docker image 
Open the command line. Specify a custom name for the image instead of IMAGE_NAME.
```
docker build -t IMAGE_NAME .
```
### 4. Run a container
Based on the image, run a container with the image name. We export data and need to keep data from simulations, this is why we need to mount the directory from the host machine into the container (-v flag).

On **Windows**
```
docker run -it -v ${pwd}:/thermal-storage IMAGE_NAME
```
On **Linux/MacOS**
```
docker run -it -v "$(pwd)":/thermal-storage IMAGE_NAME
```
## Debugging
### Enter bash before running simulations
On **Windows**
```
docker run -it -v ${pwd}:/thermal-storage IMAGE_NAME bash
```
On **Linux/MacOS**
```
docker run -it -v "$(pwd)":/thermal-storage IMAGE_NAME bash
```
`cd thermal-storage` to get into the directory in the container.


