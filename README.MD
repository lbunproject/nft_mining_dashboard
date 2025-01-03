# LBUN NFT Mining Dashboard

![LBUN NFT Mining Dashboard](https://your-repo-url.com/banner-image.png)

Welcome to the **LBUN NFT Mining Dashboard**! This interactive dashboard provides comprehensive insights into NFT mining activities, including performance metrics, rewards distribution, ownership statistics, and more. Built with **Streamlit** and **Docker**, it offers a seamless user experience both locally and in production environments.

## Table of Contents

- [Features](#features)
- [Demo](#demo)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Clone the Repository](#clone-the-repository)
  - [Setting Up the Environment](#setting-up-the-environment)
- [Running the Dashboard Locally](#running-the-dashboard-locally)
- [Deployment Using Docker](#deployment-using-docker)
  - [1. Dockerfile](#1-dockerfile)
  - [2. Building the Docker Image](#2-building-the-docker-image)
  - [3. Running the Docker Container](#3-running-the-docker-container)
  - [4. Configuring Nginx as a Reverse Proxy](#4-configuring-nginx-as-a-reverse-proxy)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
- [Data Files](#data-files)
  - [nft_details.csv](#nft_detailscsv)
  - [winner_list.csv](#winner_listcsv)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features

- **Interactive Dashboard:** Visualize NFT mining data with dynamic charts and tables.
- **Leaderboards:** 
  - Top Ten Owners by Rewards Won
  - Top Ten Owners by Wins
  - Top Ten Owners by NFTs Owned
  - Top Ten Equipment/Boost Combinations by Rewards Won
  - Bottom Ten Owners by Rewards Won
  - Bottom Ten Owners by Wins
- **Filters:** Filter NFTs based on Equipment and Wallet Address.
- **Lifecycle Tracking:** Display the remaining life of each NFT with indicators for expired NFTs.
- **Responsive Design:** Accessible across various devices and screen sizes.
- **Dockerized Deployment:** Easy to deploy and scale using Docker and Nginx.

## Demo

![Dashboard Screenshot](https://your-repo-url.com/dashboard-screenshot.png)

*Explore the dashboard in action! [View Live Demo](http://159.223.229.105/dashboard)*

## Prerequisites

Before you begin, ensure you have met the following requirements:

- **Operating System:** Linux (preferred for Docker deployment) or Windows/MacOS.
- **Python:** Version 3.9 or higher.
- **Docker:** Installed and running on your machine.
- **Nginx:** Installed if deploying with reverse proxy (optional but recommended).
- **Git:** For cloning the repository.
- **Network Access:** Ensure required ports (default: 8501 for Streamlit) are accessible.

## Installation

### Clone the Repository

```bash
git clone https://github.com/your-username/lbun-nft-mining-dashboard.git
cd lbun-nft-mining-dashboard
```

### Setting Up the Environment

It's recommended to use a virtual environment to manage dependencies.

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt
```

## Running the Dashboard Locally

To run the Streamlit dashboard on your local machine:

```bash
streamlit run streamlit_app.py
```

- **Access the Dashboard:** Open your browser and navigate to `http://localhost:8501`

## Deployment Using Docker

Deploying the Streamlit app using Docker ensures consistency across different environments and simplifies the deployment process.

### 1. Dockerfile

Create a `Dockerfile` in the root directory of your project with the following content:

```dockerfile
# Use the official lightweight Python image.
FROM python:3.9-slim

# Set the working directory in the container.
WORKDIR /app

# Install system dependencies.
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container.
COPY requirements.txt .

# Install Python dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app's code into the container.
COPY . .

# Expose the port that Streamlit runs on.
EXPOSE 8501

# Define environment variables.
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLECORS=false

# Health check to ensure Streamlit is running.
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run the Streamlit app.
ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Explanation:**

- **Base Image:** Uses `python:3.9-slim` for a lightweight Python environment.
- **Working Directory:** Sets `/app` as the working directory inside the container.
- **System Dependencies:** Installs necessary system packages like `build-essential`, `curl`, and `git`.
- **Python Dependencies:** Copies `requirements.txt` and installs Python packages using `pip`.
- **App Code:** Copies all your application code into the container.
- **Port Exposure:** Exposes port `8501`, the default port for Streamlit.
- **Environment Variables:**
  - `STREAMLIT_SERVER_PORT`: Specifies the port Streamlit listens on.
  - `STREAMLIT_SERVER_HEADLESS`: Runs Streamlit in headless mode.
  - `STREAMLIT_SERVER_ENABLECORS`: Disables CORS to allow Nginx to proxy requests.
- **Health Check:** Ensures the Streamlit app is running by checking the health endpoint.
- **Entry Point:** Defines the command to run your Streamlit app.

### 2. Building the Docker Image

Navigate to the directory containing your `Dockerfile` and run:

```bash
docker build -t lbun_streamlit_app .
```

- **`-t lbun_streamlit_app`**: Tags the image with the name `lbun_streamlit_app`.
- **`.`**: Specifies the current directory as the build context.

*Ensure that your `requirements.txt` and `streamlit_app.py` are present in this directory.*

### 3. Running the Docker Container

Run the Docker container for your Streamlit app and connect it to the same Docker network as your existing Nginx container.

#### Identify Your Docker Network

First, determine the Docker network your Nginx container is using:

```bash
docker network ls
```

Assuming your existing containers are part of a network named `oracle_feeder_network`, connect the Streamlit app to this network.

#### Run the Streamlit Container

```bash
docker run -d \
  --name lbun_streamlit_app \
  --network oracle_feeder_network \
  -p 8501:8501 \
  lbun_streamlit_app
```

- **`-d`**: Runs the container in detached mode.
- **`--name lbun_streamlit_app`**: Names the container for easy reference.
- **`--network oracle_feeder_network`**: Connects the container to the specified Docker network.
- **`-p 8501:8501`**: Maps port `8501` of the container to port `8501` on the host.
- **`lbun_streamlit_app`**: Specifies the image to use.

*If you're using Portainer, you can perform these steps through its UI by creating a new container with the specified configurations.*

### 4. Configuring Nginx as a Reverse Proxy

To access your Streamlit app via Nginx, update your Nginx configuration to proxy requests to the Streamlit container.

#### Sample Nginx Configuration

Assuming you want to access your Streamlit app at `http://159.223.229.105/dashboard`, add the following configuration to your Nginx setup.

##### Edit Nginx Configuration

Locate your Nginx configuration file. This could be within your Docker setup or mapped to a host directory. Common locations include:

- `/etc/nginx/nginx.conf`
- `/etc/nginx/sites-available/default`
- A custom path defined in your Docker setup.

##### Add Reverse Proxy Settings

Add the following `location` block within your `server` block:

```nginx
server {
    listen 80;
    server_name 159.223.229.105;

    # Existing configurations...

    location /dashboard/ {
        proxy_pass http://lbun_streamlit_app:8501/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Optional WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Existing configurations...
}
```

**Explanation:**

- **`location /dashboard/`**: Defines the URL path to access the Streamlit app.
- **`proxy_pass http://lbun_streamlit_app:8501/;`**: Routes requests to the Streamlit container using its Docker service name (`lbun_streamlit_app`) and port `8501`.
- **Headers:**
  - **`Host`**, **`X-Real-IP`**, **`X-Forwarded-For`**, **`X-Forwarded-Proto`**: Forward client information to Streamlit.
- **WebSocket Support:**
  - Ensures that WebSockets (if used by Streamlit) function correctly.

##### Reload Nginx Configuration

After updating the configuration, reload Nginx to apply the changes:

```bash
docker exec -it oracle_feeder_nginx_1 nginx -s reload
```

*Replace `oracle_feeder_nginx_1` with your actual Nginx container name if different.*

*Alternatively, if you have access to the host system's Nginx:*

```bash
sudo nginx -s reload
```

## Configuration

### Environment Variables

You can configure various aspects of the Streamlit app using environment variables. These are already set in the `Dockerfile`, but you can modify them as needed.

- **`STREAMLIT_SERVER_PORT`**: Port Streamlit listens on (default: `8501`).
- **`STREAMLIT_SERVER_HEADLESS`**: Runs Streamlit in headless mode (`true`).
- **`STREAMLIT_SERVER_ENABLECORS`**: Disables CORS to allow Nginx to proxy requests (`false`).

To override these settings, you can pass different environment variables when running the Docker container:

```bash
docker run -d \
  --name lbun_streamlit_app \
  --network oracle_feeder_network \
  -p 8501:8501 \
  -e STREAMLIT_SERVER_PORT=8501 \
  -e STREAMLIT_SERVER_HEADLESS=true \
  -e STREAMLIT_SERVER_ENABLECORS=false \
  lbun_streamlit_app
```

## Data Files

The dashboard relies on two primary CSV files:

### `nft_details.csv`

Contains detailed information about each NFT.

**Columns:**

- **`token_id`**: Unique identifier for the NFT.
- **`market`**: The marketplace where the NFT is listed.
- **`equipment`**: Type of equipment associated with the NFT.
- **`boost`**: Boost level or type.
- **`owner`**: Wallet address of the NFT owner.
- **`minted`**: Date when the NFT was minted (format: `mm/dd/yyyy`).

**Sample:**

| token_id | market    | equipment | boost          | owner                                    | minted    |
|----------|-----------|-----------|----------------|------------------------------------------|-----------|
| 1        | OpenSea   | TNT       | Standard       | 0xA1B2C3D4E5F60718293A4B5C6D7E8F9A0B1C2D3 | 01/01/2024 |
| 2        | Rarible   | Excavator | Precision Control | 0xB1C2D3E4F5G60718293A4B5C6D7E8F9A0B1C2D3 | 01/02/2024 |

### `winner_list.csv`

Tracks the winners of each virtual block.

**Columns:**

- **`Virtual Block`**: Identifier for the virtual block.
- **`Date`**: Date of the virtual block.
- **`Time`**: Time of the virtual block.
- **`Block`**: Block number.
- **`Hash`**: Hash of the block.
- **`Winner (Row)`**: The row number in `nft_details.csv` representing the winning NFT.
- **`Reward (BASE)`**: Reward amount in BASE tokens.
- **`nftLife`**: Total lifespan of the NFT (days).
- **`NumofMiners`**: Number of miners participating.

**Sample:**

| Virtual Block | Date      | Time  | Block    | Hash                                                            | Winner (Row) | Reward (BASE) | nftLife | NumofMiners |
|---------------|-----------|-------|----------|-----------------------------------------------------------------|--------------|---------------|---------|-------------|
| 1             | 01/01/2024 | 00:00 | 16092971 | E4ED3880BC7A4CD2F1FE2F5B362833254B97579F93626115138EB17F40FD750D | 1            | 61            | 365     | 240         |
| 2             | 01/01/2024 | 01:00 | 16093571 | 8E809EE54C48BA9DAF8C43BBAF90710E1BA60C6888A7A9203234ECB08F0845EF | 3            | 89.67         | 365     | 240         |
| 3             | 01/01/2024 | 02:00 | 16094171 | 4CFFA36C205BADC0B76E7FF43116818C4590D4E3E3D2FBE96704A97AD701D657 | 2            | 61            | 365     | 240         |

## Troubleshooting

### Serialization Error with `life_left` Column

**Error Message:**

```
Serialization of dataframe to Arrow table was unsuccessful due to: ("Expected bytes, got a 'int' object", 'Conversion failed for column life_left with type object'). Applying automatic fixes for column types to make the dataframe Arrow-compatible.
```

**Cause:**

- The `life_left` column contains mixed data types (`int` and `str`), which is incompatible with Arrow's serialization requirements.

**Solution:**

- Ensure that the `life_left` column contains only strings by converting all integer values to strings and retaining `"Expired"` as a string.

**Implemented Fix:**

```python
# Calculate 'life_left'
nft_details['life_left'] = 365 - (today_date - nft_details['minted_date']).dt.days
# Convert 'life_left' to string, replace negatives with 'Expired', and cap at 365
nft_details['life_left'] = nft_details['life_left'].apply(lambda x: str(min(x, 365)) if x >= 0 else 'Expired')
```

**Steps to Implement:**

1. Open `streamlit_app.py`.
2. Locate the section where `life_left` is calculated.
3. Replace the existing `life_left` calculation with the above code snippet.
4. Save the changes and rebuild your Docker image.
5. Redeploy the Docker container.

### General Tips

- **Check Docker Logs:**

  ```bash
  docker logs -f lbun_streamlit_app
  ```

- **Verify Network Connectivity:**

  Ensure that Nginx and Streamlit containers are on the same Docker network.

- **Health Checks:**

  Ensure that health checks are passing to confirm the Streamlit app is running.

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. **Fork the Repository**
2. **Create a Feature Branch**

   ```bash
   git checkout -b feature/YourFeature
   ```

3. **Commit Your Changes**

   ```bash
   git commit -m "Add Your Feature"
   ```

4. **Push to the Branch**

   ```bash
   git push origin feature/YourFeature
   ```

5. **Open a Pull Request**

   Describe your changes and submit the pull request for review.

## License

Distributed under the [MIT License](LICENSE).

## Contact

**Your Name** – [@your-twitter](https://twitter.com/your-twitter) – your.email@example.com

Project Link: [https://github.com/your-username/lbun-nft-mining-dashboard](https://github.com/your-username/lbun-nft-mining-dashboard)

---

*This README was generated to provide comprehensive guidance on setting up, running, and deploying the LBUN NFT Mining Dashboard. For any further assistance, please reach out through the contact information provided above.*