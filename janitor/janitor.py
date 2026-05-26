import boto3
import json
import argparse
from datetime import datetime, timezone
from constants import PRICING, REQUIRED_TAGS

parser = argparse.ArgumentParser()

parser.add_argument("--dry-run", action="store_true", default=True)
parser.add_argument("--delete", action="store_true")
parser.add_argument("--stopped-days", type=int, default=14)

args = parser.parse_args()

ec2 = boto3.client(
    "ec2",
    region_name="us-east-1",
    endpoint_url="http://localhost:4566",
    aws_access_key_id="test",
    aws_secret_access_key="test"
)

findings = []

def get_tags(tag_list):
    if not tag_list:
        return {}

    return {tag["Key"]: tag["Value"] for tag in tag_list}

def missing_required(tags):
    return any(tag not in tags for tag in REQUIRED_TAGS)

# Check unattached EBS volumes
volumes = ec2.describe_volumes()["Volumes"]

for volume in volumes:
    if volume["State"] == "available":

        tags = get_tags(volume.get("Tags", []))

        findings.append({
            "resource_id": volume["VolumeId"],
            "resource_type": "ebs_volume",
            "reason": "unattached",
            "age_days": 0,
            "estimated_monthly_cost_usd": (
                volume["Size"] * PRICING["ebs_gp3_per_gb"]
            ),
            "tags": tags,
            "suggested_action": "delete",
            "safe_to_auto_delete": False
        })

# Check stopped EC2 instances
reservations = ec2.describe_instances()["Reservations"]

for reservation in reservations:
    for instance in reservation["Instances"]:

        tags = get_tags(instance.get("Tags", []))

        if instance["State"]["Name"] == "stopped":

            findings.append({
                "resource_id": instance["InstanceId"],
                "resource_type": "ec2_instance",
                "reason": "stopped",
                "age_days": 0,
                "estimated_monthly_cost_usd": (
                    PRICING["stopped_instance_monthly"]
                ),
                "tags": tags,
                "suggested_action": "terminate",
                "safe_to_auto_delete": False
            })

        # Missing required tags
        if missing_required(tags):

            findings.append({
                "resource_id": instance["InstanceId"],
                "resource_type": "ec2_instance",
                "reason": "missing_required_tags",
                "age_days": 0,
                "estimated_monthly_cost_usd": 0,
                "tags": tags,
                "suggested_action": "tag_resource",
                "safe_to_auto_delete": False
            })

# Check Elastic IPs
addresses = ec2.describe_addresses()["Addresses"]

for address in addresses:

    if "InstanceId" not in address:

        findings.append({
            "resource_id": address["AllocationId"],
            "resource_type": "elastic_ip",
            "reason": "unassociated",
            "age_days": 0,
            "estimated_monthly_cost_usd": (
                PRICING["eip_monthly"]
            ),
            "tags": {},
            "suggested_action": "release",
            "safe_to_auto_delete": False
        })

# Final report structure
report = {
    "scan_timestamp": datetime.now(
        timezone.utc
    ).isoformat(),

    "account_id": "000000000000",

    "region": "us-east-1",

    "summary": {
        "total_orphans": len(findings),

        "estimated_monthly_waste_usd": round(
            sum(
                finding["estimated_monthly_cost_usd"]
                for finding in findings
            ),
            2
        )
    },

    "findings": findings
}

# Write JSON report
with open("report.json", "w") as json_file:
    json.dump(report, json_file, indent=2)

# Write Markdown summary
with open("report.md", "w") as markdown_file:

    markdown_file.write("# Cost Janitor Report\n\n")

    if findings:

        for finding in findings:

            markdown_file.write(
                f"- {finding['resource_type']} "
                f"{finding['resource_id']} "
                f"({finding['reason']})\n"
            )

    else:
        markdown_file.write(
            "No orphaned resources found.\n"
        )

# Print report to console
print(json.dumps(report, indent=2))

# Fail CI in dry-run mode if findings exist
if args.dry_run and findings:
    exit(1)