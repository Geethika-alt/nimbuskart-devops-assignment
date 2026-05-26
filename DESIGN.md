## Architecture Decisions

- Terraform was chosen for Infrastructure as Code to ensure reproducible and version-controlled infrastructure deployments.
- The infrastructure was modularized using Terraform modules to improve maintainability and scalability.
- LocalStack was used to simulate AWS services locally and avoid unnecessary cloud costs during development.
- GitHub Actions was selected for CI/CD automation because of its native GitHub integration and ease of workflow management.
- Python was used for the Cost Janitor utility because of its strong AWS SDK (boto3) ecosystem and scripting simplicity.
- The janitor tool generates both Markdown and JSON reports for human readability and machine processing.


## Security Considerations

- Sensitive credentials are intended to be stored using GitHub Secrets instead of hardcoding values in the repository.
- IAM permissions should follow the principle of least privilege in production deployments.
- Terraform state files should not be committed to source control because they may contain infrastructure metadata.
- S3 bucket versioning and encryption can be enabled in production environments for better durability and security.
- Input validation and tagging standards were added to improve governance and resource traceability.


## Monitoring Ideas

- CloudWatch metrics and alarms can be configured for infrastructure health monitoring.
- GitHub Actions workflow runs provide CI/CD execution visibility and deployment tracking.
- The janitor reports can be integrated with Slack or email notifications for operational alerts.
- Centralized logging can be implemented using CloudWatch Logs or ELK stack integrations.
- Infrastructure drift detection can be added using scheduled Terraform plan executions.


## Scaling Approach

- Terraform modules allow the infrastructure to scale across multiple environments such as development, staging, and production.
- Additional AWS services can be integrated without major architectural changes.
- CI/CD workflows can be extended to support multiple deployment stages and approval gates.
- The janitor utility can be enhanced to scan multiple AWS accounts and regions.
- Containerization support can be added for easier deployment and portability.


## Future Improvements

- Add automated Terraform testing using Terratest or Checkov.
- Add unit tests and integration tests for the janitor utility.
- Integrate notifications using Slack, Microsoft Teams, or email.
- Implement dashboard visualization for cost reports.
- Add support for additional AWS resource cleanup checks.
- Improve LocalStack compatibility for lifecycle configuration testing.
- Add Docker Compose support for easier local environment setup.


