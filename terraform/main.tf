provider "google" {
  project = var.project_id
  region  = var.region
}

# GCP Service Account for the application
resource "google_service_account" "va_app_sa" {
  account_id   = "va-app-sa"
  display_name = "VA Application Service Account"
  description  = "Service account for Vulnerability Assessment application"
}

# Grant necessary permissions to the service account
resource "google_project_iam_member" "va_app_scc_viewer" {
  project = var.project_id
  role    = "roles/securitycenter.findingsViewer"
  member  = "serviceAccount:${google_service_account.va_app_sa.email}"
}

resource "google_project_iam_member" "va_app_logging_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.va_app_sa.email}"
}

# GKE Cluster for hosting the application
resource "google_container_cluster" "va_cluster" {
  name     = "va-cluster"
  location = var.region
  
  remove_default_node_pool = true
  initial_node_count       = 1
  
  network    = google_compute_network.vpc.name
  subnetwork = google_compute_subnetwork.subnet.name
}

resource "google_container_node_pool" "va_nodes" {
  name       = "va-node-pool"
  location   = var.region
  cluster    = google_container_cluster.va_cluster.name
  node_count = 2
  
  node_config {
    machine_type = "e2-medium"
    
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
    
    service_account = google_service_account.va_app_sa.email
  }
}

# VPC Network
resource "google_compute_network" "vpc" {
  name                    = "va-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "subnet" {
  name          = "va-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.vpc.name
}

# Cloud Run alternative (simpler deployment)
resource "google_cloud_run_service" "va_service" {
  name     = "va-reports-service"
  location = var.region
  
  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/va-backend:latest"
        
        env {
          name  = "GOOGLE_CLOUD_PROJECT"
          value = var.project_id
        }
      }
      
      service_account_name = google_service_account.va_app_sa.email
    }
  }
  
  traffic {
    percent         = 100
    latest_revision = true
  }
}

# IAM policy to allow public access to Cloud Run service
data "google_iam_policy" "noauth" {
  binding {
    role = "roles/run.invoker"
    members = [
      "allUsers",
    ]
  }
}

resource "google_cloud_run_service_iam_policy" "noauth" {
  location    = google_cloud_run_service.va_service.location
  project     = google_cloud_run_service.va_service.project
  service     = google_cloud_run_service.va_service.name
  
  policy_data = data.google_iam_policy.noauth.policy_data
}
