# Agentic AI: Azure Landing Zone Visualizer & Risk Analyzer

This project provides an autonomous agent to scan Azure subscriptions within a landing zone, map resource dependencies, identify security and cost risks, and generate an interactive, downloadable HTML graph report.

The application is containerized with Docker and designed for secure, multi-tenant deployment in Azure Container Instances (ACI), authenticating via Azure Active Directory.

## Features

- **Comprehensive Scanning:** Discovers a wide range of Azure resources:
  - **Networking:** VNets, Subnets, VNet Peerings, VNet Gateways, Virtual WANs, Route Tables, Network Security Groups (NSGs) & Rules.
  - **Governance & Security:** Management Groups, IAM Role Assignments, Azure Policies, Microsoft Defender for Cloud alerts.
  - **Cost Management:** Azure Advisor recommendations and Reservation details.
- **Dependency Mapping:** Intelligently parses resource properties to build a dependency graph (e.g., Subnet -> VNet, Subnet -> NSG).
- **Risk Analysis:** Automatically highlights potential risks in the generated report.
- **Interactive Visualization:** Generates a dynamic HTML graph using `pyvis`, allowing users to explore the Azure environment visually.
- **Secure & Scalable:**
  - Runs in a secure, isolated Azure Container Instance.
  - Uses Azure AD for authentication with a multi-tenant App Registration, making it "plug and play" for different clients.
  - Leverages Managed Identity in ACI for passwordless access to Azure APIs.
- **Easy Deployment:** Includes an automation script to set up all required Azure infrastructure.

## Architecture

1.  **User** accesses the web application running on **Azure Container Instances (ACI)**.
2.  The ACI has a **System-Assigned Managed Identity**. This identity is granted `Reader` permissions on the target Azure scope (e.g., root Management Group).
3.  The Python application uses the `DefaultAzureCredential` library, which automatically uses the ACI's Managed Identity to authenticate with **Azure APIs**.
4.  The application scans all subscriptions and resources the Managed Identity can access.
5.  It processes the data, builds a dependency graph, and analyzes for risks.
6.  A self-contained, interactive `report.html` is generated and served back to the user for viewing and download.



## Highlighted Risks

The agent actively scans for and flags the following common configuration risks:

| Category      | Risk Description                                                              | Severity |
|---------------|-------------------------------------------------------------------------------|----------|
| **Network**   | NSG rule allows traffic from `Any` or `Internet` on sensitive ports (RDP/SSH).| **High**     |
| **Network**   | Subnet without an NSG attached.                                               | Medium   |
| **Network**   | Public IP address attached to a non-gateway/non-load-balancer resource.       | Medium   |
| **IAM**       | Excessive `Owner` roles assigned at the subscription scope.                   | **High**     |
| **IAM**       | Classic Administrators are still enabled on a subscription.                   | **High**     |
| **Security**  | High-severity alerts present in Microsoft Defender for Cloud.                 | **High**     |
| **Policy**    | Non-compliant resources against assigned Azure Policies.                      | Medium   |
| **Cost**      | "High Impact" cost-saving recommendations from Azure Advisor.                 | Low      |


## Prerequisites

- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- [Docker](https://www.docker.com/products/docker-desktop)
- An Azure account with permissions to create resources (Resource Groups, ACI, ACR) and create Azure AD App Registrations.

## Deployment Guide

The provided `deploy.sh` script automates these steps.

### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd azure-visualizer
```

### Step 2: Configure and Run the Deployment Script

The `deploy.sh` script will:
1.  Prompt for a unique name for your resources (e.g., `myclientviz`).
2.  Prompt for the Azure Tenant ID you want to scan.
3.  Create a Resource Group.
4.  Create an Azure Container Registry (ACR).
5.  Build the Docker image and push it to your new ACR.
6.  Create an Azure AD Application and Service Principal for multi-tenant authentication.
7.  Create an Azure Container Instance (ACI) with a Managed Identity.
8.  Grant the ACI's Managed Identity `Reader` role at the tenant root scope. **This requires Global Admin or User Access Administrator permissions.**
9.  Output the URL of the running application.

**Important:** The script requires elevated permissions (`User Access Administrator` or `Global Administrator`) to grant the `Reader` role at the tenant root (`/`). If you don't have these permissions, you can manually assign the `Reader` role on specific Management Groups or Subscriptions you want to scan.

```bash
chmod +x deploy.sh
./deploy.sh
```

### Step 3: Access the Application

Once the script completes, it will print the FQDN of your ACI instance. Open this URL in your browser to access the tool.

## Usage

1.  Navigate to the application URL.
2.  Click the "Start Scan & Generate Report" button.
3.  The scan may take several minutes depending on the size of your environment.
4.  Once complete, a link to the downloadable HTML report will appear.
5.  Click the link to view the interactive graph in your browser or right-click to save it.

## Code Structure
