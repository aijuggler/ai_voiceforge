# AI VoiceForge: Podcast Generator

This project is a web application that generates podcasts using AI. It consists of a Python backend for the core logic and a JavaScript frontend for the user interface.

## Prerequisites

Before you begin, ensure you have the following tools installed:

*   [Docker Desktop](https://www.docker.com/products/docker-desktop)
*   [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
*   An active Azure Subscription

## Deploying to Azure

This guide will walk you through deploying the application to Azure using Azure App Service for Containers.

### Step 1: Log in to Azure

Open your terminal and log in to your Azure account:

```bash
az login
```

### Step 2: Create Azure Resources

You'll need a Resource Group to manage your Azure services and a Container Registry to store your Docker images.

1.  **Create a Resource Group:**
    A resource group is a container that holds related resources for an Azure solution.

    ```bash
az group create --name ai-voiceforge-rg --location eastus
```

2.  **Create an Azure Container Registry (ACR):**
    ACR is a private Docker registry in Azure. Replace `<your-acr-name>` with a unique name for your registry (e.g., `aivoiceforgeregistry`).

    ```bash
az acr create --resource-group ai-voiceforge-rg --name <your-acr-name> --sku Basic --admin-enabled true
```

3.  **Log in to Your ACR:**
    This allows Docker to push images to your private registry.

    ```bash
az acr login --name <your-acr-name>
```

### Step 3: Build and Push Docker Images

Next, you'll build the Docker images for the frontend and backend, tag them, and push them to your ACR.

1.  **Get Your ACR Login Server:**
    You'll need this to tag your images correctly.

    ```bash
az acr show --name <your-acr-name> --query loginServer --output tsv
```
    This command will output a URL like `<your-acr-name>.azurecr.io`.

2.  **Build and Push the Backend Image:**
    Run these commands from the root directory of the project.

    ```bash
    # Build the backend image
    docker build -t backend:latest ./backend

    # Tag the image to point to your ACR
    docker tag backend:latest <your-acr-name>.azurecr.io/backend:latest

    # Push the image to your ACR
    docker push <your-acr-name>.azurecr.io/backend:latest
    ```

3.  **Build and Push the Frontend Image:**

    ```bash
    # Build the frontend image
    docker build -t frontend:latest ./frontend

    # Tag the image to point to your ACR
    docker tag frontend:latest <your-acr-name>.azurecr.io/frontend:latest

    # Push the image to your ACR
    docker push <your-acr-name>.azurecr.io/frontend:latest
    ```

### Step 4: Prepare the Docker Compose File for Azure

You need a version of your `compose.yml` that points to the images in your ACR instead of building them locally.

1.  Create a new file named `compose.azure.yml` in the root of your project.
2.  Add the following content to it, replacing `<your-acr-name>.azurecr.io` with your ACR login server URL:

    ```yaml
    version: "3.8"
    services:
      backend:
        image: <your-acr-name>.azurecr.io/backend:latest
        ports:
          - "8000:8000"
        env_file:
          - .env
      frontend:
        image: <your-acr-name>.azurecr.io/frontend:latest
        ports:
          - "80:80" # Azure App Service directs traffic to port 80
        depends_on:
          - backend
    ```

### Step 5: Deploy to Azure App Service

Now you can create the App Service and deploy your containers.

1.  **Create an App Service Plan:**
    This defines the computing resources for your app.

    ```bash
az appservice plan create --name ai-voiceforge-plan --resource-group ai-voiceforge-rg --is-linux
```

2.  **Create the Multi-Container Web App:**
    This command tells Azure to create a web app using your Docker Compose file. Replace `<your-unique-app-name>` with a unique name for your application (e.g., `ai-voiceforge-app`).

    ```bash
az webapp create \
  --resource-group ai-voiceforge-rg \
  --plan ai-voiceforge-plan \
  --name <your-unique-app-name> \
  --multicontainer-config-type COMPOSE \
  --multicontainer-config-file compose.azure.yml
```

3.  **Configure App Service to Use Your ACR:**
    Tell your new App Service how to pull images from your private registry.

    ```bash
az webapp config container set \
  --name <your-unique-app-name> \
  --resource-group ai-voiceforge-rg \
  --docker-registry-server-url https://<your-acr-name>.azurecr.io \
  --docker-registry-server-user $(az acr credential show --name <your-acr-name> --query username --output tsv) \
  --docker-registry-server-password $(az acr credential show --name <your-acr-name> --query passwords[0].value --output tsv)
```

4.  **Set Environment Variables:**
    Your backend needs environment variables (like API keys) to run. You must set them in the App Service configuration. For each variable in your `.env` file, run the following command:

    ```bash
az webapp config appsettings set \
  --resource-group ai-voiceforge-rg \
  --name <your-unique-app-name> \
  --settings "VARIABLE_NAME=your_value" "ANOTHER_VARIABLE=another_value"
```

### Step 6: Access Your Application

Your application is now deployed! You can access it at the following URL:

`http://<your-unique-app-name>.azurewebsites.net`

It may take a few minutes for the containers to start up. You can check the logs in the Azure portal under your App Service's "Log stream" section.
