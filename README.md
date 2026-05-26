

=======
## Overview

This project implements a lightweight FinOps and infrastructure automation solution for NimbusKart using Terraform, Python, GitHub Actions, and LocalStack. The Terraform stack provisions a reusable staging environment consisting of networking resources, EC2 instances, an S3 logging bucket, and intentionally orphaned infrastructure for testing. The Cost Janitor automation scans the environment for wasteful or orphaned AWS resources, generates JSON and Markdown reports, and integrates with GitHub Actions to enforce automated cost-governance checks during pull requests.


## How to run locally

```bash
git clone https://github.com/<your-username>/nimbuskart-devops-assignment.git

cd nimbuskart-devops-assignment

docker run -d -p 4566:4566 --name localstack -e ACTIVATE_PRO=0 localstack/localstack:latest

cd terraform

tflocal init

tflocal apply -auto-approve

cd ../janitor

python janitor.py --dry-run


## Architecture


                    +----------------------+
                    |      Developer       |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |    GitHub Actions    |
                    +----------+-----------+
                               |
                +--------------+--------------+
                |                             |
                v                             v
      +------------------+         +------------------+
      |    Terraform     |         |   Cost Janitor  |
      +------------------+         +------------------+
                |                             |
                v                             |
      +------------------+                    |
      |    LocalStack    |<-------------------+
      | (AWS Emulator)   |
      +------------------+
                |
                v
      +------------------+
      | AWS-like Resources|
      | EC2 / EBS / S3   |
      +------------------+

                |
                v

      +------------------+
      | report.json      |
      | report.md        |
      +------------------+


## Decisions & deviations

- SSH access from 0.0.0.0/0 is insecure for production environments but was retained because it was explicitly requested in the assignment specification.
- Static pricing constants were used instead of live AWS Pricing APIs to keep the Janitor deterministic, lightweight, and CI-friendly.
- An intentionally unattached EBS volume was provisioned to validate orphan-resource detection logic in the Janitor workflow.
- Terraform resources were modularized to improve maintainability and support future infrastructure reuse.
- LocalStack behavior differed slightly between local execution and GitHub Actions CI execution, particularly around lifecycle configuration handling.
      

## Trade-offs

- The Janitor currently uses static cost estimates rather than real-time AWS pricing data.
- The implementation focuses on AWS-compatible LocalStack resources and does not yet include native multi-cloud providers such as Azure or GCP.
- Automated deletion logic is intentionally conservative to reduce the risk of accidental outages.
- Advanced observability integrations such as Prometheus, Grafana, or Slack alerting were intentionally left out to keep the scope manageable.
- The workflow prioritizes reproducibility and assignment requirements over production-grade scalability.


## AI usage disclosure

- ChatGPT was used for troubleshooting LocalStack, and Python debugging issues during development.
- AI assistance was used to accelerate Terraform boilerplate generation and improve documentation structure.
- One issue encountered with AI-generated suggestions involved LocalStack image selection and lifecycle configuration compatibility, which required manual debugging and validation.
- The GitHub Actions debugging process and repository structure setup were completed manually to better understand the CI/CD workflow behavior.
 
